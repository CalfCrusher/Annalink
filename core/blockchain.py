"""
Blockchain module for Annalink blockchain.

This module defines the Blockchain class, which manages the chain of blocks,
validates new blocks, and handles chain state.
"""

import time
from typing import List, Optional
from .block import Block
from .transaction import Transaction


class Blockchain:
    """
    Represents the blockchain data structure.

    Attributes:
        chain (List[Block]): List of blocks in the chain
        difficulty (int): Current mining difficulty
        pending_transactions (List[Transaction]): Mempool of pending transactions
        mining_reward (float): Reward for mining a block
    """

    def __init__(self, difficulty: int = 4, mining_reward: float = 50.0):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = mining_reward

        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create and add the genesis block."""
        genesis_tx = Transaction(
            sender="0" * 34,  # Coinbase
            receiver="0" * 34,  # No receiver for genesis
            amount=0.0,
            fee=0.0
        )
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the mempool if valid."""
        if not transaction.is_valid():
            return False

        # Check for double spending (simplified - in real impl, check UTXO)
        # For now, just add to mempool
        self.pending_transactions.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Mine a new block with pending transactions."""
        if not self.pending_transactions:
            return None

        # Add coinbase transaction
        coinbase_tx = Transaction(
            sender="0" * 34,
            receiver=miner_address,
            amount=self.mining_reward,
            fee=0.0
        )

        # Create new block
        new_block = Block(
            index=len(self.chain),
            transactions=[coinbase_tx] + self.pending_transactions,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )

        # Mine the block
        new_block.mine_block(self.difficulty)

        # Add to chain
        if self.add_block(new_block):
            # Clear mempool except coinbase
            self.pending_transactions = []
            return new_block
        return None

    def add_block(self, block: Block) -> bool:
        """Add a block to the chain if valid."""
        if block.is_valid(self.get_latest_block()):
            self.chain.append(block)
            return True
        return False

    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if not current_block.is_valid(previous_block):
                return False
        return True

    def get_balance(self, address: str) -> float:
        """Get the balance of an address (simplified UTXO model)."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount + tx.fee
                if tx.receiver == address:
                    balance += tx.amount
        return balance

    def adjust_difficulty(self) -> None:
        """Adjust mining difficulty based on block time (simplified)."""
        # This is a basic implementation - real adjustment would be more complex
        if len(self.chain) % 10 == 0:  # Every 10 blocks
            # Calculate average block time
            if len(self.chain) > 10:
                recent_blocks = self.chain[-10:]
                total_time = sum(b.timestamp for b in recent_blocks[1:]) - sum(b.timestamp for b in recent_blocks[:-1])
                avg_time = total_time / 9
                target_time = 600  # 10 minutes

                if avg_time < target_time:
                    self.difficulty += 1
                elif avg_time > target_time and self.difficulty > 1:
                    self.difficulty -= 1