"""
Consensus module for Annalink blockchain.

This module implements Proof-of-Work consensus mechanism,
including mining, difficulty adjustment, and validation.
"""

import time
import hashlib
from typing import List
from .block import Block


class ProofOfWork:
    """
    Proof-of-Work consensus implementation.

    Attributes:
        difficulty (int): Current mining difficulty
        target_block_time (int): Target time between blocks in seconds
        adjustment_interval (int): Number of blocks between difficulty adjustments
    """

    def __init__(self, difficulty: int = 4, target_block_time: int = 600,
                 adjustment_interval: int = 10):
        self.difficulty = difficulty
        self.target_block_time = target_block_time
        self.adjustment_interval = adjustment_interval

    def mine_block(self, block: Block) -> Block:
        """Mine a block by finding a valid nonce."""
        target = '0' * self.difficulty

        start_time = time.time()
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()

            # Prevent infinite loop in case of too high difficulty
            if time.time() - start_time > 300:  # 5 minutes timeout
                raise TimeoutError("Mining timeout - difficulty too high")

        return block

    def validate_proof(self, block: Block) -> bool:
        """Validate that the block's proof-of-work is correct."""
        target = '0' * block.difficulty
        return block.hash[:block.difficulty] == target

    def calculate_difficulty(self, blocks: List[Block]) -> int:
        """Calculate new difficulty based on recent block times."""
        if len(blocks) < self.adjustment_interval + 1:
            return self.difficulty

        # Get the last adjustment_interval blocks
        recent_blocks = blocks[-self.adjustment_interval:]

        # Calculate actual time taken
        start_time = recent_blocks[0].timestamp
        end_time = recent_blocks[-1].timestamp
        actual_time = end_time - start_time

        # Expected time
        expected_time = self.target_block_time * (self.adjustment_interval - 1)

        # Adjust difficulty
        if actual_time < expected_time / 2:
            # Too fast, increase difficulty
            return min(self.difficulty + 1, 256)  # Cap at 256
        elif actual_time > expected_time * 2:
            # Too slow, decrease difficulty
            return max(self.difficulty - 1, 1)  # Minimum 1
        else:
            # Within range, keep same
            return self.difficulty

    def get_mining_reward(self, block_height: int) -> float:
        """Calculate mining reward for a given block height."""
        # Halving every 210000 blocks (like Bitcoin)
        halvings = block_height // 210000
        reward = 50.0 / (2 ** halvings)
        return max(reward, 0.0)  # Minimum reward