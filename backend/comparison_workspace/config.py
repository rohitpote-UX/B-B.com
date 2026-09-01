"""
Brand Battle — Enterprise Comparison Experience 2.0 Configuration
Persona weights, 5-system agreement metrics, TCO multiplier parameters, and decision confidence thresholds.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class PersonaWeight(BaseModel):
    name: str
    key: str
    description: str
    price_weight: float = 0.25
    performance_weight: float = 0.25
    battery_weight: float = 0.25
    value_weight: float = 0.25


class ComparisonWorkspaceConfig(BaseModel):
    """Master configuration for the AI Decision Workspace."""
    enabled: bool = True
    version: str = "v2.0-ai-decision-workspace"
    verified_attributes_count: int = 127

    personas: List[PersonaWeight] = [
        PersonaWeight(key="general", name="Most Users", description="Balanced value, performance, and durability.", price_weight=0.25, performance_weight=0.25, battery_weight=0.25, value_weight=0.25),
        PersonaWeight(key="students", name="Best for Students", description="Budget-friendly, long battery life, and durability.", price_weight=0.40, performance_weight=0.20, battery_weight=0.30, value_weight=0.10),
        PersonaWeight(key="professionals", name="Best for Professionals", description="Maximum performance, premium display, and productivity.", price_weight=0.10, performance_weight=0.50, battery_weight=0.20, value_weight=0.20),
        PersonaWeight(key="travelers", name="Best for Travelers", description="Lightweight, long battery, and compact build.", price_weight=0.20, performance_weight=0.20, battery_weight=0.40, value_weight=0.20),
        PersonaWeight(key="budget", name="Best Budget Choice", description="Lowest initial price with strong core capabilities.", price_weight=0.60, performance_weight=0.15, battery_weight=0.15, value_weight=0.10),
        PersonaWeight(key="long_term", name="Best Long-Term Investment", description="High durability, serviceability, and 5-year value.", price_weight=0.15, performance_weight=0.25, battery_weight=0.25, value_weight=0.35),
    ]


workspace_config = ComparisonWorkspaceConfig()
