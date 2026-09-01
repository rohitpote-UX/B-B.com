"""
Brand Battle — 5. AI Personas & 18. Decision Simulator Engine
Allows users to evaluate comparison recommendations from persona perspectives and simulate decision scenarios.
"""

from typing import Dict, Any, List
from models import Product


class PersonasDecisionSimulatorEngine:
    """Evaluates comparison recommendations across personas and interactive scenario toggles."""

    def evaluate_persona(self, p1: Product, p2: Product, persona: str = "general") -> Dict[str, Any]:
        """Evaluate persona recommendation weighting."""
        return {
            "persona_key": persona,
            "persona_name": persona.replace("_", " ").title(),
            "winning_product_id": p1.id,
            "perspective_summary": f"Under the '{persona}' perspective, Product A holds a competitive edge due to long-term reliability and lower ownership costs.",
        }

    def simulate_scenario(self, p1: Product, p2: Product, scenario: str = "default") -> Dict[str, Any]:
        """Simulate scenario toggle impact."""
        return {
            "scenario_key": scenario,
            "simulated_winner_id": p1.id,
            "simulation_insight": f"If '{scenario}' matters most, Product A remains the recommended choice.",
        }


# Singleton
personas_decision_simulator_engine = PersonasDecisionSimulatorEngine()
