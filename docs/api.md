# Annalink API Documentation

## REST API

The REST API provides HTTP endpoints for interacting with the blockchain.

### Endpoints

#### GET /info
Get node information.

**Response:**
```json
{
  "host": "0.0.0.0",
  "port": 8333,
  "peers": 5,
  "version": "1.0"
}
```

#### GET /blockchain
Get blockchain statistics.

**Response:**
```json
{
  "blocks": 100,
  "difficulty": 4,
  "pending_transactions": 5,
  "mining_reward": 50.0
}
```

#### GET /blocks
Get blocks (paginated).

**Parameters:**
- `limit` (int): Number of blocks to return (default: 10)
- `offset` (int): Starting block index (default: 0)

**Response:** Array of block objects

#### GET /blocks/{block_index}
Get specific block by index.

**Response:** Block object

#### GET /transactions/pending
Get pending transactions in mempool.

**Response:** Array of transaction objects

#### POST /transactions
Submit a new transaction.

**Request:**
```json
{
  "sender": "1ABC...",
  "receiver": "1DEF...",
  "amount": 10.0,
  "fee": 0.0,
  "signature": "hex_signature"
}
```

#### GET /balance/{address}
Get balance for an address.

**Response:**
```json
{
  "address": "1ABC...",
  "balance": 100.0
}
```

#### POST /mine
Mine a new block.

**Request:**
```json
{
  "miner_address": "1ABC..."
}
```

**Response:**
```json
{
  "block_index": 101,
  "transactions": 3,
  "hash": "block_hash"
}
```

#### GET /peers
Get connected peers.

**Response:** Array of peer objects

## CLI Commands

### Wallet Management

```bash
# Create new wallet
annalink-cli create-wallet --save wallet.json

# Send transaction
annalink-cli send --wallet-file wallet.json --to 1ABC... --amount 10.0

# Check balance
annalink-cli balance --wallet-file wallet.json
```

### Mining

```bash
# Start mining
annalink-cli mine --wallet-file wallet.json
```

### Node Operations

```bash
# Start node
annalink-cli node

# Show blockchain info
annalink-cli blockchain
```

## Data Structures

### Transaction
```json
{
  "txid": "transaction_hash",
  "sender": "sender_address",
  "receiver": "receiver_address",
  "amount": 10.0,
  "fee": 0.0,
  "timestamp": 1234567890.0,
  "signature": "hex_signature",
  "public_key": "hex_public_key"
}
```

### Block
```json
{
  "index": 100,
  "timestamp": 1234567890.0,
  "transactions": [...],
  "previous_hash": "prev_hash",
  "nonce": 12345,
  "hash": "block_hash",
  "difficulty": 4
}
```

### Peer
```json
{
  "host": "192.168.1.1",
  "port": 8333
}
```