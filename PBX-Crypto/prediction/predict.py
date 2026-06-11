import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import joblib
import pandas as pd
from utils.binance_data import get_binance_data
from indicators.indicators import add_indicators
from utils.dependency import get_btc_dependency

# کدهای رنگی ANSI (برای ترمینال)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"



print("\nSelect Prediction Timeframe:")

print("1 = 1 Hour")
print("2 = 4 Hours")
print("3 = 12 Hours")
print("4 = 24 Hours")

choice = input("Choice: ")

model_map = {
    "1": "models/xgb_1h.pkl",
    "2": "models/xgb_4h.pkl",
    "3": "models/xgb_12h.pkl",
    "4": "models/xgb_24h.pkl"
}

timeframe_names = {
    "1": "1H",
    "2": "4H",
    "3": "12H",
    "4": "24H"
}

interval_map = {
    "1": "5m",
    "2": "15m",
    "3": "30m",
    "4": "1h"
}

selected_timeframe = timeframe_names.get(choice, "1H")

interval = interval_map.get(choice, "5m")

model_path = model_map.get(choice, "models/xgb_1h.pkl")

model = joblib.load(model_path)

if interval == "5m":
    period = "7d"
elif interval == "15m":
    period = "30d"
elif interval == "30m":
    period = "60d"
else:  # "1h"
    period = "90d"


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
    "PYTH-USD",
    "TIA-USD",
    "STRK-USD",
    "AR-USD",
    "KAS-USD",
    "RUNE-USD"
]


symbol_map = {
    symbol: idx + 1
    for idx, symbol in enumerate(symbols)
}


symbol = input("Enter coin symbol: ")

# دریافت سرمایه کاربر

try:
    capital = float(input("Enter your capital (USD): "))
    if capital <= 0:
        raise ValueError
except ValueError:
    print("⚠️ Invalid input. Using default capital $10,000.")
    capital = 10000.0


# ========== فیلتر سمبل‌های ضعیف ==========
weak_symbols = {
    "TRX-USD": ["1H"],     # تایم‌فریم ۱ ساعت
    "BNB-USD": ["12H"],    # تایم‌فریم ۱۲ ساعت
    "SOL-USD": ["12H"]     # تایم‌فریم ۱۲ ساعت
}

if symbol in weak_symbols and selected_timeframe in weak_symbols[symbol]:
    print("\n⚠️  WARNING: This symbol/timeframe showed weak performance in backtesting.")
    print("    Proceed with caution or choose another timeframe.\n")
# ========================================


future_map = {
    "1": 12,
    "2": 48,
    "3": 144,
    "4": 288
}

future_candles = future_map.get(choice, 12)


selected_timeframe = timeframe_names.get(choice, "1H")


df = get_binance_data(

    symbol=symbol,
    interval=interval,
    limit=300,
    period=period
)

# بعد از df = get_binance_data(...)
if 'Datetime' in df.columns:
    last_time = df['Datetime'].iloc[-1]
elif df.index.name == 'Datetime' or isinstance(df.index, pd.DatetimeIndex):
    last_time = df.index[-1]
else:
    # تلاش برای پیدا کردن ستون تاریخ
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    if date_cols:
        last_time = df[date_cols[0]].iloc[-1]
    else:
        last_time = "نامشخص"



if df.empty:
    print("There isn't any data. please check your Internet")
    exit()

    
df = add_indicators(df)

df.dropna(inplace=True)

latest = df.iloc[-1]

latest['symbol_id'] = symbol_map[symbol]


features = [[

    latest['symbol_id'],
    latest['close'],
    latest['volume'],
    latest['rsi'],
    latest['macd'],
    latest['macd_signal'],
    latest['ema_20'],
    latest['sma_20'],
    latest['bb_high'],
    latest['bb_low'],
    latest['high'],
    latest['low'],
    latest['atr'],
    latest['stoch_rsi'],
    latest['momentum']
]]

current_price = latest['close']


pred_percent = float(model.predict(features)[0])

# محدود کردن پیش‌بینی
pred_percent = max(min(pred_percent, 5), -5)

# قیمت پیش‌بینی شده
prediction = current_price * (1 + pred_percent / 100)

# درصد واقعی تغییر
real_percent = (
    (prediction - current_price)
    / current_price
) * 100

# تشخیص روند
trend = "UP 🟢"

if latest['ema_20'] < latest['sma_20']:
    trend = "DOWN 🔴"

# حمایت و مقاومت
support = df['low'].tail(50).min()
resistance = df['high'].tail(50).max()

# بررسی حجم معاملات
avg_volume = df['volume'].tail(20).mean()

high_volume = latest['volume'] > avg_volume

# ساخت سیگنال حرفه‌ای
change = pred_percent

if change > 0.5 and high_volume:
    signal = "STRONG BUY 🟢🔥"

