# 🔮 PBX-Crypto Forecasting Engine

> AI-based cryptocurrency forecasting system with XGBoost, technical indicators, and real‑time dashboard

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7+-orange.svg)](https://xgboost.ai/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/8504/badge)](https://www.bestpractices.dev/projects/8504)

---

## 🚀 Overview

PBX-Crypto Forecasting Engine is a professional trading assistant that combines XGBoost regression with over 15 technical indicators to predict price movements for 50+ cryptocurrencies across 4 timeframes (1H, 4H, 12H, 24H). It provides actionable buy/sell signals, dynamic risk management, backtesting, and an interactive dashboard.

✅ Live prediction (CLI & Telegram-ready)  
✅ Interactive dashboard (Streamlit)  
✅ Backtest with 0.1% fee simulation  
✅ Risk management (ATR-based SL/TP)  
✅ BTC dependency & AI confidence score

---

## 📊 Performance Metrics (30‑day backtest)

| Metric               | Value      |
|----------------------|------------|
| Win Rate         | 63.2%      |
| Total Return     | +27.83%    |
| Max Drawdown     | ~10%       |
| Avg Profit/Trade | +0.8%      |
| Trades           | 44         |

> *All results include 0.1% trading fees.*

---

## 🧠 System Architecture

Tech stack:  
Python 3.11 • XGBoost • pandas • numpy • ta • scikit-learn • streamlit • plotly • yfinance

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/parsaBABALOO/PBX-Crypto-Forecasting-Engine.git
cd PBX-Crypto-Forecasting-Engine
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run CLI prediction
```bash
py -m prediction.predict
```
### 4. Launch interactive dashboard
```bash
streamlit run dashboard.py
```
🧪 Example Output (CLI)
```bash
===== PRO TRADING AI =====
Coin: ETH-USD
Current Price: 2133.89
Data Time: 2026-06-01 14:20:00
📊 Trend: DOWN 🔴
🎯 Predicted Price (1H): 2115.61
📈 Predicted Change: -0.86%
⚡ Signal: SELL 🔴
💰 Risk Management:
   Stop Loss: 2141.87
   Take Profit: 2120.60
   Risk/Reward: 1.67
🔥 AI Confidence: [████████████████████░░░░░░░░] 65%
==================================================
📌 FINAL RECOMMENDATION: SELL 🔴
```

🧪 Backtest
```bash
py backtest.py
```
Output includes:

· Win rate per symbol & timeframe
· Total return with fees
· Max drawdown
· Best performing timeframe

---

🗺️ Roadmap

· Telegram bot integration (auto‑signal delivery)
· Real‑time data from Iranian exchanges (Nobitex, Wallex)
· Sentiment analysis (FinBERT) on crypto news
· Out‑of‑sample backtest (walk‑forward validation)
· Docker deployment & cloud hosting guide

---

🤝 Contributing

Issues and pull requests are welcome. For major changes, please open an issue first.

---
📬 Contact

Developer: PARSA BABALOO
Email: parsababalo1403@gmail.com

Note: Any other contact information (including Telegram channels or usernames) associated with this project is not official and should be considered invalid or unrelated to the developer.

Telegram Channel: @PBX_CRYPTO

---

## ⚠️ Proprietary Notice & Intellectual Property

**Copyright (c) 2026. All rights reserved.**

This repository contains proprietary source code, architecture designs, and visual assets. By accessing this repository, you agree to the following strict terms and conditions:

* **Educational Use Only:** Permission is granted solely for personal learning, educational simulation, and code-review purposes.
* **No Replication or Modification:** You may not copy, modify, alter, or create derivative works (such as apps, themes, or websites) based on this source code.
* **No Redistribution:** You are strictly prohibited from redistributing, publishing, or sub-licensing this code or any part of it anywhere on the web, including other personal or public repositories.
* **No Commercialization:** This project may not be used, directly or indirectly, for any commercial ventures, business operations, or portfolio claiming.
* **No Re-branding:** Claiming this specific architecture, logic layout, or styling as your own authorship is legally actionable.

*Failure to comply with these terms constitutes a direct breach of copyright law and intellectual property rights.*
---
⭐ If this project helped you, please give it a star! ⭐
