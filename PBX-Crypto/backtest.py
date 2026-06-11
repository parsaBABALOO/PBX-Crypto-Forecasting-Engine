# backtest_corrected.py - High Win Rate with Many Trades 

import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from utils.binance_data import get_binance_data
from indicators.indicators import add_indicators

# ============================================================================
# CONFIGURATION (SOFTENED FOR MORE TRADES)
# ============================================================================
SYMBOLS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "TRX-USD", "DOT-USD", "LTC-USD"
]

TIMEFRAMES = {
    "1H": {"interval": "5m", "shift": 12, "model": "models/xgb_1h.pkl"},
    "4H": {"interval": "15m", "shift": 16, "model": "models/xgb_4h.pkl"},
    "12H": {"interval": "30m", "shift": 24, "model": "models/xgb_12h.pkl"},
    "24H": {"interval": "1h", "shift": 24, "model": "models/xgb_24h.pkl"}
}

BACKTEST_DAYS = 30
BASE_THRESHOLD = 0.07           # Lower threshold = more trades
FEE = 0.001
MIN_ATR_PCT = 0.0015            # 0.15% min volatility
USE_ADX_FILTER = False          # Disabled to increase trades (was True)
ADX_THRESHOLD = 18
USE_VOLUME_FILTER = False
USE_CONFIDENCE_FILTER = False   # Disabled for more trades
CONFIDENCE_PERCENTILE = 60
USE_EARLY_TAKE_PROFIT = True
EARLY_TP_PCT = 1.5
EARLY_TP_ACTIVE_BARS = 8
USE_TIME_FILTER = False         # Disabled

# Dynamic range
MIN_THRESHOLD = 0.03
MAX_THRESHOLD = 0.25

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def load_model(path):
    return joblib.load(path)

def get_features(df, symbol_id):
    latest = df.iloc[-1]
    return [[
        symbol_id,
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

def add_advanced_indicators(df):
    # ADX (optional)
    high = df['high']
    low = df['low']
    close = df['close']
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = abs(minus_dm)
    tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    atr_ = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr_)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr_)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(14).mean()
    
    df['sma_200'] = df['close'].rolling(200).mean()
    df['regime'] = np.where(df['close'] > df['sma_200'], 1, -1)
    return df

def compute_dynamic_threshold(atr_pct, recent_preds, percentile=60):
    """Safe version - always returns a float"""
    vol_factor = max(0.6, min(1.4, atr_pct / 0.008))
    base = BASE_THRESHOLD * vol_factor
    if USE_CONFIDENCE_FILTER and len(recent_preds) > 20:
        try:
            high_conf = np.percentile(np.abs(recent_preds), percentile)
            dynamic = max(base, high_conf * 0.7)
        except:
            dynamic = base
    else:
        dynamic = base
    return np.clip(dynamic, MIN_THRESHOLD, MAX_THRESHOLD)

def get_secondary_signal(df_slice):
    """RSI + MACD based signal"""
    latest = df_slice.iloc[-1]
    rsi = latest['rsi']
    macd = latest['macd']
    macd_signal = latest['macd_signal']
    if rsi < 35 or (macd > macd_signal and macd > 0):
        return 1
    elif rsi > 65 or (macd < macd_signal and macd < 0):
        return -1
    else:
        return 0

def simulate_exit_with_early_tp(df, entry_idx, shift, entry_price, signal):
    exit_idx = entry_idx + shift
    if exit_idx >= len(df):
        return None, None, None
    if USE_EARLY_TAKE_PROFIT:
        max_check = min(entry_idx + EARLY_TP_ACTIVE_BARS, exit_idx)
        for j in range(entry_idx + 1, max_check + 1):
            high = df.iloc[j]['high']
            low = df.iloc[j]['low']
            if signal == 1 and high >= entry_price * (1 + EARLY_TP_PCT/100):
                return entry_price * (1 + EARLY_TP_PCT/100), j, df.index[j]
            if signal == -1 and low <= entry_price * (1 - EARLY_TP_PCT/100):
                return entry_price * (1 - EARLY_TP_PCT/100), j, df.index[j]
    return df.iloc[exit_idx]['close'], exit_idx, df.index[exit_idx]

