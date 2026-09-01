"""
MarketDataFeed — fetches OHLCV data from Yahoo Finance (yfinance) with:
  * a short-lived in-memory cache (avoids hammering the upstream feed / rate limits)
  * a deterministic synthetic generator used whenever the live feed is
    unavailable, rate-limited, or an operator has forced degraded mode
  * a manual override (`toggle_degraded`) exposed via the API for the demo

Every call returns (dataframe, feed_status) where feed_status is one of
"LIVE_FEED" or "DEGRADED_SYNTHETIC" so callers can propagate it into the
JSON contract without knowing anything about *why* it happened.
"""

import time
import hashlib
import logging

import numpy as np
import pandas as pd

import config as cfg

logger = logging.getLogger("m2.data_feed")

LIVE_FEED = "LIVE_FEED"
DEGRADED_SYNTHETIC = "DEGRADED_SYNTHETIC"


def _seed_for(symbol: str) -> int:
    """Deterministic seed so the same symbol always gets the same synthetic
    series shape within a process run (stable demo behaviour)."""
    digest = hashlib.sha256(symbol.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _base_price_for(symbol: str) -> float:
    """Deterministic-but-plausible starting price per symbol so the demo
    doesn't show every stock trading at the same level."""
    seed = _seed_for(symbol + "_price")
    rng = np.random.RandomState(seed % (2**32 - 1))
    return float(rng.uniform(150, 3500))


class MarketDataFeed:
    def __init__(self):
        self._cache = {}          # symbol -> (dataframe, feed_status, fetched_at)
        self._force_degraded = False
        self._last_status_per_symbol = {}

    # ------------------------------------------------------------------ #
    # Public controls
    # ------------------------------------------------------------------ #
    def toggle_degraded(self, status: bool) -> None:
        self._force_degraded = bool(status)
        if self._force_degraded:
            self._cache.clear()  # force a re-fetch through the synthetic path

    @property
    def is_forced_degraded(self) -> bool:
        return self._force_degraded

    def overall_feed_status(self) -> str:
        """Best-effort system-wide status for /health — LIVE_FEED only if
        the last attempt for every symbol we've touched was live."""
        if self._force_degraded:
            return DEGRADED_SYNTHETIC
        if not self._last_status_per_symbol:
            return "UNKNOWN"
        statuses = set(self._last_status_per_symbol.values())
        return LIVE_FEED if statuses == {LIVE_FEED} else DEGRADED_SYNTHETIC

    # ------------------------------------------------------------------ #
    # Core fetch
    # ------------------------------------------------------------------ #
    def get_ohlcv(self, symbol: str, force_refresh: bool = False):
        """Returns (df, feed_status) for `symbol`. df has columns:
        Open, High, Low, Close, Volume with a DatetimeIndex, newest last."""
        cached = self._cache.get(symbol)
        if cached and not force_refresh:
            df, status, fetched_at = cached
            if time.time() - fetched_at < cfg.CACHE_TTL_SECONDS:
                return df, status

        if self._force_degraded:
            df = self._generate_synthetic(symbol)
            status = DEGRADED_SYNTHETIC
        else:
            df, status = self._try_live_fetch(symbol)

        self._cache[symbol] = (df, status, time.time())
        self._last_status_per_symbol[symbol] = status
        return df, status

    def _try_live_fetch(self, symbol: str):
        try:
            import yfinance as yf  # imported lazily so the app still boots offline

            ticker = yf.Ticker(symbol)
            df = ticker.history(
                period=cfg.HISTORY_PERIOD,
                interval=cfg.HISTORY_INTERVAL,
                timeout=cfg.FEED_TIMEOUT,
                auto_adjust=True,
            )
            if df is None or df.empty or len(df) < 30:
                raise ValueError(f"empty or insufficient live data for {symbol}")

            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df = df.dropna(subset=["Close"])
            if df.empty:
                raise ValueError(f"live data for {symbol} was entirely NaN")
            return df, LIVE_FEED

        except Exception as exc:  # noqa: BLE001 - any failure means "go synthetic"
            logger.warning("Live feed failed for %s (%s) — falling back to synthetic", symbol, exc)
            return self._generate_synthetic(symbol), DEGRADED_SYNTHETIC

    # ------------------------------------------------------------------ #
    # Synthetic fallback
    # ------------------------------------------------------------------ #
    def _generate_synthetic(self, symbol: str, days: int = 260) -> pd.DataFrame:
        """Deterministic geometric-random-walk OHLCV generator. Keeps the
        rest of the pipeline (indicators, signal engine) fully exercised
        even with zero network access."""
        seed = _seed_for(symbol) % (2**32 - 1)
        rng = np.random.RandomState(seed)

        base_price = _base_price_for(symbol)
        dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)

        # Daily log-returns: small drift + noise, occasional volatility clusters
        drift = rng.uniform(-0.0003, 0.0006)
        vol = rng.uniform(0.012, 0.022)
        shocks = rng.normal(loc=drift, scale=vol, size=days)
        # inject a couple of volatility/volume "events" for a livelier demo
        event_idx = rng.choice(days, size=max(2, days // 60), replace=False)
        shocks[event_idx] *= rng.uniform(2.5, 4.0)

        log_prices = np.cumsum(shocks) + np.log(base_price)
        close = np.exp(log_prices)

        daily_range = close * rng.uniform(0.006, 0.018, size=days)
        high = close + daily_range * rng.uniform(0.3, 0.7, size=days)
        low = close - daily_range * rng.uniform(0.3, 0.7, size=days)
        open_ = low + (high - low) * rng.uniform(0.2, 0.8, size=days)

        base_volume = rng.uniform(3e5, 6e6)
        volume = base_volume * rng.lognormal(mean=0, sigma=0.35, size=days)
        volume[event_idx] *= rng.uniform(2.0, 5.0)

        df = pd.DataFrame(
            {
                "Open": open_,
                "High": np.maximum.reduce([high, open_, close]),
                "Low": np.minimum.reduce([low, open_, close]),
                "Close": close,
                "Volume": volume.astype(np.int64),
            },
            index=dates,
        )
        return df