elif change > 0.1:
    signal = "BUY 🟢"

elif change < -0.5 and high_volume:
    signal = "STRONG SELL 🔴🔥"

elif change < -0.1:
    signal = "SELL 🔴"

else:
    signal = "HOLD 🟡"

# محاسبه حد ضرر و حد سود بر اساس ATR
atr = latest['atr']
if signal in ["BUY 🟢", "STRONG BUY 🟢🔥"]:
    stop_loss = current_price - 1.5 * atr
    take_profit = current_price + 2.5 * atr
    risk_reward = (take_profit - current_price) / (current_price - stop_loss)
elif signal in ["SELL 🔴", "STRONG SELL 🔴🔥"]:
    stop_loss = current_price + 1.5 * atr
    take_profit = current_price - 2.5 * atr
    risk_reward = (current_price - take_profit) / (stop_loss - current_price)
else:
    stop_loss = take_profit = risk_reward = None


# =========================
# AI SIGNAL STRENGTH
# =========================
# ========  امتیازدهی جدید  ========

trend_score = 40 if trend == "UP 🟢" else 25

rsi_val = latest['rsi']
if 40 <= rsi_val <= 60:
    rsi_score = 20
elif 30 <= rsi_val <= 70:
    rsi_score = 15
else:
    rsi_score = 10

macd_diff_ratio = abs(latest['macd'] - latest['macd_signal']) / (latest['atr'] + 0.01)
if macd_diff_ratio > 0.5:
    macd_score = 25
elif macd_diff_ratio > 0.2:
    macd_score = 18
else:
    macd_score = 12

change_abs = abs(real_percent)
if change_abs > 2:
    pred_score = 30
elif change_abs > 1:
    pred_score = 24
elif change_abs > 0.5:
    pred_score = 18
elif change_abs > 0.2:
    pred_score = 12
else:
    pred_score = 8

ai_confidence = trend_score + rsi_score + macd_score + pred_score
ai_confidence = min(ai_confidence, 95)   # حداکثر 95
ai_confidence = round(ai_confidence, 1)


# اگر df ایندکس تاریخ دارد (که yfinance می‌دهد)

last_time = df.index[-1].strftime('%Y-%m-%d %H:%M:%S')

# چاپ خروجی
print("\n===== PRO TRADING AI =====")

print(f"Coin: {symbol}")

print(f"Current Price: {current_price:.4f}")

print(f"Data Time: {last_time}")

dep = get_btc_dependency(symbol)
print(f":link: BTC Dependency: {dep}%")

print(f"\n📊 Trend: {trend}")

print(f"🟢 Support: {support:.4f}")

print(f"🔴 Resistance: {resistance:.4f}")

print(f"\n🎯 Predicted Price ({selected_timeframe}): {prediction:.4f}")

print(f"📈 Predicted Change: {real_percent:.2f}%")

print(f"\n📦 Volume Status: {'HIGH 📈' if high_volume else 'NORMAL'}")

print(f"\n⚡ Signal: {signal}")

# پیشنهاد حجم معامله (ریسک ۲٪ سرمایه)

risk_per_trade = 0.02

if stop_loss:
    risk_amount = capital * risk_per_trade
    position_size = risk_amount / abs(current_price - stop_loss)
    print(f"\n💰 Risk Management:")
    print(f"   Stop Loss: {stop_loss:.4f}")
    print(f"   Take Profit: {take_profit:.4f}")
    print(f"   Risk/Reward: {risk_reward:.2f}")
    print(f"   Position Size: {position_size:.2f} units (${position_size * current_price:.0f})")
    #درصد فاصله تا . SL/TP
    sl_pct = (abs(current_price - stop_loss) / current_price) * 100
    tp_pct = (abs(take_profit - current_price) / current_price) * 100
    print(f"    Stop Loss Dist: {sl_pct:.2f}%")
    print(f"    Take Profit Dist: {tp_pct:.2f}%")

if stop_loss:
    sl_pct = (abs(current_price - stop_loss) / current_price) * 100
    tp_pct = (abs(take_profit - current_price) / current_price) * 100
    print(f"   Stop Loss Distance: {sl_pct:.4f}%")
    print(f"   Take Profit Distance: {tp_pct:.4f}%")

print(f"\n📈 Buy Zone: {support:.4f} - {support*1.002:.4f}")

print(f"📉 Sell Zone: {resistance*0.998:.4f} - {resistance:.4f}")
# ساخت نوار پیشرفت
bar_length = int(ai_confidence / 2)  # چون حداکثر ۹۵ است، نوار ۵۰ کاراکتری
bar = '█' * bar_length + '░' * (50 - bar_length)
print(f"\n🔥 AI Signal Strength: [{bar}] {ai_confidence}%")

print("\n" + "="*50)
print(f"{BOLD}📌 FINAL RECOMMENDATION: {signal}{RESET}")
print("="*50)


