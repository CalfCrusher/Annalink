"""
Blockchain module for Annalink blockchain.

This module defines the Blockchain class, which manages the chain of blocks,
validates new blocks, and handles chain state.
"""

import time
import logging
from typing import List, Optional
from .block import Block
from .transaction import Transaction
from .consensus import ProofOfWork
from ..storage.database import BlockchainDatabase


class Blockchain:
    """
    Represents the blockchain data structure.

    Attributes:
        chain (List[Block]): List of blocks in the chain (loaded on demand)
        pow (ProofOfWork): Proof-of-work consensus instance
        pending_transactions (List[Transaction]): Mempool of pending transactions
        mining_reward (float): Reward for mining a block
        db (BlockchainDatabase): Database instance for persistence
        logger (logging.Logger): Logger instance
    """

    def __init__(self, difficulty: int = 4, mining_reward: float = 50.0, db_path: str = "blockchain.db"):
        self.pow = ProofOfWork(difficulty=difficulty)
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = mining_reward
        self.db = BlockchainDatabase(db_path)
        self.logger = logging.getLogger(__name__)

        # Load existing chain or create genesis
        self.chain = self.db.load_all_blocks()
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create and add the genesis block."""
        self.logger.info("Creating genesis block")
        genesis_tx = Transaction(
            sender="0" * 34,  # Coinbase
            receiver="0" * 34,  # No receiver for genesis
            amount=0.0,
            fee=0.0
        )
        genesis_block = Block(0, [genesis_tx], "0")
        self.pow.mine_block(genesis_block)
        self.chain.append(genesis_block)
        self.db.save_block(genesis_block)
        self.logger.info("Genesis block created and saved")

    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the mempool if valid."""
        if not transaction.is_valid():
            self.logger.warning(f"Invalid transaction: {transaction.txid}")
            return False

        # Check for sufficient balance
        balance = self.get_balance(transaction.sender)
        if balance < transaction.amount + transaction.fee:
            self.logger.warning(f"Insufficient balance for transaction: {transaction.txid}")
            return False

        # Check for double spending in mempool
        for pending_tx in self.pending_transactions:
            if pending_tx.sender == transaction.sender:
                # Simplified: don't allow multiple pending tx from same sender
                self.logger.warning(f"Double spend attempt: {transaction.txid}")
                return False

        self.pending_transactions.append(transaction)
        self.logger.info(f"Transaction added to mempool: {transaction.txid}")
        return True

    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Mine a new block with pending transactions."""
        # Allow mining even with no pending transactions for mining rewards
        # if not self.pending_transactions:
        #     self.logger.debug("No pending transactions to mine")
        #     return None

        # Update mining reward based on block height
        self.mining_reward = self.pow.get_mining_reward(len(self.chain))

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
            difficulty=self.pow.difficulty
        )

        self.logger.info(f"Mining block {new_block.index} with {len(self.pending_transactions)} transactions")

        # Mine the block
        try:
            self.pow.mine_block(new_block)
        except TimeoutError:
            self.logger.error("Mining timeout")
            return None

        # Add to chain
        if self.add_block(new_block):
            # Clear mempool except coinbase
            self.pending_transactions = []
            # Adjust difficulty
            self.pow.difficulty = self.pow.calculate_difficulty(self.chain)
            self.logger.info(f"Block {new_block.index} mined and added to chain")
            return new_block
        return None

    def add_block(self, block: Block) -> bool:
        """Add a block to the chain if valid."""
        if block.is_valid(self.get_latest_block()):
            self.chain.append(block)
            self.db.save_block(block)
            self.logger.info(f"Block {block.index} added to chain")
            return True
        self.logger.warning(f"Invalid block rejected: {block.index}")
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

    def close(self) -> None:
        """Close database connection."""
        self.db.close()