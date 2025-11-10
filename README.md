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

```bash
annalink-cli --help
```

### REST API

Start the node with API:

```bash
python -m annalink.api.rest
```

## Documentation

See [docs/](docs/) for detailed documentation.

## Development

Run tests: `pytest`

## License

MIT