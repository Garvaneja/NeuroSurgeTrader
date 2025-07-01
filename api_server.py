from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
import pandas as pd
import numpy as np
from kraken_trader import KrakenTrader
from rl_model import TradingEnv, RLTrader
from cryptography.fernet import Fernet
import logging
import asyncio
import os
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class APIKeys(BaseModel):
    api_key: str
    api_secret: str

class BacktestRequest(BaseModel):
    start_date: str
    end_date: str

with open('config_meme.yaml', 'r') as file:
    config = yaml.safe_load(file)

trader = KrakenTrader(api_key=config['kraken']['api_key'], api_secret=config['kraken']['api_secret'])

key_file = 'encryption_key.key'
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
with open(key_file, 'rb') as f:
    key = f.read()
cipher = Fernet(key)

@app.post("/api/save-api-keys")
async def save_api_keys(keys: APIKeys):
    try:
        encrypted_key = cipher.encrypt(keys.api_key.encode()).decode()
        encrypted_secret = cipher.encrypt(keys.api_secret.encode()).decode()
        config['kraken']['api_key'] = encrypted_key
        config['kraken']['api_secret'] = encrypted_secret
        with open('config_meme.yaml', 'w') as file:
            yaml.dump(config, file)
        return {"status": "API keys saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bot-status")
async def get_bot_status():
    try:
        with open('bot_status.json', 'r') as f:
            return json.load(f)
    except:
        return {
            "bot_name": "NeuroMemeSurge",
            "status": "Stopped",
            "portfolio_value": 400.0,
            "last_trade": "None",
            "alpha": 0.0
        }

@app.post("/api/backtest")
async def run_backtest(request: BacktestRequest):
    try:
        data = {}
        for asset in config['assets']:
            df = await trader.get_historical_data(asset, interval=60)
            df = df[(df['time'] >= pd.to_datetime(request.start_date)) & (df['time'] <= pd.to_datetime(request.end_date))]
            data[asset] = df['close']
            data[asset + '_volume'] = df['volume']
        data = pd.DataFrame(data)
        
        env = TradingEnv(data, config['assets'], config['capital'])
        rl_trader = RLTrader(env)
        if os.path.exists("ppo_model.zip"):
            rl_trader.load("ppo_model.zip")
        
        obs = env.reset()
        returns = []
        while True:
            action = rl_trader.predict(obs)
            obs, reward, done, info = env.step(action)
            returns.append(reward)
            if done:
                break
        
        cumulative_return = np.prod(1 + np.array(returns)) - 1
        return {
            "cumulative_return": cumulative_return,
            "sharpe_ratio": np.mean(returns) / np.std(returns) * np.sqrt(252),
            "max_drawdown": np.min(np.cumsum(returns) - np.maximum.accumulate(np.cumsum(returns)))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live-trades")
async def get_live_trades():
    try:
        with open('bot_status.json', 'r') as f:
            status = json.load(f)
        return [status["last_trade"]] if status["last_trade"] != "None" else []
    except:
        return []

@app.get("/api/portfolio")
async def get_portfolio():
    try:
        with open('bot_status.json', 'r') as f:
            status = json.load(f)
        return {
            "value": status["portfolio_value"],
            "assets": [
                {"asset": asset, "quantity": 0, "value": 0} for asset in config['assets']
            ]
        }
    except:
        return {
            "value": 400.0,
            "assets": [
                {"asset": asset, "quantity": 0, "value": 0} for asset in config['assets']
            ]
        }