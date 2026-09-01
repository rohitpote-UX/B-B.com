"""
Brand Battle — Enterprise Decision Intelligence & Analytics Configuration
Centralized settings, stream buffer limits, latency targets (<20ms ingestion, <150ms P95 query), and retention rules.
"""

from pydantic import BaseModel
from typing import Dict, Any, List


class LatencySLOs(BaseModel):
    """Performance targets (milliseconds)."""
    ingestion_latency_ms: int = 20
    dashboard_refresh_sec: int = 2
    p95_query_latency_ms: int = 150
    realtime_stream_delay_sec: int = 5


class StreamConfig(BaseModel):
    """Redis Stream settings."""
    stream_name: str = "brandbattle:events"
    max_len: int = 50000
    group_name: str = "analytics_processors"


class AnalyticsPlatformConfig(BaseModel):
    """Master configuration for the Analytics & Decision Intelligence Platform."""
    enabled: bool = True
    algorithm_version: str = "v7.0.0-enterprise-analytics-platform"
    retention_days: int = 365
    slo: LatencySLOs = LatencySLOs()
    stream: StreamConfig = StreamConfig()

    # Feature flags
    enable_redis_stream: bool = True
    enable_anomaly_detection: bool = True
    enable_ai_insights: bool = True
    enable_continuous_learning: bool = True
    enable_experimentation: bool = True


analytics_config = AnalyticsPlatformConfig()
