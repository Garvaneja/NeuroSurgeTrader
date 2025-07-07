import krakenex
import pandas as pd
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KrakenTrader:
    def __init__(self, api_key: str, api_secret: str):
        self.client = krakenex.API(key=api_key, secret=api_secret)
        self.asset_map = {"SOLUSD": "SOLUSD", "DOGEUSD": "XDGUSD", "SHIBUSD": "SHIBUSD"}

    async def get_balance(self) -> dict:
        loop = asyncio.get_event_loop()
        try:
            balance = await loop.run_in_executor(None, lambda: self.client.query_private('Balance'))
            if 'error' in balance and balance['error']:
                logger.error(f"Balance error: {balance['error']}")
                return {}
            return balance['result']
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}

    async def get_ticker(self, pair: str) -> dict:
        loop = asyncio.get_event_loop()
        try:
            kraken_pair = self.asset_map.get(pair, pair)
            ticker = await loop.run_in_executor(None, lambda: self.client.query_public('Ticker', {'pair': kraken_pair}))
            if 'error' in ticker and ticker['error']:
                logger.error(f"Ticker error for {pair}: {ticker['error']}")
                return {}
            return ticker['result'][kraken_pair]
        except Exception as e:
            logger.error(f"Error fetching ticker for {pair}: {e}")
            return {}

    async def place_market_order(self, pair: str, quantity: float, order_type: str) -> dict:
        loop = asyncio.get_event_loop()
        try:
            order = await loop.run_in_executor(None, lambda: self.client.query_private('AddOrder', {
                'pair': self.asset_map.get(pair, pair),
                'type': order_type,
                'ordertype': 'market',
                'volume': quantity
            }))
            if 'error' in order and order['error']:
                logger.error(f"Order error for {pair}: {order['error']}")
                return {}
            return order['result']
        except Exception as e:
            logger.error(f"Error placing order for {pair}: {e}")
            return {}

    async def get_historical_data(self, pair: str, interval: int = 60) -> pd.DataFrame:
        loop = asyncio.get_event_loop()
        try:
            kraken_pair = self.asset_map.get(pair, pair)
            ohlc = await loop.run_in_executor(None, lambda: self.client.query_public('OHLC', {'pair': kraken_pair, 'interval': interval}))
            if 'error' in ohlc and ohlc['error']:
                logger.error(f"OHLC error for {pair}: {ohlc['error']}")
                return pd.DataFrame()
            data = ohlc['result'][kraken_pair]
            logger.info(f"Fetched {len(data)} rows for {pair}: {data[-5:]}")
            df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df[['close', 'volume']]
        except Exception as e:
            logger.error(f"Error fetching OHLC for {pair}: {e}")
            return pd.DataFrame()