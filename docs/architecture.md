# Annalink Blockchain Architecture

## Overview

Annalink is a production-ready custom blockchain implementation built from scratch using Python. It features persistent storage, P2P networking, wallet management, and Proof-of-Work consensus.

## Core Components

### Blockchain Core (`core/`)

- **blockchain.py**: Main blockchain class managing the chain, transactions, and mining
- **block.py**: Block data structure with transactions and mining logic
- **transaction.py**: Transaction class with ECDSA signing and validation
- **wallet.py**: Wallet management with key generation and Base58 addresses
- **consensus.py**: Proof-of-Work consensus implementation

### Networking (`networking/`)

- **node.py**: Main blockchain node with P2P communication
- **peer.py**: Peer management and discovery

### Storage (`storage/`)

- **database.py**: SQLite-based persistent storage for blocks and transactions

### API (`api/`)

- **cli.py**: Command-line interface for node operations
- **rest.py**: FastAPI-based REST API for external interactions

### Configuration (`config/`)

- **default.yaml**: Default configuration file
- **__init__.py**: Configuration loading utilities

## Data Flow

1. **Transaction Creation**: Users create transactions via CLI or REST API
2. **Transaction Validation**: Transactions are validated and added to mempool
3. **Block Mining**: Miners collect transactions and mine new blocks
4. **Block Propagation**: New blocks are broadcast to all peers
5. **Chain Validation**: Nodes validate incoming blocks and resolve forks

## Consensus Mechanism

Annalink uses Proof-of-Work (PoW) consensus:

- Difficulty adjusts every 10 blocks based on target block time (10 minutes)
- Mining reward halves every 210,000 blocks
- Blocks contain coinbase transaction for miner rewards

## Networking Protocol

Nodes communicate via TCP with JSON messages:

- Handshake: Initial connection establishment
- GetBlocks: Request block data from peers
- NewTransaction: Broadcast new transactions
- NewBlock: Broadcast mined blocks
- GetPeers: Request peer list for discovery

## Security Features

- ECDSA signature verification for transactions
- Double-spend prevention in mempool
- Block hash validation
- Address checksum validation

## Storage

All blockchain data is stored in SQLite:

- `blocks` table: Block metadata and JSON data
- `transactions` table: Transaction details
- `chain_state` table: Consensus parameters

## Configuration

Configurable via `config/default.yaml`:

- Network settings (host, port, peers)
- Consensus parameters (difficulty, block time)
- Storage paths
- API settings

## Extensibility

The modular design allows for:

- Custom transaction types
- Alternative consensus mechanisms
- Additional networking protocols
- Plugin systems for new features