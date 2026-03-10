"""Analysis feature — aggregation, statistics, scoring, comparison."""
from app.features.analysis.schemas import ComparisonEntry, AggregatedMetrics, ScoreBreakdown
from app.features.analysis.aggregations import aggregate_results
from app.features.analysis.statistics import coefficient_of_variation, percentile
from app.features.analysis.scoring import compute_score
from app.features.analysis.comparator import build_comparison

__all__ = [
    "ComparisonEntry", "AggregatedMetrics", "ScoreBreakdown",
    "aggregate_results", "coefficient_of_variation", "percentile",
    "compute_score", "build_comparison",
]
