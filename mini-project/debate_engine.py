import ollama
from market_state import ResearchInput
from agents.bullish import BullishResearcher
from agents.bearish import BearishResearcher
from agents.facilitator import Facilitator


class DebateEngine:
    def __init__(self, model_name: str = "llama3.2", rounds: int = 2):
        self.model_name = model_name
        self.rounds = rounds
        self.bull = BullishResearcher(model_name)
        self.bear = BearishResearcher(model_name)
        self.facilitator = Facilitator(model_name)

    def run(self, research_input: ResearchInput, verbose: bool = True):
        """
        Run the debate for n rounds.
        Returns a dict with debate history and facilitator's decision.
        """
        history = []
        last_bull_arg = None
        last_bear_arg = None

        print(f"\n{'=' * 60}")
        print(f"📊 DEBATE: {research_input.company_name} ({research_input.ticker})")
        print(f"{'=' * 60}\n")

        for round_num in range(1, self.rounds + 1):
            print(f"\n{'─' * 60}")
            print(f"ROUND {round_num}")
            print(f"{'─' * 60}")

            # Bull's turn
            print("\n🔵 BULLISH RESEARCHER:")
            bull_arg = self.bull.generate_argument(research_input, last_bear_arg)
            history.append(("Bull", bull_arg))
            last_bull_arg = bull_arg
            if verbose:
                print(bull_arg)
                print()

            # Bear's turn
            print("\n🔴 BEARISH RESEARCHER:")
            bear_arg = self.bear.generate_argument(research_input, last_bull_arg)
            history.append(("Bear", bear_arg))
            last_bear_arg = bear_arg
            if verbose:
                print(bear_arg)
                print()

        # Facilitator
        print(f"\n{'─' * 60}")
        print("⚖️  FACILITATOR DECISION")
        print(f"{'─' * 60}")
        decision = self.facilitator.evaluate(research_input, history)
        if verbose:
            print(f"\nWinner: {decision.get('winner')}")
            print(f"Action: {decision.get('recommended_action')}")
            print(f"Confidence: {decision.get('confidence')}/10")
            print(f"Deciding Factor: {decision.get('deciding_factor')}")

        print(f"\n{'=' * 60}")
        print("✅ DEBATE COMPLETE")
        print(f"{'=' * 60}")

        return {
            "debate_history": history,
            "decision": decision
        }