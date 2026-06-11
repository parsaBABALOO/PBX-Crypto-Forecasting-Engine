import ta


def add_indicators(df):

    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()

    macd = ta.trend.MACD(df['close'])

    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    df['ema_20'] = ta.trend.EMAIndicator(
        df['close'],
        window=20
    ).ema_indicator()

    df['sma_20'] = ta.trend.SMAIndicator(
        df['close'],
        window=20
    ).sma_indicator()

    boll = ta.volatility.BollingerBands(df['close'])

    df['bb_high'] = boll.bollinger_hband()
    df['bb_low'] = boll.bollinger_lband()
    # ATR (قدرت نوسان)
    df['atr'] = ta.volatility.AverageTrueRange(
        df['high'],
        df['low'],
        df['close']
        ).average_true_range()

# Stochastic RSI
    stoch = ta.momentum.StochRSIIndicator(df['close'])
    df['stoch_rsi'] = stoch.stochrsi()
    # Momentum
    df['momentum'] = ta.momentum.ROCIndicator(
       df['close']
       ).roc()
    
    return df


def add_trend(df):

    df['trend'] = 0

    df.loc[df['ema_20'] > df['sma_20'], 'trend'] = 1
    df.loc[df['ema_20'] < df['sma_20'], 'trend'] = -1

    return df

