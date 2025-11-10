"""
CLI module for Annalink blockchain.

This module provides a command-line interface for interacting with the blockchain node.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from ..core.wallet import Wallet
from ..core.transaction import Transaction
from ..networking.node import BlockchainNode
from ..config import load_config


def create_wallet(args) -> None:
    """Create a new wallet."""
    wallet = Wallet.generate_wallet()
    print(f"New wallet created!")
    print(f"Address: {wallet.address}")
    print(f"Private Key: {wallet.private_key.privkey.secret_multiplier.to_bytes(32, 'big').hex()}")

    if args.save:
        filepath = args.save
        wallet.save_to_file(filepath)
        print(f"Wallet saved to {filepath}")


def load_wallet(args) -> Wallet:
    """Load wallet from file."""
    if not args.wallet_file:
        print("Error: Wallet file required")
        sys.exit(1)

    try:
        wallet = Wallet.load_from_file(args.wallet_file)
        print(f"Wallet loaded: {wallet.address}")
        return wallet
    except Exception as e:
        print(f"Error loading wallet: {e}")
        sys.exit(1)


def send_transaction(args) -> None:
    """Send a transaction."""
    wallet = load_wallet(args)
    node = BlockchainNode()

    # Create transaction
    tx = Transaction(
        sender=wallet.address,
        receiver=args.to,
        amount=args.amount,
        fee=args.fee or 0.0
    )

    # Sign transaction
    tx_data = {
        'sender': tx.sender,
        'receiver': tx.receiver,
        'amount': tx.amount,
        'fee': tx.fee,
        'timestamp': tx.timestamp
    }
    tx.signature = wallet.sign_transaction(tx_data)

    # Add to blockchain
    if node.blockchain.add_transaction(tx):
        print(f"Transaction sent: {tx.txid}")
        # In real implementation, broadcast to network
    else:
        print("Failed to send transaction")


def mine_blocks(args) -> None:
    """Mine blocks."""
    wallet = load_wallet(args)
    node = BlockchainNode()

    print("Starting mining... Press Ctrl+C to stop")

    try:
        while True:
            block = node.mine_block(wallet.address)
            if block:
                print(f"Mined block {block.index} with {len(block.transactions)} transactions")
                print(f"Reward: {node.blockchain.mining_reward}")
            else:
                print("No transactions to mine")
                asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Mining stopped")


def show_balance(args) -> None:
    """Show wallet balance."""
    wallet = load_wallet(args)
    node = BlockchainNode()
    balance = node.blockchain.get_balance(wallet.address)
    print(f"Balance: {balance}")


def show_blockchain(args) -> None:
    """Show blockchain info."""
    node = BlockchainNode()
    print(f"Blocks: {len(node.blockchain.chain)}")
    print(f"Difficulty: {node.blockchain.pow.difficulty}")
    print(f"Pending transactions: {len(node.blockchain.pending_transactions)}")


def start_node(args) -> None:
    """Start blockchain node."""
    node = BlockchainNode(
        host=args.host,
        port=args.port
    )

    async def run_node():
        await node.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await node.stop()

    asyncio.run(run_node())


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Annalink Blockchain CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create wallet
    create_parser = subparsers.add_parser('create-wallet', help='Create a new wallet')
    create_parser.add_argument('--save', help='Save wallet to file')
    create_parser.set_defaults(func=create_wallet)

    # Send transaction
    send_parser = subparsers.add_parser('send', help='Send a transaction')
    send_parser.add_argument('--wallet-file', required=True, help='Wallet file')
    send_parser.add_argument('--to', required=True, help='Recipient address')
    send_parser.add_argument('--amount', type=float, required=True, help='Amount to send')
    send_parser.add_argument('--fee', type=float, default=0.0, help='Transaction fee')
    send_parser.set_defaults(func=send_transaction)

    # Mine blocks
    mine_parser = subparsers.add_parser('mine', help='Mine blocks')
    mine_parser.add_argument('--wallet-file', required=True, help='Wallet file for rewards')
    mine_parser.set_defaults(func=mine_blocks)

    # Show balance
    balance_parser = subparsers.add_parser('balance', help='Show wallet balance')
    balance_parser.add_argument('--wallet-file', required=True, help='Wallet file')
    balance_parser.set_defaults(func=show_balance)

    # Show blockchain
    blockchain_parser = subparsers.add_parser('blockchain', help='Show blockchain info')
    blockchain_parser.set_defaults(func=show_blockchain)

    # Start node
    node_parser = subparsers.add_parser('node', help='Start blockchain node')
    node_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    node_parser.add_argument('--port', type=int, default=8333, help='Port to bind to (default: 8333)')
    node_parser.set_defaults(func=start_node)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()