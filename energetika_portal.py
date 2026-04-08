from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

import streamlit as st


ROOT = Path(__file__).resolve().parent
APPS: dict[str, tuple[str, Path]] = {
    "trenazer": ("Trenažér dispečera", ROOT / "dispecer_trenazer.py"),
    "dashboard": ("BI dashboard", ROOT / "streamlit_app.py"),
}


st.set_page_config(page_title="Energetika | Portal", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0a0f1a !important;
        color: #ecf3ff !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1a2b 0%, #0b1320 100%) !important;
        border-right: 1px solid #25324a !important;
    }
    [data-testid="stSidebar"] * {
        color: #ecf3ff !important;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stCaptionContainer"] {
        color: #cbd5e1 !important;
    }
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.55rem;
        flex-wrap: wrap;
        margin: 0.1rem 0 0.55rem 0;
    }
    .top-nav a {
        text-decoration: none;
        padding: 0.34rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(100, 116, 139, 0.5);
        background: rgba(15, 23, 42, 0.45);
        color: #dbeafe;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .top-nav a:hover {
        border-color: rgba(56, 189, 248, 0.75);
        color: #e0f2fe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _qp_value(name: str, default: str) -> str:
    value: Any = st.query_params.get(name, default)
    if isinstance(value, list):
        if not value:
            return default
        return str(value[0]).lower()
    return str(value).lower()


def _run_embedded_app(script_path: Path) -> None:
    original_set_page_config = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None  # type: ignore[assignment]
    try:
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        st.set_page_config = original_set_page_config


requested_view = _qp_value("sekce", "trenazer")
if requested_view not in APPS:
    requested_view = "trenazer"

if "portal_view" not in st.session_state:
    st.session_state["portal_view"] = requested_view

if st.session_state["portal_view"] != requested_view:
    st.session_state["portal_view"] = requested_view

st.markdown(
    """
    <div class="top-nav">
      <a href="?sekce=trenazer">Trenažér</a>
      <a href="?sekce=dashboard">BI dashboard</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

app_path = APPS[st.session_state["portal_view"]][1]
if not app_path.exists():
    st.error(f"Nenalezen soubor aplikace: {app_path.name}")
    st.stop()

_run_embedded_app(app_path)
