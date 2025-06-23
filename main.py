import grpc
import time
from collections import deque

import orderbook_pb2
import orderbook_pb2_grpc

from features import FeatureEngine, OrderBookSnapshot, Order
from strategy import TradingStrategy


class TradingClient:
    def __init__(self, symbol: str, grpc_address="localhost:50051"):
        self.symbol = symbol
        self.grpc_address = grpc_address
        self.channel = grpc.insecure_channel(self.grpc_address)
        self.stub = orderbook_pb2_grpc.OrderBookServiceStub(self.channel)

        self.feature_engine = FeatureEngine()
        self.strategy = TradingStrategy()
        self.snapshot_cache = deque(maxlen=50)

    def convert_grpc_response(self, response: orderbook_pb2.OrderBookResponse) -> OrderBookSnapshot:
        bids = [Order(price=o.price, volume=o.volume) for o in response.bids]
        asks = [Order(price=o.price, volume=o.volume) for o in response.asks]
        return OrderBookSnapshot(
            symbol=response.symbol,
            bids=bids,
            asks=asks,
            best_bid=response.best_bid,
            best_ask=response.best_ask,
            timestamp=response.timestamp
        )

    def run(self, polling_interval_ms=50):
        print(f"Connecting to gRPC server at {self.grpc_address} for symbol '{self.symbol}'...")

        request = orderbook_pb2.OrderBookRequest(symbol=self.symbol)

        while True:
            try:
                response = self.stub.GetOrderBook(request)
                snapshot = self.convert_grpc_response(response)

                self.snapshot_cache.append(snapshot)

                features = self.feature_engine.build_feature_vector(snapshot)
                signal = self.strategy.generate_signal(features)

                print(f"[{snapshot.timestamp}] Signal: {signal.upper()} | Mid: {features.get('mid_price'):.2f} | Imb: {features.get('imbalance'):.2f} | MACD Hist: {features.get('macd_hist'):.5f}")

                time.sleep(polling_interval_ms / 1000.0)

            except grpc.RpcError as e:
                print(f"gRPC error: {e}")
                time.sleep(1.0)
            except Exception as ex:
                print(f"Unexpected error: {ex}")
                time.sleep(1.0)


if __name__ == "__main__":
    client = TradingClient(symbol="ethusd")
    client.run()
