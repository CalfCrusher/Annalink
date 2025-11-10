# Annalink Blockchain

A production-ready custom blockchain implementation built from scratch.

## Features

- Persistent storage with SQLite
- P2P networking over TCP
- Wallet management with ECDSA keys and Base58 addresses
- Proof-of-Work consensus
- Transaction validation and mempool
- Chain validation and fork resolution
- CLI and REST API interfaces
- Configurable parameters
- Comprehensive testing

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run setup: `python setup.py develop`

## Usage

### CLI

The Annalink CLI provides a complete interface for interacting with the blockchain:

```bash
# Get help
annalink-cli --help

# Create a new wallet
annalink-cli create-wallet [--save WALLET_FILE]

# Send a transaction
annalink-cli send --wallet-file WALLET_FILE --to RECIPIENT_ADDRESS --amount AMOUNT [--fee FEE]

# Mine blocks (requires wallet for mining rewards)
annalink-cli mine --wallet-file WALLET_FILE

# Check wallet balance
annalink-cli balance --wallet-file WALLET_FILE

# View blockchain information
annalink-cli blockchain

# Start a blockchain node
annalink-cli node [--host HOST] [--port PORT]
```

#### Examples

```bash
# Create and save a wallet
annalink-cli create-wallet --save my_wallet.json

# Send 10 coins to an address
annalink-cli send --wallet-file my_wallet.json --to 1ABC... --amount 10

# Start mining with your wallet
annalink-cli mine --wallet-file my_wallet.json

# Check your balance
annalink-cli balance --wallet-file my_wallet.json

# Start a node on port 5001
annalink-cli node --port 5001

# View blockchain status
annalink-cli blockchain
```

### REST API

Start the node with REST API:

```bash
python -m annalink.api.rest
```

The API will be available at `http://localhost:8000` with endpoints for:
- `/blockchain` - Get blockchain info
- `/transactions` - Send transactions
- `/mine` - Mine blocks
- `/wallet/balance` - Check balance
- `/health` - Health check

## Documentation

See [docs/](docs/) for detailed documentation.

## Development

Run tests: `pytest`

## License

MIT