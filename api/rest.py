"""
REST API module for Annalink blockchain.

This module provides a FastAPI-based HTTP REST API for interacting with the blockchain.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..core.blockchain import Blockchain
from ..core.transaction import Transaction
from ..core.block import Block
from ..networking.node import BlockchainNode
from ..config import load_config


# Pydantic models for request/response
class TransactionRequest(BaseModel):
    sender: str
    receiver: str
    amount: float
    fee: float = 0.0
    signature: str


class TransactionResponse(BaseModel):
    txid: str
    sender: str
    receiver: str
    amount: float
    fee: float
    timestamp: float
    signature: str


class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[TransactionResponse]
    previous_hash: str
    nonce: int
    hash: str
    difficulty: int


class BlockchainInfo(BaseModel):
    blocks: int
    difficulty: int
    pending_transactions: int
    mining_reward: float


class NodeInfo(BaseModel):
    host: str
    port: int
    peers: int
    version: str = "1.0"


# Global instances
blockchain = Blockchain()
node = BlockchainNode(blockchain=blockchain)

app = FastAPI(title="Annalink Blockchain API", version="1.0.0")

# CORS middleware
config = load_config()
if config.get('api', {}).get('enable_cors', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    """Initialize node on startup."""
    await node.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown node on shutdown."""
    await node.stop()


@app.get("/info", response_model=NodeInfo)
async def get_node_info():
    """Get node information."""
    return NodeInfo(
        host=node.host,
        port=node.port,
        peers=len(node.peer_manager.get_connected_peers()),
        version="1.0"
    )


@app.get("/blockchain", response_model=BlockchainInfo)
async def get_blockchain_info():
    """Get blockchain information."""
    return BlockchainInfo(
        blocks=len(blockchain.chain),
        difficulty=blockchain.pow.difficulty,
        pending_transactions=len(blockchain.pending_transactions),
        mining_reward=blockchain.mining_reward
    )


@app.get("/blocks", response_model=List[BlockResponse])
async def get_blocks(limit: int = 10, offset: int = 0):
    """Get blocks from the blockchain."""
    blocks = blockchain.chain[offset:offset + limit]
    return [BlockResponse(
        index=block.index,
        timestamp=block.timestamp,
        transactions=[TransactionResponse(
            txid=tx.txid,
            sender=tx.sender,
            receiver=tx.receiver,
            amount=tx.amount,
            fee=tx.fee,
            timestamp=tx.timestamp,
            signature=tx.signature
        ) for tx in block.transactions],
        previous_hash=block.previous_hash,
        nonce=block.nonce,
        hash=block.hash,
        difficulty=block.difficulty
    ) for block in blocks]


@app.get("/blocks/{block_index}", response_model=BlockResponse)
async def get_block(block_index: int):
    """Get a specific block by index."""
    if block_index < 0 or block_index >= len(blockchain.chain):
        raise HTTPException(status_code=404, detail="Block not found")

    block = blockchain.chain[block_index]
    return BlockResponse(
        index=block.index,
        timestamp=block.timestamp,
        transactions=[TransactionResponse(
            txid=tx.txid,
            sender=tx.sender,
            receiver=tx.receiver,
            amount=tx.amount,
            fee=tx.fee,
            timestamp=tx.timestamp,
            signature=tx.signature
        ) for tx in block.transactions],
        previous_hash=block.previous_hash,
        nonce=block.nonce,
        hash=block.hash,
        difficulty=block.difficulty
    )


@app.get("/transactions/pending", response_model=List[TransactionResponse])
async def get_pending_transactions():
    """Get pending transactions in mempool."""
    return [TransactionResponse(
        txid=tx.txid,
        sender=tx.sender,
        receiver=tx.receiver,
        amount=tx.amount,
        fee=tx.fee,
        timestamp=tx.timestamp,
        signature=tx.signature
    ) for tx in blockchain.pending_transactions]


@app.post("/transactions", response_model=TransactionResponse)
async def submit_transaction(tx_request: TransactionRequest):
    """Submit a new transaction."""
    # Create transaction object
    tx = Transaction(
        sender=tx_request.sender,
        receiver=tx_request.receiver,
        amount=tx_request.amount,
        fee=tx_request.fee,
        signature=tx_request.signature
    )

    # Validate and add to blockchain
    if not blockchain.add_transaction(tx):
        raise HTTPException(status_code=400, detail="Invalid transaction")

    # Broadcast to network
    await node.broadcast_transaction(tx)

    return TransactionResponse(
        txid=tx.txid,
        sender=tx.sender,
        receiver=tx.receiver,
        amount=tx.amount,
        fee=tx.fee,
        timestamp=tx.timestamp,
        signature=tx.signature
    )


@app.get("/balance/{address}")
async def get_balance(address: str):
    """Get balance for an address."""
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance}


@app.post("/mine")
async def mine_block(miner_address: str):
    """Mine a new block."""
    block = node.mine_block(miner_address)
    if not block:
        raise HTTPException(status_code=400, detail="No transactions to mine")

    # Broadcast new block
    await node.broadcast_block(block)

    return {
        "block_index": block.index,
        "transactions": len(block.transactions),
        "hash": block.hash
    }


@app.get("/peers")
async def get_peers():
    """Get connected peers."""
    peers = node.peer_manager.get_connected_peers()
    return [{"host": peer.host, "port": peer.port} for peer in peers]


if __name__ == "__main__":
    import uvicorn
    config = load_config()
    port = config.get('api', {}).get('rest_port', 8080)
    uvicorn.run(app, host="0.0.0.0", port=port)