"""
SignalEngine — the 3-dimensional classification core of Module M2.

Dimension 1 (Momentum):   RSI(14), MACD(12,26,9), EMA20 vs EMA50
Dimension 2 (Volume):     volume vs 20d SMA, volume spike ratio, VWAP deviation
Dimension 3 (Volatility): Bollinger squeeze/breakout, ATR-based regime

Each dimension returns a dict matching the M1/M5 JSON contract:
    classification, score [-1, 1], confidence [0, 1], indicators, reasoning

`aggregate()` combines the three into a single actionable recommendation
with a synthesis summary that names which dimension drove the call —
this is the "explainable citation" the orchestrator/frontend surfaces.
"""

import numpy as np
import pandas as pd

import config as cfg


def _clip(x, lo=-1.0, hi=1.0):
    return float(np.clip(x, lo, hi))


def _safe(x, default=0.0):
    """Cast numpy scalar -> python float, guarding against NaN/inf so the
    response always serializes and never crashes the demo."""
    try:
        val = float(x)
    except (TypeError, ValueError):
        return default
    return default if (np.isnan(val) or np.isinf(val)) else val


def _round(x, nd=4):
    return round(_safe(x), nd)


class SignalEngine:
    # ------------------------------------------------------------------ #
    # Dimension 1 — Momentum
    # ------------------------------------------------------------------ #
    def classify_momentum(self, row: pd.Series) -> dict:
        rsi = _safe(row["rsi"], 50.0)
        macd_hist = _safe(row["macd_hist"])
        close = _safe(row["Close"], 1.0) or 1.0
        ema_fast, ema_slow = _safe(row["ema_fast"]), _safe(row["ema_slow"])

        rsi_score = _clip((rsi - 50.0) / 25.0)
        macd_score = _clip(macd_hist / (0.015 * close))
        ema_trend = "ABOVE_EMA50" if ema_fast > ema_slow else "BELOW_EMA50"
        ema_gap_pct = (ema_fast - ema_slow) / ema_slow * 100 if ema_slow else 0.0
        ema_score = _clip(ema_gap_pct / 3.0)

        score = _clip(0.4 * rsi_score + 0.35 * macd_score + 0.25 * ema_score)
        confidence = _clip(
            0.30
            + 0.35 * min(abs(rsi - 50.0) / 30.0, 1.0)
            + 0.35 * min(abs(macd_score), 1.0),
            0.0,
            1.0,
        )

        if score >= 0.55:
            classification = "STRONG_BULLISH"
        elif score >= 0.15:
            classification = "BULLISH"
        elif score <= -0.55:
            classification = "STRONG_BEARISH"
        elif score <= -0.15:
            classification = "BEARISH"
        else:
            classification = "NEUTRAL"

        overbought_note = ""
        if rsi >= 70:
            overbought_note = " Note: RSI is in overbought territory (>=70), raising pullback risk."
        elif rsi <= 30:
            overbought_note = " Note: RSI is in oversold territory (<=30), suggesting a potential bounce."

        macd_state = "crossed above" if macd_hist > 0 else "crossed below"
        reasoning = (
            f"RSI at {rsi:.1f} indicates "
            f"{'upward' if rsi >= 50 else 'downward'} momentum; "
            f"MACD line has {macd_state} its signal line (histogram {macd_hist:.2f}); "
            f"20-EMA is {'above' if ema_fast > ema_slow else 'below'} the 50-EMA "
            f"({ema_gap_pct:+.2f}% gap), confirming the {'ABOVE_EMA50' if ema_fast > ema_slow else 'BELOW_EMA50'} trend."
            f"{overbought_note}"
        )

        return {
            "classification": classification,
            "score": _round(score),
            "confidence": _round(confidence),
            "indicators": {
                "rsi": _round(rsi, 2),
                "macd_diff": _round(macd_hist, 2),
                "ema_trend": ema_trend,
            },
            "reasoning": reasoning,
        }

    # ------------------------------------------------------------------ #
    # Dimension 2 — Volume Anomaly
    # ------------------------------------------------------------------ #
    def classify_volume(self, row: pd.Series, prev_close: float) -> dict:
        volume = _safe(row["Volume"])
        volume_sma = _safe(row["volume_sma"], volume or 1.0) or 1.0
        spike_ratio = volume / volume_sma if volume_sma else 1.0

        close = _safe(row["Close"])
        vwap = _safe(row["vwap"], close) or close or 1.0
        vwap_diff_pct = (close - vwap) / vwap * 100 if vwap else 0.0
        price_change_pct = (
            (close - prev_close) / prev_close * 100 if prev_close else 0.0
        )

        direction = 1.0 if (vwap_diff_pct >= 0 and price_change_pct >= 0) else (
            -1.0 if (vwap_diff_pct < 0 and price_change_pct < 0) else np.sign(vwap_diff_pct) or 1.0
        )
        score = _clip(((spike_ratio - 1.0) / 2.0) * direction)
        confidence = _clip(0.25 + min(abs(spike_ratio - 1.0) / 2.5, 1.0) * 0.65, 0.0, 1.0)

        if spike_ratio >= 1.5 and vwap_diff_pct > 0:
            classification = "ANOMALY_HIGH_BUY"
        elif spike_ratio >= 1.5 and vwap_diff_pct < 0:
            classification = "ANOMALY_HIGH_SELL"
        elif spike_ratio <= 0.5:
            classification = "LOW_LIQUIDITY"
        else:
            classification = "NORMAL"

        reasoning = (
            f"Current volume is {spike_ratio:.2f}x the 20-day moving average "
            f"({'above' if spike_ratio > 1 else 'below'} typical participation); "
            f"price is trading {vwap_diff_pct:+.2f}% {'above' if vwap_diff_pct >= 0 else 'below'} VWAP, "
            f"{'confirming' if classification.startswith('ANOMALY') else 'consistent with'} "
            f"{'institutional buying pressure' if classification == 'ANOMALY_HIGH_BUY' else 'distribution/selling pressure' if classification == 'ANOMALY_HIGH_SELL' else 'ordinary trading activity'}."
        )

        return {
            "classification": classification,
            "score": _round(score),
            "confidence": _round(confidence),
            "indicators": {
                "volume_spike_ratio": _round(spike_ratio, 2),
                "vwap_diff_pct": _round(vwap_diff_pct, 2),
            },
            "reasoning": reasoning,
        }

    # ------------------------------------------------------------------ #
    # Dimension 3 — Volatility & Market Regime
    # ------------------------------------------------------------------ #
    def classify_volatility(self, row: pd.Series, prev_close: float) -> dict:
        bb_width = _safe(row["bb_width"])
        bb_pctile = _safe(row.get("bb_width_pctile", np.nan), 0.5)
        atr = _safe(row["atr"])
        close = _safe(row["Close"], 1.0) or 1.0
        atr_pct = atr / close * 100 if close else 0.0
        bb_upper, bb_lower = _safe(row["bb_upper"]), _safe(row["bb_lower"])

        short_term_move_pct = (
            (close - prev_close) / prev_close * 100 if prev_close else 0.0
        )
        direction = np.sign(short_term_move_pct) or 1.0
        squeeze = bb_pctile <= 0.25
        breakout_up = close >= bb_upper
        breakout_down = close <= bb_lower

        if squeeze and breakout_up:
            classification = "SQUEEZE_BREAKOUT_BULLISH"
            score = _clip(0.5 + min(atr_pct / 10.0, 0.5))
        elif squeeze and breakout_down:
            classification = "SQUEEZE_BREAKOUT_BEARISH"
            score = _clip(-0.5 - min(atr_pct / 10.0, 0.5))
        elif squeeze:
            classification = "VOLATILITY_SQUEEZE"
            score = _clip(0.1 * direction)
        elif bb_pctile >= 0.85:
            classification = "HIGH_VOLATILITY_EXPANSION"
            score = _clip(0.3 * direction)
        else:
            classification = "NEUTRAL_EXPANSION"
            score = _clip(0.2 * direction)

        confidence = _clip(0.35 + 0.4 * abs(bb_pctile - 0.5) * 2 + 0.15 * min(atr_pct / 5.0, 1.0), 0.0, 1.0)

        detail_by_classification = {
            "SQUEEZE_BREAKOUT_BULLISH": "Price has broken above the upper band immediately after a low-volatility squeeze, often a strong continuation signal.",
            "SQUEEZE_BREAKOUT_BEARISH": "Price has broken below the lower band immediately after a low-volatility squeeze, often a strong continuation signal.",
            "VOLATILITY_SQUEEZE": "Bands are unusually tight with price still contained between them — a breakout has not yet confirmed a direction.",
            "HIGH_VOLATILITY_EXPANSION": "Bands are wide relative to their trailing range, reflecting an elevated-volatility regime.",
            "NEUTRAL_EXPANSION": "Bands are expanding at a typical pace, supporting continuation of the current trend.",
        }
        reasoning = (
            f"Bollinger Band width sits at the {bb_pctile * 100:.0f}th percentile of its trailing range "
            f"({'a squeeze' if squeeze else 'not currently a squeeze'}); "
            f"ATR implies daily moves of ~{atr_pct:.2f}% of price. "
            f"{detail_by_classification[classification]}"
        )

        return {
            "classification": classification,
            "score": _round(score),
            "confidence": _round(confidence),
            "indicators": {
                "bb_band_width": _round(bb_width, 4),
                "atr": _round(atr, 2),
            },
            "reasoning": reasoning,
        }

    # ------------------------------------------------------------------ #
    # Aggregation
    # ------------------------------------------------------------------ #
    def aggregate(self, momentum: dict, volume: dict, volatility: dict) -> dict:
        w = cfg.DIMENSION_WEIGHTS
        composite_score = _clip(
            w["momentum"] * momentum["score"]
            + w["volume"] * volume["score"]
            + w["volatility"] * volatility["score"]
        )
        composite_confidence = _clip(
            w["momentum"] * momentum["confidence"]
            + w["volume"] * volume["confidence"]
            + w["volatility"] * volatility["confidence"],
            0.0,
            1.0,
        )

        if composite_score >= 0.6:
            action = "STRONG_BUY"
        elif composite_score >= 0.2:
            action = "BUY"
        elif composite_score <= -0.6:
            action = "STRONG_SELL"
        elif composite_score <= -0.2:
            action = "SELL"
        else:
            action = "HOLD"

        dims = {"momentum": momentum, "volume": volume, "volatility": volatility}
        lead_dim = max(dims, key=lambda d: abs(dims[d]["score"]))
        lead_label = dims[lead_dim]["classification"]

        summary = (
            f"{'Bullish' if composite_score > 0 else 'Bearish' if composite_score < 0 else 'Mixed'} "
            f"confluence led by {lead_dim} ({lead_label}); "
            f"momentum is {momentum['classification'].lower()}, "
            f"volume is {volume['classification'].lower()}, "
            f"and volatility regime is {volatility['classification'].lower()}."
        )

        return {
            "action": action,
            "composite_score": _round(composite_score),
            "composite_confidence": _round(composite_confidence),
            "synthesis_summary": summary,
        }
