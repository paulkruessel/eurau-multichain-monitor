from fastapi import FastAPI, HTTPException, status
import os

from web3 import Web3

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/connection")
async def getConnectionInfo():
    rpc_url = os.environ["BASE_RPC_URL"]

    if not rpc_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="BASE_RPC_URL is not configured"
        )

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if (not w3.is_connected()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RPC Endpoint with URL {rpc_url} is unavailable."
        )

    if (w3.eth.chain_id != 8453):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chain Id {w3.eth.chain_id} is not  correct id 8453."
        )

    return {
        "connected": True,
        "chain_id": w3.eth.chain_id,
        "block_number": w3.eth.block_number
    }