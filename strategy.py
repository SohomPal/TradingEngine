# trading_strategy.py

class TradingStrategy:
    def __init__(self):
        self.last_signal = "hold"

    def generate_signal(self, features: dict) -> str:
        imbalance = features.get("imbalance", 0.5)
        momentum = features.get("momentum_250ms", 0.0)
        macd_hist = features.get("macd_hist", 0.0)
        mid_price = features.get("mid_price", 0.0)

        # Fibonacci levels (optional filters)
        fib_res = features.get("fib_resistance", None)
        fib_sup = features.get("fib_support", None)

        # Buy logic
        if imbalance > 0.65 and momentum > 0 and macd_hist > 0:
            if fib_res is None or mid_price < fib_res:
                self.last_signal = "buy"
                return "buy"

        # Sell logic
        if imbalance < 0.35 and momentum < 0 and macd_hist < 0:
            if fib_sup is None or mid_price > fib_sup:
                self.last_signal = "sell"
                return "sell"

        self.last_signal = "hold"
        return "hold"
