# utils/dependency.py

BTC_DEP = {
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

def get_btc_dependency(symbol):
    return BTC_DEP.get(symbol, 60)
