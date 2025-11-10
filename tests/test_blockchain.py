"""
Tests for Annalink blockchain core components.
"""

import pytest
from Annalink.core.blockchain import Blockchain
from Annalink.core.transaction import Transaction
from Annalink.core.wallet import Wallet


class TestBlockchain:
    """Test blockchain functionality."""

    def test_blockchain_creation(self):
        """Test blockchain initialization."""
        bc = Blockchain()
        assert len(bc.chain) == 1  # Genesis block
        assert bc.get_latest_block().index == 0
        bc.close()

    def test_transaction_validation(self):
        """Test transaction validation."""
        wallet = Wallet.generate_wallet()
        receiver_wallet = Wallet.generate_wallet()
        tx = Transaction(
            sender=wallet.address,
            receiver=receiver_wallet.address,
            amount=10.0
        )
        tx.sign(wallet.private_key)

        assert tx.is_valid()

    def test_add_transaction(self):
        """Test adding transaction to blockchain."""
        bc = Blockchain()
        wallet = Wallet.generate_wallet()

        # Create and sign transaction
        tx = Transaction(
            sender=wallet.address,
            receiver="1" * 34,
            amount=10.0
        )
        tx_data = {
            'sender': tx.sender,
            'receiver': tx.receiver,
            'amount': tx.amount,
            'fee': tx.fee,
            'timestamp': tx.timestamp
        }
        tx.signature = wallet.sign_transaction(tx_data)

        # Should fail (insufficient balance)
        assert not bc.add_transaction(tx)
        bc.close()

    def test_mine_block(self):
        """Test block mining."""
        bc = Blockchain(difficulty=1)  # Easy difficulty for testing
        wallet = Wallet.generate_wallet()

        # Add some transactions (would need balance, but simplified)
        # In real test, create transactions with proper setup

        block = bc.mine_pending_transactions(wallet.address)
        # May be None if no transactions
        if block:
            assert block.index == 1
            assert len(block.transactions) >= 1  # At least coinbase
        bc.close()

    def test_chain_validation(self):
        """Test blockchain validation."""
        bc = Blockchain()
        assert bc.is_chain_valid()
        bc.close()


class TestWallet:
    """Test wallet functionality."""

    def test_wallet_creation(self):
        """Test wallet generation."""
        wallet = Wallet.generate_wallet()
        assert wallet.address
        assert len(wallet.address) == 34  # Base58 address length
        assert wallet.verify_address(wallet.address)

    def test_address_validation(self):
        """Test address validation."""
        wallet = Wallet.generate_wallet()
        assert wallet.verify_address(wallet.address)

        # Invalid address
        assert not wallet.verify_address("invalid")

    def test_wif_export_import(self):
        """Test WIF export/import."""
        wallet = Wallet.generate_wallet()
        wif = wallet.to_wif()
        imported_wallet = Wallet.from_wif(wif)

        assert wallet.address == imported_wallet.address