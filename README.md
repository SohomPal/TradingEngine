# Trading Application

This is a trading application that connects to a gRPC server to fetch order book data, extract features, and generate trading signals based on a strategy.

## Features

- **Order Book Snapshot**: Fetches real-time order book data for a specific symbol.
- **Feature Extraction**: Extracts features such as mid-price, spread, imbalance, VWAP, momentum, MACD, and Fibonacci levels.
- **Trading Strategy**: Generates buy, sell, or hold signals based on extracted features.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TradingApplication.git
   cd TradingApplication/TradingEngine
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the gRPC server (ensure it's running on `localhost:50051`).
2. Run the trading client:
   ```bash
   python main.py
   ```

## Requirements

- **Python**: Version 3.8 or higher
- **gRPC Server**: Running on `localhost:50051`

## License

This project is licensed under the MIT License.