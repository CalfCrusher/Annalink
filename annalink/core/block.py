"""
Block module for Annalink blockchain.

This module defines the Block class, which contains a list of transactions
and is linked to the previous block in the chain.
"""

import time
import hashlib
import json
from typing import List, Dict, Any
from .transaction import Transaction


class Block:
    """
    Represents a block in the blockchain.

    Attributes:
        index (int): Block index
        timestamp (float): Block creation timestamp
        transactions (List[Transaction]): List of transactions in the block
        previous_hash (str): Hash of the previous block
        nonce (int): Nonce for proof-of-work
        hash (str): Block hash
        difficulty (int): Mining difficulty
    """

    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str,
                 timestamp: float = None, nonce: int = 0, difficulty: int = 4):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the block hash."""
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.txid for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine the block by finding a nonce that satisfies the difficulty."""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for serialization."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash,
            'difficulty': self.difficulty
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Create block from dictionary."""
        transactions = [Transaction.from_dict(tx_data) for tx_data in data['transactions']]
        return cls(
            index=data['index'],
            transactions=transactions,
            previous_hash=data['previous_hash'],
            timestamp=data['timestamp'],
            nonce=data['nonce'],
            difficulty=data.get('difficulty', 4)
        )

    def is_valid(self, previous_block: 'Block' = None) -> bool:
        """Validate the block."""
        # Check hash
        if self.hash != self.calculate_hash():
            return False

        # Check proof-of-work
        if self.hash[:self.difficulty] != '0' * self.difficulty:
            return False

        # Check transactions
        for tx in self.transactions:
            if not tx.is_valid():
                return False

        # Check previous hash if previous block provided
        if previous_block and self.previous_hash != previous_block.hash:
            return False

        return True