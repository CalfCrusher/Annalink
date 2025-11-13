"""
Node module for Annalink blockchain.

This module implements the main blockchain node with P2P networking,
blockchain management, and message handling.
"""

import asyncio
import json
import logging
import time
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
    GET_PEERS = "get_peers"
    PEERS = "peers"


class BlockchainNode:
    """
    Main blockchain node with P2P networking.

    Attributes:
        host (str): Node host
        port (int): Node port
        blockchain (Blockchain): Blockchain instance
        peer_manager (PeerManager): Peer manager
        server (asyncio.Server): TCP server
        logger (logging.Logger): Logger instance
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8333,
                 blockchain: Optional[Blockchain] = None):
        self.host = host
        self.port = port
        self.blockchain = blockchain or Blockchain()
        self.peer_manager = PeerManager()
        self.server: Optional[asyncio.Server] = None
        self.logger = logging.getLogger(__name__)

        # Set up logging
        logging.basicConfig(level=logging.INFO)

    async def start(self) -> None:
        """Start the blockchain node."""
        self.logger.info(f"Starting node on {self.host}:{self.port}")

        # Start TCP server
        self.server = await asyncio.start_server(
            self.handle_connection, self.host, self.port
        )

        # Discover initial peers
        await self.discover_peers()

        # Start background tasks
        asyncio.create_task(self.sync_with_peers())
        asyncio.create_task(self.broadcast_pending_transactions())

        self.logger.info("Node started successfully")

    async def stop(self) -> None:
        """Stop the blockchain node."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.blockchain.close()
        self.logger.info("Node stopped")

    async def handle_connection(self, reader: asyncio.StreamReader,
                               writer: asyncio.StreamWriter) -> None:
        """Handle incoming peer connection."""
        peer_addr = writer.get_extra_info('peername')
        peer = Peer(peer_addr[0], peer_addr[1])
        self.peer_manager.add_peer(peer)
        self.peer_manager.update_peer_status(peer, True)

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                message = json.loads(data.decode())
                await self.handle_message(message, writer)

        except Exception as e:
            self.logger.error(f"Error handling connection: {e}")
        finally:
            self.peer_manager.update_peer_status(peer, False)
            writer.close()
            await writer.wait_closed()

    async def handle_message(self, message: Dict[str, Any],
                           writer: asyncio.StreamWriter) -> None:
        """Handle incoming message from peer."""
        msg_type = message.get('type')
        data = message.get('data', {})

        if msg_type == MessageType.HANDSHAKE:
            await self.handle_handshake(data, writer)
        elif msg_type == MessageType.GET_BLOCKS:
            await self.handle_get_blocks(data, writer)
        elif msg_type == MessageType.BLOCKS:
            await self.handle_blocks(data)
        elif msg_type == MessageType.NEW_TRANSACTION:
            await self.handle_new_transaction(data)
        elif msg_type == MessageType.NEW_BLOCK:
            await self.handle_new_block(data)
        elif msg_type == MessageType.GET_PEERS:
            await self.handle_get_peers(writer)
        elif msg_type == MessageType.PEERS:
            await self.handle_peers(data)

    async def handle_handshake(self, data: Dict[str, Any],
                              writer: asyncio.StreamWriter) -> None:
        """Handle handshake message."""
        # Respond with our blockchain info
        response = {
            'type': MessageType.HANDSHAKE,
            'data': {
                'version': '1.0',
                'best_height': len(self.blockchain.chain) - 1,
                'host': self.host,
                'port': self.port
            }
        }
        await self.send_message(response, writer)

    async def handle_get_blocks(self, data: Dict[str, Any],
                               writer: asyncio.StreamWriter) -> None:
        """Handle get blocks request."""
        start_height = data.get('start_height', 0)
        blocks = self.blockchain.chain[start_height:start_height + 50]  # Limit to 50 blocks

        response = {
            'type': MessageType.BLOCKS,
            'data': {
                'blocks': [block.to_dict() for block in blocks]
            }
        }
        await self.send_message(response, writer)

    async def handle_blocks(self, data: Dict[str, Any]) -> None:
        """Handle received blocks."""
        blocks_data = data.get('blocks', [])
        if not blocks_data:
            return
        
        # Convert to Block objects
        received_blocks = [Block.from_dict(block_data) for block_data in blocks_data]
        
        # If we received multiple blocks, try chain replacement
        if len(received_blocks) > 1:
            # Build potential new chain
            new_chain = self.blockchain.chain[:received_blocks[0].index] + received_blocks
            if self.blockchain.replace_chain(new_chain):
                self.logger.info(f"Chain replaced with {len(new_chain)} blocks")
        else:
            # Single block, try to add normally
            block = received_blocks[0]
            if self.blockchain.add_block(block):
                self.logger.info(f"Added block {block.index} from peer")

    async def handle_new_transaction(self, data: Dict[str, Any]) -> None:
        """Handle new transaction."""
        tx = Transaction.from_dict(data)
        if self.blockchain.add_transaction(tx):
            self.logger.info(f"Added transaction {tx.txid} to mempool")
            # Broadcast to other peers
            await self.broadcast_transaction(tx)

    async def handle_new_block(self, data: Dict[str, Any]) -> None:
        """Handle new block."""
        block = Block.from_dict(data)
        if self.blockchain.add_block(block):
            self.logger.info(f"Added block {block.index} from peer")
            # Broadcast to other peers
            await self.broadcast_block(block)

    async def handle_get_peers(self, writer: asyncio.StreamWriter) -> None:
        """Handle get peers request."""
        peers = self.peer_manager.get_known_peers()
        response = {
            'type': MessageType.PEERS,
            'data': {
                'peers': [peer.to_dict() for peer in peers]
            }
        }
        await self.send_message(response, writer)

    async def handle_peers(self, data: Dict[str, Any]) -> None:
        """Handle received peers list."""
        peers_data = data.get('peers', [])
        for peer_data in peers_data:
            peer = Peer.from_dict(peer_data)
            self.peer_manager.add_peer(peer)

    async def send_message(self, message: Dict[str, Any],
                          writer: asyncio.StreamWriter) -> None:
        """Send message to peer."""
        data = json.dumps(message).encode()
        writer.write(data)
        await writer.drain()

    async def connect_to_peer(self, peer: Peer) -> None:
        """Connect to a peer."""
        try:
            reader, writer = await asyncio.open_connection(peer.host, peer.port)

            # Mark peer as connected
            self.peer_manager.update_peer_status(peer, True)
            
            # Send handshake
            handshake = {
                'type': MessageType.HANDSHAKE,
                'data': {
                    'version': '1.0',
                    'best_height': len(self.blockchain.chain) - 1,
                    'host': self.host,
                    'port': self.port
                }
            }
            await self.send_message(handshake, writer)

            # Handle responses
            asyncio.create_task(self.handle_connection(reader, writer))

        except Exception as e:
            self.logger.error(f"Failed to connect to peer {peer}: {e}")
            self.peer_manager.update_peer_status(peer, False)

    async def discover_peers(self) -> None:
        """Discover peers from seed nodes."""
        # Load seed nodes from config or use empty list for now
        seed_nodes = []  # TODO: Load from config
        self.peer_manager.discover_peers(seed_nodes)

        # Connect to discovered peers
        for peer in self.peer_manager.get_known_peers():
            if not peer.connected:
                asyncio.create_task(self.connect_to_peer(peer))

    async def sync_with_peers(self) -> None:
        """Sync blockchain with peers."""
        while True:
            await asyncio.sleep(10)  # Sync every 10 seconds

            connected_peers = self.peer_manager.get_connected_peers()
            self.logger.info(f"Syncing with {len(connected_peers)} connected peers")
            
            for peer in connected_peers:
                # Request blocks if behind
                if peer.connected:
                    try:
                        reader, writer = await asyncio.open_connection(peer.host, peer.port)
                        
                        # Request blocks starting from our current height
                        request = {
                            'type': MessageType.GET_BLOCKS,
                            'data': {
                                'start_height': len(self.blockchain.chain)
                            }
                        }
                        self.logger.info(f"Requesting blocks from {peer} starting at height {len(self.blockchain.chain)}")
                        await self.send_message(request, writer)
                        
                        # Wait for response
                        data = await asyncio.wait_for(reader.read(1024000), timeout=5.0)
                        if data:
                            response = json.loads(data.decode())
                            await self.handle_message(response, writer)
                        
                        writer.close()
                        await writer.wait_closed()
                    except Exception as e:
                        self.logger.debug(f"Sync with {peer} failed: {e}")

    async def broadcast_transaction(self, transaction: Transaction) -> None:
        """Broadcast transaction to all connected peers."""
        message = {
            'type': MessageType.NEW_TRANSACTION,
            'data': transaction.to_dict()
        }
        await self.broadcast_message(message)

    async def broadcast_block(self, block: Block) -> None:
        """Broadcast block to all connected peers."""
        message = {
            'type': MessageType.NEW_BLOCK,
            'data': block.to_dict()
        }
        await self.broadcast_message(message)

    async def broadcast_pending_transactions(self) -> None:
        """Broadcast pending transactions periodically."""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds
            for tx in self.blockchain.pending_transactions:
                await self.broadcast_transaction(tx)

    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected peers."""
        for peer in self.peer_manager.get_connected_peers():
            try:
                reader, writer = await asyncio.open_connection(peer.host, peer.port)
                await self.send_message(message, writer)
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                self.logger.error(f"Failed to broadcast to {peer}: {e}")

    def mine_block(self, miner_address: str) -> Optional[Block]:
        """Mine a new block."""
        return self.blockchain.mine_pending_transactions(miner_address)