# ============================================================================
# MAIN BACKTEST FUNCTION (FIXED)
# ============================================================================
def backtest_symbol(symbol, tf_name, tf_config):
    print(f"\n--- Backtesting {symbol} on {tf_name} ---")
    try:
        interval = tf_config["interval"]
        shift = tf_config["shift"]
        model = load_model(tf_config["model"])

        limit = shift + 500
        period = f"{BACKTEST_DAYS + 10}d"
        df = get_binance_data(symbol, interval, limit, period)
        df = add_indicators(df)
        df = add_advanced_indicators(df)
        df.dropna(inplace=True)

        if len(df) < shift + 100:
            print(f"   ⚠️ Insufficient data ({len(df)} candles)")
            return None

        symbols_all = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
                       "ADA-USD", "DOGE-USD", "TRX-USD", "DOT-USD", "LTC-USD"]
        symbol_map = {sym: idx+1 for idx, sym in enumerate(symbols_all)}
        symbol_id = symbol_map.get(symbol, 1)

        trades = []
        recent_preds = []
        start_idx = 300
        end_idx = len(df) - shift

        for i in range(start_idx, end_idx):
            df_slice = df.iloc[:i+1].copy()
            if len(df_slice) < 100:
                continue

            latest = df_slice.iloc[-1]
            current_price = latest['close']
            atr_pct = latest['atr'] / current_price

            # Basic filters
            if atr_pct < MIN_ATR_PCT:
                continue
            if USE_ADX_FILTER and latest['adx'] < ADX_THRESHOLD:
                continue

            # Model prediction
            features = get_features(df_slice, symbol_id)
            pred_pct = float(model.predict(features)[0])
            pred_pct = max(min(pred_pct, 5), -5)

            recent_preds.append(abs(pred_pct))
            if len(recent_preds) > 50:
                recent_preds.pop(0)

            # SAFE: assign default value first
            dynamic_thresh = BASE_THRESHOLD  # fallback
            try:
                dynamic_thresh = compute_dynamic_threshold(atr_pct, recent_preds, CONFIDENCE_PERCENTILE)
            except Exception as e:
                pass  # keep default

            # Primary signal
            if pred_pct > dynamic_thresh:
                signal = 1
            elif pred_pct < -dynamic_thresh:
                signal = -1
            else:
                signal = 0

            # Secondary signal if model is uncertain (abs(pred) between 50% and 100% of threshold)
            if signal == 0 and abs(pred_pct) > dynamic_thresh * 0.5:
                sec = get_secondary_signal(df_slice)
                if sec != 0:
                    signal = sec

            if signal == 0:
                continue

            # Regime filter (soft)
            regime = latest['regime']
            if regime == 1 and signal == -1 and pred_pct < -0.15:
                continue
            if regime == -1 and signal == 1 and pred_pct > 0.15:
                continue

            # Entry
            entry_price = current_price
            entry_time = df.index[i]

            # Exit
            exit_price, exit_idx, exit_time = simulate_exit_with_early_tp(df, i, shift, entry_price, signal)
            if exit_price is None:
                continue
            # PnL
            if signal == 1:
                pnl_pct = ((exit_price * (1 - FEE)) - (entry_price * (1 + FEE))) / (entry_price * (1 + FEE)) * 100
            else:
                pnl_pct = ((entry_price * (1 - FEE)) - (exit_price * (1 + FEE))) / (entry_price * (1 + FEE)) * 100

            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'signal': signal,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pnl_pct': pnl_pct,
                'pred_pct': pred_pct
            })

        if len(trades) == 0:
            print(f"   No trades")
            return None

        df_trades = pd.DataFrame(trades)
        win_rate = (df_trades['pnl_pct'] > 0).mean() * 100
        total_return = df_trades['pnl_pct'].sum()
        avg_pnl = df_trades['pnl_pct'].mean()
        cum_ret = (1 + df_trades['pnl_pct'] / 100).cumprod()
        peak = cum_ret.expanding().max()
        max_dd = ((cum_ret - peak) / peak * 100).min() if len(cum_ret) > 0 else 0

        long_cnt = len(df_trades[df_trades['signal'] == 1])
        short_cnt = len(df_trades[df_trades['signal'] == -1])

        print(f"   📊 Trades: {len(trades)} (L:{long_cnt} S:{short_cnt})")
        print(f"   ✅ Win rate: {win_rate:.1f}%")
        print(f"   💰 Total return: {total_return:.2f}%")
        print(f"   ⚡ Avg profit/trade: {avg_pnl:.2f}%")
        print(f"   📉 Max DD: {max_dd:.2f}%")

        return {
            'symbol': symbol,
            'tf': tf_name,
            'trades': len(trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_pnl': avg_pnl,
            'max_dd': max_dd
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 80)
    print("FIXED BACKTEST - HIGH WIN RATE WITH MANY TRADES")
    print("=" * 80)
    print(f"Period: {BACKTEST_DAYS} days | Base threshold: {BASE_THRESHOLD}%")
    print(f"Min ATR: {MIN_ATR_PCT*100}% | Early TP: {EARLY_TP_PCT}%")
    print(f"ADX filter: OFF | Confidence filter: OFF | Time filter: OFF\n")

    results = []
    for tf_name, cfg in TIMEFRAMES.items():
        print(f"\n{'='*60}")
        print(f"🔄 TIMEFRAME: {tf_name}")
        print(f"{'='*60}")
        for sym in SYMBOLS:
            res = backtest_symbol(sym, tf_name, cfg)
            if res:
                results.append(res)

    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    if results:
        df_res = pd.DataFrame(results)
        avg_win = df_res['win_rate'].mean()
        avg_ret = df_res['total_return'].mean()
        avg_trades = df_res['trades'].mean()
        total_trades = df_res['trades'].sum()
        print(f"📌 OVERALL AVERAGE WIN RATE: {avg_win:.1f}%")
        print(f"📌 OVERALL AVERAGE TOTAL RETURN: {avg_ret:.2f}%")
        print(f"📌 AVERAGE TRADES PER SYMBOL: {avg_trades:.1f}")
        print(f"📌 TOTAL TRADES: {total_trades}")

        tf_summary = df_res.groupby('tf').agg({'win_rate': 'mean', 'trades': 'sum', 'total_return': 'mean'}).round(1)
        print("\n🏆 TIMEFRAME PERFORMANCE:")
        print(tf_summary)

        high_win = df_res[(df_res['win_rate'] >= 60) & (df_res['trades'] >= 5)]
        if len(high_win) > 0:
            print("\n✅ SYMBOLS WITH WIN RATE >=60% and >=5 trades:")
            for _, row in high_win.iterrows():
                print(f"   {row['symbol']} ({row['tf']}): {row['win_rate']:.1f}% win, {row['total_return']:.2f}% ret, {row['trades']} trades")
        else:
            print("\n⚠️ No symbol with 60% win rate and 5+ trades. Try lowering BASE_THRESHOLD to 0.05")
    else:
        print("No results. Check model paths.")


if __name__ == "__main__":
    main()