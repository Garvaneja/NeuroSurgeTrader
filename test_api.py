import krakenex
import base64
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Initialize Kraken client
    client = krakenex.API(
        key="VCiZhBqaeNYCbOncCih+vEZiFbY3zgWSBmhN1Tngf0w51WKZF7jM4/84",
        secret="1MfU5HaddCWge9KOlOH7w9rkToZPQDrQb9d5VOFN+ekBLhV9ngZMPi0d1Pm1yijPVOVn+5Ah0gurpgZqcPU1Lg=="  # Ensure this matches Kraken
    )
    
    # Test balance
    balance = client.query_private('Balance')
    if 'error' in balance and balance['error']:
        logger.error(f"Balance error: {balance['error']}")
    else:
        logger.info(f"Balance: {balance['result']}")
        print(f"Balance: {balance['result']}")

    # Estimate SOLUSD price and required funds
    ticker = client.query_public('Ticker', {'pair': 'SOLUSD'})
    if 'error' in ticker and ticker['error']:
        logger.error(f"Ticker error: {ticker['error']}")
    else:
        sol_price = float(ticker['result']['SOLUSD']['c'][0])
        volume = 0.2  # Kraken minimum for SOLUSD
        usd_cost = volume * sol_price * 1.0026  # Include 0.26% taker fee
        cad_cost = usd_cost * 1.37  # Higher spread (2%)
        available_cad = float(balance['result'].get('ZCAD', 0))
        available_usd = float(balance['result'].get('ZUSD', 0))

        logger.info(f"SOLUSD price: ${sol_price:.2f}, Required CAD: ${cad_cost:.2f}, Available CAD: ${available_cad:.2f}, Available USD: ${available_usd:.2f}")
        if available_usd >= usd_cost:
            logger.info("Using USD balance for SOLUSD order")
            order = client.query_private('AddOrder', {
                'pair': 'SOLUSD',
                'type': 'buy',
                'ordertype': 'market',
                'volume': volume
            })
        elif available_cad >= cad_cost:
            logger.info("Using CAD balance for SOLUSD order")
            order = client.query_private('AddOrder', {
                'pair': 'SOLUSD',
                'type': 'buy',
                'ordertype': 'market',
                'volume': volume
            })
        else:
            logger.error(f"Insufficient funds for SOLUSD: Need ${cad_cost:.2f} CAD or ${usd_cost:.2f} USD")
            # Try DOGEUSD (smaller order)
            ticker_doge = client.query_public('Ticker', {'pair': 'DOGEUSD'})
            if 'error' in ticker_doge and ticker_doge['error']:
                logger.error(f"DOGEUSD Ticker error: {ticker_doge['error']}")
            else:
                doge_price = float(ticker_doge['result']['DOGEUSD']['c'][0])
                volume_doge = 50.0  # Kraken minimum for DOGEUSD
                usd_cost_doge = volume_doge * doge_price * 1.0026
                cad_cost_doge = usd_cost_doge * 1.37
                logger.info(f"DOGEUSD price: ${doge_price:.4f}, Required CAD: ${cad_cost_doge:.2f}, Available CAD: ${available_cad:.2f}")
                if available_cad >= cad_cost_doge:
                    order = client.query_private('AddOrder', {
                        'pair': 'DOGEUSD',
                        'type': 'buy',
                        'ordertype': 'market',
                        'volume': volume_doge
                    })
                else:
                    logger.error(f"Insufficient funds for DOGEUSD: Need ${cad_cost_doge:.2f} CAD")
                    order = {'error': ['EOrder:Insufficient funds']}

        if 'error' in order and order['error']:
            logger.error(f"Order error: {order['error']}")
        else:
            logger.info(f"Order: {order['result']}")
            print(f"Order: {order['result']}")
except Exception as e:
    logger.error(f"API error: {e}")
    print(f"Error: {e}")