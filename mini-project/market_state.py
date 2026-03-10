from dataclasses import dataclass
from typing import Optional, List


@dataclass
class HistoricalContext:
    """Historical data for comparison"""
    previous_rsi: List[float]  # Last 5 RSI values
    previous_macd: List[str]  # Last 5 MACD signals
    previous_sentiment: List[float]  # Last 5 sentiment scores
    accuracy_score: float  # How accurate past predictions were (0-1)

    def get_trend_consistency(self) -> str:
        """Check if current trend matches historical pattern"""
        if not self.previous_rsi or len(self.previous_rsi) < 2:
            return "insufficient_data"

        # Check if RSI is consistently moving in one direction
        rsi_trend = "up" if self.previous_rsi[-1] > self.previous_rsi[0] else "down"

        # Check if MACD signals are consistent
        macd_consistency = "mixed"
        if all(m == "bullish" for m in self.previous_macd[-3:]):
            macd_consistency = "consistent_bullish"
        elif all(m == "bearish" for m in self.previous_macd[-3:]):
            macd_consistency = "consistent_bearish"

        return f"rsi_{rsi_trend}_trend_with_{macd_consistency}_signals"


@dataclass
class ResearchInput:
    """
    Container for all data the researcher agents receive.
    Now includes historical context!
    """
    # Technical indicators
    rsi: float
    macd_signal: str  # 'bullish', 'bearish', or 'neutral'
    price_vs_ma50: str  # 'above', 'below', or 'at'
    volume_trend: str  # 'increasing', 'decreasing', or 'neutral'

    # Sentiment data
    news_sentiment: float  # -1 to +1
    social_sentiment: float  # -1 to +1
    major_event_risk: float  # 0 to 1 (higher = more risk)

    # Market context
    market_trend: str  # 'bullish', 'bearish', or 'sideways'
    sector_performance: str  # 'strong', 'weak', or 'neutral'

    # Historical context
    historical: Optional[HistoricalContext] = None

    # Optional metadata (ticker, company name, etc.)
    ticker: Optional[str] = "AAPL"
    company_name: Optional[str] = "Apple Inc."

    def to_readable_string(self) -> str:
        """Format the data nicely for prompts with historical context."""
        base_str = f"""
=== TECHNICAL INDICATORS (from Technical Agent) ===
RSI:                  {self.rsi}
MACD Signal:          {self.macd_signal}
Price vs MA50:        {self.price_vs_ma50}
Volume Trend:         {self.volume_trend}

=== SENTIMENT & NEWS DATA (from Sentiment Agent) ===
News Sentiment Score: {self.news_sentiment}   (scale: -1 to +1)
Social Sentiment:     {self.social_sentiment}  (scale: -1 to +1)
Major Event Risk:     {self.major_event_risk}         (scale: 0 to 1)

=== MARKET CONTEXT ===
Market Trend:         {self.market_trend}
Sector Performance:   {self.sector_performance}
"""

        # Add historical context if available
        if self.historical:
            base_str += f"""
=== HISTORICAL CONTEXT ===
Previous RSI Values:  {[round(r, 1) for r in self.historical.previous_rsi[-3:]]}
Previous MACD:        {self.historical.previous_macd[-3:]}
Previous Sentiment:   {self.historical.previous_sentiment[-3:]}
Prediction Accuracy:  {self.historical.accuracy_score * 100}%
Trend Analysis:       {self.historical.get_trend_consistency()}
"""

        return base_str