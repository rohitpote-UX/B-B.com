"""
Brand Battle — Price Intelligence Statistical Utilities
Mathematical and statistical helper functions for mean, stddev, percentile, moving averages, and time series trend calculation.
"""

import math
from typing import List, Tuple, Optional


def mean(numbers: List[float]) -> float:
    """Compute arithmetic mean."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def stddev(numbers: List[float]) -> float:
    """Compute sample standard deviation."""
    if len(numbers) < 2:
        return 0.0
    avg = mean(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / (len(numbers) - 1)
    return math.sqrt(variance)


def variance(numbers: List[float]) -> float:
    """Compute sample variance."""
    if len(numbers) < 2:
        return 0.0
    avg = mean(numbers)
    return sum((x - avg) ** 2 for x in numbers) / (len(numbers) - 1)


def percentile(numbers: List[float], p: float) -> float:
    """Compute the p-th percentile of a list of numbers."""
    if not numbers:
        return 0.0
    sorted_nums = sorted(numbers)
    k = (len(sorted_nums) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_nums[int(k)]
    d0 = sorted_nums[int(f)] * (c - k)
    d1 = sorted_nums[int(c)] * (k - f)
    return d0 + d1


def simple_moving_average(numbers: List[float], window: int = 7) -> List[float]:
    """Compute simple moving average over a window."""
    if not numbers:
        return []
    result = []
    for i in range(len(numbers)):
        start = max(0, i - window + 1)
        chunk = numbers[start:i + 1]
        result.append(mean(chunk))
    return result


def exponential_moving_average(numbers: List[float], alpha: float = 0.3) -> List[float]:
    """Compute exponential moving average."""
    if not numbers:
        return []
    ema = [numbers[0]]
    for i in range(1, len(numbers)):
        ema.append(alpha * numbers[i] + (1 - alpha) * ema[i - 1])
    return ema


def linear_regression_slope(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Compute slope (m) and intercept (c) for y = mx + c."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0, 0.0

    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))

    denom = (n * sum_x2 - sum_x ** 2)
    if denom == 0:
        return 0.0, mean(y)

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    return slope, intercept
