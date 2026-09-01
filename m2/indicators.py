"""
Vectorized technical indicator calculations built on pandas/numpy.
No external TA library dependency — keeps the module portable and easy to
reason about/debug live during the hackathon demo.

All functions take a pandas Series/DataFrame with a DatetimeIndex and
columns: Open, High, Low, Close, Volume (standard OHLCV) and return either
a Series (same index) or a tuple of Series.
"""

import numpy as np
import pandas as pd


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def compute_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Returns (macd_line, signal_line, histogram)."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def compute_ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def compute_volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
    return volume.rolling(window=period, min_periods=1).mean()


def compute_vwap(df: pd.DataFrame) -> pd.Series:
    """Cumulative (session-to-date-style) VWAP over the whole fetched window."""
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    cum_vp = (typical_price * df["Volume"]).cumsum()
    cum_vol = df["Volume"].cumsum().replace(0, np.nan)
    vwap = cum_vp / cum_vol
    return vwap.fillna(df["Close"])


def compute_bollinger(close: pd.Series, period: int = 20, num_std: float = 2.0):
    """Returns (upper, middle, lower, band_width_pct_of_middle)."""
    middle = close.rolling(window=period, min_periods=1).mean()
    std = close.rolling(window=period, min_periods=1).std().fillna(0)
    upper = middle + num_std * std
    lower = middle - num_std * std
    width = (upper - lower) / middle.replace(0, np.nan)
    return upper, middle, lower, width.fillna(0)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    return atr.fillna(tr)


def enrich_with_indicators(df: pd.DataFrame, cfg) -> pd.DataFrame:
    """Attach every indicator the signal engine needs as extra columns."""
    out = df.copy()
    out["rsi"] = compute_rsi(out["Close"], cfg.RSI_PERIOD)
    macd_line, macd_signal, macd_hist = compute_macd(
        out["Close"], cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL
    )
    out["macd"] = macd_line
    out["macd_signal"] = macd_signal
    out["macd_hist"] = macd_hist
    out["ema_fast"] = compute_ema(out["Close"], cfg.EMA_FAST)
    out["ema_slow"] = compute_ema(out["Close"], cfg.EMA_SLOW)
    out["volume_sma"] = compute_volume_sma(out["Volume"], cfg.VOLUME_SMA_PERIOD)
    out["vwap"] = compute_vwap(out)
    bb_upper, bb_mid, bb_lower, bb_width = compute_bollinger(
        out["Close"], cfg.BOLLINGER_PERIOD, cfg.BOLLINGER_STD
    )
    out["bb_upper"] = bb_upper
    out["bb_mid"] = bb_mid
    out["bb_lower"] = bb_lower
    out["bb_width"] = bb_width
    out["bb_width_pctile"] = out["bb_width"].rolling(60, min_periods=5).rank(pct=True)
    out["atr"] = compute_atr(out, cfg.ATR_PERIOD)
    return out
