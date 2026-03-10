"""Dashboard session state helpers."""
from __future__ import annotations

from typing import List

import streamlit as st

from app.core.schemas import BenchmarkResult


def init_state() -> None:
    """Initialise default session state keys if not present."""
    defaults = {
        "results": [],
        "last_result": None,
        "current_page": "Home",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_results() -> List[BenchmarkResult]:
    return st.session_state.get("results", [])


def add_result(result: BenchmarkResult) -> None:
    if "results" not in st.session_state:
        st.session_state["results"] = []
    st.session_state["results"].append(result)
    st.session_state["last_result"] = result


def clear_results() -> None:
    st.session_state["results"] = []
    st.session_state["last_result"] = None
