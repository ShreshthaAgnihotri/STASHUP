"""
Configuration constants for Module M2 — Market Data & Signal Engine.
"""

# Default watchlist shown on the frontend dashboard
DEFAULT_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "^NSEI"]

# How long a fetched OHLCV frame is considered fresh (seconds)
CACHE_TTL_SECONDS = 60

# History window pulled from yfinance / synthetic generator.
# 1y of daily bars is enough for EMA50, MACD(26,9) warm-up and a genuine 52w hi/lo.
HISTORY_PERIOD = "1y"
HISTORY_INTERVAL = "1d"

# Indicator windows
RSI_PERIOD = 14
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
EMA_FAST, EMA_SLOW = 20, 50
VOLUME_SMA_PERIOD = 20
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2
ATR_PERIOD = 14

# Aggregate weighting across the three signal dimensions
DIMENSION_WEIGHTS = {"momentum": 0.40, "volume": 0.35, "volatility": 0.25}

# Network timeout (seconds) for each yfinance call before falling back to synthetic
FEED_TIMEOUT = 6
