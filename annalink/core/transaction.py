"""
Transaction module for Annalink blockchain.

This module defines the Transaction class, which represents a transfer of value
between two addresses in the blockchain network.
"""

import time
import hashlib
import json
from typing import Dict, Any
from ecdsa import VerifyingKey, SigningKey, SECP256k1
import base58


class Transaction:
    """
    Represents a blockchain transaction.

    Attributes:
        sender (str): Base58 encoded sender address
        receiver (str): Base58 encoded receiver address
        amount (float): Amount to transfer
        fee (float): Transaction fee
        timestamp (float): Unix timestamp
        signature (str): Hex encoded signature
        txid (str): Transaction ID (hash)
        public_key (str): Hex encoded sender public key
    """

    def __init__(self, sender: str, receiver: str, amount: float, fee: float = 0.0,
                 timestamp: float = None, signature: str = None, public_key: str = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.timestamp = timestamp or time.time()
        self.signature = signature
        self.public_key = public_key
        self.txid = self.calculate_txid()

    def calculate_txid(self) -> str:
        """Calculate the transaction ID as SHA256 hash of transaction data."""
        tx_data = {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'public_key': self.public_key
        }
        tx_string = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for serialization."""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'txid': self.txid,
            'public_key': self.public_key
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            sender=data['sender'],
            receiver=data['receiver'],
            amount=data['amount'],
            fee=data.get('fee', 0.0),
            timestamp=data['timestamp'],
            signature=data.get('signature'),
            public_key=data.get('public_key')
        )

    def sign(self, private_key: SigningKey) -> None:
        """Sign the transaction with a private key."""
        if not self.public_key:
            self.public_key = private_key.verifying_key.to_string().hex()

        tx_data = {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'public_key': self.public_key
        }
        tx_string = json.dumps(tx_data, sort_keys=True)
        signature = private_key.sign(tx_string.encode())
        self.signature = signature.hex()

    def verify_signature(self) -> bool:
        """Verify the transaction signature."""
        if not self.signature or not self.public_key:
            return False

        try:
            pub_key = VerifyingKey.from_string(bytes.fromhex(self.public_key), curve=SECP256k1)
        except:
            return False

        tx_data = {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'fee': self.fee,
            'timestamp': self.timestamp,
            'public_key': self.public_key
        }
        tx_string = json.dumps(tx_data, sort_keys=True)

        try:
            return pub_key.verify(bytes.fromhex(self.signature), tx_string.encode())
        except:
            return False

    def is_valid(self) -> bool:
        """Check if transaction is valid."""
        # Basic validation
        if self.amount <= 0 or self.fee < 0:
            return False
        if not self.sender or not self.receiver:
            return False
        if len(self.sender) != 34 or len(self.receiver) != 34:  # Base58 address length
            return False
        if not self.public_key:
            return False
        if not self.verify_signature():
            return False
        return True