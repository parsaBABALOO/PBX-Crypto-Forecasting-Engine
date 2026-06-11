# dashboard.py (نسخه نهایی با نمودار قابل تنظیم)
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from utils.binance_data import get_binance_data
from indicators.indicators import add_indicators

st.set_page_config(
    page_title="PBX Crypto AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<h1 style='text-align: center; color: #00FFAA;'>
🚀 PBX CRYPTO AI TERMINAL
</h1>

<p style='text-align: center; color: gray; font-size:18px;'>
Advanced AI-Powered Crypto Prediction System
</p>

<hr>
""", unsafe_allow_html=True)


# ========== تنظیمات ==========
SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "TRX-USD", "DOT-USD", "LTC-USD",
    "BCH-USD", "LINK-USD", "XLM-USD", "ATOM-USD", "ETC-USD",
    "XMR-USD", "HBAR-USD", "ICP-USD", "FIL-USD", "RUNE-USD",
    "OP-USD", "AVAX-USD", "SEI-USD", "NEAR-USD", "AAVE-USD",
    "MKR-USD", "INJ-USD", "RENDER-USD", "FET-USD", "ALGO-USD",
    "EGLD-USD", "THETA-USD", "SAND-USD", "MANA-USD", "AXS-USD",
    "FLOW-USD", "CHZ-USD", "CRV-USD", "LDO-USD", "SNX-USD",
    "DYDX-USD", "1INCH-USD", "BAT-USD", "ZRX-USD", "ENS-USD",
    "CAKE-USD", "APE-USD", "SHIB-USD", "FLOKI-USD", "BONK-USD",
    "WIF-USD", "PYTH-USD", "TIA-USD", "STRK-USD","AR-USD",
    "KAS-USD"
]

TIMEFRAMES = {
    "1H": {"model": "models/xgb_1h.pkl", "interval": "5m", "shift": 12, "name": "1 Hour"},
    "4H": {"model": "models/xgb_4h.pkl", "interval": "15m", "shift": 16, "name": "4 Hours"},
    "12H": {"model": "models/xgb_12h.pkl", "interval": "30m", "shift": 24, "name": "12 Hours"},
    "24H": {"model": "models/xgb_24h.pkl", "interval": "1h", "shift": 24, "name": "24 Hours"}
}

# Static BTC Dependency (manual)
BTC_DEP_MANUAL = {
    "BTC-USD": 100, "ETH-USD": 85, "BNB-USD": 80, "SOL-USD": 75,
    "XRP-USD": 70, "ADA-USD": 65, "DOGE-USD": 60, "TRX-USD": 55,
    "DOT-USD": 65, "LTC-USD": 70, "BCH-USD": 70, "LINK-USD": 68,
    "XLM-USD": 65, "ATOM-USD": 62, "ETC-USD": 68, "XMR-USD": 60,
    "HBAR-USD": 50, "ICP-USD": 55, "FIL-USD": 58, "ARB-USD": 70,
    "OP-USD": 68, "AVAX-USD": 72, "SEI-USD": 65, "NEAR-USD": 68,
    "AAVE-USD": 65, "MKR-USD": 60, "INJ-USD": 65, "RENDER-USD": 60,
    "FET-USD": 65, "ALGO-USD": 60, "EGLD-USD": 60, "THETA-USD": 65,
    "SAND-USD": 65, "MANA-USD": 65, "AXS-USD": 65, "FLOW-USD": 60,
    "CHZ-USD": 60, "CRV-USD": 60, "LDO-USD": 60, "SNX-USD": 60,
    "DYDX-USD": 65, "1INCH-USD": 60, "BAT-USD": 55, "ZRX-USD": 55,
    "ENS-USD": 60, "CAKE-USD": 55, "APE-USD": 65, "SHIB-USD": 60,
    "FLOKI-USD": 60, "BONK-USD": 60, "WIF-USD": 60, "JUP-USD": 65,
    "PYTH-USD": 65, "TIA-USD": 60, "STRK-USD": 60, "AR-USD": 55,
    "KAS-USD": 60, "RUNE-USD": 65,
}
def get_static_dep(symbol):
    return BTC_DEP_MANUAL.get(symbol, 60)

@st.cache_resource
def load_model(path):
    return joblib.load(path)

def get_features(df, symbol_id):
    latest = df.iloc[-1]
    return [[
        symbol_id,
        latest['close'], latest['volume'], latest['rsi'],
        latest['macd'], latest['macd_signal'], latest['ema_20'],
        latest['sma_20'], latest['bb_high'], latest['bb_low'],
        latest['high'], latest['low'], latest['atr'],
        latest['stoch_rsi'], latest['momentum']
    ]]

@st.cache_data(ttl=300)
def get_prediction(symbol, tf_key):
    config = TIMEFRAMES[tf_key]
    interval = config["interval"]
    model = load_model(config["model"])
    df = get_binance_data(symbol=symbol, interval=interval, limit=300, period="7d")
    if df.empty:
        return None, None, None, None
    df = add_indicators(df)
    df.dropna(inplace=True)
    if len(df) < 50:
        return None, None, None, None
    symbol_id = SYMBOLS.index(symbol)+1 if symbol in SYMBOLS else 1
    features = get_features(df, symbol_id)
    pred_percent = float(model.predict(features)[0])
    pred_percent = max(min(pred_percent, 5), -5)
    current_price = df['close'].iloc[-1]
    pred_price = current_price * (1 + pred_percent/100)
    # ===== Signal =====
    if pred_percent > 0.25:
        signal = "🟢 BUY"
    elif pred_percent < -0.25:
        signal = "🔴 SELL"
    else:
        signal = "🟡 HOLD"


    # ===== AI Confidence =====
    latest = df.iloc[-1]
    confidence = 50

    # RSI
    if latest['rsi'] > 60 or latest['rsi'] < 40:
        confidence += 10

    # MACD
    if abs(latest['macd'] - latest['macd_signal']) > 0.02:
        confidence += 10

    # Volume
    avg_volume = df['volume'].tail(20).mean()
    if latest['volume'] > avg_volume * 1.5:
        confidence += 10

    # ATR
    if latest['atr'] > df['atr'].tail(20).mean():
        confidence += 5

    # Prediction strength
    if abs(pred_percent) > 1:
        confidence += 10
    if abs(pred_percent) > 2:
        confidence += 5
        
    confidence = min(confidence, 95)

    dep = get_static_dep(symbol)
    return current_price, pred_price, pred_percent, signal, dep, confidence


# تغییر در تابع رسم نمودار: اضافه شدن پارامترهای کنترلی
@st.cache_data(ttl=300)
def plot_price_signals(symbol, tf_key, days=30,
                       show_ema=False,
                       show_sma=False,
                       show_bb=False,
                       show_signals=False):
    config = TIMEFRAMES[tf_key]
    interval = config["interval"]
    model = load_model(config["model"])
    df = get_binance_data(symbol=symbol, interval=interval, limit=500, period=f"{days+5}d")
    if df.empty:
        return None
    df = add_indicators(df)
    df.dropna(inplace=True)
    if len(df) < 50:
        return None
    symbol_id = SYMBOLS.index(symbol)+1 if symbol in SYMBOLS else 1
    signals = []
    pred_changes = []
    for i in range(50, len(df)):
        window = df.iloc[:i+1]
        latest = window.iloc[-1]
        features = [[
            symbol_id, latest['close'], latest['volume'], latest['rsi'],
            latest['macd'], latest['macd_signal'], latest['ema_20'],
            latest['sma_20'], latest['bb_high'], latest['bb_low'],
            latest['high'], latest['low'], latest['atr'],
            latest['stoch_rsi'], latest['momentum']
        ]]
        pred = float(model.predict(features)[0])
        pred = max(min(pred, 5), -5)
        pred_changes.append(pred)
        if pred > 0.1:
            signals.append(1)
        elif pred < -0.1:
            signals.append(-1)
        else:
            signals.append(0)
    df_signal = df.iloc[50:].copy()
    df_signal['signal'] = signals
    df_signal['pred_change'] = pred_changes
    
    # ساخت subplot (دو ردیف: قیمت و درصد تغییرات)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        row_heights=[0.7, 0.3],
                        subplot_titles=(f"{symbol} Price & Signals", "Predicted Change %"))
    
    # همیشه کندل‌ها را رسم کن
    fig.add_trace(go.Candlestick(x=df_signal.index,
                                 open=df_signal['open'],
                                 high=df_signal['high'],
                                 low=df_signal['low'],
                                 close=df_signal['close'],
                                 name='Candles'),
                  row=1, col=1)
    
    # EMA 20 (اختیاری)
    if show_ema:
        fig.add_trace(go.Scatter(x=df_signal.index, y=df_signal['ema_20'],
                                 mode='lines', name='EMA 20',
                                 line=dict(color='yellow')),
                      row=1, col=1)
    
    # SMA 20 (اختیاری)
    if show_sma:fig.add_trace(go.Scatter(x=df_signal.index, y=df_signal['sma_20'],
                                 mode='lines', name='SMA 20',
                                 line=dict(color='cyan')),
                      row=1, col=1)
    
    # باندهای بولینگر (اختیاری)
    if show_bb:
        fig.add_trace(go.Scatter(x=df_signal.index, y=df_signal['bb_high'],
                                 mode='lines', name='BB High',
                                 line=dict(color='gray', dash='dot')),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df_signal.index, y=df_signal['bb_low'],
                                 mode='lines', name='BB Low',
                                 line=dict(color='gray', dash='dot')),
                      row=1, col=1)
    
    # نقاط خرید/فروش هوش مصنوعی (اختیاری)
    if show_signals:
        buy = df_signal[df_signal['signal'] == 1]
        sell = df_signal[df_signal['signal'] == -1]
        fig.add_trace(go.Scatter(x=buy.index, y=buy['close'],
                                 mode='markers', name='Buy',
                                 marker=dict(color='green', size=10, symbol='triangle-up')),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=sell.index, y=sell['close'],
                                 mode='markers', name='Sell',
                                 marker=dict(color='red', size=10, symbol='triangle-down')),
                      row=1, col=1)
    
    # ردیف دوم: درصد تغییرات پیش‌بینی شده (همیشه نمایش داده شود)
    fig.add_trace(go.Scatter(x=df_signal.index, y=df_signal['pred_change'],
                             mode='lines', name='Predicted %',
                             line=dict(color='orange', dash='dot')),
                  row=2, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(height=600, title_text=f"{symbol} - {tf_key} Timeframe",
                      hovermode='x unified', template="plotly_dark",
                      xaxis_rangeslider_visible=False)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Change (%)", row=2, col=1)
    return fig


# ========== سایدبار ==========
st.sidebar.header("⚙️ Settings")
selected_tf = st.sidebar.selectbox("Forecast time frame", list(TIMEFRAMES.keys()), index=0)

# ========== جدول اصلی (بدون حلقه) ==========
rows = []
for sym in SYMBOLS:
    price, pred_price, change, signal, dep, confidence = get_prediction(sym, selected_tf)
    if price:
        rows.append({
            "Symbol": sym,
            "Current Price": f"{price:.7f}",
            "Predicted Price": f"{pred_price:.7f}",
            "Change %": f"{change:.2f}%",
            "Signal": signal,
            "AI Confidence": f"{confidence:.1f}%",
            "BTC Dep": f"{dep}%",
            "Time": datetime.now().strftime("%H:%M:%S")
        })
    else:
        rows.append({
            "Symbol": sym,
            "Current Price": "N/A",
            "Predicted Price": "N/A",
            "Change %": "N/A",
            "Signal": "⚠️ No data",
            "BTC Dep": "N/A",
            "Time": datetime.now().strftime("%H:%M:%S")
        })
df_display = pd.DataFrame(rows)
def color_signal(val):
    if "BUY" in str(val):
        return "color: lime"
    elif "SELL" in str(val):
        return "color: red"
    elif "HOLD" in str(val):
        return "color: orange"
    return ""

styled_df = df_display.style.map(color_signal, subset=["Signal"])
st.dataframe(styled_df, width='stretch', height=400)

# جمع‌بندی سیگنال‌ها
st.markdown("---")
st_autorefresh(interval=300000, key="refresh")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🟢 BUY", len(df_display[df_display["Signal"] == "🟢 BUY"]))
with col2:
    st.metric("🔴 SELL", len(df_display[df_display["Signal"] == "🔴 SELL"]))
with col3:
    st.metric("🟡 HOLD", len(df_display[df_display["Signal"] == "🟡 HOLD"]))
with col4:
    total = len(df_display)
    st.metric("📊 All", total)
    market_buy = len(df_display[df_display["Signal"] == "🟢 BUY"])

if market_buy > total * 0.6:
    sentiment = "BULLISH 🟢"
elif market_buy < total * 0.4:
    sentiment = "BEARISH 🔴"
else:
    sentiment = "SIDEWAYS 🟡"

st.metric("🌍 Market", sentiment)
    
st.markdown("---")

st.subheader("🔥 Top Buy Signals")
top_buys = df_display[df_display["Signal"] == "🟢 BUY"].head(5)
st.table(top_buys)

st.subheader("🩸 Top Sell Signals")
top_sells = df_display[df_display["Signal"] == "🔴 SELL"].head(5)
st.table(top_sells)

st.markdown("---")
st.subheader("📊 Deep analysis and show chart")

# بخش انتخاب سکه و گزینه‌های نمایش اندیکاتور
col1, col2 = st.columns(2)
with col1:
    selected_symbol = st.selectbox("Choose your coin", SYMBOLS)
with col2:
    # چک‌باکس‌های انتخاب اندیکاتور
    show_ema = st.checkbox("📈 EMA 20", value=False)
    show_sma = st.checkbox("📉 SMA 20", value=False)
    show_bb = st.checkbox("📊 Bollinger Bands", value=False)
    show_ai_signals = st.checkbox("🤖 AI Buy/Sell Signals", value=False)

show_chart = st.button("Show coin chart display and analysis")

chart_placeholder = st.empty()

if show_chart:
    with chart_placeholder.container():
        with st.spinner("📊 Loading chart..."):
            fig = plot_price_signals(
                selected_symbol,
                selected_tf,
                days=30,
                show_ema=show_ema,
                show_sma=show_sma,
                show_bb=show_bb,
                show_signals=show_ai_signals
            )
            if fig:
                st.plotly_chart(fig, width='stretch')
            else:
                st.error("No chart data found.")

                
#Developer: Parsa Babaloo