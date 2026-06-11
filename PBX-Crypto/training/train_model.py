import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from xgboost import XGBRegressor

import joblib

from indicators.indicators import add_indicators
from indicators.indicators import add_trend

from utils.binance_data import get_binance_data


print("Downloading market data...")


# =========================
# Choose Timeframe
# =========================

print("\nSelect Training Timeframe:")

print("1 = 1 Hour")
print("2 = 4 Hours")
print("3 = 12 Hours")
print("4 = 24 Hours")

choice = input("Choice: ")


if choice == "1":

    interval = "5m"
    period = "30d"

elif choice == "2":

    interval = "15m"
    period = "60d"

elif choice == "3":

    interval = "30m"
    period = "60d"

else:

    interval = "1h"
    period = "730d"

# =========================
# Future
# =========================

future_map = {

    "1": 12,
    "2": 16,
    "3": 24,
    "4": 24
}

future_shift = future_map.get(choice, 12)


# =========================
# File Model's Name
# =========================

model_names = {

    "1": "xgb_1h.pkl",
    "2": "xgb_4h.pkl",
    "3": "xgb_12h.pkl",
    "4": "xgb_24h.pkl"
}

model_file = model_names.get(choice, "xgb_1h.pkl")

# =========================
# Symbol's list
# =========================

symbols = [

    "BTC-USD",
    "ETH-USD",
    "BNB-USD",
    "SOL-USD",
    "XRP-USD",
    "ADA-USD",
    "DOGE-USD",
    "TRX-USD",
    "DOT-USD",
    "LTC-USD",
    "BCH-USD",
    "LINK-USD",
    "XLM-USD",
    "ATOM-USD",
    "ETC-USD",
    "XMR-USD",
    "HBAR-USD",
    "ICP-USD",
    "FIL-USD",
    "ARB-USD",
    "OP-USD",
    "AVAX-USD",
    "SEI-USD",
    "NEAR-USD",
    "AAVE-USD",
    "MKR-USD",
    "INJ-USD",
    "RENDER-USD",
    "FET-USD",
    "ALGO-USD",
    "EGLD-USD",
    "THETA-USD",
    "SAND-USD",
    "MANA-USD",
    "AXS-USD",
    "FLOW-USD",
    "CHZ-USD",
    "CRV-USD",
    "LDO-USD",
    "SNX-USD",
    "DYDX-USD",
    "1INCH-USD",
    "BAT-USD",
    "ZRX-USD",
    "ENS-USD",
    "CAKE-USD",
    "APE-USD",
    "SHIB-USD",
    "FLOKI-USD",
    "BONK-USD",
    "WIF-USD",
    "JUP-USD",
    "TIA-USD",
    "STRK-USD",
    "AR-USD",
    "KAS-USD",
    "RUNE-USD"
]

# =========================
# Make Symbol Id
# =========================

symbol_map = {

    symbol: idx + 1
    for idx, symbol in enumerate(symbols)
}


all_data = []


# =========================
# Download Data
# =========================

for symbol in symbols:

    try:

        print(f"Downloading {symbol} ...")

        df = get_binance_data(

            symbol=symbol,
            interval=interval,
            limit=1500,
            period=period
        )

        df = add_indicators(df)

        df = add_trend(df)

        df['symbol_id'] = symbol_map[symbol]

        all_data.append(df)

    except Exception as e:

        print(f"Skipped {symbol} -> {e}")

# =========================
# Mixing Data
# =========================

df = pd.concat(all_data)


print("Calculating indicators...")


# =========================
# Target
# =========================

df['target'] = (

    (df['close'].shift(-future_shift) - df['close'])
    / df['close']

) * 100


# محدود کردن تغییرات شدید

df['target'] = df['target'].clip(-5, 5)


# حذف داده خالی

df.dropna(inplace=True)


# =========================
# Features
# =========================

features = [

    'symbol_id',
    'close',
    'volume',
    'rsi',
    'macd',
    'macd_signal',
    'ema_20',
    'sma_20',
    'bb_high',
    'bb_low',
    'high',
    'low',
    'atr',
    'stoch_rsi',
    'momentum'
]


X = df[features]

y = df['target']


# =========================
# Train Test Split
# =========================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    shuffle=False
)


print("Training XGBoost model...")

# =========================
# Model
# =========================

model = XGBRegressor(

    n_estimators=300,

    learning_rate=0.05,

    max_depth=6,

    subsample=0.9,

    colsample_bytree=0.9,

)


# =========================
# Train
# =========================

model.fit(X_train, y_train,)


# =========================
# Predict
# =========================

preds = model.predict(X_test)


mae = mean_absolute_error(y_test, preds)

print(f"MAE Error: {mae:.2f}")


# =========================
# Save Model
# =========================

joblib.dump(model, f'models/{model_file}')

print("Model saved successfully!")



