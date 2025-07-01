import yaml
import pandas as pd
import numpy as np
from kraken_trader import KrakenTrader
from rl_model import TradingEnv, RLTrader
import logging
from datetime import datetime, timedelta
import asyncio
import json
import os
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XSentimentAnalyzer:
    def __init__(self, bearer_token: str = None):
        self.bearer_token = bearer_token or "MOCK_TOKEN"
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.analyzer = SentimentIntensityAnalyzer()
        self.assets = ["SOLUSD", "DOGEUSD", "SHIBUSD"]
        self.query_map = {
            "SOLUSD": "$SOL OR Solana",
            "DOGEUSD": "$DOGE OR Dogecoin",
            "SHIBUSD": "$SHIB OR Shiba Inu"
        }

    def fetch_posts(self, query: str, max_results: int = 10) -> List[str]:
        if self.bearer_token == "MOCK_TOKEN":
            logger.warning("Using mock X data")
            return [f"Sample tweet about {query}" for _ in range(max_results)]
        try:
            url = "https://api.x.com/2/tweets/search/recent"
            params = {"query": query + " -is:retweet lang:en", "max_results": max_results, "tweet.fields": "text,created_at"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return [post["text"] for post in response.json().get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching X posts for {query}: {e}")
            return []

    async def get_sentiment_scores(self) -> List[float]:
        scores = []
        for asset in self.assets:
            posts = self.fetch_posts(self.query_map[asset])
            avg_score = np.mean([self.analyze_sentiment(post) for post in posts]) if posts else 0.0
            normalized_score = (avg_score + 1) / 2
            scores.append(normalized_score)
            logger.info(f"Sentiment for {asset}: {normalized_score:.4f}")
            await asyncio.sleep(5)  # Avoid rate limits
        return scores

    def analyze_sentiment(self, text: str) -> float:
        return self.analyzer.polarity_scores(text)["compound"]

class NeuroMemeSurge:
    def __init__(self, config_path: str = 'config_meme.yaml'):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.trader = KrakenTrader(api_key=self.config['kraken']['api_key'], api_secret=self.config['kraken']['api_secret'])
        self.x_analyzer = XSentimentAnalyzer()
        self.assets = self.config['assets']
        self.initial_capital = self.config['capital']
        self.capital = self.initial_capital
        self.portfolio_value = self.initial_capital
        self.positions = {asset: 0 for asset in self.assets}
        self.entry_prices = {asset: 0 for asset in self.assets}
        self.trade_log = []
        self.status = "Stopped"
        self.max_drawdown = 0.25
        self.max_position_size = 0.3
        self.min_order_sizes = {'SOLUSD': 0.1, 'DOGEUSD': 50.0, 'SHIBUSD': 500000.0}
        self.trade_frequency = timedelta(seconds=self.config['trade_frequency'])
        self.cad_usd_rate = 1.37
        self.fee_rate = 0.0026
        
        # Sync positions with Kraken balance
        loop = asyncio.get_event_loop()
        balance = loop.run_until_complete(self.trader.get_balance())
        self.positions['SOLUSD'] = float(balance.get('SOL', 0))
        self.positions['DOGEUSD'] = float(balance.get('XXDG', 0))
        self.positions['SHIBUSD'] = float(balance.get('SHIB', 0))
        
        self.data = self._fetch_initial_data()
        self.env = TradingEnv(self.data, self.assets, self.initial_capital)
        self.rl_trader = RLTrader(self.env)
        if os.path.exists("ppo_model.zip"):
            self.rl_trader.load("ppo_model.zip")
        else:
            self._train_rl()

    def _fetch_initial_data(self) -> pd.DataFrame:
        size = 1000
        data = {}
        for asset in self.assets:
            base_price = 150.0 if asset == 'SOLUSD' else 0.15 if asset == 'DOGEUSD' else 0.000015
            prices = np.random.lognormal(mean=np.log(base_price), sigma=0.1, size=size)
            prices = np.where(np.isnan(prices) | np.isinf(prices), base_price, prices)
            data[asset] = pd.Series(prices)
            data[f"{asset}_volume"] = pd.Series(np.random.uniform(1000, 10000, size))
        return pd.DataFrame(data)

    def _train_rl(self):
        logger.info("Training RL model...")
        self.rl_trader.train(total_timesteps=50000)
        self.rl_trader.save("ppo_model.zip")

    def _calculate_momentum(self, data: pd.DataFrame) -> Dict[str, float]:
        momentum = {}
        for asset in self.assets:
            if len(data[asset]) >= 20:
                mom20 = data[asset].iloc[-1] / data[asset].iloc[-20] - 1
                mom5 = data[asset].iloc[-1] / data[asset].iloc[-5] - 1
                momentum[asset] = 0.7 * mom5 + 0.3 * mom20
            else:
                momentum[asset] = 0.0
        return momentum

    async def _get_current_price(self, asset: str) -> float:
        try:
            ticker = await self.trader.get_ticker(asset)
            return float(ticker['c'][0])
        except Exception as e:
            logger.error(f"Error fetching price for {asset}: {e}")
            return 150.0 if asset == 'SOLUSD' else 0.15 if asset == 'DOGEUSD' else 0.000015

    async def _check_funds(self, asset: str, quantity: float, price: float) -> bool:
        usd_cost = quantity * price * (1 + self.fee_rate)
        cad_cost = usd_cost * self.cad_usd_rate
        balance = await self.trader.get_balance()
        available_cad = float(balance.get('ZCAD', 0))
        available_usd = float(balance.get('ZUSD', 0))
        logger.info(f"Checking funds for {asset}: Need ${usd_cost:.2f} USD or ${cad_cost:.2f} CAD, Available USD: ${available_usd:.2f}, CAD: ${available_cad:.2f}")
        if available_usd >= usd_cost or available_cad >= cad_cost:
            return True
        logger.error(f"Insufficient funds for {asset}: Need ${usd_cost:.2f} USD or ${cad_cost:.2f} CAD")
        return False

    async def _execute_order(self, asset: str, quantity: float, order_type: str, price: float):
        if quantity < self.min_order_sizes[asset]:
            logger.warning(f"Order quantity {quantity} for {asset} below minimum {self.min_order_sizes[asset]}")
            return
        if not await self._check_funds(asset, quantity, price):
            return
        order = await self.trader.place_market_order(asset, quantity, order_type)
        if order:
            usd_cost = quantity * price * (1 + self.fee_rate if order_type == 'buy' else 1 - self.fee_rate)
            cad_cost = usd_cost * self.cad_usd_rate
            if order_type == 'buy':
                self.positions[asset] += quantity
                self.capital -= cad_cost
                self.entry_prices[asset] = price
            else:
                self.positions[asset] -= quantity
                self.capital += cad_cost
            self.trade_log.append({"asset": asset, "type": order_type, "quantity": quantity, "price": price, "time": datetime.now().isoformat()})
            logger.info(f"Executed {order_type} {quantity} {asset} at ${price}")

    async def fetch_enhanced_data(self) -> pd.DataFrame:
        data = {}
        for asset in self.assets:
            df = await self.trader.get_historical_data(asset, interval=60)
            if df is None or df.empty:
                logger.warning(f"No data for {asset}, using fallback")
                base_price = 150.0 if asset == 'SOLUSD' else 0.15 if asset == 'DOGEUSD' else 0.000015
                df = pd.DataFrame({
                    'close': np.random.lognormal(mean=np.log(base_price), sigma=0.1, size=60),
                    'volume': np.random.uniform(1000, 10000, 60)
                })
            data[asset] = df['close']
            data[f"{asset}_volume"] = df['volume']
        return pd.DataFrame(data)

    async def check_drawdown(self) -> bool:
        drawdown = (self.initial_capital - self.portfolio_value) / self.initial_capital
        if drawdown > self.max_drawdown:
            logger.error(f"Max drawdown exceeded: {drawdown:.2%}")
            self.status = "Paused"
            return False
        return True

    async def execute_aggressive_trades(self, data: pd.DataFrame):
        if not await self.check_drawdown():
            return
        prices = {asset: await self._get_current_price(asset) for asset in self.assets}
        momentum = self._calculate_momentum(data)
        self.portfolio_value = sum(self.positions[asset] * prices[asset] for asset in self.assets) + self.capital
        observation = await self._create_observation(data, prices)
        
        if np.any(np.isnan(observation)) or np.any(np.isinf(observation)):
            logger.error(f"Invalid observation: {observation}")
            return
        
        action = self.rl_trader.predict(observation)
        for i, asset in enumerate(self.assets):
            action_type = action[i * 2]
            quantity = abs(action[i * 2 + 1]) * self.portfolio_value / prices[asset]
            momentum_multiplier = 0.5 + min(max(momentum[asset], -0.5), 0.5) * 2
            quantity *= momentum_multiplier
            max_possible = min(quantity, self.max_position_size * self.portfolio_value / prices[asset])
            max_possible = max(max_possible, self.min_order_sizes[asset])  # Enforce minimum order size
            
            if action_type > 0.3 and await self._check_funds(asset, max_possible, prices[asset]):
                await self._execute_order(asset, max_possible, 'buy', prices[asset])
            elif action_type < -0.3 and self.positions[asset] >= self.min_order_sizes[asset]:
                sell_quantity = min(max_possible, self.positions[asset])
                await self._execute_order(asset, sell_quantity, 'sell', prices[asset])

    async def _create_observation(self, data: pd.DataFrame, prices: Dict[str, float]) -> np.ndarray:
        volumes = [data[f"{asset}_volume"].iloc[-1] for asset in self.assets]
        sentiment_scores = await self.x_analyzer.get_sentiment_scores()
        position_values = [self.positions[asset] * prices[asset] for asset in self.assets]
        momentum = list(self._calculate_momentum(data).values())
        return np.array(list(prices.values()) + volumes + sentiment_scores + momentum + position_values + [self.capital], dtype=np.float32)

    async def run(self):
        self.status = "Running"
        logger.info("Starting NeuroMemeSurge in AGGRESSIVE mode")
        while self.status == "Running":
            try:
                data = await self.fetch_enhanced_data()
                await self.execute_aggressive_trades(data)
                self.save_status()
                await asyncio.sleep(self.trade_frequency.total_seconds())
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(60)

    def save_status(self):
        with open('bot_status.json', 'w') as f:
            json.dump({
                "bot_name": "NeuroMemeSurge",
                "status": self.status,
                "portfolio_value": self.portfolio_value,
                "last_trade": self.trade_log[-1] if self.trade_log else None,
                "positions": self.positions
            }, f)

if __name__ == "__main__":
    bot = NeuroMemeSurge()
    asyncio.run(bot.run())