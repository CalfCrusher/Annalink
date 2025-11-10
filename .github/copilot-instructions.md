Build a real, production-ready custom blockchain project from scratch.

**CORE REQUIREMENTS:**
- Persistent storage: all blocks, transactions, wallets, and chain state must be stored to disk and loaded at startup (not just in-memory).
- True peer-to-peer networking: nodes must discover, connect, and propagate data over real networks (TCP/UDP), supporting NAT traversal and custom IP/port configuration. No simulation or “localhost only.”
- Wallet and private key management: generate, import/export, and encrypt keys; address generation compliant with blockchain standards (Base58, Bech32, etc.).
- Transaction handling: transactions must be validated (cryptographically signed), checked for double spending, added to a mempool, and mined into blocks.
- Consensus: implement Proof-of-Work (or Proof-of-Stake, or let me choose), including fork detection and resolution, block finality, and difficulty adjustment.
- API/UX: Provide a CLI and/or HTTP REST API for sending transactions, mining blocks, viewing blockchain state, peer management, and wallet operations.
- Chain validation: validate blocks, detect tampering, handle chain reorganizations, partition healing, and orphan blocks.
- Configuration: all network, consensus, and chain params must be configurable via env files or config files.
- Security: implement signature verification, rate limiting, anti-spam/DOS protections, chain integrity checks.
- Documentation: every function, module, and feature must be clearly documented with example usage, architecture, and installation/deployment steps.
- Extensibility: code structure must support easy addition of new transaction types, consensus mechanisms, plugins, and upgrades (protocol versioning).
- Testing: include unit, integration, and network tests covering all critical paths (block/transaction validation, multi-node sync, fork resolution).
- Resource management: code must manage memory, disk, and CPU efficiently. Use async or concurrent design for networking and mining.
- Monitoring: basic health checks, node status, and logs.

**CODE/TECH:**
- Prefer Python, Go, Rust, or similar language suitable for networking and disk IO. If recommending another language, justify why.
- Must run across independent machines (Linux/Windows/Mac) connected over the internet.
- No simulated, mock, or shortcut solutions are acceptable.

**GOAL:**
Produce clear, robust, real-world code that allows a user to deploy, run, and operate a functioning blockchain protocol with multiple nodes, wallets, and real transactions managed on real networks and persistent storage.

**EXTRA:**
Any additional best practices or security/hardening recommendations are welcome.

