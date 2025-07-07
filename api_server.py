from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import yaml

from fastapi.responses import JSONResponse
from neuro_meme_surge import NeuroMemeSurge
import asyncio
import logging

app = FastAPI()
bot = NeuroMemeSurge()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/config")
def get_config():
    with open("config_meme.yaml", "r") as f:
        config = yaml.safe_load(f)
    return JSONResponse(content=config)

@app.get("/api/portfolio")
async def get_portfolio():
    return {
        "portfolio_value": bot.portfolio_value,
        "positions": bot.positions,
        "last_trade": bot.trade_log[-1] if bot.trade_log else None,
        "status": bot.status,
        "alpha": 0.51
    }

@app.get("/api/historical-data/{asset}")
async def get_historical_data(asset: str):
    df = await bot.trader.get_historical_data(asset)
    return df.reset_index().to_dict(orient="records")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({
                "status": bot.status,
                "portfolio_value": bot.portfolio_value,
                "positions": bot.positions,
                "last_trade": bot.trade_log[-1] if bot.trade_log else None,
                "alpha": 0.51
            })
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logging.warning("WebSocket disconnected.")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")