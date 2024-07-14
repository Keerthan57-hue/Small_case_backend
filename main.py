import uvicorn
from fastapi import FastAPI, Request, Query
import requests
import jwt
import datetime
import logging

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GATEWAY_SECRET = "gatewayDemo_secret"
GATEWAY = "gatewaydemo"
logging.basicConfig(level=logging.INFO)


@app.post("/create_transaction")
async def create_transaction():
    payload = {
        "intent": "HOLDINGS_IMPORT",
        "version": "v2",
        "assetConfig": {"mfHoldings": True},
    }
    headers = {
        "accept": "application/json",
        "x-gateway-secret": GATEWAY_SECRET,
        "x-gateway-authtoken": create_guest_jwt(),
        "content-type": "application/json"
    }

    logging.info(f"Headers: {headers}")

    url = f"https://gatewayapi.smallcase.com/gateway/{GATEWAY}/transaction"
    response = requests.post(url, json=payload, headers=headers)
    token = headers["x-gateway-authtoken"]

    logging.info(f"Response: {response.json()}")
    logging.info(f"Token: {token}")

    return {
        "response": response.json(),
        "token": token,
        "gateway": GATEWAY
    }


@app.get("/fetch_holdings")
async def fetch_holdings(auth_token: str, include_mf: bool = Query(False), v2_format: bool = Query(False)):
    params = {
        "version": "v2" if v2_format else "v1",
        "mfHoldings": include_mf,
    }

    headers = {
        "x-gateway-secret": GATEWAY_SECRET,
        "x-gateway-authtoken": auth_token,
        "accept": "application/json"
    }

    logging.info(f"Fetch Holdings Headers: {headers}")

    url = f"https://gatewayapi.smallcase.com/v1/{GATEWAY}/engine/user/holdings"
    response = requests.get(url, params=params, headers=headers)
    return response.json()


def create_guest_jwt():
    issue = datetime.datetime.utcnow()
    expire = issue + datetime.timedelta(days=1)
    payload = {
        "guest": True,
        "exp": expire,
    }
    token = jwt.encode(payload, GATEWAY_SECRET, algorithm="HS256")
    logging.info(f"Generated JWT: {token}")
    return token


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
