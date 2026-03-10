import json
import ollama
from data_collector import DataCollector
from debate_engine import DebateEngine

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
MODEL_NAME = "llama3.2"
DEBATE_ROUNDS = 2
TICKER = "MSFT"  # Change this to any stock symbol!


def main():
    print("\n" + "=" * 60)
    print("🚀 TRADING AGENTS RESEARCH TEAM")
    print("=" * 60)

    # Get LIVE data with historical context
    print(f"\n📡 Fetching live data for {TICKER}...")
    collector = DataCollector(TICKER)
    research_input = collector.get_research_input()

    print(f"\n📊 Market Data for {research_input.company_name} ({research_input.ticker})")
    print(research_input.to_readable_string())
    print("=" * 60)

    print(f"\n🤖 Starting debate with {MODEL_NAME}...")
    print(
        f"📅 Historical accuracy: {research_input.historical.accuracy_score * 100 if research_input.historical else 'N/A'}%")
    print("=" * 60)

    # Run the debate
    engine = DebateEngine(model_name=MODEL_NAME, rounds=DEBATE_ROUNDS)
    result = engine.run(research_input, verbose=True)

    # Save results
    output_path = "debate_output.json"
    with open(output_path, "w") as f:
        # Convert tuple history to dict for JSON serialization
        result["debate_history"] = [
            {"speaker": speaker, "argument": arg}
            for speaker, arg in result["debate_history"]
        ]
        json.dump(result, f, indent=2)

    print(f"\n💾 Full debate saved to: {output_path}")
    print("\n📋 SUMMARY:")
    print(f"  Winner:          {result['decision'].get('winner')}")
    print(f"  Action:          {result['decision'].get('recommended_action')}")
    print(f"  Confidence:      {result['decision'].get('confidence')}/10")
    print(f"  Deciding Factor: {result['decision'].get('deciding_factor')}")
    print("=" * 60)


if __name__ == "__main__":
    main()