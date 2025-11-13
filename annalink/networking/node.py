"""
Node module for Annalink blockchain - FIXED VERSION.

This module implements the main blockchain node with P2P networking,
blockchain management, and message handling.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from ..core.blockchain import Blockchain
from ..core.transaction import Transaction
from ..core.block import Block
from .peer import Peer, PeerManager


class MessageType:
    """Message types for P2P communication."""
    HANDSHAKE = "handshake"
    GET_BLOCKS = "get_blocks"
    BLOCKS = "blocks"
    NEW_TRANSACTION = "new_transaction"
    NEW_BLOCK = "new_block"


class BlockchainNode:
    """
    Main blockchain node with P2P networking.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8333,
                 blockchain: Optional[Blockchain] = None):
        self.host = host
        self.port = port
        self.blockchain = blockchain or Blockchain()
        self.peer_manager = PeerManager()
        self.server: Optional[asyncio.Server] = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def start(self) -> None:
        """Start the blockchain node."""
        self.logger.info(f"Starting node on {self.host}:{self.port}")

        # Start TCP server
        self.server = await asyncio.start_server(
            self.handle_incoming_connection, self.host, self.port
        )

        # Start background sync task
        asyncio.create_task(self.sync_loop())

        self.logger.info("Node started successfully")

    async def stop(self) -> None:
        """Stop the blockchain node."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.blockchain.close()
        self.logger.info("Node stopped")

    async def send_message(self, writer: asyncio.StreamWriter, message: Dict[str, Any]) -> None:
        """Send a message with length-prefix framing."""
        data = json.dumps(message).encode('utf-8')
        length = len(data)
        writer.write(length.to_bytes(4, 'big'))
        writer.write(data)
        await writer.drain()

    async def receive_message(self, reader: asyncio.StreamReader) -> Optional[Dict[str, Any]]:
        """Receive a message with length-prefix framing."""
        try:
            # Read 4-byte length prefix
            length_bytes = await reader.readexactly(4)
            length = int.from_bytes(length_bytes, 'big')
            
            # Read exact message
            data = await reader.readexactly(length)
            return json.loads(data.decode('utf-8'))
        except asyncio.IncompleteReadError:
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return None

    async def handle_incoming_connection(self, reader: asyncio.StreamReader,
                                        writer: asyncio.StreamWriter) -> None:
        """Handle incoming connection from a peer."""
        peer_addr = writer.get_extra_info('peername')
        self.logger.info(f"Incoming connection from {peer_addr[0]}:{peer_addr[1]}")

        try:
            while True:
                message = await self.receive_message(reader)
                if not message:
                    break

                msg_type = message.get('type')
                data = message.get('data', {})

                if msg_type == MessageType.HANDSHAKE:
                    response = {
                        'type': MessageType.HANDSHAKE,
                        'data': {
                            'version': '1.0',
                            'best_height': len(self.blockchain.chain) - 1
                        }
                    }
                    await self.send_message(writer, response)

                elif msg_type == MessageType.GET_BLOCKS:
                    start_height = data.get('start_height', 0)
                    end_height = min(start_height + 100, len(self.blockchain.chain))
                    blocks = self.blockchain.chain[start_height:end_height]

                    self.logger.info(f"Sending {len(blocks)} blocks to {peer_addr[0]}")
                    
                    response = {
                        'type': MessageType.BLOCKS,
                        'data': {
                            'blocks': [block.to_dict() for block in blocks]
                        }
                    }
                    await self.send_message(writer, response)

        except Exception as e:
            self.logger.debug(f"Connection handler error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def request_blocks_from_peer(self, peer: Peer) -> bool:
        """Request and sync blocks from a specific peer."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(peer.host, peer.port),
                timeout=5.0
            )

            # Send handshake
            handshake = {
                'type': MessageType.HANDSHAKE,
                'data': {
                    'version': '1.0',
                    'best_height': len(self.blockchain.chain) - 1
                }
            }
            await self.send_message(writer, handshake)
            
            # Receive handshake response
            response = await asyncio.wait_for(self.receive_message(reader), timeout=5.0)
            if not response:
                writer.close()
                await writer.wait_closed()
                return False

            # Request full blockchain
            request = {
                'type': MessageType.GET_BLOCKS,
                'data': {
                    'start_height': 0
                }
            }
            await self.send_message(writer, request)

            # Receive blocks
            blocks_msg = await asyncio.wait_for(self.receive_message(reader), timeout=30.0)
            
            writer.close()
            await writer.wait_closed()

            if blocks_msg and blocks_msg.get('type') == MessageType.BLOCKS:
                blocks_data = blocks_msg.get('data', {}).get('blocks', [])
                if blocks_data:
                    received_blocks = [Block.from_dict(bd) for bd in blocks_data]
                    self.logger.info(f"Received {len(received_blocks)} blocks from {peer}")
                    
                    # Replace chain if longer
                    if len(received_blocks) > len(self.blockchain.chain):
                        if self.blockchain.replace_chain(received_blocks):
                            self.logger.info(f"✓ Chain replaced with {len(received_blocks)} blocks")
                            return True
                        else:
                            self.logger.warning("✗ Chain replacement failed - invalid chain")
                    # Try to add new blocks if same length but has newer blocks
                    elif len(received_blocks) == len(self.blockchain.chain):
                        # Check if we need any blocks
                        added = False
                        for block in received_blocks:
                            if block.index >= len(self.blockchain.chain):
                                if self.blockchain.add_block(block):
                                    self.logger.info(f"✓ Added new block {block.index}")
                                    added = True
                        return added
                    else:
                        self.logger.debug(f"Peer chain not longer ({len(received_blocks)} vs {len(self.blockchain.chain)})")

            return False

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout connecting to {peer}")
            return False
        except Exception as e:
            self.logger.error(f"Error syncing with {peer}: {e}")
            return False

    async def connect_to_peer(self, peer: Peer) -> None:
        """Connect to a peer and sync once."""
        self.peer_manager.add_peer(peer)
        self.peer_manager.update_peer_status(peer, True)
        
        success = await self.request_blocks_from_peer(peer)
        
        if success:
            self.logger.info(f"Successfully synced with {peer}")

    async def sync_loop(self) -> None:
        """Periodically sync with all known peers."""
        await asyncio.sleep(5)  # Initial delay
        
        while True:
            connected_peers = self.peer_manager.get_connected_peers()
            
            if connected_peers:
                self.logger.info(f"Syncing with {len(connected_peers)} peer(s)")
                
                for peer in connected_peers:
                    await self.request_blocks_from_peer(peer)
            
            await asyncio.sleep(15)  # Sync every 15 seconds

    def mine_block(self, miner_address: str) -> Optional[Block]:
        """Mine a new block."""
        return self.blockchain.mine_pending_transactions(miner_address)
