from __future__ import annotations

import html
import importlib.util
import time
from pathlib import Path
from typing import TypedDict, cast

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Interaktivní trenažér dispečera", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, #1b2a43 0%, rgba(27, 42, 67, 0.35) 28%, rgba(9, 14, 24, 0.92) 60%),
            linear-gradient(145deg, #090f1a 0%, #101a2d 55%, #090f1a 100%);
    }
    .hero-card {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.92), rgba(15, 23, 42, 0.85));
        margin-bottom: 0.8rem;
    }
    .hero-title {
        font-size: 1.02rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .hero-sub {
        color: #cbd5e1;
        font-size: 0.92rem;
        margin-bottom: 0;
    }
    .kpi-card {
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.75));
        padding: 0.55rem 0.75rem;
        min-height: 82px;
        position: relative;
    }
    .kpi-label {
        color: #cbd5e1;
        font-size: 0.78rem;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .kpi-info {
        position: absolute;
        top: 6px;
        right: 8px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        border: 1px solid rgba(148, 163, 184, 0.6);
        color: #cbd5e1;
        font-size: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: default;
        background: rgba(15, 23, 42, 0.8);
    }
    .kpi-tip {
        display: none;
        position: absolute;
        top: 28px;
        right: 8px;
        width: 190px;
        padding: 0.35rem 0.45rem;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: rgba(15, 23, 42, 0.95);
        color: #cbd5e1;
        font-size: 0.72rem;
        z-index: 30;
    }
    .kpi-info:hover + .kpi-tip {
        display: block;
    }
    .ap-badge {
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 0.4rem 0.65rem;
        background: rgba(14, 116, 144, 0.16);
        margin-bottom: 0.5rem;
    }
    .ap-title {
        font-size: 0.78rem;
        color: #bae6fd;
        margin-bottom: 0.1rem;
    }
    .ap-value {
        font-size: 1.02rem;
        font-weight: 700;
        color: #e0f2fe;
    }
    .pulse-bolt {
        animation: pulseGlow 0.45s ease-in-out 2;
        font-size: 1.1rem;
        font-weight: 700;
        color: #fde047;
        padding: 0.45rem 0.7rem;
        border: 1px solid rgba(253, 224, 71, 0.35);
        border-radius: 10px;
        background: rgba(120, 53, 15, 0.2);
        margin: 0.45rem 0;
    }
    .impact-wrap {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 10px;
        padding: 0.45rem;
        margin-top: 0.35rem;
        background: rgba(15, 23, 42, 0.45);
    }
    .impact-row {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 0.35rem;
    }
    .impact-row:last-child {
        margin-bottom: 0;
    }
    .impact-icon {
        width: 22px;
        height: 22px;
        min-width: 22px;
        border-radius: 50%;
        border: 1px solid rgba(148, 163, 184, 0.45);
        color: #e2e8f0;
        font-size: 11px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(30, 41, 59, 0.9);
    }
    .impact-main {
        flex: 1;
    }
    .impact-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-bottom: 0.12rem;
    }
    .impact-metric {
        color: #cbd5e1;
        font-size: 0.74rem;
    }
    .impact-badge {
        font-size: 0.7rem;
        padding: 0.1rem 0.38rem;
        border-radius: 999px;
        border: 1px solid transparent;
        font-weight: 600;
        white-space: nowrap;
    }
    .impact-good {
        color: #86efac;
        background: rgba(22, 163, 74, 0.2);
        border-color: rgba(134, 239, 172, 0.45);
    }
    .impact-bad {
        color: #fca5a5;
        background: rgba(220, 38, 38, 0.18);
        border-color: rgba(252, 165, 165, 0.45);
    }
    .impact-neutral {
        color: #cbd5e1;
        background: rgba(100, 116, 139, 0.2);
        border-color: rgba(203, 213, 225, 0.35);
    }
    .impact-bar {
        height: 6px;
        border-radius: 999px;
        background: rgba(51, 65, 85, 0.65);
        overflow: hidden;
    }
    .impact-fill {
        height: 100%;
        border-radius: 999px;
    }
    .impact-fill.impact-good {
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.5), rgba(134, 239, 172, 0.9));
    }
    .impact-fill.impact-bad {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.5), rgba(252, 165, 165, 0.9));
    }
    .impact-fill.impact-neutral {
        background: linear-gradient(90deg, rgba(148, 163, 184, 0.35), rgba(203, 213, 225, 0.7));
    }
    .scene-card {
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 14px;
        margin-bottom: 0.8rem;
        overflow: hidden;
        background: rgba(15, 23, 42, 0.72);
    }
    .scene-top {
        padding: 0.55rem 0.8rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.28);
        display: flex;
        justify-content: space-between;
        gap: 0.8rem;
        align-items: center;
    }
    .scene-title {
        font-size: 0.9rem;
        color: #f8fafc;
        font-weight: 700;
    }
    .scene-sub {
        font-size: 0.78rem;
        color: #cbd5e1;
    }
    .scene-emoji {
        font-size: 1.5rem;
        line-height: 1;
    }
    .scene-visual {
        padding: 0.55rem 0.8rem 0.75rem 0.8rem;
    }
    .scene-sky {
        height: 84px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        position: relative;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    .scene-sky.phase-morning {
        background: linear-gradient(145deg, rgba(59, 130, 246, 0.36), rgba(15, 23, 42, 0.92));
    }
    .scene-sky.phase-day {
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.33), rgba(15, 23, 42, 0.90));
    }
    .scene-sky.phase-evening {
        background: linear-gradient(145deg, rgba(249, 115, 22, 0.35), rgba(15, 23, 42, 0.92));
    }
    .scene-sky.phase-night {
        background: linear-gradient(145deg, rgba(67, 56, 202, 0.30), rgba(2, 6, 23, 0.95));
    }
    .scene-sun,
    .scene-moon {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        position: absolute;
        top: 14px;
        right: 22px;
    }
    .scene-sun {
        background: radial-gradient(circle, rgba(254, 240, 138, 0.95), rgba(250, 204, 21, 0.75));
        box-shadow: 0 0 18px rgba(250, 204, 21, 0.45);
        animation: sunPulse 3.2s ease-in-out infinite;
    }
    .scene-moon {
        background: radial-gradient(circle, rgba(226, 232, 240, 0.92), rgba(148, 163, 184, 0.7));
        box-shadow: 0 0 14px rgba(148, 163, 184, 0.35);
        animation: moonFloat 4.5s ease-in-out infinite;
        display: none;
    }
    .scene-sky.phase-night .scene-sun {
        display: none;
    }
    .scene-sky.phase-night .scene-moon {
        display: block;
    }
    .scene-cloud {
        position: absolute;
        top: 26px;
        width: 48px;
        height: 18px;
        border-radius: 999px;
        background: rgba(226, 232, 240, 0.65);
        opacity: 0.5;
    }
    .scene-cloud::before,
    .scene-cloud::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        background: inherit;
    }
    .scene-cloud::before {
        width: 16px;
        height: 16px;
        left: 8px;
        top: -8px;
    }
    .scene-cloud::after {
        width: 20px;
        height: 20px;
        left: 24px;
        top: -10px;
    }
    .scene-cloud.cloud-a {
        left: -60px;
        animation: cloudDriftA 16s linear infinite;
    }
    .scene-cloud.cloud-b {
        top: 40px;
        left: -90px;
        animation: cloudDriftB 21s linear infinite;
    }
    .scene-sky.weather-clear .scene-cloud {
        opacity: 0.24;
    }
    .scene-sky.weather-mixed .scene-cloud {
        opacity: 0.52;
    }
    .scene-sky.weather-cloudy .scene-cloud {
        opacity: 0.86;
    }
    .scene-rain {
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            100deg,
            rgba(147, 197, 253, 0.0) 0,
            rgba(147, 197, 253, 0.0) 13px,
            rgba(147, 197, 253, 0.45) 13px,
            rgba(147, 197, 253, 0.45) 15px
        );
        opacity: 0;
        transform: translateY(-16px);
    }
    .scene-sky.weather-cloudy .scene-rain {
        opacity: 0.45;
        animation: rainFall 1.2s linear infinite;
    }
    .scene-sky.is-crisis .scene-rain {
        opacity: 0.62;
        animation-duration: 0.9s;
    }
    .scene-city {
        height: 46px;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.3);
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.45), rgba(15, 23, 42, 0.88));
        margin-top: 0.5rem;
        position: relative;
        overflow: hidden;
    }
    .scene-city-glow {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 70%;
        background: repeating-linear-gradient(
            90deg,
            rgba(251, 191, 36, 0.16) 0,
            rgba(251, 191, 36, 0.16) 7px,
            rgba(15, 23, 42, 0.0) 7px,
            rgba(15, 23, 42, 0.0) 11px
        );
        transition: opacity 0.35s ease;
    }
    .scene-city-alert {
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.0), rgba(239, 68, 68, 0.20), rgba(239, 68, 68, 0.0));
        display: none;
    }
    .scene-city.is-crisis .scene-city-alert {
        display: block;
        animation: blackoutBlink 1.1s ease-in-out infinite;
    }
    .scene-legend {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.35rem;
        margin-top: 0.45rem;
    }
    .scene-chip {
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 999px;
        font-size: 0.7rem;
        color: #dbeafe;
        padding: 0.18rem 0.45rem;
        background: rgba(15, 23, 42, 0.56);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .scene-chip.good {
        border-color: rgba(74, 222, 128, 0.55);
        color: #bbf7d0;
    }
    .scene-chip.warn {
        border-color: rgba(251, 191, 36, 0.55);
        color: #fde68a;
    }
    .scene-chip.danger {
        border-color: rgba(248, 113, 113, 0.55);
        color: #fecaca;
    }
    .scene-risk-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-top: 0.45rem;
    }
    .scene-risk-label {
        font-size: 0.72rem;
        color: #cbd5e1;
    }
    .scene-risk-value {
        font-size: 0.72rem;
        color: #dbeafe;
        font-weight: 600;
    }
    .scene-risk-track {
        height: 8px;
        border-radius: 999px;
        background: rgba(51, 65, 85, 0.72);
        overflow: hidden;
        margin-top: 0.2rem;
    }
    .scene-risk-fill {
        height: 100%;
        border-radius: 999px;
        min-width: 4px;
    }
    .scene-risk-fill.good {
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.45), rgba(134, 239, 172, 0.92));
    }
    .scene-risk-fill.warn {
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.45), rgba(253, 224, 71, 0.92));
    }
    .scene-risk-fill.danger {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.45), rgba(252, 165, 165, 0.92));
    }
    }
    .mood-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.45rem;
        margin: 0.55rem 0 0.8rem 0;
    }
    .mood-card {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 10px;
        padding: 0.42rem 0.5rem;
        background: rgba(15, 23, 42, 0.46);
    }
    .mood-head {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin-bottom: 0.16rem;
        font-weight: 600;
        font-size: 0.8rem;
        color: #e2e8f0;
    }
    .mood-head span {
        font-size: 0.96rem;
    }
    .mood-text {
        font-size: 0.73rem;
        color: #cbd5e1;
        line-height: 1.35;
    }
    .mood-ok {
        border-color: rgba(74, 222, 128, 0.45);
        background: rgba(22, 163, 74, 0.14);
    }
    .mood-warn {
        border-color: rgba(251, 191, 36, 0.45);
        background: rgba(202, 138, 4, 0.14);
    }
    .mood-alert {
        border-color: rgba(248, 113, 113, 0.5);
        background: rgba(220, 38, 38, 0.18);
    }
    .mood-alert.blink {
        animation: warningBlink 1.1s ease-in-out infinite;
    }
    .op-map {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 12px;
        padding: 0.55rem;
        margin-top: 0.5rem;
        background: rgba(15, 23, 42, 0.45);
    }
    .op-map-title {
        font-size: 0.8rem;
        color: #dbeafe;
        margin-bottom: 0.35rem;
        font-weight: 600;
    }
    .op-row {
        display: grid;
        grid-template-columns: 122px 1fr 54px;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 0.28rem;
    }
    .op-row:last-child {
        margin-bottom: 0;
    }
    .op-label {
        color: #cbd5e1;
        font-size: 0.74rem;
        white-space: nowrap;
    }
    .op-track {
        height: 8px;
        border-radius: 999px;
        background: rgba(51, 65, 85, 0.75);
        overflow: hidden;
        position: relative;
    }
    .op-fill {
        height: 100%;
        border-radius: 999px;
    }
    .op-pos {
        background: linear-gradient(90deg, rgba(34, 197, 94, 0.45), rgba(134, 239, 172, 0.9));
    }
    .op-neg {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.45), rgba(252, 165, 165, 0.9));
    }
    .op-neu {
        background: linear-gradient(90deg, rgba(148, 163, 184, 0.4), rgba(203, 213, 225, 0.72));
    }
    .op-val {
        color: #cbd5e1;
        font-size: 0.72rem;
        text-align: right;
    }
    .op-map.flash {
        animation: pulseGlow 0.4s ease-in-out 3;
    }
    @keyframes pulseGlow {
        0% { transform: scale(1.0); opacity: 0.7; }
        50% { transform: scale(1.03); opacity: 1.0; }
        100% { transform: scale(1.0); opacity: 0.7; }
    }
    @keyframes warningBlink {
        0% { box-shadow: 0 0 0 rgba(248, 113, 113, 0.0); }
        50% { box-shadow: 0 0 16px rgba(248, 113, 113, 0.35); }
        100% { box-shadow: 0 0 0 rgba(248, 113, 113, 0.0); }
    }
    @keyframes sunPulse {
        0% { transform: scale(1); opacity: 0.88; }
        50% { transform: scale(1.08); opacity: 1; }
        100% { transform: scale(1); opacity: 0.88; }
    }
    @keyframes moonFloat {
        0% { transform: translateY(0); }
        50% { transform: translateY(-2px); }
        100% { transform: translateY(0); }
    }
    @keyframes cloudDriftA {
        0% { transform: translateX(0); }
        100% { transform: translateX(360px); }
    }
    @keyframes cloudDriftB {
        0% { transform: translateX(0); }
        100% { transform: translateX(420px); }
    }
    @keyframes rainFall {
        0% { transform: translateY(-14px); }
        100% { transform: translateY(14px); }
    }
    @keyframes blackoutBlink {
        0% { opacity: 0.15; }
        50% { opacity: 0.5; }
        100% { opacity: 0.15; }
    }
    div[data-testid="stMetricValue"] {
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


STEP_COUNT = 10
START_HOUR = 8.0
DT = 0.0625


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def score_band(score: float) -> str:
    if score >= 85:
        return "Elitní dispečer"
    if score >= 70:
        return "Stabilní provoz"
    if score >= 55:
        return "Napjatá směna"
    return "Krizový režim"


def estimate_step_score(metrics: dict[str, float]) -> float:
    score = 100.0
    score -= metrics["blackout_h"] * 65.0
    score -= clamp(-metrics["worst_balance"], 0.0, 850.0) / 12.0
    score -= clamp(metrics["avg_price"] - 90.0, 0.0, 150.0) / 4.0
    score -= metrics["variable_cost"] / 9000.0
    return clamp(score, 0.0, 100.0)


def estimate_live_score(trust: float, stress: float, balance_now: float, price_now: float) -> float:
    score = 0.68 * trust + 0.32 * (100.0 - stress)
    if balance_now < 0:
        score -= min(25.0, abs(balance_now) / 38.0)
    score -= clamp(price_now - 95.0, 0.0, 160.0) / 6.5
    return clamp(score, 0.0, 100.0)


def render_kpi_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, info_text) in zip(cols, items):
        safe_label = html.escape(label)
        safe_value = html.escape(value)
        info_html = ""
        if info_text:
            safe_info = html.escape(info_text)
            info_html = f'<div class="kpi-info">i</div><div class="kpi-tip">{safe_info}</div>'
        card_html = (
            '<div class="kpi-card">'
            f"{info_html}"
            f'<div class="kpi-label">{safe_label}</div>'
            f'<div class="kpi-value">{safe_value}</div>'
            '</div>'
        )
        col.markdown(
            card_html,
            unsafe_allow_html=True,
        )


