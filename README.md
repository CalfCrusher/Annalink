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
	- Basic TCP P2P; limited peer discovery; no seed list bootstrap, NAT traversal guarantees, message signing, or encryption between peers.
	- No rate limiting or DoS protection; message size is naive; no compression.

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