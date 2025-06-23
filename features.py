from dataclasses import dataclass
from typing import List, Dict
import numpy as np
import pandas as pd
from collections import deque

@dataclass
class Order:
    price: float
    volume: float

@dataclass
class OrderBookSnapshot:
    symbol: str
    bids: List[Order]  # descending price
    asks: List[Order]  # ascending price
    best_bid: float
    best_ask: float
    timestamp: int

class OrderBookFeatures:
    def __init__(self, depth=10):
        self.depth = depth
        self.history = deque(maxlen=200)  # for short-term momentum/Fibonacci/MACD

    def extract_features(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        bids = snapshot.bids[:self.depth]
        asks = snapshot.asks[:self.depth]

        bid_prices = np.array([o.price for o in bids])
        bid_volumes = np.array([o.volume for o in bids])
        ask_prices = np.array([o.price for o in asks])
        ask_volumes = np.array([o.volume for o in asks])

        total_bid_vol = bid_volumes.sum()
        total_ask_vol = ask_volumes.sum()

        # Mid price & spread
        mid = (snapshot.best_bid + snapshot.best_ask) / 2
        spread = snapshot.best_ask - snapshot.best_bid

        # Volume imbalance
        imbalance = total_bid_vol / (total_bid_vol + total_ask_vol + 1e-9)

        # VWAP for both sides
        bid_vwap = np.sum(bid_prices * bid_volumes) / total_bid_vol
        ask_vwap = np.sum(ask_prices * ask_volumes) / total_ask_vol

        # Historical tracking for momentum & indicators
        self.history.append({
            'timestamp': snapshot.timestamp,
            'mid': mid,
            'bid_vwap': bid_vwap,
            'ask_vwap': ask_vwap,
            'imbalance': imbalance
        })

        # Price momentum over last N points (e.g., 5 * 50ms = 250ms)
        mom = None
        if len(self.history) > 5:
            mom = mid - self.history[-5]['mid']

        return {
            "symbol": snapshot.symbol,
            "mid_price": mid,
            "spread": spread,
            "imbalance": imbalance,
            "bid_vwap": bid_vwap,
            "ask_vwap": ask_vwap,
            "momentum_250ms": mom if mom is not None else 0.0,
        }

class TechnicalIndicators:
    def __init__(self):
        self.mid_prices = deque(maxlen=200)

    def update(self, mid_price: float):
        self.mid_prices.append(mid_price)

    def compute_macd(self, fast=12, slow=26, signal=9) -> Dict[str, float]:
        if len(self.mid_prices) < slow:
            return {"macd": 0.0, "macd_signal": 0.0, "macd_hist": 0.0}
        
        close = pd.Series(self.mid_prices)
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        hist = macd.iloc[-1] - macd_signal.iloc[-1]

        return {
            "macd": macd.iloc[-1],
            "macd_signal": macd_signal.iloc[-1],
            "macd_hist": hist
        }

    def compute_fibonacci_levels(self) -> Dict[str, float]:
        if len(self.mid_prices) < 10:
            return {}

        high = max(self.mid_prices)
        low = min(self.mid_prices)

        diff = high - low
        return {
            "fib_23.6": high - 0.236 * diff,
            "fib_38.2": high - 0.382 * diff,
            "fib_61.8": high - 0.618 * diff,
            "fib_support": low,
            "fib_resistance": high,
        }

class FeatureEngine:
    def __init__(self):
        self.ob_engine = OrderBookFeatures()
        self.tech_engine = TechnicalIndicators()

    def build_feature_vector(self, snapshot: OrderBookSnapshot) -> Dict[str, float]:
        ob_features = self.ob_engine.extract_features(snapshot)
        self.tech_engine.update(ob_features["mid_price"])

        tech_macd = self.tech_engine.compute_macd()
        tech_fib = self.tech_engine.compute_fibonacci_levels()

        return {
            **ob_features,
            **tech_macd,
            **tech_fib
        }