def load_model_module():
    model_path = Path(__file__).with_name("SFD Energetika.py")
    spec = importlib.util.spec_from_file_location("sfd_energetika_core", model_path)
    if spec is None or spec.loader is None:
        raise ImportError("Nepodařilo se načíst modelové jádro.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@st.cache_resource
def get_model_module():
    return load_model_module()


def generate_step_durations(seed: int, n_steps: int = STEP_COUNT) -> list[float]:
    # 24 hodin = 48 pulhodinovych jednotek, kazdy krok 1..8 jednotek (0.5..4 h)
    rng = np.random.default_rng(seed)
    units = [1] * n_steps
    remaining = 48 - n_steps

    for i in range(n_steps):
        left = n_steps - i - 1
        min_add = max(0, remaining - left * 7)
        max_add = min(7, remaining)
        add = int(rng.integers(min_add, max_add + 1))
        units[i] += add
        remaining -= add

    return [u * 0.5 for u in units]


def format_clock(hour_float: float) -> str:
    h = hour_float % 24.0
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh = (hh + 1) % 24
        mm = 0
    return f"{hh:02d}:{mm:02d}"


def build_step_table(durations: list[float], start_hour: float = START_HOUR) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    t = start_hour
    for idx, dur in enumerate(durations, start=1):
        t_end = t + dur
        rows.append(
            {
                "krok": idx,
                "od_h": t,
                "do_h": t_end,
                "delka_h": dur,
                "cas": f"{format_clock(t)} -> {format_clock(t_end)}",
            }
        )
        t = t_end
    return pd.DataFrame(rows)


EVENTS: list[dict[str, str]] = [
    {"titulek": "Nástup do služby", "text": "Je 08:00. Převzal(a) jsi směnu dispečera české soustavy."},
    {"titulek": "Počasí se láme", "text": "Model počasí naznačuje rychlé změny ve větru i oblačnosti."},
    {"titulek": "Průmysl přidává odběr", "text": "Několik velkých podniků najíždí výrobu dříve než obvykle."},
    {"titulek": "Napětí na trhu", "text": "Přeshraniční trh je nervózní, ceny i dostupnost toků kolísají."},
    {"titulek": "Technická nejistota", "text": "Dispečink hlásí zvýšené riziko závad flexibilních zdrojů."},
    {"titulek": "Odpolední špička", "text": "Spotřeba roste a roste i citlivost soustavy na chybný zásah."},
    {"titulek": "Nestabilní večer", "text": "Krátké výkyvy výroby komplikují držení bilance."},
    {"titulek": "Noční přeliv", "text": "V některých hodinách hrozí naopak přebytek a nutnost omezování."},
    {"titulek": "Křehká rovnováha", "text": "Síť je po sérii zásahů citlivá na další rozhodnutí."},
    {"titulek": "Předranní útlum", "text": "Nízká spotřeba skrývá riziko špatného načasování výroby."},
    {"titulek": "Ranní náběh", "text": "Blíží se ráno a s ním prudký růst poptávky."},
    {"titulek": "Předání směny", "text": "Poslední krok určí, v jakém stavu síť předáš dalšímu dispečerovi."},
]


class ActionCard(TypedDict):
    id: str
    label: str
    cost: int
    popis: str
    params: dict[str, float]
    trust_delta: float
    stress_delta: float


class EventData(TypedDict):
    weather: str
    demand: str
    market: str
    tech: str
    krize: str
    params: dict[str, float]
    trust_delta: float
    stress_delta: float


class ActionUiCard(TypedDict):
    id: str
    label: str
    cost: int
    popis: str
    enabled: bool
    hint: str
    priority: int


ACTION_CARDS: list[ActionCard] = [
    {
        "id": "gas_surge",
        "label": "Rychlý náběh plynu",
        "cost": 2,
        "popis": "Velká stabilizační síla, ale drahý a emisně náročný zásah.",
        "params": {"max_kapacita_plynu": 3200.0, "doba_nabehu_plynu": 0.08},
        "trust_delta": 2.0,
        "stress_delta": 9.0,
    },
    {
        "id": "import_shield",
        "label": "Otevřít importní koridor",
        "cost": 2,
        "popis": "Zvýší stabilitu při deficitu, ale zvyšuje náklady.",
        "params": {"max_prenosova_kapacita": 7000.0},
        "trust_delta": 0.5,
        "stress_delta": 4.0,
    },
    {
        "id": "demand_response",
        "label": "Aktivovat řízení spotřeby",
        "cost": 1,
        "popis": "Sníží poptávku, ale veřejnost to nemusí nést dobře.",
        "params": {"init_poptavka": 3800.0},
        "trust_delta": -7.0,
        "stress_delta": -3.0,
    },
    {
        "id": "battery_push",
        "label": "Agresivní bateriový režim",
        "cost": 1,
        "popis": "Vyšší flexibilita baterií, ale rychlejší opotřebení.",
        "params": {"max_vykon_baterie": 2200.0, "kapacita_baterie": 3200.0},
        "trust_delta": 1.0,
        "stress_delta": 8.0,
    },
    {
        "id": "hydro_ramp",
        "label": "Rychlé PVE manévry",
        "cost": 1,
        "popis": "Pomůže vykrýt špičky, ale může zvýšit nestabilitu toků.",
        "params": {"max_vykon_pve": 3200.0},
        "trust_delta": 0.0,
        "stress_delta": 7.0,
    },
    {
        "id": "coal_commit",
        "label": "Tvrdý závazek uhlí",
        "cost": 2,
        "popis": "Silná základna výkonu, nižší cena, ale vyšší emise.",
        "params": {"max_kapacita_uhli": 7800.0, "technicke_minimum_uhli": 2200.0},
        "trust_delta": -3.0,
        "stress_delta": 5.0,
    },
    {
        "id": "public_alert",
        "label": "Včasná komunikace veřejnosti",
        "cost": 1,
        "popis": "Zvyšuje důvěru, ale operativně nepomáhá bilanci.",
        "params": {},
        "trust_delta": 9.0,
        "stress_delta": -4.0,
    },
]


def get_action(card_id: str) -> ActionCard:
    for card in ACTION_CARDS:
        if card["id"] == card_id:
            return card
    return ACTION_CARDS[0]


def intensity_label(intensity: float) -> str:
    if intensity < 0.8:
        return "nízká"
    if intensity < 1.2:
        return "střední"
    if intensity < 1.7:
        return "vysoká"
    return "extrémní"


def card_plain_meaning(card_id: str) -> str:
    meanings = {
        "gas_surge": "Navýšíš a zrychlíš plyn, abys rychle zalepil deficit výkonu.",
        "import_shield": "Zvýšíš přeshraniční kapacitu, takže síť snáz doveze/exportuje energii.",
        "demand_response": "Aktivně utlumíš odběr části spotřeby, aby okamžitě klesla poptávka.",
        "battery_push": "Povolíš bateriím agresivnější nabíjení/vybíjení pro rychlejší regulaci.",
        "hydro_ramp": "PVE pojede ostřeji, tedy rychlejší čerpání/turbínování podle bilance.",
        "coal_commit": "Zvýšíš dostupný uhelný výkon a technické minimum pro jistotu základu.",
        "public_alert": "Půjdeš do aktivní komunikace směrem k veřejnosti a trhu.",
    }
    return meanings.get(card_id, "Operativní zásah do řízení sítě.")


def action_effect_preview(
    card_id: str,
    intensity: float,
    balance_now: float,
    price_now: float,
    pve_limited: bool,
) -> list[str]:
    s = intensity_label(intensity)
    if card_id == "gas_surge":
        return [
            f"[SÍLA {s}] Bilance -> výrazně nahoru (typicky +{int(400 * intensity)} až +{int(900 * intensity)} MW).",
            "Cena -> spíš nahoru, protože plyn je dražší zdroj.",
            "Stres -> krátkodobě nahoru kvůli agresivnímu rampování.",
        ]

    if card_id == "import_shield":
        support = "pomůže" if balance_now < -120 else "spíš jen zvýší flexibilitu"
        return [
            f"[SÍLA {s}] Otevíráš víc přeshraniční kapacity: import/export může téct ve větším objemu.",
            f"Teď to nejspíš {support} bilanci (aktuálně {balance_now:.0f} MW).",
            "Cena -> může jít nahoru při drahém importu, ale padá riziko deficitu.",
        ]

    if card_id == "demand_response":
        return [
            f"[SÍLA {s}] Poptávka -> dolů (typicky -{int(250 * intensity)} až -{int(700 * intensity)} MW).",
            "Bilance -> zlepší se hlavně při deficitu.",
            "Důvěra -> může krátkodobě klesnout, zásah je citlivý pro odběratele.",
        ]

    if card_id == "battery_push":
        return [
            f"[SÍLA {s}] Baterie -> rychlejší reakce na výkyvy (hladší krátké špičky).",
            "Bilance -> lepší v minutách až desítkách minut, neřeší dlouhý deficit sama.",
            "Stres -> spíš nahoru, protože baterie jedou agresivněji.",
        ]

    if card_id == "hydro_ramp":
        limited_txt = "PVE je ale omezené, efekt bude slabší." if pve_limited else "PVE by mělo mít dobrý regulační efekt."
        return [
            f"[SÍLA {s}] PVE -> rychlejší turbínování/čerpání podle bilance.",
            limited_txt,
            "Bilance -> obvykle výrazně stabilnější, ale může růst technický stres.",
        ]

    if card_id == "coal_commit":
        return [
            f"[SÍLA {s}] Uhlí -> silnější základ výkonu (lepší jistota pokrytí).",
            "Cena -> často mírně dolů proti plynu/importu.",
            "Udržitelnost a důvěra -> spíš dolů kvůli emisnímu profilu.",
        ]

    if card_id == "public_alert":
        return [
            f"[SÍLA {s}] Důvěra -> nahoru, protože veřejnost dostane jasný plán.",
            "Bilance ani cena se tím přímo nezmění.",
            "Vhodné hlavně při růstu stresu nebo po krizovém kroku.",
        ]

    return [
        f"[SÍLA {s}] Očekávej změnu parametrů podle zvolené intenzity.",
    ]


def action_effect_badges(
    card_id: str,
    intensity: float,
    balance_now: float,
    price_now: float,
    pve_limited: bool,
) -> list[dict[str, object]]:
    effects: dict[str, float]
    if card_id == "gas_surge":
        effects = {"Bilance": 2.5 * intensity, "Cena": 1.8 * intensity, "Důvěra": 0.4 * intensity, "Stres": 2.2 * intensity}
    elif card_id == "import_shield":
        base_bal = 1.8 if balance_now < -120 else 1.0
        base_price = 0.9 if price_now < 120 else 0.6
        effects = {"Bilance": base_bal * intensity, "Cena": base_price * intensity, "Důvěra": 0.2 * intensity, "Stres": 0.9 * intensity}
    elif card_id == "demand_response":
        effects = {"Bilance": 1.9 * intensity, "Cena": -0.9 * intensity, "Důvěra": -2.3 * intensity, "Stres": -1.1 * intensity}
    elif card_id == "battery_push":
        effects = {"Bilance": 1.4 * intensity, "Cena": 0.2 * intensity, "Důvěra": 0.3 * intensity, "Stres": 2.0 * intensity}
    elif card_id == "hydro_ramp":
        bal = (0.8 if pve_limited else 2.1) * intensity
        effects = {"Bilance": bal, "Cena": -0.4 * intensity, "Důvěra": 0.2 * intensity, "Stres": 1.8 * intensity}
    elif card_id == "coal_commit":
        effects = {"Bilance": 2.1 * intensity, "Cena": -1.0 * intensity, "Důvěra": -1.5 * intensity, "Stres": 1.5 * intensity}
    elif card_id == "public_alert":
        effects = {"Bilance": 0.0, "Cena": 0.0, "Důvěra": 2.8 * intensity, "Stres": -1.4 * intensity}
    else:
        effects = {"Bilance": 0.2 * intensity, "Cena": 0.0, "Důvěra": 0.0, "Stres": 0.0}

    desirable_positive = {"Bilance": True, "Cena": False, "Důvěra": True, "Stres": False}
    metric_icons = {"Bilance": "BL", "Cena": "CZ", "Důvěra": "DV", "Stres": "ST"}

    badges: list[dict[str, object]] = []
    for metric in ["Bilance", "Cena", "Důvěra", "Stres"]:
        value = float(effects.get(metric, 0.0))
        strength = abs(value)
        if strength < 0.35:
            cls = "impact-neutral"
            text = "~ beze změny"
        else:
            is_good = (value > 0) if desirable_positive[metric] else (value < 0)
            cls = "impact-good" if is_good else "impact-bad"
            if strength < 1.2:
                lvl = "slabě"
            elif strength < 2.2:
                lvl = "středně"
            else:
                lvl = "silně"
            arrow = "↑" if value > 0 else "↓"
            text = f"{arrow} {lvl}"

        width = int(clamp(22 + strength * 24, 22, 96))
        badges.append(
            {
                "metric": metric,
                "icon": metric_icons[metric],
                "class": cls,
                "text": text,
                "width": width,
            }
        )

    return badges


def render_action_effect_badges(badges: list[dict[str, object]]) -> str:
    rows: list[str] = ['<div class="impact-wrap">']
    for b in badges:
        metric = html.escape(str(b["metric"]))
        icon = html.escape(str(b["icon"]))
        cls = html.escape(str(b["class"]))
        text = html.escape(str(b["text"]))
        width = int(float(cast(float, b["width"])))
        rows.append(
            '<div class="impact-row">'
            f'<div class="impact-icon">{icon}</div>'
            '<div class="impact-main">'
            '<div class="impact-top">'
            f'<span class="impact-metric">{metric}</span>'
            f'<span class="impact-badge {cls}">{text}</span>'
            '</div>'
            '<div class="impact-bar">'
            f'<div class="impact-fill {cls}" style="width:{width}%"></div>'
            '</div>'
            '</div>'
            '</div>'
        )
    rows.append("</div>")
    return "".join(rows)


def render_day_scene(hour_now: float, event: EventData, balance_now: float, blackout_risk: float) -> str:
    crisis_now = bool(event["krize"]) or blackout_risk > 0.5 or balance_now < -450
    weather_low = event["weather"].lower()

    if hour_now < 10.0:
        phase = "Ráno"
        phase_class = "phase-morning"
    elif hour_now < 17.0:
        phase = "Den"
        phase_class = "phase-day"
    elif hour_now < 21.0:
        phase = "Večer"
        phase_class = "phase-evening"
    else:
        phase = "Noc"
        phase_class = "phase-night"

    if "nepříznivé" in weather_low or "slabý" in weather_low:
        symbol = "☁"
        weather_class = "weather-cloudy"
        weather_desc = "Zhoršené počasí"
        weather_chip_cls = "danger"
    elif "příznivé" in weather_low:
        symbol = "☀"
        weather_class = "weather-clear"
        weather_desc = "Příznivé počasí"
        weather_chip_cls = "good"
    else:
        symbol = "⛅"
        weather_class = "weather-mixed"
        weather_desc = "Smíšené počasí"
        weather_chip_cls = "warn"

    risk_pct = float(clamp(blackout_risk * 100.0, 0.0, 100.0))
    if risk_pct >= 50.0:
        risk_class = "danger"
    elif risk_pct >= 20.0:
        risk_class = "warn"
    else:
        risk_class = "good"

    if balance_now < -200.0:
        balance_chip = "Deficit bilance"
        balance_class = "danger"
    elif balance_now > 250.0:
        balance_chip = "Přebytek bilance"
        balance_class = "warn"
    else:
        balance_chip = "Bilance vyrovnaná"
        balance_class = "good"

    city_glow = "0.18" if crisis_now else "0.78"
    state = "Síť je v krizovém napětí" if crisis_now else "Síť je stabilní a pod kontrolou"
    summary = f"{phase} | Bilance {balance_now:.0f} MW | Riziko blackoutu {blackout_risk:.2f}"
    scene_class = f"scene-sky {phase_class} {weather_class} {'is-crisis' if crisis_now else 'is-stable'}"
    city_class = f"scene-city {'is-crisis' if crisis_now else 'is-stable'}"

    return (
        '<div class="scene-card">'
        '<div class="scene-top">'
        '<div>'
        '<div class="scene-title">Dynamická scéna dne</div>'
        f'<div class="scene-sub">{html.escape(summary)}</div>'
        '</div>'
        f'<div class="scene-emoji">{html.escape(symbol)}</div>'
        '</div>'
        '<div class="scene-visual">'
        f'<div class="{scene_class}">'
        '<div class="scene-sun"></div>'
        '<div class="scene-moon"></div>'
        '<div class="scene-cloud cloud-a"></div>'
        '<div class="scene-cloud cloud-b"></div>'
        '<div class="scene-rain"></div>'
        '</div>'
        f'<div class="{city_class}">'
        f'<div class="scene-city-glow" style="opacity:{city_glow};"></div>'
        '<div class="scene-city-alert"></div>'
        '</div>'
        '<div class="scene-legend">'
        f'<div class="scene-chip">Fáze: {html.escape(phase)}</div>'
        f'<div class="scene-chip {weather_chip_cls}">Počasí: {html.escape(weather_desc)}</div>'
        f'<div class="scene-chip {balance_class}">{html.escape(balance_chip)}</div>'
        '</div>'
        '<div class="scene-risk-wrap">'
        '<div class="scene-risk-label">Riziko blackoutu (nižší je lepší)</div>'
        f'<div class="scene-risk-value">{risk_pct:.0f}%</div>'
        '</div>'
        '<div class="scene-risk-track">'
        f'<div class="scene-risk-fill {risk_class}" style="width:{risk_pct:.0f}%"></div>'
        '</div>'
        f'<div class="scene-sub" style="margin-top:0.4rem;">{html.escape(state)}</div>'
        '<div class="scene-sub" style="margin-top:0.18rem;">'
        'Legenda: jasnější město = stabilnější síť, ztmavení/červené pulzy = krizový stav.'
        '</div>'
        '</div>'
        '</div>'
    )


def _mood_state(text: str, positive_tokens: list[str], negative_tokens: list[str]) -> str:
    low = text.lower()
    if any(tok in low for tok in negative_tokens):
        return "mood-alert"
    if any(tok in low for tok in positive_tokens):
        return "mood-ok"
    return "mood-warn"


def render_mood_panels(event: EventData) -> str:
    weather_state = _mood_state(event["weather"], ["příznivé", "normálu"], ["nepříznivé", "slabý"])
    demand_state = _mood_state(event["demand"], ["nízká"], ["roste nad plán"])
    market_state = _mood_state(event["market"], ["dobrá", "standardní"], ["napjatý", "omezený"])
    tech_state = _mood_state(event["tech"], ["bez mimořádné", "obnovena"], ["výpadek", "závada"])

    crisis_now = bool(event["krize"])
    tech_cls = f"{tech_state} blink" if crisis_now or tech_state == "mood-alert" else tech_state

    cards = [
        ("Počasí", "☀", weather_state, event["weather"]),
        ("Spotřeba", "⚡", demand_state, event["demand"]),
        ("Technika", "🛠", tech_cls, event["tech"]),
        ("Trh", "💱", market_state, event["market"]),
    ]

    rows: list[str] = ['<div class="mood-grid">']
    for title, icon, cls, text in cards:
        rows.append(
            f'<div class="mood-card {html.escape(cls)}">'
            f'<div class="mood-head"><span>{html.escape(icon)}</span>{html.escape(title)}</div>'
            f'<div class="mood-text">{html.escape(text)}</div>'
            '</div>'
        )
    rows.append("</div>")
    return "".join(rows)


def build_operation_map_impacts(selected_cards: list[str], event: EventData) -> dict[str, float]:
    impacts = {"Výroba": 0.0, "Přenos": 0.0, "Spotřeba": 0.0, "Zásoby": 0.0}

    for card_id in selected_cards:
        if card_id == "gas_surge":
            impacts["Výroba"] += 2.4
            impacts["Přenos"] += 0.6
        elif card_id == "import_shield":
            impacts["Přenos"] += 2.3
        elif card_id == "demand_response":
            impacts["Spotřeba"] -= 2.4
            impacts["Přenos"] += 0.4
        elif card_id == "battery_push":
            impacts["Zásoby"] += 2.2
            impacts["Výroba"] += 0.5
        elif card_id == "hydro_ramp":
            impacts["Zásoby"] += 1.7
            impacts["Výroba"] += 1.2
        elif card_id == "coal_commit":
            impacts["Výroba"] += 2.0
            impacts["Spotřeba"] += 0.3
        elif card_id == "public_alert":
            impacts["Přenos"] += 0.3

    if event["krize"]:
        impacts["Přenos"] -= 0.9

    for key in impacts:
        impacts[key] = float(clamp(impacts[key], -3.0, 3.0))
    return impacts


def render_operation_map(impacts: dict[str, float], flash: bool) -> str:
    rows = [f'<div class="op-map{" flash" if flash else ""}">', '<div class="op-map-title">Operační mapa dopadu voleb</div>']
    order = [("Výroba", "🏭"), ("Přenos", "🔌"), ("Spotřeba", "🏙"), ("Zásoby", "🔋")]

    for name, icon in order:
        val = float(impacts.get(name, 0.0))
        strength = abs(val)
        width = int(clamp(16 + strength * 26, 16, 94))
        if strength < 0.25:
            cls = "op-neu"
            txt = "~"
        elif val > 0:
            cls = "op-pos"
            txt = f"+{val:.1f}"
        else:
            cls = "op-neg"
            txt = f"{val:.1f}"

        rows.append(
            '<div class="op-row">'
            f'<div class="op-label">{html.escape(icon)} {html.escape(name)}</div>'
            '<div class="op-track">'
            f'<div class="op-fill {cls}" style="width:{width}%"></div>'
            '</div>'
            f'<div class="op-val">{html.escape(txt)}</div>'
            '</div>'
        )

    rows.append('</div>')
    return ''.join(rows)


def get_dynamic_action_cards(event: EventData, last: pd.Series | None, trust: float, stress: float) -> list[ActionUiCard]:
    cards: list[ActionUiCard] = []
    balance_now = float(last["bilance_site"]) if last is not None else 0.0
    price_now = float(last["okamzita_cena"]) if last is not None else 95.0
    pve_cap = float(event["params"].get("max_vykon_pve", 1170.0))

    for card in ACTION_CARDS:
        card_id = str(card["id"])
        enabled = True
        hint = ""
        priority = 0

        if balance_now < -180 and card_id in {"gas_surge", "import_shield", "battery_push", "hydro_ramp"}:
            priority += 3
            hint = "Priorita: síť je v deficitu"

        if price_now > 125 and card_id in {"demand_response", "coal_commit"}:
            priority += 2
            hint = "Priorita: cena je vysoká"

        if trust < 45 and card_id == "public_alert":
            priority += 2
            hint = "Priorita: důvěra je nízká"

        if stress > 75 and card_id in {"public_alert", "import_shield"}:
            priority += 1
            hint = "Priorita: stres je vysoký"

        if card_id == "hydro_ramp" and ("Závada PVE" in event["tech"] or pve_cap < 500.0):
            enabled = False
            hint = "Dočasně nedostupné: PVE je omezené"

        cards.append(
            {
                "id": card_id,
                "label": str(card["label"]),
                "cost": int(card["cost"]),
                "popis": str(card["popis"]),
                "enabled": enabled,
                "hint": hint,
                "priority": priority,
            }
        )

    cards.sort(key=lambda x: (x["enabled"], x["priority"]), reverse=True)
    return cards


def generate_agent_events(
    seed: int,
    step_df: pd.DataFrame,
    defaults: dict[str, float],
) -> dict[int, EventData]:
    rng = np.random.default_rng(seed + 999)
    events: dict[int, EventData] = {}

    for _, row in step_df.iterrows():
        step_id = int(row["krok"])

        wind_mult = float(rng.uniform(0.45, 1.40))
        solar_mult = float(rng.uniform(0.40, 1.30))
        demand_shift = float(rng.normal(0.0, 420.0))
        market_mult = float(rng.uniform(0.45, 1.35))

        params: dict[str, float] = {
            "max_kapacita_vetrne": max(80.0, defaults["max_kapacita_vetrne"] * wind_mult),
            "max_kapacita_fve": max(1000.0, defaults["max_kapacita_fve"] * solar_mult),
            "init_poptavka": max(3600.0, defaults["init_poptavka"] + demand_shift),
            "max_prenosova_kapacita": max(700.0, defaults["max_prenosova_kapacita"] * market_mult),
        }

        weather_text = "Vítr i FVE jsou v normálu."
        if wind_mult < 0.70 and solar_mult < 0.70:
            weather_text = "Počasí je velmi nepříznivé: slabý vítr i slabá FVE."
        elif wind_mult > 1.20 or solar_mult > 1.15:
            weather_text = "Počasí je příznivé: OZE mohou dodat nadprůměrný výkon."

        demand_text = "Spotřeba je blízko očekávání."
        if demand_shift > 250:
            demand_text = "Spotřeba roste nad plán."
        elif demand_shift < -250:
            demand_text = "Spotřeba je nezvykle nízká."

        market_text = "Přeshraniční toky jsou standardní."
        if market_mult < 0.75:
            market_text = "Trh je napjatý, import/export je omezený."
        elif market_mult > 1.15:
            market_text = "Na trhu je dobrá likvidita, přeshraniční toky jsou vysoké."

        tech_text = "Technika zatím bez mimořádné události."
        trust_delta = 0.0
        stress_delta = 0.0
        crisis_name = ""

        tech_roll = float(rng.random())
        if tech_roll < 0.14:
            tech_text = "Výpadek části uhlí: dostupný výkon uhlí je omezen." 
            params["max_kapacita_uhli"] = 3200.0
            crisis_name = "Výpadek uhelného bloku"
            stress_delta += 8.0
        elif tech_roll < 0.22:
            tech_text = "Závada PVE: výrazně klesla rychlost regulačních zásahů." 
            params["max_vykon_pve"] = 350.0
            crisis_name = "Závada PVE"
            stress_delta += 6.0
        elif tech_roll > 0.94:
            tech_text = "Nouzová podpora obnovena: technický tým zrychlil rampování plynu." 
            params["doba_nabehu_plynu"] = 0.12
            trust_delta += 2.0

        if wind_mult < 0.60 and solar_mult < 0.55 and not crisis_name:
            crisis_name = "Kombinovaný výpadek OZE"
            stress_delta += 5.0

        if market_mult < 0.65 and not crisis_name:
            crisis_name = "Přeshraniční omezení"
            trust_delta -= 2.0
            stress_delta += 4.0

        events[step_id] = {
            "weather": weather_text,
            "demand": demand_text,
            "market": market_text,
            "tech": tech_text,
            "krize": crisis_name,
            "params": params,
            "trust_delta": trust_delta,
            "stress_delta": stress_delta,
        }

    # Zaručíme alespoň jednu výraznou krizi za směnu.
    if not any(bool(events[s]["krize"]) for s in events):
        forced_step = int(rng.integers(3, STEP_COUNT + 1))
        events[forced_step]["krize"] = "Náhlé bezvětří"
        events[forced_step]["tech"] = "Náhlé bezvětří: větrné parky hlásí minimální výkon."
        events[forced_step]["params"]["max_kapacita_vetrne"] = 100.0
        events[forced_step]["stress_delta"] = float(events[forced_step]["stress_delta"] + 6.0)

    return events


def build_overrides(
    step_df: pd.DataFrame,
    defaults: dict[str, float],
    decisions: dict[int, list[str]],
    events_by_step: dict[int, EventData],
    upto_step: int,
    intensity_by_step: dict[int, float] | None = None,
) -> list[dict[str, object]]:
    overrides: list[dict[str, object]] = []
    n_steps = len(step_df)

    for _, row in step_df.iterrows():
        step_id = int(row["krok"])
        if step_id > upto_step:
            break

        merged: dict[str, float] = {}

        event_data = events_by_step.get(step_id)
        if event_data:
            for key, value in event_data["params"].items():
                merged[str(key)] = float(value)

        for card_id in decisions.get(step_id, []):
            card = get_action(card_id)
            params_raw = card.get("params", {})
            if isinstance(params_raw, dict):
                intensity = float(intensity_by_step.get(step_id, 1.0)) if intensity_by_step else 1.0
                for key, value in params_raw.items():
                    key_str = str(key)
                    val = float(value)
                    base = float(defaults.get(key_str, val))
                    merged[key_str] = base + (val - base) * intensity

        if not merged:
            continue

        end = float(row["do_h"])
        if step_id == n_steps:
            end += 1e-9

        overrides.append(
            {
                "start": float(row["od_h"]),
                "end": end,
                "params": merged,
            }
        )

    return overrides


def run_engine(
    model,
    defaults: dict[str, float],
    overrides: list[dict[str, object]],
    final_time: float,
    seed_obl: int,
    seed_vitr: int,
    seed_sum: int,
) -> pd.DataFrame:
    return model.simulate_sfd_energetika(
        initial_time=START_HOUR,
        final_time=final_time,
        dt=DT,
        model_params=dict(defaults),
        param_overrides=overrides,
        seed_oblacnost=seed_obl,
        seed_vitr=seed_vitr,
        seed_sum=seed_sum,
    )


def segment_metrics(df: pd.DataFrame, start_h: float, end_h: float, dt: float) -> dict[str, float]:
    seg = df[(df["time"] >= start_h) & (df["time"] <= end_h)]
    if seg.empty:
        seg = df.iloc[[-1]]

    blackout_h = float((seg["riziko_blackoutu"] > 0.5).sum() * dt)
    deficit_mwh = float((-seg["bilance_site"].clip(upper=0.0)).sum() * dt)
    worst_balance = float(seg["bilance_site"].min())
    avg_price = float(seg["okamzita_cena"].mean())

    variable_cost = float(
        (
            seg["aktualni_vyroba_uhli"] * 40.0
            + seg["aktualni_vyroba_plynu"] * 95.0
            + seg["import"] * 130.0
            - seg["export"] * 15.0
        ).sum()
        * dt
    )

    co2_proxy_t = float((seg["aktualni_vyroba_uhli"] * 0.90 + seg["aktualni_vyroba_plynu"] * 0.45).sum() * dt)

    return {
        "blackout_h": blackout_h,
        "deficit_mwh": deficit_mwh,
        "worst_balance": worst_balance,
        "avg_price": avg_price,
        "variable_cost": variable_cost,
        "co2_proxy_t": co2_proxy_t,
    }


def compute_action_points(trust: float, stress: float) -> int:
    points = 3
    if stress > 75:
        points -= 1
    if trust > 85:
        points += 1
    return int(clamp(points, 2, 4))


def evaluate_action_impacts(
    model,
    defaults: dict[str, float],
    step_df: pd.DataFrame,
    decisions: dict[int, list[str]],
    events_by_step: dict[int, EventData],
    step_id: int,
    seeds: tuple[int, int, int],
) -> pd.DataFrame:
    row = step_df.loc[step_df["krok"] == step_id].iloc[0]
    horizon_end = float(row["do_h"])

    preview_rows: list[dict[str, object]] = []

    candidates: list[tuple[str, list[str]]] = [("Bez zásahu", [])]
    for card in ACTION_CARDS:
        candidates.append((str(card["label"]), [str(card["id"])]))

    for label, candidate_actions in candidates:
        candidate_decisions = {k: list(v) for k, v in decisions.items()}
        candidate_decisions[step_id] = candidate_actions

        overrides = build_overrides(step_df, defaults, candidate_decisions, events_by_step, upto_step=step_id)
        sim = run_engine(
            model,
            defaults,
            overrides,
            final_time=horizon_end,
            seed_obl=seeds[0],
            seed_vitr=seeds[1],
            seed_sum=seeds[2],
        )
        metrics = segment_metrics(sim, float(row["od_h"]), horizon_end, DT)

        preview_rows.append(
            {
                "volba": label,
                "nejhorší bilance [MW]": round(metrics["worst_balance"], 1),
                "průměrná cena [EUR/MWh]": round(metrics["avg_price"], 1),
                "riziko blackoutu [h]": round(metrics["blackout_h"], 2),
                "náklady kroku [EUR]": round(metrics["variable_cost"], 0),
                "odhad skóre [0-100]": round(estimate_step_score(metrics), 1),
            }
        )

    return pd.DataFrame(preview_rows)


def apply_step_state_update(
    trust: float,
    stress: float,
    event: EventData,
    selected_cards: list[str],
    metrics: dict[str, float],
    action_intensity: float = 1.0,
) -> tuple[float, float, str]:
    trust_new = trust
    stress_new = stress

    trust_new += event["trust_delta"]
    stress_new += event["stress_delta"]

    for card_id in selected_cards:
        card = get_action(card_id)
        trust_new += card["trust_delta"] * action_intensity
        stress_new += card["stress_delta"] * action_intensity

    if metrics["blackout_h"] > 0:
        trust_new -= 14.0
        stress_new += 12.0
    else:
        trust_new += 2.5

    trust_new -= clamp(metrics["avg_price"] - 80.0, 0.0, 60.0) / 10.0
    stress_new += clamp(-metrics["worst_balance"] / 140.0, 0.0, 20.0)
    trust_new -= clamp(metrics["deficit_mwh"] / 180.0, 0.0, 12.0)

    trust_new = clamp(trust_new, 0.0, 100.0)
    stress_new = clamp(stress_new, 0.0, 100.0)

    if metrics["blackout_h"] > 0:
        feedback = "Krok dopadl kriticky: síť šla do blackoutu, důvěra veřejnosti výrazně klesla."
    elif metrics["worst_balance"] < -250:
        feedback = "Síť zůstala pod tlakem. Deficit se držel vysoký a roste technický stres."
    elif metrics["avg_price"] > 130:
        feedback = "Stabilitu se podařilo držet, ale za cenu velmi drahého provozu."
    else:
        feedback = "Solidní krok: bilance se držela pod kontrolou bez výrazného negativního efektu."

    return trust_new, stress_new, feedback


def init_new_game(seed_steps: int, seed_obl: int, seed_vitr: int, seed_sum: int, defaults: dict[str, float]) -> None:
    durations = generate_step_durations(seed_steps, n_steps=STEP_COUNT)
    step_df = build_step_table(durations, start_hour=START_HOUR)
    events = generate_agent_events(seed_steps, step_df, defaults)

    st.session_state["game_started"] = True
    st.session_state["step_df"] = step_df.to_dict("records")
    st.session_state["events"] = events
    st.session_state["current_step"] = 1
    st.session_state["decisions"] = {}
    st.session_state["history"] = []
    st.session_state["trust"] = 70.0
    st.session_state["stress"] = 30.0
    st.session_state["last_feedback"] = ""
    st.session_state["seed_steps"] = seed_steps
    st.session_state["seed_obl"] = seed_obl
    st.session_state["seed_vitr"] = seed_vitr
    st.session_state["seed_sum"] = seed_sum
    st.session_state["step_intensity"] = {}
    st.session_state["pending_round_summary"] = None
    st.session_state["pending_next_step"] = None
    st.session_state["scroll_to_top_once"] = False
    st.session_state["map_flash_until"] = 0.0


model = get_model_module()
defaults = model.get_default_params()

st.title("Interaktivní trenažér dispečera")
st.caption(
    f"Jsi dispečer přenosové soustavy v ČR. Během 24 hodin uděláš {STEP_COUNT} rozhodnutí. "
    "V každém kroku působí současně agent počasí, spotřeby, techniky a trhu."
)

st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Cíl dne: předat síť stabilní bez blackoutu a se skóre alespoň 75</div>
            <p class="hero-sub">Hlídáš 4 věci: bilanci, cenu, důvěru veřejnosti a technický stres. Každý krok má reálné trade-offy.</p>
        </div>
        """,
        unsafe_allow_html=True,
)

if st.session_state.get("scroll_to_top_once", False):
    components.html(
        """
        <script>
        const main = window.parent.document.querySelector('section.main');
        if (main) {
            main.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        }
        </script>
        """,
        height=0,
    )
    st.session_state["scroll_to_top_once"] = False

with st.sidebar:
    st.header("Nastavení")
    with st.expander("Pokročilé: seedy scénáře", expanded=False):
        seed_steps = st.number_input("Seed kroků", min_value=0, max_value=9999, value=2026, step=1)
        seed_obl = st.number_input("Seed oblačnosti", min_value=0, max_value=9999, value=11, step=1)
        seed_vitr = st.number_input("Seed větru", min_value=0, max_value=9999, value=2, step=1)
        seed_sum = st.number_input("Seed šumu", min_value=0, max_value=9999, value=11, step=1)

    if st.button("Začít novou směnu", width="stretch", type="primary"):
        init_new_game(int(seed_steps), int(seed_obl), int(seed_vitr), int(seed_sum), defaults)
        st.rerun()

    if st.session_state.get("game_started", False):
        if st.button("Restartovat", width="stretch"):
            init_new_game(int(seed_steps), int(seed_obl), int(seed_vitr), int(seed_sum), defaults)
            st.rerun()

if not st.session_state.get("game_started", False):
    st.markdown("## Jak vyhrát směnu")
    g1, g2, g3 = st.columns(3)
    g1.info("Bez blackoutu a bez dlouhého deficitu")
    g2.info("Rozumná cena provozu")
    g3.info("Důvěra veřejnosti nad 60")

    with st.expander("Jak funguje skóre", expanded=False):
        st.markdown("- Spolehlivost: penalizuje blackout a deficit.")
        st.markdown("- Cena: penalizuje drahé zásahy.")
        st.markdown("- Udržitelnost: penalizuje emisní mix.")
        st.markdown("- Důvěra: reaguje na dopady rozhodnutí.")

    st.caption("Volitelně můžeš nejdřív nastavit seedy v levém panelu (Pokročilé).")
    if st.button("Začít novou směnu", type="primary"):
        init_new_game(int(seed_steps), int(seed_obl), int(seed_vitr), int(seed_sum), defaults)
        st.rerun()
    st.stop()

step_df = pd.DataFrame(st.session_state["step_df"])
events_by_step = cast(dict[int, EventData], st.session_state["events"])
current_step = int(st.session_state["current_step"])
decisions: dict[int, list[str]] = dict(st.session_state["decisions"])
history: list[dict[str, object]] = list(st.session_state["history"])
trust = float(st.session_state["trust"])
stress = float(st.session_state["stress"])
step_intensity_map = cast(dict[int, float], st.session_state.get("step_intensity", {}))
event_for_actions: EventData | None = events_by_step.get(current_step)

if st.session_state.get("pending_round_summary"):
    summary = cast(dict[str, object], st.session_state["pending_round_summary"])
    st.markdown("### Kolo uzavřeno")
    with st.container(border=True):
        st.success(str(summary.get("headline", "Kolo bylo vyhodnoceno")))
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Čas", str(summary.get("time_block", "-")))
        k2.metric("Cena", str(summary.get("avg_price", "-")))
        k3.metric("Nejhorší bilance", str(summary.get("worst_balance", "-")))
        k4.metric("Skóre kroku", str(summary.get("step_score", "-")))

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Δ skóre", str(summary.get("delta_score", "-")))
        d2.metric("Δ důvěra", str(summary.get("delta_trust", "-")))
        d3.metric("Δ stres", str(summary.get("delta_stress", "-")))
        d4.metric("Δ cena vs bez zásahu", str(summary.get("delta_price", "-")))

        st.info(str(summary.get("feedback", "")))
        st.caption(str(summary.get("prediction_note", "")))
        if st.button("Pokračovat na další krok", type="primary", width="stretch"):
            st.session_state["pending_round_summary"] = None
            st.session_state["current_step"] = int(st.session_state.get("pending_next_step", current_step))
            st.session_state["pending_next_step"] = None
            st.session_state["scroll_to_top_once"] = True
            st.rerun()
    st.stop()

left_col, right_col = st.columns([3, 7], gap="large")
current_intensity_factor = float(step_intensity_map.get(current_step, 1.0))
selected_cards: list[str] = []
total_cost = 0
confirm_clicked = False
confirm_disabled = False
action_points = compute_action_points(trust, stress)
dynamic_cards: list[ActionUiCard] = []
balance_now_for_cards = 0.0
price_now_for_cards = 95.0
pve_limited_now = False

if current_step <= STEP_COUNT and event_for_actions is not None:
    row_for_actions = step_df.iloc[current_step - 1]
    prev_overrides_for_actions = build_overrides(
        step_df,
        defaults,
        decisions,
        events_by_step,
        upto_step=current_step - 1,
        intensity_by_step=step_intensity_map,
    )
    status_end_for_actions = max(START_HOUR + DT, float(row_for_actions["od_h"]))
    status_df_for_actions = run_engine(
        model,
        defaults,
        prev_overrides_for_actions,
        final_time=status_end_for_actions,
        seed_obl=int(st.session_state["seed_obl"]),
        seed_vitr=int(st.session_state["seed_vitr"]),
        seed_sum=int(st.session_state["seed_sum"]),
    )
    last_for_actions = status_df_for_actions.iloc[-1]
    dynamic_cards = get_dynamic_action_cards(event_for_actions, last_for_actions, trust, stress)

    intensity_default = int(round(step_intensity_map.get(current_step, 1.0) * 100.0))
    intensity_pct = int(st.session_state.get(f"intensity_{current_step}", intensity_default))
    current_intensity_factor = float(intensity_pct) / 100.0

    pve_limited_now = bool(
        "Závada PVE" in str(event_for_actions.get("tech", ""))
        or float(event_for_actions.get("params", {}).get("max_vykon_pve", 1170.0)) < 500.0
    )
    balance_now_for_cards = float(last_for_actions["bilance_site"])
    price_now_for_cards = float(last_for_actions["okamzita_cena"])

    for card in dynamic_cards:
        key = f"step_{current_step}_card_{card['id']}"
        if not card["enabled"]:
            st.session_state[key] = False
        if bool(st.session_state.get(key, False)):
            selected_cards.append(str(card["id"]))
            total_cost += int(card["cost"])

with left_col:
    st.subheader("Směna")
    progress = min(current_step - 1, STEP_COUNT) / STEP_COUNT
    st.progress(progress)
    st.caption(f"Rozhodnuto {min(current_step - 1, STEP_COUNT)}/{STEP_COUNT} kroků")

    current_live_score = float(clamp(0.68 * trust + 0.32 * (100.0 - stress), 0.0, 100.0))
    render_kpi_row(
        [
            (
                "Důvěra veřejnosti",
                f"{trust:.0f} / 100",
                "Vyšší je lepší. Roste při stabilním provozu bez blackoutu, klesá při drahém provozu a velkých deficitech.",
            ),
            (
                "Technický stres",
                f"{stress:.0f} / 100",
                "Nižší je lepší. Roste při krizích a nestabilní bilanci, klesá při klidném průběhu směny.",
            ),
            (
                "Průběžné skóre",
                f"{current_live_score:.0f}",
                "Orientační mix důvěry, stresu, bilance a ceny. Cíl je držet skóre co nejvýš.",
            ),
        ]
    )

    st.caption(f"Hodnost: {score_band(current_live_score)}")
    st.caption("Tip: Technický stres chceš držet co nejníž.")

    if current_step <= STEP_COUNT and event_for_actions is not None:
        st.markdown(f"### Krok {current_step}/{STEP_COUNT} | {EVENTS[current_step - 1]['titulek']}")
        st.caption(f"Časový blok: {step_df.iloc[current_step - 1]['cas']}")
        st.write(EVENTS[current_step - 1]["text"])
        if event_for_actions["krize"]:
            st.error(f"Krize: {event_for_actions['krize']}")

        st.markdown("### Agentní briefing")
        st.markdown(render_mood_panels(event_for_actions), unsafe_allow_html=True)

preview_intensity_map = dict(step_intensity_map)
if current_step <= STEP_COUNT:
    preview_intensity_map[current_step] = current_intensity_factor

if current_step <= STEP_COUNT:
    row = step_df.iloc[current_step - 1]
    event = events_by_step[current_step]

    prev_overrides = build_overrides(
        step_df,
        defaults,
        decisions,
        events_by_step,
        upto_step=current_step - 1,
        intensity_by_step=step_intensity_map,
    )
    status_end = max(START_HOUR + DT, float(row["od_h"]))

    status_df = run_engine(
        model,
        defaults,
        prev_overrides,
        final_time=status_end,
        seed_obl=int(st.session_state["seed_obl"]),
        seed_vitr=int(st.session_state["seed_vitr"]),
        seed_sum=int(st.session_state["seed_sum"]),
    )

    last = status_df.iloc[-1]
    action_points = compute_action_points(trust, stress)

    selected_decisions = {k: list(v) for k, v in decisions.items()}
    selected_decisions[current_step] = list(selected_cards)
    selected_overrides = build_overrides(
        step_df,
        defaults,
        selected_decisions,
        events_by_step,
        upto_step=current_step,
        intensity_by_step=preview_intensity_map,
    )

    no_action_decisions = {k: list(v) for k, v in decisions.items()}
    no_action_decisions[current_step] = []
    no_action_overrides = build_overrides(
        step_df,
        defaults,
        no_action_decisions,
        events_by_step,
        upto_step=current_step,
        intensity_by_step=step_intensity_map,
    )

    sim_selected = run_engine(
        model,
        defaults,
        selected_overrides,
        final_time=START_HOUR + 24.0,
        seed_obl=int(st.session_state["seed_obl"]),
        seed_vitr=int(st.session_state["seed_vitr"]),
        seed_sum=int(st.session_state["seed_sum"]),
    )
    sim_no_action = run_engine(
        model,
        defaults,
        no_action_overrides,
        final_time=START_HOUR + 24.0,
        seed_obl=int(st.session_state["seed_obl"]),
        seed_vitr=int(st.session_state["seed_vitr"]),
        seed_sum=int(st.session_state["seed_sum"]),
    )

    scenario_opt_map = dict(preview_intensity_map)
    scenario_stress_map = dict(preview_intensity_map)
    scenario_opt_map[current_step] = clamp(current_intensity_factor * 1.2, 0.5, 2.5)
    scenario_stress_map[current_step] = clamp(current_intensity_factor * 0.75, 0.5, 2.5)

    selected_overrides_opt = build_overrides(
        step_df,
        defaults,
        selected_decisions,
        events_by_step,
        upto_step=current_step,
        intensity_by_step=scenario_opt_map,
    )
    selected_overrides_stress = build_overrides(
        step_df,
        defaults,
        selected_decisions,
        events_by_step,
        upto_step=current_step,
        intensity_by_step=scenario_stress_map,
    )

    sim_selected_opt = run_engine(
        model,
        defaults,
        selected_overrides_opt,
        final_time=START_HOUR + 24.0,
        seed_obl=int(st.session_state["seed_obl"] + 17),
        seed_vitr=int(st.session_state["seed_vitr"] + 23),
        seed_sum=int(st.session_state["seed_sum"] + 31),
    )
    sim_selected_stress = run_engine(
        model,
        defaults,
        selected_overrides_stress,
        final_time=START_HOUR + 24.0,
        seed_obl=int(st.session_state["seed_obl"] + 101),
        seed_vitr=int(st.session_state["seed_vitr"] + 137),
        seed_sum=int(st.session_state["seed_sum"] + 149),
    )

    for frame in (status_df, sim_selected, sim_no_action, sim_selected_opt, sim_selected_stress):
        frame["pve_netto"] = frame["turbinovani_pve"] - frame["cerpani_pve"]
        frame["baterie_pct"] = np.clip(frame["energie_v_bateriich"] / max(defaults["kapacita_baterie"], 1.0) * 100.0, 0.0, 100.0)
        frame["nadrz_pct"] = np.clip(frame["voda_v_horni_nadrzi"] / max(defaults["kapacita_horni_nadrze"], 1.0) * 100.0, 0.0, 100.0)

    with right_col:
        st.subheader("Grafy")

        render_kpi_row(
            [
                ("Bilance teď [MW]", f"{last['bilance_site']:.1f}", ""),
                ("Cena teď [EUR/MWh]", f"{last['okamzita_cena']:.1f}", ""),
                ("Plyn teď [MW]", f"{last['aktualni_vyroba_plynu']:.1f}", ""),
                ("AP pro tento krok", f"{action_points}", ""),
            ]
        )

        live_score = estimate_live_score(
            trust,
            stress,
            float(last["bilance_site"]),
            float(last["okamzita_cena"]),
        )
        st.progress(float(live_score / 100.0))
        st.caption(f"Aktuální herní skóre: {live_score:.0f}/100 | {score_band(live_score)}")

        with st.expander("Co znamenají metriky", expanded=False):
            st.markdown("- Bilance: pod 0 znamená deficit výkonu.")
            st.markdown("- Cena: vyšší cena obvykle znamená dražší zásahy.")
            st.markdown("- AP: kolik akcí si můžeš v tomto kroku dovolit.")

        graph_menu = st.radio(
            "Zobrazení grafu",
            ["Bilance", "Výroba zdrojů", "Cena + predikce", "Mix a zásoby"],
            horizontal=True,
            label_visibility="collapsed",
        )

        now_h = float(row["od_h"])
        pred_sel = sim_selected[sim_selected["time"] >= now_h]
        pred_none = sim_no_action[sim_no_action["time"] >= now_h]
        pred_opt = sim_selected_opt[sim_selected_opt["time"] >= now_h]
        pred_stress = sim_selected_stress[sim_selected_stress["time"] >= now_h]

        if graph_menu == "Bilance":
            fig_balance = go.Figure()
            band_balance_low = np.minimum(pred_opt["bilance_site"].to_numpy(), pred_stress["bilance_site"].to_numpy())
            band_balance_high = np.maximum(pred_opt["bilance_site"].to_numpy(), pred_stress["bilance_site"].to_numpy())
            fig_balance.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=band_balance_high,
                    mode="lines",
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig_balance.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=band_balance_low,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(245, 158, 11, 0.20)",
                    name="Rozptyl scénářů",
                )
            )
            fig_balance.add_trace(
                go.Scatter(
                    x=status_df["time"],
                    y=status_df["bilance_site"],
                    mode="lines",
                    name="Historie bilance",
                    line=dict(width=2, color="#22d3ee"),
                )
            )
            fig_balance.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=pred_sel["bilance_site"],
                    mode="lines",
                    name="Predikce (dle výběru)",
                    line=dict(width=2, dash="dash", color="#f59e0b"),
                )
            )
            fig_balance.add_trace(
                go.Scatter(
                    x=pred_none["time"],
                    y=pred_none["bilance_site"],
                    mode="lines",
                    name="Predikce (bez zásahu)",
                    line=dict(width=2, dash="dot", color="#a3e635"),
                )
            )
            fig_balance.add_hline(y=0, line_dash="dot")
            fig_balance.add_hline(y=-500, line_dash="dot", line_color="red")
            fig_balance.add_vline(x=now_h, line_dash="dash", line_color="#94a3b8")
            fig_balance.update_layout(
                title="Bilance sítě: historie + dvě predikce",
                xaxis_title="Čas [h]",
                yaxis_title="MW",
                template="plotly_dark",
                height=360,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_balance, width="stretch")

        elif graph_menu == "Výroba zdrojů":
            fig_sources = go.Figure()
            total_low = np.minimum(pred_opt["celkova_vyroba"].to_numpy(), pred_stress["celkova_vyroba"].to_numpy())
            total_high = np.maximum(pred_opt["celkova_vyroba"].to_numpy(), pred_stress["celkova_vyroba"].to_numpy())
            fig_sources.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=total_high,
                    mode="lines",
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig_sources.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=total_low,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(125, 211, 252, 0.12)",
                    name="Rozptyl celkové výroby",
                )
            )
            sources = [
                ("aktualni_vyroba_uhli", "Uhlí", "#f97316"),
                ("vyroba_jadra", "Jádro", "#a78bfa"),
                ("aktualni_vyroba_plynu", "Plyn", "#22c55e"),
                ("vyroba_fve", "FVE", "#facc15"),
                ("vyroba_vetrne_energie", "Vítr", "#38bdf8"),
                ("pve_netto", "PVE netto", "#14b8a6"),
                ("import", "Import", "#e879f9"),
            ]
            for col_name, label, color in sources:
                fig_sources.add_trace(
                    go.Scatter(
                        x=status_df["time"],
                        y=status_df[col_name],
                        mode="lines",
                        name=f"{label} historie",
                        line=dict(width=1.8, color=color),
                    )
                )
                fig_sources.add_trace(
                    go.Scatter(
                        x=pred_sel["time"],
                        y=pred_sel[col_name],
                        mode="lines",
                        name=f"{label} predikce",
                        line=dict(width=2.0, dash="dash", color=color),
                    )
                )
            fig_sources.add_vline(x=now_h, line_dash="dash", line_color="#94a3b8")
            fig_sources.update_layout(
                title="Výroba zdrojů v čase (včetně PVE) + predikce dle volby",
                xaxis_title="Čas [h]",
                yaxis_title="MW",
                template="plotly_dark",
                height=420,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_sources, width="stretch")

        elif graph_menu == "Cena + predikce":
            fig_price = go.Figure()
            band_price_low = np.minimum(pred_opt["okamzita_cena"].to_numpy(), pred_stress["okamzita_cena"].to_numpy())
            band_price_high = np.maximum(pred_opt["okamzita_cena"].to_numpy(), pred_stress["okamzita_cena"].to_numpy())
            fig_price.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=band_price_high,
                    mode="lines",
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig_price.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=band_price_low,
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(245, 158, 11, 0.20)",
                    name="Rozptyl scénářů",
                )
            )
            fig_price.add_trace(
                go.Scatter(
                    x=status_df["time"],
                    y=status_df["okamzita_cena"],
                    mode="lines",
                    name="Historie ceny",
                    line=dict(width=2, color="#22d3ee"),
                )
            )
            fig_price.add_trace(
                go.Scatter(
                    x=pred_sel["time"],
                    y=pred_sel["okamzita_cena"],
                    mode="lines",
                    name="Predikce ceny (dle výběru)",
                    line=dict(width=2, dash="dash", color="#f59e0b"),
                )
            )
            fig_price.add_trace(
                go.Scatter(
                    x=pred_none["time"],
                    y=pred_none["okamzita_cena"],
                    mode="lines",
                    name="Predikce ceny (bez zásahu)",
                    line=dict(width=2, dash="dot", color="#a3e635"),
                )
            )
            fig_price.add_vline(x=now_h, line_dash="dash", line_color="#94a3b8")
            fig_price.update_layout(
                title="Průběh ceny a srovnání predikcí",
                xaxis_title="Čas [h]",
                yaxis_title="EUR/MWh",
                template="plotly_dark",
                height=360,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_price, width="stretch")

        else:
            source_now = pd.DataFrame(
                {
                    "zdroj": ["Uhlí", "Jádro", "Plyn", "FVE", "Vítr", "PVE turbína", "Import"],
                    "MW": [
                        float(last["aktualni_vyroba_uhli"]),
                        float(last["vyroba_jadra"]),
                        float(last["aktualni_vyroba_plynu"]),
                        float(last["vyroba_fve"]),
                        float(last["vyroba_vetrne_energie"]),
                        float(last["turbinovani_pve"]),
                        float(last["import"]),
                    ],
                }
            )
            source_now = source_now[source_now["MW"] > 1e-6]

            b1, b2 = st.columns(2)
            with b1:
                fig_pie = px.pie(
                    source_now,
                    names="zdroj",
                    values="MW",
                    hole=0.45,
                    template="plotly_dark",
                    title="Okamžitý mix výroby",
                )
                fig_pie.update_layout(height=320, showlegend=True, legend=dict(orientation="h"))
                st.plotly_chart(fig_pie, width="stretch")
            with b2:
                fig_storage = go.Figure()
                fig_storage.add_trace(
                    go.Scatter(
                        x=status_df["time"],
                        y=status_df["baterie_pct"],
                        mode="lines",
                        name="Baterie historie",
                        line=dict(width=2, color="#22c55e"),
                    )
                )
                fig_storage.add_trace(
                    go.Scatter(
                        x=pred_sel["time"],
                        y=pred_sel["baterie_pct"],
                        mode="lines",
                        name="Baterie predikce",
                        line=dict(width=2, dash="dash", color="#22c55e"),
                    )
                )
                fig_storage.add_trace(
                    go.Scatter(
                        x=status_df["time"],
                        y=status_df["nadrz_pct"],
                        mode="lines",
                        name="Nádrž historie",
                        line=dict(width=2, color="#38bdf8"),
                    )
                )
                fig_storage.add_trace(
                    go.Scatter(
                        x=pred_sel["time"],
                        y=pred_sel["nadrz_pct"],
                        mode="lines",
                        name="Nádrž predikce",
                        line=dict(width=2, dash="dash", color="#38bdf8"),
                    )
                )
                bat_low = np.minimum(pred_opt["baterie_pct"].to_numpy(), pred_stress["baterie_pct"].to_numpy())
                bat_high = np.maximum(pred_opt["baterie_pct"].to_numpy(), pred_stress["baterie_pct"].to_numpy())
                fig_storage.add_trace(
                    go.Scatter(
                        x=pred_sel["time"],
                        y=bat_high,
                        mode="lines",
                        line=dict(width=0),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )
                fig_storage.add_trace(
                    go.Scatter(
                        x=pred_sel["time"],
                        y=bat_low,
                        mode="lines",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(34, 197, 94, 0.12)",
                        name="Rozptyl baterie",
                    )
                )
                fig_storage.add_vline(x=now_h, line_dash="dash", line_color="#94a3b8")
                fig_storage.update_layout(
                    title="Zásoby: baterie a horní nádrž [%]",
                    xaxis_title="Čas [h]",
                    yaxis_title="% kapacity",
                    yaxis=dict(range=[0, 100]),
                    template="plotly_dark",
                    height=320,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                )
                st.plotly_chart(fig_storage, width="stretch")

        preview = evaluate_action_impacts(
            model,
            defaults,
            step_df,
            decisions,
            events_by_step,
            step_id=current_step,
            seeds=(
                int(st.session_state["seed_obl"]),
                int(st.session_state["seed_vitr"]),
                int(st.session_state["seed_sum"]),
            ),
        )
        with st.expander("Predikce dopadů (single-akce)", expanded=False):
            preview_sorted = preview.sort_values("odhad skóre [0-100]", ascending=False)
            best_row = preview_sorted.iloc[0]
            st.caption(f"Doporučená single-akce: {best_row['volba']} | odhad skóre {best_row['odhad skóre [0-100]']:.1f}")
            st.dataframe(preview_sorted, width="stretch", hide_index=True)

            if selected_cards:
                selected_metrics = segment_metrics(sim_selected, float(row["od_h"]), float(row["do_h"]), DT)
                optimistic_metrics = segment_metrics(sim_selected_opt, float(row["od_h"]), float(row["do_h"]), DT)
                stress_metrics = segment_metrics(sim_selected_stress, float(row["od_h"]), float(row["do_h"]), DT)
                selected_score = estimate_step_score(selected_metrics)
                st.info(
                    "Predikce aktuální volby | "
                    f"skóre kroku {selected_score:.1f}, "
                    f"nejhorší bilance {selected_metrics['worst_balance']:.1f} MW, "
                    f"cena {selected_metrics['avg_price']:.1f} EUR/MWh"
                )
                scenario_df = pd.DataFrame(
                    [
                        {
                            "scénář": "Stresový",
                            "intenzita": f"{scenario_stress_map[current_step]*100:.0f}%",
                            "skóre": round(estimate_step_score(stress_metrics), 1),
                            "nejhorší bilance [MW]": round(stress_metrics["worst_balance"], 1),
                            "cena [EUR/MWh]": round(stress_metrics["avg_price"], 1),
                        },
                        {
                            "scénář": "Základní",
                            "intenzita": f"{preview_intensity_map[current_step]*100:.0f}%",
                            "skóre": round(estimate_step_score(selected_metrics), 1),
                            "nejhorší bilance [MW]": round(selected_metrics["worst_balance"], 1),
                            "cena [EUR/MWh]": round(selected_metrics["avg_price"], 1),
                        },
                        {
                            "scénář": "Optimistický",
                            "intenzita": f"{scenario_opt_map[current_step]*100:.0f}%",
                            "skóre": round(estimate_step_score(optimistic_metrics), 1),
                            "nejhorší bilance [MW]": round(optimistic_metrics["worst_balance"], 1),
                            "cena [EUR/MWh]": round(optimistic_metrics["avg_price"], 1),
                        },
                    ]
                )
                st.caption("Rozptyl predikce (scénáře) pro aktuální volbu")
                st.dataframe(scenario_df, width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("Vyber akce pro tento krok")
    st.markdown(
        f"""
        <div class="ap-badge">
            <div class="ap-title">Co je AP?</div>
            <div class="ap-value">Akční body (AP) jsou rozpočet zásahů v kroku. Máš {action_points} AP.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    intensity_default = int(round(step_intensity_map.get(current_step, 1.0) * 100.0))
    intensity_pct = st.slider(
        "Intenzita zásahu [%]",
        min_value=50,
        max_value=220,
        value=intensity_default,
        step=5,
        help="Určuje, jak silně se vybrané akce promítnou do parametrů modelu.",
        key=f"intensity_{current_step}",
    )
    current_intensity_factor = float(intensity_pct) / 100.0
    st.caption(f"Aktuální intenzita: {intensity_pct}%")

    selected_cards_runtime: list[str] = []
    total_cost_runtime = 0
    grid_top = st.columns(4)
    grid_bottom = st.columns(4)

    for idx in range(8):
        target_cols = grid_top if idx < 4 else grid_bottom
        with target_cols[idx % 4]:
            if idx < len(dynamic_cards):
                card = dynamic_cards[idx]
                with st.container(border=True):
                    key = f"step_{current_step}_card_{card['id']}"
                    checked = st.checkbox(
                        f"{card['label']} (AP: {card['cost']})",
                        key=key,
                        disabled=not card["enabled"],
                    )
                    st.caption(str(card["popis"]))
                    st.caption(f"Co to znamená: {card_plain_meaning(str(card['id']))}")
                    if card["hint"]:
                        st.caption(str(card["hint"]))

                    if checked:
                        badges = action_effect_badges(
                            str(card["id"]),
                            current_intensity_factor,
                            balance_now_for_cards,
                            price_now_for_cards,
                            pve_limited_now,
                        )
                        preview_lines = action_effect_preview(
                            str(card["id"]),
                            current_intensity_factor,
                            balance_now_for_cards,
                            price_now_for_cards,
                            pve_limited_now,
                        )
                        st.markdown("<hr style='margin:0.35rem 0 0.5rem 0;border-color:rgba(148,163,184,0.28);'>", unsafe_allow_html=True)
                        st.markdown(f"**Co se nejspíš stane při intenzitě {intensity_pct}%**")
                        st.markdown(render_action_effect_badges(badges), unsafe_allow_html=True)
                        for line in preview_lines:
                            st.caption(f"-> {line}")

                        selected_cards_runtime.append(str(card["id"]))
                        total_cost_runtime += int(card["cost"])
            elif idx == 7:
                selected_cards = selected_cards_runtime
                total_cost = total_cost_runtime
                map_impacts = build_operation_map_impacts(selected_cards, event)
                map_flash = time.time() < float(st.session_state.get("map_flash_until", 0.0))
                st.markdown(render_operation_map(map_impacts, map_flash), unsafe_allow_html=True)

                ap_ratio = min(total_cost / max(action_points, 1), 1.0)
                st.progress(ap_ratio, text=f"AP využito: {total_cost}/{action_points}")
                if total_cost > action_points:
                    st.error("Překročil(a) jsi AP. Odeber některou akci.")
                confirm_disabled = total_cost > action_points
                confirm_clicked = st.button("Potvrdit krok", type="primary", disabled=confirm_disabled, width="stretch")
            else:
                st.empty()

    selected_cards = selected_cards_runtime
    total_cost = total_cost_runtime

    st.markdown("---")
    st.subheader("Poslední feedback")
    st.markdown(
        render_day_scene(
            float(row["od_h"]),
            event,
            float(last["bilance_site"]),
            float(last["riziko_blackoutu"]),
        ),
        unsafe_allow_html=True,
    )
    if history:
        st.info(str(st.session_state.get("last_feedback", "")))
    else:
        st.caption("Zatím žádný feedback. Potvrď první krok.")


    if confirm_clicked:
        st.markdown('<div class="pulse-bolt">⚡ Přepočítávám krok... čas běží</div>', unsafe_allow_html=True)
        time.sleep(1.8)
        st.session_state["map_flash_until"] = time.time() + 2.0

        decisions[current_step] = selected_cards
        st.session_state["decisions"] = decisions
        step_intensity_map[current_step] = current_intensity_factor
        st.session_state["step_intensity"] = step_intensity_map

        metrics = segment_metrics(sim_selected, float(row["od_h"]), float(row["do_h"]), DT)
        no_action_metrics = segment_metrics(sim_no_action, float(row["od_h"]), float(row["do_h"]), DT)
        step_score = estimate_step_score(metrics)
        trust_new, stress_new, feedback = apply_step_state_update(
            trust,
            stress,
            event,
            selected_cards,
            metrics,
            action_intensity=current_intensity_factor,
        )

        st.session_state["trust"] = trust_new
        st.session_state["stress"] = stress_new
        st.session_state["last_feedback"] = feedback

        pre_score = estimate_live_score(
            trust,
            stress,
            float(last["bilance_site"]),
            float(last["okamzita_cena"]),
        )
        end_step_df = sim_selected[sim_selected["time"] <= float(row["do_h"])]
        if end_step_df.empty:
            end_step = sim_selected.iloc[-1]
        else:
            end_step = end_step_df.iloc[-1]
        post_score = estimate_live_score(
            trust_new,
            stress_new,
            float(end_step["bilance_site"]),
            float(end_step["okamzita_cena"]),
        )

        history.append(
            {
                "krok": current_step,
                "čas": row["cas"],
                "krize": event["krize"] or "-",
                "akce": ", ".join([get_action(cid)["label"] for cid in selected_cards]) if selected_cards else "Bez zásahu",
                "nejhorší bilance [MW]": round(metrics["worst_balance"], 1),
                "průměrná cena [EUR/MWh]": round(metrics["avg_price"], 1),
                "blackout [h]": round(metrics["blackout_h"], 2),
                "skóre kroku": round(step_score, 1),
                "důvěra po kroku": round(trust_new, 1),
                "stres po kroku": round(stress_new, 1),
            }
        )
        st.session_state["history"] = history

        delta_price = metrics["avg_price"] - no_action_metrics["avg_price"]
        delta_balance = metrics["worst_balance"] - no_action_metrics["worst_balance"]
        prediction_note = (
            f"Srovnání proti bez zásahu | Δcena {delta_price:+.1f} EUR/MWh, "
            f"Δnejhorší bilance {delta_balance:+.1f} MW"
        )
        st.session_state["pending_round_summary"] = {
            "headline": f"{format_clock(float(row['do_h']))}: krok uzavřen",
            "time_block": str(row["cas"]),
            "avg_price": f"{metrics['avg_price']:.1f} EUR/MWh",
            "worst_balance": f"{metrics['worst_balance']:.1f} MW",
            "step_score": f"{step_score:.1f}",
            "delta_score": f"{(post_score - pre_score):+.1f}",
            "delta_trust": f"{(trust_new - trust):+.1f}",
            "delta_stress": f"{(stress_new - stress):+.1f}",
            "delta_price": f"{delta_price:+.1f} EUR/MWh",
            "feedback": feedback,
            "prediction_note": prediction_note,
        }
        st.session_state["pending_next_step"] = current_step + 1
        st.session_state["scroll_to_top_once"] = True
        st.rerun()

else:
    all_overrides = build_overrides(
        step_df,
        defaults,
        decisions,
        events_by_step,
        upto_step=STEP_COUNT,
        intensity_by_step=cast(dict[int, float], st.session_state.get("step_intensity", {})),
    )
    full_df = run_engine(
        model,
        defaults,
        all_overrides,
        final_time=START_HOUR + 24.0,
        seed_obl=int(st.session_state["seed_obl"]),
        seed_vitr=int(st.session_state["seed_vitr"]),
        seed_sum=int(st.session_state["seed_sum"]),
    )

    total_metrics = segment_metrics(full_df, START_HOUR, START_HOUR + 24.0, DT)

    reliability = clamp(100.0 - total_metrics["blackout_h"] * 35.0 - total_metrics["deficit_mwh"] / 35.0, 0.0, 100.0)
    affordability = clamp(100.0 - total_metrics["variable_cost"] / 13000.0, 0.0, 100.0)
    sustainability = clamp(100.0 - total_metrics["co2_proxy_t"] / 55.0, 0.0, 100.0)
    public_score = float(clamp(st.session_state["trust"], 0.0, 100.0))
    avg_price_day = float(full_df["okamzita_cena"].mean())
    total_score = 0.38 * reliability + 0.24 * affordability + 0.18 * sustainability + 0.20 * public_score
    performance_label = score_band(total_score)

    with right_col:
        st.subheader("Konec směny: výsledky")
        if total_score >= 75 and total_metrics["blackout_h"] <= 0.1:
            st.success(f"Mise splněna | {performance_label}")
        else:
            st.warning(f"Mise částečně splněna | {performance_label}")

        render_kpi_row(
            [
                ("Celkové skóre", f"{total_score:.0f} / 100", ""),
                ("Spolehlivost", f"{reliability:.1f}", ""),
                ("Dostupnost ceny", f"{affordability:.1f}", ""),
                ("Udržitelnost", f"{sustainability:.1f}", ""),
            ]
        )
        render_kpi_row(
            [
                ("Důvěra veřejnosti", f"{public_score:.1f}", ""),
                ("Blackout [h]", f"{total_metrics['blackout_h']:.2f}", ""),
                ("Deficit [MWh]", f"{total_metrics['deficit_mwh']:.1f}", ""),
                ("Průměrná cena", f"{avg_price_day:.1f} EUR/MWh", ""),
            ]
        )

        fig_kpi_bg = go.Figure()
        fig_kpi_bg.add_trace(
            go.Scatter(
                x=full_df["time"],
                y=full_df["bilance_site"],
                mode="lines",
                name="Bilance (podklad)",
                line=dict(width=2.1, color="rgba(56, 189, 248, 0.70)"),
                fill="tozeroy",
                fillcolor="rgba(56, 189, 248, 0.10)",
            )
        )
        fig_kpi_bg.add_trace(
            go.Scatter(
                x=full_df["time"],
                y=(full_df["okamzita_cena"] - full_df["okamzita_cena"].mean()) * 8.0,
                mode="lines",
                name="Cena (podklad, škálováno)",
                line=dict(width=1.8, color="rgba(244, 114, 182, 0.55)", dash="dot"),
            )
        )
        fig_kpi_bg.update_layout(
            title="Podkladový trend během dne",
            template="plotly_dark",
            height=220,
            margin=dict(l=20, r=20, t=35, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_kpi_bg, width="stretch")

        fig_balance = go.Figure()
        fig_balance.add_trace(
            go.Scatter(x=full_df["time"], y=full_df["bilance_site"], mode="lines", name="Bilance sítě", line=dict(width=2))
        )
        for boundary in step_df["do_h"][:-1]:
            fig_balance.add_vline(x=float(boundary), line_dash="dot", line_color="#64748b")
        fig_balance.add_hline(y=0, line_dash="dot")
        fig_balance.add_hline(y=-500, line_dash="dot", line_color="red")
        fig_balance.update_layout(
            title="Bilance během celé směny",
            xaxis_title="Čas [h]",
            yaxis_title="MW",
            template="plotly_dark",
            height=340,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        st.plotly_chart(fig_balance, width="stretch")

        radar_df = pd.DataFrame(
            {
                "metrika": ["Spolehlivost", "Dostupnost ceny", "Udržitelnost", "Důvěra"],
                "hodnota": [reliability, affordability, sustainability, public_score],
            }
        )
        fig_radar = px.line_polar(
            radar_df,
            r="hodnota",
            theta="metrika",
            line_close=True,
            range_r=[0, 100],
            template="plotly_dark",
            title="Profil výkonu dispečera",
        )
        fig_radar.update_traces(fill="toself")
        fig_radar.update_layout(height=360, showlegend=True)
        st.plotly_chart(fig_radar, width="stretch")

        history_df = pd.DataFrame(history)
        if not history_df.empty:
            st.subheader("Kroková historie rozhodnutí")
            st.dataframe(history_df, width="stretch", hide_index=True)

        if st.button("Hrát znovu", type="primary"):
            init_new_game(
                int(st.session_state["seed_steps"]),
                int(st.session_state["seed_obl"]),
                int(st.session_state["seed_vitr"]),
                int(st.session_state["seed_sum"]),
                defaults,
            )
            st.rerun()
