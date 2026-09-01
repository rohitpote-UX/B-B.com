"""
Brand Battle — Commission Engine
Calculates commission rates and EPC metrics.
"""

class CommissionEngine:
    def calculate_commission(self, amount: float, rate_pct: float = 5.0) -> float:
        return round(amount * (rate_pct / 100.0), 2)

commission_engine = CommissionEngine()
