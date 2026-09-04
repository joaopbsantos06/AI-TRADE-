import pandas as pd
import numpy as np


def calculate(candles):
    if len(candles) < 30:
        return {}
    df = pd.DataFrame([x.model_dump() for x in candles])
    close = df.close
    sma20 = close.rolling(20).mean().iloc[-1]
    ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rsi = 100 - 100 / (1 + gain.iloc[-1] / max(loss.iloc[-1], 1e-9))
    atr = (df.high - df.low).rolling(14).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]
    return {
        "sma_20": float(sma20),
        "ema_12": float(ema12),
        "ema_26": float(ema26),
        "rsi_14": float(rsi),
        "macd": float(ema12 - ema26),
        "atr_14": float(atr),
        "volatility_20": float(std / close.iloc[-1]),
        "support_20": float(close.tail(20).min()),
        "resistance_20": float(close.tail(20).max()),
        "volume_20": float(df.volume.tail(20).mean()),
    }
