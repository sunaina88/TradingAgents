import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from market_state import ResearchInput, HistoricalContext


class DataCollector:
    """Collects live and historical data for any stock"""

    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def calculate_rsi(self, prices, periods=14):
        """Calculate RSI from price data"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def get_historical_rsi(self, days=180):
        """Get last 5 historical RSI values"""
        hist = self.stock.history(period=f"{days}d")
        if len(hist) < 20:
            return [50.0, 52.0, 54.0, 56.0, 58.0]  # Fallback data

        prices = hist['Close']
        rsi_series = self.calculate_rsi(prices)
        rsi_values = rsi_series.dropna().tolist()
        return rsi_values[-5:] if len(rsi_values) >= 5 else [50.0, 52.0, 54.0, 56.0, 58.0]

    def get_historical_macd(self, days=180):
        """Get last 5 historical MACD signals"""
        hist = self.stock.history(period=f"{days}d")
        if len(hist) < 26:
            return ["bullish", "bullish", "neutral", "neutral", "bullish"]

        prices = hist['Close']
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        signals = []
        for i in range(-5, 0):
            if macd.iloc[i] > signal.iloc[i]:
                signals.append("bullish")
            elif macd.iloc[i] < signal.iloc[i]:
                signals.append("bearish")
            else:
                signals.append("neutral")

        return signals

    def get_historical_sentiment(self, days=180):
        """Simulate historical sentiment (in production, use news API)"""
        # This is simulated - in real app, you'd fetch from news API
        base = 0.3
        sentiment = []
        for i in range(5):
            sentiment.append(round(base + np.random.uniform(-0.2, 0.2), 2))
        return sentiment

    def get_current_data(self):
        """Get current market data"""
        try:
            info = self.stock.info
            hist = self.stock.history(period="2mo")

            if len(hist) < 50:
                return self._get_fallback_data()

            # Current RSI
            rsi_series = self.calculate_rsi(hist['Close'])
            current_rsi = round(rsi_series.iloc[-1], 1)

            # Price vs MA50
            ma50 = hist['Close'].tail(50).mean()
            current_price = hist['Close'].iloc[-1]
            price_vs_ma50 = "above" if current_price > ma50 else "below"

            # Volume trend
            recent_volume = hist['Volume'].tail(5).mean()
            older_volume = hist['Volume'].tail(10).head(5).mean()
            volume_trend = "increasing" if recent_volume > older_volume else "decreasing"

            # MACD signal
            exp1 = hist['Close'].ewm(span=12).mean()
            exp2 = hist['Close'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            macd_signal = "bullish" if macd.iloc[-1] > signal.iloc[-1] else "bearish"

            # Market trend
            returns = hist['Close'].pct_change().dropna()
            market_trend = "bullish" if returns.tail(20).mean() > 0.001 else "bearish" if returns.tail(
                20).mean() < -0.001 else "sideways"

            # Sector performance (simplified - compare to SPY)
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1mo")
            spy_return = spy_hist['Close'].pct_change().sum()
            stock_return = hist['Close'].tail(20).pct_change().sum()
            sector_performance = "strong" if stock_return > spy_return + 0.02 else "weak" if stock_return < spy_return - 0.02 else "neutral"

            return {
                "rsi": current_rsi,
                "macd_signal": macd_signal,
                "price_vs_ma50": price_vs_ma50,
                "volume_trend": volume_trend,
                "market_trend": market_trend,
                "sector_performance": sector_performance,
                "current_price": current_price
            }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return self._get_fallback_data()

    def _get_fallback_data(self):
        """Return fallback data if API fails"""
        return {
            "rsi": 55.0,
            "macd_signal": "neutral",
            "price_vs_ma50": "above",
            "volume_trend": "neutral",
            "market_trend": "sideways",
            "sector_performance": "neutral",
            "current_price": 150.0
        }

    def get_accuracy_score(self):
        """Calculate historical prediction accuracy"""
        try:
            hist = self.stock.history(period="1y")
            if len(hist) < 100:
                return 0.65

            rsi_series = self.calculate_rsi(hist['Close'])
            rsi_values = rsi_series.dropna()

            correct = 0
            total = 0

            for i in range(len(rsi_values) - 20):
                if rsi_values.iloc[i] > 70:  # Overbought signal
                    total += 1
                    future_return = hist['Close'].iloc[i + 20:i + 40].pct_change().sum()
                    if future_return < -0.03:  # Dropped 3%
                        correct += 1
                elif rsi_values.iloc[i] < 30:  # Oversold signal
                    total += 1
                    future_return = hist['Close'].iloc[i + 20:i + 40].pct_change().sum()
                    if future_return > 0.03:  # Rose 3%
                        correct += 1

            return round(correct / total, 2) if total > 0 else 0.65
        except:
            return 0.65

    def get_sentiment_data(self):
        """Simulate sentiment data (replace with actual news API)"""
        # In production, use NewsAPI, Finnhub, etc.
        return {
            "news_sentiment": round(np.random.uniform(-0.3, 0.8), 2),
            "social_sentiment": round(np.random.uniform(-0.2, 0.7), 2),
            "major_event_risk": round(np.random.uniform(0.1, 0.6), 2)
        }

    def get_research_input(self):
        """Get complete ResearchInput with live and historical data"""

        # Get current data
        current = self.get_current_data()

        # Get historical data
        hist_rsi = self.get_historical_rsi()
        hist_macd = self.get_historical_macd()
        hist_sentiment = self.get_historical_sentiment()

        # Get sentiment
        sentiment = self.get_sentiment_data()

        # Get accuracy score
        accuracy = self.get_accuracy_score()

        # Create historical context
        historical = HistoricalContext(
            previous_rsi=hist_rsi,
            previous_macd=hist_macd,
            previous_sentiment=hist_sentiment,
            accuracy_score=accuracy
        )

        # Create research input
        research_input = ResearchInput(
            rsi=current['rsi'],
            macd_signal=current['macd_signal'],
            price_vs_ma50=current['price_vs_ma50'],
            volume_trend=current['volume_trend'],
            news_sentiment=sentiment['news_sentiment'],
            social_sentiment=sentiment['social_sentiment'],
            major_event_risk=sentiment['major_event_risk'],
            market_trend=current['market_trend'],
            sector_performance=current['sector_performance'],
            ticker=self.ticker,
            company_name=self.stock.info.get('longName', self.ticker),
            historical=historical
        )

        return research_input


# Quick test
if __name__ == "__main__":
    collector = DataCollector("AAPL")
    data = collector.get_research_input()
    print(data.to_readable_string())