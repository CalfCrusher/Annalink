# Annalink Blockchain

A production-ready custom blockchain implementation built from scratch.

## Features

- **Persistent storage** with SQLite - blocks and transactions saved to disk
- **P2P networking** over TCP with automatic peer discovery and bidirectional sync
- **Wallet management** with ECDSA (secp256k1) keys and Base58 addresses
- **Proof-of-Work consensus** with configurable difficulty
- **Transaction validation** with signature verification and double-spend prevention
- **Mempool** for pending transactions
- **Chain validation** and longest-chain selection
- **CLI interface** for all blockchain operations
- **REST API** for programmatic access
- **Configurable parameters** via YAML config files
- **Graceful shutdown** handling (Ctrl+C)
- **Cross-computer deployment** - real P2P over internet/LAN

## Installation

Prerequisites: Python 3.8+ and a virtual environment. The commands below assume bash/zsh on macOS/Linux.

1. Clone the repository
2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Upgrade build tools and install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

4. Install Annalink in editable mode (recommended)

```bash
pip install -e .
```

Notes
- Editable install is the modern replacement for `python setup.py develop`.
- If you still prefer the legacy command, ensure `setuptools` is installed first: `pip install setuptools wheel`.

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
annalink-cli node [--host HOST] [--port PORT] [--peer PEER_ADDRESS]
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

# Start a standalone node on default port 8333
annalink-cli node

# Start a node on custom port
annalink-cli node --port 5001

# Start a node and connect to a peer
annalink-cli node --port 8334 --peer 192.168.1.100:8333

# View blockchain status
annalink-cli blockchain
```

### Multi-Computer Network Setup

To create a P2P blockchain network across multiple computers:

**Computer 1 (First Node):**
```bash
# Create wallets
annalink-cli create-wallet --save wallet1.json
annalink-cli create-wallet --save wallet2.json

# Mine some initial blocks
annalink-cli mine --wallet-file wallet1.json
# Press Ctrl+C after mining a few blocks

# Start the node (note your IP address)
annalink-cli node --host 0.0.0.0 --port 8333
```

**Computer 2 (Connecting Node):**
```bash
# Create wallets
annalink-cli create-wallet --save wallet1.json
annalink-cli create-wallet --save wallet2.json

# Connect to Computer 1 (replace with actual IP)
annalink-cli node --host 0.0.0.0 --port 8334 --peer 192.168.1.100:8333
```

The nodes will automatically:
- Sync the blockchain (Computer 2 downloads blocks from Computer 1)
- Propagate new blocks and transactions
- Maintain bidirectional sync every 15 seconds

**Cross-Computer Transactions:**
```bash
# On Computer 1: Send coins to Computer 2's wallet
annalink-cli send --wallet-file wallet1.json --to <COMPUTER2_ADDRESS> --amount 50 --fee 1

# On Computer 2: Check balance after sync (wait ~15 seconds)
annalink-cli balance --wallet-file wallet1.json
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

## Disclaimer & Limitations

This project is a functional, educational blockchain intended for small, trusted networks and prototyping. It is not a production public cryptocurrency. Use at your own risk.

- Scope and intended use
	- Designed for small, cooperative deployments: roughly 50–200 users and ~500–2,000 transactions/day across 5–10 nodes.
	- Excellent for learning, demos, private pilots, and internal apps. Not suitable for adversarial public environments or high-value transactions.

- Consensus and protocol
	- Proof‑of‑Work without slashing/finality; vulnerable to 51% and selfish‑mining attacks.
	- No formal fork resolution/longest‑chain arbitration beyond basic validation; chain splits can persist without manual intervention.
	- No protocol upgrade/feature negotiation mechanism (no versioned hard/soft‑fork orchestration).

- Networking
	- TCP P2P with length-prefixed message framing; peers exchange listening ports via handshake for bidirectional sync
	- Automatic peer discovery from incoming connections; sync every 15 seconds with all known peers
	- Limited peer discovery; no seed list bootstrap or DNS discovery
	- No NAT traversal guarantees, message signing, or encryption between peers
	- No rate limiting or DoS protection; no message compression

- Storage and performance
	- SQLite single‑writer storage; no replication, sharding, or pruning.
	- Full chain loaded in memory at startup; balance calculation scans the chain (O(n²) pattern across blocks×txns); will slow as data grows.
	- No Merkle proofs; blocks reference transactions by ID only for hashing.

- Wallets and security
	- Keys are ECDSA (secp256k1) with Base58 addresses; no multi‑sig, hardware wallet support, or HD wallets.
	- Wallet export files are JSON; optional password uses simple XOR and is not production‑grade encryption.
	- CLI may print private keys; ensure safe operational practices; never commit wallet files (JSON is ignored via .gitignore).
	- Not quantum‑resistant; cryptographic assumptions may degrade over time.

- Economics
	- Fixed PoW reward schedule with halvings; no fee market or mempool prioritization; miner incentives may degrade as rewards halve.

- Monitoring & ops
	- Basic logging and health endpoints only; no metrics, alerting, backups, or automated recovery.

- Maintenance expectations (honest outlook)
	- Without maintenance: 2–5 years before dependency/security rot, performance degradation, or operational drift cause failures.
	- Minimal maintenance: 5–15 years (periodic library upgrades, backups, and occasional fixes).
	- Active stewardship: 20–50 years with planned upgrades (DB indexing/UTXO set, fork resolution, peer bootstrap, security hardening).
	- Example recurring tasks: dependency updates, database backups, security patches, seed peer management, and incident response.

- Known missing features for public‑grade deployments
	- Robust fork resolution/longest chain, finalized consensus, peer authentication & encryption, seed/bootstrap services, DoS protections, UTXO/state index, pruning, fee market, comprehensive API auth/rate‑limits, CI/CD, observability, and formal audits.

By using this software you acknowledge these limitations and accept all risks. Contributions and issues are welcome to evolve the project.