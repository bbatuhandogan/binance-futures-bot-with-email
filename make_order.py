import ccxt
import config
import pandas as pd

# API CONNECT
exchange = ccxt.binance({
    "apiKey": config.apiKey,
    "secret": config.secretKey,

    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})
symbol = "BTC/USDT"
newSymbol = "BTCUSDT"

def position_info():
    balance = exchange.fetch_balance()
    positions = balance['info']['positions']
    current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == newSymbol]
    position_bilgi = pd.DataFrame(current_positions,
                                  columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt",
                                           "positionSide"])
    return position_bilgi

def refresh_data():
    balance = exchange.fetch_balance()
    free_balance = exchange.fetch_free_balance()
    positions = balance['info']['positions']
    current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == newSymbol]
    position_bilgi = pd.DataFrame(current_positions,
                                  columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt",
                                           "positionSide"])

    bars = exchange.fetch_ohlcv(symbol, limit = 1)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    alinacak_miktar = (float(free_balance["USDT"]) * 6.0 / (float(df["close"][len(df.index) - 1]) + 100))
    return alinacak_miktar

def longEnter():
    try:
        alinacak_miktar = refresh_data()
        order = exchange.create_market_buy_order(symbol, alinacak_miktar)
        print("long isleme giriliyor")
    except ccxt.BaseError as Error:
        print("[ERROR] ", Error)

def longExit():
    try:
        position_bilgi = position_info()
        order = exchange.create_market_sell_order(symbol,
                                                  float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]),
                                                  {"reduceOnly": True})
        print("long islemden cikiliyor")
    except ccxt.BaseError as Error:
        print("[ERROR] ", Error)
def shortEnter():
    try:
        alinacak_miktar = refresh_data()
        order = exchange.create_market_sell_order(symbol, alinacak_miktar)
    except ccxt.BaseError as Error:
        print("[ERROR] ", Error)
def shortExit():
    try:
        position_bilgi = position_info()
        order = exchange.create_market_buy_order(symbol,
                                             (float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) * -1),
                                             {"reduceOnly": True})
        print("short islemden cikiliyor")
    except ccxt.BaseError as Error:
        print("[ERROR] ", Error)


