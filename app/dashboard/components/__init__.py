"""Dashboard components package."""
from app.dashboard.components.layout import inject_css, page_header, section_divider
from app.dashboard.components.metric_cards import metric_card, metric_row
from app.dashboard.components.charts import (
    render_latency_histogram, render_latency_timeline,
    render_throughput_comparison, render_resource_chart, render_score_radar,
)
from app.dashboard.components.benchmark_form import benchmark_form
from app.dashboard.components.status_panel import render_status_panel, render_error_panel
from app.dashboard.components.data_table import render_results_table, render_single_result_detail

__all__ = [
    "inject_css", "page_header", "section_divider",
    "metric_card", "metric_row",
    "render_latency_histogram", "render_latency_timeline",
    "render_throughput_comparison", "render_resource_chart", "render_score_radar",
    "benchmark_form",
    "render_status_panel", "render_error_panel",
    "render_results_table", "render_single_result_detail",
]
