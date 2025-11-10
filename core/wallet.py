"""
Wallet module for Annalink blockchain.

This module provides wallet functionality including key generation,
address creation, transaction signing, and key management.
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import base58


class Wallet:
    """
    Represents a blockchain wallet with private/public key pair.

    Attributes:
        private_key (SigningKey): ECDSA private key
        public_key (VerifyingKey): ECDSA public key
        address (str): Base58 encoded address
    """

    def __init__(self, private_key: Optional[SigningKey] = None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = SigningKey.generate(curve=SECP256k1)

        self.public_key = self.private_key.verifying_key
        self.address = self._generate_address()

    def _generate_address(self) -> str:
        """Generate Base58 address from public key."""
        # Get public key bytes
        pub_key_bytes = b'\x04' + self.public_key.to_string()  # Uncompressed with 0x04 prefix

        # SHA256 hash
        sha = hashlib.sha256(pub_key_bytes).digest()

        # RIPEMD160 hash
        rip = hashlib.new('ripemd160')
        rip.update(sha)
        pub_key_hash = rip.digest()

        # Add version byte (0x00 for mainnet)
        version_pub_key_hash = b'\x00' + pub_key_hash

        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(version_pub_key_hash).digest()).digest()[:4]

        # Combine and encode
        address_bytes = version_pub_key_hash + checksum
        return base58.b58encode(address_bytes).decode()

    @classmethod
    def from_private_key_hex(cls, private_key_hex: str) -> 'Wallet':
        """Create wallet from hex private key."""
        private_key_int = int(private_key_hex, 16)
        private_key = SigningKey.from_secret_exponent(private_key_int, curve=SECP256k1)
        return cls(private_key)

    @classmethod
    def from_wif(cls, wif: str) -> 'Wallet':
        """Create wallet from Wallet Import Format (WIF)."""
        # Decode Base58
        decoded = base58.b58decode(wif)

        # Remove checksum (last 4 bytes)
        private_key_bytes = decoded[:-4]

        # Remove version byte if present
        if len(private_key_bytes) == 33:
            private_key_bytes = private_key_bytes[1:]

        # Create private key
        private_key_int = int.from_bytes(private_key_bytes, 'big')
        private_key = SigningKey.from_secret_exponent(private_key_int, curve=SECP256k1)
        return cls(private_key)

    def to_wif(self, compressed: bool = True) -> str:
        """Export private key to Wallet Import Format (WIF)."""
        # Get private key bytes
        private_key_bytes = self.private_key.privkey.secret_multiplier.to_bytes(32, 'big')

        # Add compression flag if compressed
        if compressed:
            private_key_bytes += b'\x01'

        # Add version byte
        version_private_key = b'\x80' + private_key_bytes

        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(version_private_key).digest()).digest()[:4]

        # Combine and encode
        wif_bytes = version_private_key + checksum
        return base58.b58encode(wif_bytes).decode()

    def sign_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Sign transaction data and return hex signature."""
        tx_string = json.dumps(transaction_data, sort_keys=True)
        signature = self.private_key.sign(tx_string.encode())
        return signature.hex()

    def verify_address(self, address: str) -> bool:
        """Verify if an address is valid."""
        try:
            decoded = base58.b58decode(address)
            if len(decoded) != 25:  # 1 version + 20 hash + 4 checksum
                return False

            # Check checksum
            version_pub_key_hash = decoded[:-4]
            checksum = decoded[-4:]
            calculated_checksum = hashlib.sha256(hashlib.sha256(version_pub_key_hash).digest()).digest()[:4]

            return checksum == calculated_checksum
        except:
            return False

    def save_to_file(self, filepath: str, password: Optional[str] = None) -> None:
        """Save wallet to encrypted file."""
        wallet_data = {
            'private_key': self.private_key.to_secret_exponent().to_bytes(32, 'big').hex(),
            'address': self.address
        }

        # Simple encryption with password (in production, use proper encryption)
        if password:
            # XOR with password hash (not secure, just for demo)
            pass_hash = hashlib.sha256(password.encode()).digest()
            data_str = json.dumps(wallet_data)
            encrypted = bytes([b ^ pass_hash[i % len(pass_hash)] for i, b in enumerate(data_str.encode())])
            with open(filepath, 'wb') as f:
                f.write(encrypted)
        else:
            with open(filepath, 'w') as f:
                json.dump(wallet_data, f)

    @classmethod
    def load_from_file(cls, filepath: str, password: Optional[str] = None) -> 'Wallet':
        """Load wallet from file."""
        if password:
            with open(filepath, 'rb') as f:
                encrypted = f.read()
            pass_hash = hashlib.sha256(password.encode()).digest()
            decrypted = bytes([b ^ pass_hash[i % len(pass_hash)] for i, b in enumerate(encrypted)])
            wallet_data = json.loads(decrypted.decode())
        else:
            with open(filepath, 'r') as f:
                wallet_data = json.load(f)

        private_key_hex = wallet_data['private_key']
        return cls.from_private_key_hex(private_key_hex)

    @staticmethod
    def generate_wallet() -> 'Wallet':
        """Generate a new wallet."""
        return Wallet()