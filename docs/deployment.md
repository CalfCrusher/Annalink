# Annalink Deployment Guide

## Prerequisites

- Python 3.8+
- pip
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/CalfCrusher/Annalink.git
cd Annalink
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Edit `config/default.yaml` or create `config/local.yaml`:

```yaml
network:
  host: "0.0.0.0"
  port: 8333
  max_peers: 10
  seed_nodes:
    - "seed.annalink.net:8333"

consensus:
  difficulty_target: 4
  block_time: 600

storage:
  db_path: "blockchain.db"

api:
  rest_port: 8080
  enable_cors: true
```

## Running a Node

### Start Node with REST API
```bash
python -m annalink.api.rest
```

### Start Node with CLI
```bash
annalink-cli node
```

### Mining
```bash
annalink-cli mine --wallet-file wallet.json
```

## Multi-Node Setup

1. Start first node (seed node)
2. Configure other nodes to connect to seed node
3. Start additional nodes

## Wallet Operations

```bash
# Create wallet
annalink-cli create-wallet --save wallet.json

# Send transaction
annalink-cli send --wallet-file wallet.json --to <address> --amount 10.0

# Check balance
annalink-cli balance --wallet-file wallet.json
```

## Monitoring

- REST API endpoints provide node status
- Logs are written to `annalink.log`
- Database file `blockchain.db` contains all chain data

## Security Considerations

- Store wallet files securely
- Use strong passwords for encrypted wallets
- Configure firewall to limit node access
- Keep software updated

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in config
2. **Database locked**: Ensure only one node uses the database
3. **Connection refused**: Check network configuration and firewalls

### Logs

Check `annalink.log` for detailed error information.

## Production Deployment

For production:

1. Use reverse proxy (nginx) for REST API
2. Set up monitoring and alerts
3. Configure backups for database
4. Use dedicated hardware for mining nodes
5. Implement load balancing for API nodes