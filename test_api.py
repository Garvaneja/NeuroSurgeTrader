import krakenex
client = krakenex.API("api_key", "api_secret")
order = client.query_private('AddOrder', {
    'pair': 'SOLUSD',
    'type': 'buy',
    'ordertype': 'market',
    'volume': 0.01
})
print(order)