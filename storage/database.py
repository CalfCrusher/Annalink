"""
Database module for Annalink blockchain.

This module provides persistent storage for blocks, transactions,
and blockchain state using SQLite.
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..core.block import Block
from ..core.transaction import Transaction


class BlockchainDatabase:
    """
    SQLite database for blockchain persistence.

    Attributes:
        db_path (str): Path to the database file
        conn (sqlite3.Connection): Database connection
    """

    def __init__(self, db_path: str = "blockchain.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize database tables."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # Blocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                index INTEGER PRIMARY KEY,
                timestamp REAL,
                previous_hash TEXT,
                nonce INTEGER,
                hash TEXT,
                difficulty INTEGER,
                data TEXT  -- JSON serialized block data
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                txid TEXT PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                amount REAL,
                fee REAL,
                timestamp REAL,
                signature TEXT,
                block_index INTEGER,
                FOREIGN KEY (block_index) REFERENCES blocks (index)
            )
        ''')

        # Chain state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chain_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        self.conn.commit()

    def save_block(self, block: Block) -> None:
        """Save a block to the database."""
        cursor = self.conn.cursor()

        # Save block
        block_data = json.dumps(block.to_dict())
        cursor.execute('''
            INSERT OR REPLACE INTO blocks
            (index, timestamp, previous_hash, nonce, hash, difficulty, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (block.index, block.timestamp, block.previous_hash, block.nonce,
              block.hash, block.difficulty, block_data))

        # Save transactions
        for tx in block.transactions:
            cursor.execute('''
                INSERT OR REPLACE INTO transactions
                (txid, sender, receiver, amount, fee, timestamp, signature, block_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tx.txid, tx.sender, tx.receiver, tx.amount, tx.fee,
                  tx.timestamp, tx.signature, block.index))

        self.conn.commit()

    def load_block(self, index: int) -> Optional[Block]:
        """Load a block from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM blocks WHERE index = ?', (index,))
        row = cursor.fetchone()

        if row:
            block_data = json.loads(row[0])
            return Block.from_dict(block_data)
        return None

    def load_latest_block(self) -> Optional[Block]:
        """Load the latest block from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT MAX(index) FROM blocks')
        max_index = cursor.fetchone()[0]

        if max_index is not None:
            return self.load_block(max_index)
        return None

    def load_all_blocks(self) -> List[Block]:
        """Load all blocks from the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM blocks ORDER BY index')
        rows = cursor.fetchall()

        blocks = []
        for row in rows:
            block_data = json.loads(row[0])
            blocks.append(Block.from_dict(block_data))
        return blocks

    def save_chain_state(self, key: str, value: Any) -> None:
        """Save chain state data."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO chain_state (key, value)
            VALUES (?, ?)
        ''', (key, json.dumps(value)))
        self.conn.commit()

    def load_chain_state(self, key: str) -> Any:
        """Load chain state data."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM chain_state WHERE key = ?', (key,))
        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def get_transaction_count(self) -> int:
        """Get total number of transactions."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM transactions')
        return cursor.fetchone()[0]

    def get_block_count(self) -> int:
        """Get total number of blocks."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM blocks')
        return cursor.fetchone()[0]

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()