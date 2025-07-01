import krakenex
import pandas as pd
import asyncio
import logging
import time

logger = logging.getLogger(__name__)

class KrakenTrader:
    def __init__(self, api_key, api_secret):
        self.client = krakenex.API(api_key, api_secret)
        self.pair_map = {
            'SOLUSD': 'SOLUSD',
            'DOGEUSD': 'XDGUSD',  # Kraken uses XDG for DOGE
            'SHIBUSD': 'SHIBUSD'
        }
        self.last_call_time = 0
        self.rate_limit_delay = 1.5  # Kraken public API rate limit: ~1 call/second

    async def _respect_rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_call_time = time.time()

    async def get_historical_data(self, pair, interval=60):
        try:
            mapped_pair = self.pair_map.get(pair, pair)
            await self._respect_rate_limit()
            logger.info(f"Fetching OHLC data for {mapped_pair} (original: {pair})")
            data = self.client.query_public('OHLC', {'pair': mapped_pair, 'interval': interval})
            if 'error' in data and data['error']:
                logger.error(f"Kraken API error for {mapped_pair}: {data['error']}")
                return None
            if mapped_pair not in data['result'] or not data['result'][mapped_pair]:
                logger.error(f"No data returned for {mapped_pair}. Response: {data}")
                return None
            df = pd.DataFrame(data['result'][mapped_pair], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            if df.empty or df['close'].isna().all():
                logger.error(f"Empty or invalid data for {mapped_pair}: {df.head() if not df.empty else 'Empty DataFrame'}")
                return None
            logger.info(f"Successfully fetched {len(df)} rows for {mapped_pair}: {df['close'].tail(5).to_list()}")
            return df
        except Exception as e:
            logger.error(f"Exception fetching historical data for {pair} (mapped: {mapped_pair}): {e}")
            return None

    async def get_current_price(self, pair):
        try:
            mapped_pair = self.pair_map.get(pair, pair)
            await self._respect_rate_limit()
            logger.info(f"Fetching ticker for {mapped_pair}")
            data = self.client.query_public('Ticker', {'pair': mapped_pair})
            if 'error' in data and data['error']:
                logger.error(f"Kraken API error for {mapped_pair}: {data['error']}")
                return None
            price = float(data['result'][mapped_pair]['c'][0])
            return price if price > 0 else None
        except Exception as e:
            logger.error(f"Error fetching current price for {pair}: {e}")
            return None

    async def place_market_order(self, pair, quantity, order_type):
        try:
            mapped_pair = self.pair_map.get(pair, pair)
            await self._respect_rate_limit()
            order = self.client.query_private('AddOrder', {
                'pair': mapped_pair,
                'type': order_type,
                'ordertype': 'market',
                'volume': abs(quantity)
            })
            if 'error' in order and order['error']:
                logger.error(f"Order failed for {mapped_pair}: {order['error']}")
                return None
            logger.info(f"Order placed: {order_type} {quantity} {mapped_pair}")
            return order
        except Exception as e:
            logger.error(f"Error placing order for {pair}: {e}")
            return None