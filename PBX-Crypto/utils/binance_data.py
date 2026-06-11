import yfinance as yf
import pandas as pd


def get_binance_data(
    symbol="BTC-USD",
    interval="5m",
    limit=1000,
    period="60d"
):
    try:

        ticker = yf.Ticker(symbol)

        df = ticker.history(
            period=period,
            interval=interval
        )

        if df.empty:
            raise Exception("No data downloaded")

        #df = df.reset_index()

        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })

        df = df[['open', 'high', 'low', 'close', 'volume']]

        return df.tail(limit)

    except Exception as e:
        raise Exception(f"Error downloading {symbol}: {e}")



