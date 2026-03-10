"""Dashboard pages package."""
from app.dashboard.pages.home import render_home
from app.dashboard.pages.run_benchmark import render_run_benchmark
from app.dashboard.pages.results import render_results
from app.dashboard.pages.system_info import render_system_info
from app.dashboard.pages.methodology import render_methodology

__all__ = [
    "render_home", "render_run_benchmark", "render_results",
    "render_system_info", "render_methodology",
]
