from fastapi import FastAPI, Request
import requests
import jwt
import datetime

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GATEWAY_SECRET = "gatewayDemo_secret"
# SECRET = "have-a-good-day"
GATEWAY = "gatewaydemo"


@app.post("/create_transaction")
async def create_transaction():
    url = f"https://gatewayapi.smallcase.com/gateway/{GATEWAY}/transaction"
    payload = {
        "intent": "HOLDINGS_IMPORT",
        "version": "v2",
        "assetConfig": {"mfHoldings": True}
    }
    headers = {
        "accept": "application/json",
        "x-gateway-secret": GATEWAY_SECRET,
        "x-gateway-authtoken": create_guest_jwt(),
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    token = headers["x-gateway-authtoken"]
    return {
        "response": response.json(),
        "token": token,
        "gateway": GATEWAY
    }


def create_guest_jwt():
    payload = {
        "guest": True,
        "exp": 2556124199,
    }
    token = jwt.encode(payload, GATEWAY_SECRET, algorithm="HS256")
    return token

@app.get("/fetch_holdings")
async def fetch_holdings(auth_token: str, version: str = "v2", mf_holdings: bool = False):
    url = f"https://gatewayapi.smallcase.com/v1/{GATEWAY}/engine/user/holdings"
    params = {
        "version": version
    }
    if mf_holdings:
        params["mfHoldings"] = "true"

    headers = {
        "x-gateway-secret": GATEWAY_SECRET,
        "x-gateway-authtoken": auth_token,
        "accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    return response.json()
