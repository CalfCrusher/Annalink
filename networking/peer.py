"""
Peer module for Annalink blockchain.

This module handles peer connections and communication in the P2P network.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Peer:
    """
    Represents a network peer.

    Attributes:
        host (str): Peer hostname/IP
        port (int): Peer port
        last_seen (float): Last time peer was active
        connected (bool): Whether currently connected
    """
    host: str
    port: int
    last_seen: float = 0.0
    connected: bool = False

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert peer to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'last_seen': self.last_seen,
            'connected': self.connected
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Peer':
        """Create peer from dictionary."""
        return cls(
            host=data['host'],
            port=data['port'],
            last_seen=data.get('last_seen', 0.0),
            connected=data.get('connected', False)
        )


class PeerManager:
    """
    Manages peer connections and discovery.

    Attributes:
        peers (Dict[str, Peer]): Known peers
        max_peers (int): Maximum number of peers
        logger (logging.Logger): Logger instance
    """

    def __init__(self, max_peers: int = 10):
        self.peers: Dict[str, Peer] = {}
        self.max_peers = max_peers
        self.logger = logging.getLogger(__name__)

    def add_peer(self, peer: Peer) -> None:
        """Add a peer to the known peers list."""
        key = str(peer)
        if key not in self.peers and len(self.peers) < self.max_peers:
            self.peers[key] = peer
            self.logger.info(f"Added peer: {peer}")

    def remove_peer(self, peer: Peer) -> None:
        """Remove a peer from the known peers list."""
        key = str(peer)
        if key in self.peers:
            del self.peers[key]
            self.logger.info(f"Removed peer: {peer}")

    def get_connected_peers(self) -> list[Peer]:
        """Get list of currently connected peers."""
        return [peer for peer in self.peers.values() if peer.connected]

    def get_known_peers(self) -> list[Peer]:
        """Get list of all known peers."""
        return list(self.peers.values())

    def update_peer_status(self, peer: Peer, connected: bool) -> None:
        """Update peer connection status."""
        key = str(peer)
        if key in self.peers:
            self.peers[key].connected = connected
            self.peers[key].last_seen = asyncio.get_event_loop().time()

    def discover_peers(self, seed_nodes: list[str]) -> None:
        """Discover peers from seed nodes."""
        for seed in seed_nodes:
            try:
                host, port = seed.split(':')
                peer = Peer(host, int(port))
                self.add_peer(peer)
            except ValueError:
                self.logger.warning(f"Invalid seed node format: {seed}")