"""Layout helpers — inject CSS, build page structure."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

_STYLES_DIR = Path(__file__).resolve().parent.parent / "styles"


def inject_css() -> None:
    """Read all CSS files from the styles directory and inject into <style>."""
    css_parts: list[str] = []
    for css_file in sorted(_STYLES_DIR.glob("*.css")):
        css_parts.append(css_file.read_text(encoding="utf-8"))
    combined = "\n".join(css_parts)
    st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Render a futuristic page header."""
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:2rem;">
            <h1 style="
                font-family:'Orbitron',sans-serif;
                font-size:2.2rem;
                background:linear-gradient(135deg,#00D4FF,#0D6EFD);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
                letter-spacing:0.06em;
                margin-bottom:0.3rem;
            ">{title}</h1>
            <p style="color:#94A3B8;font-size:0.95rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_divider(label: str = "") -> None:
    """Thin glowing divider with optional label."""
    if label:
        st.markdown(
            f'<p style="color:#64748B;font-size:0.75rem;text-transform:uppercase;'
            f'letter-spacing:0.12em;margin:1.5rem 0 0.5rem;">{label}</p>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<hr style="border:none;height:1px;'
        'background:linear-gradient(90deg,transparent,rgba(0,212,255,0.3),transparent);'
        'margin:0.5rem 0 1.5rem;">',
        unsafe_allow_html=True,
    )
