"""
Student At-Risk Recovery Planner Dashboard
==========================================
CSAI 350 - Introduction to Artificial Intelligence
Spring 2026

Run with:  streamlit run dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
from collections import Counter

from student_model import (
    State, risk_score, heuristic, is_goal, RISK_THRESHOLD,
    ALL_ACTIONS, ACTION_DESCRIPTIONS,
    load_students_csv, state_from_row, generate_sample_data,
)
from search import a_star_search, greedy_search, uniform_cost_search


# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Recovery Planner - A* Search",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===================== LUCIDE-STYLE SVG ICONS =====================
def _icon(name: str, size: int = 16, color: str = "#6b7280", sw: float = 2) -> str:
    paths = {
        "graduation-cap":      '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
        "upload":              '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
        "zap":                 '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "users":               '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "user":                '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        "play":                '<polygon points="5 3 19 12 5 21 5 3"/>',
        "flask-conical":       '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
        "bar-chart-2":         '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
        "git-compare-arrows":  '<circle cx="5" cy="6" r="3"/><path d="M12 6h5a2 2 0 0 1 2 2v7"/><path d="m15 9 3-3-3-3"/><circle cx="19" cy="18" r="3"/><path d="M12 18H7a2 2 0 0 1-2-2V9"/><path d="m9 15-3 3 3 3"/>',
        "list-checks":         '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
        "activity":            '<path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/>',
        "target":              '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        "route":               '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
        "cpu":                 '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
        "clock":               '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "map-pin":             '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
        "flag":                '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
        "circle-check":        '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
        "circle-x":            '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
        "arrow-up":            '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
        "arrow-down":          '<path d="m19 12-7 7-7-7"/><path d="M12 5v14"/>',
        "database":            '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
        "sliders-horizontal":  '<line x1="21" y1="6" x2="15" y2="6"/><line x1="9" y1="6" x2="3" y2="6"/><circle cx="12" cy="6" r="3"/><line x1="21" y1="18" x2="15" y2="18"/><line x1="9" y1="18" x2="3" y2="18"/><circle cx="12" cy="18" r="3"/>',
        "info":                '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
        "bookmark":            '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
        "scan-line":           '<path d="M22 6C22 4.9 21.1 4 20 4H4C2.9 4 2 4.9 2 6v2h20V6z"/><path d="M2 10h20"/><path d="M2 14h20"/><path d="M2 18h20"/>',
        "book-open":           '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
        "trending-up":         '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
        "battery-charging":    '<path d="M15 7h1a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2"/><path d="M6 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h1"/><path d="m11 7-3 5h4l-3 5"/><line x1="22" y1="11" x2="22" y2="13"/>',
        "calendar":            '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "pen-line":            '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>',
        "alert-triangle":      '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    }
    p = paths.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;flex-shrink:0">'
        f'{p}</svg>'
    )


# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp {
        background-color: #f9fafb !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: #111827 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }
    section[data-testid="stSidebar"] > div { background-color: #ffffff !important; }
    .block-container {
        padding-top: 1.75rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }

    /* ── Sidebar labels ─────────────────────────── */
    .sb-label {
        display: flex; align-items: center; gap: 7px;
        font-size: 0.69rem; font-weight: 600; color: #9ca3af;
        text-transform: uppercase; letter-spacing: 0.09em;
        margin: 18px 0 8px 0;
    }
    .sb-divider { height: 1px; background: #f3f4f6; margin: 14px 0; }

    /* ── Page header ────────────────────────────── */
    .page-header {
        display: flex; align-items: flex-start; gap: 14px;
        padding-bottom: 22px; margin-bottom: 4px;
        border-bottom: 1px solid #e5e7eb;
    }
    .page-header-icon {
        width: 40px; height: 40px; border-radius: 9px;
        background: #eff6ff;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .page-header-text h1 {
        font-size: 1.4rem !important; font-weight: 700 !important;
        color: #111827 !important; margin: 0 0 3px 0 !important;
        letter-spacing: -0.025em; line-height: 1.2;
    }
    .page-header-text p {
        font-size: 0.84rem !important; color: #6b7280 !important;
        margin: 0 !important;
    }

    /* ── Metric card ────────────────────────────── */
    .metric-card {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 15px 18px;
    }
    .metric-label {
        display: flex; align-items: center; gap: 5px;
        font-size: 0.69rem; font-weight: 600; color: #9ca3af;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.5rem; font-weight: 700; line-height: 1;
        font-family: 'JetBrains Mono', monospace; color: #111827;
    }

    /* ── Input section card ─────────────────────── */
    .input-section {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 22px 24px; margin-bottom: 16px;
    }
    .input-section-title {
        display: flex; align-items: center; gap: 8px;
        font-size: 0.8rem; font-weight: 600; color: #374151;
        margin-bottom: 18px; padding-bottom: 12px;
        border-bottom: 1px solid #f3f4f6;
    }

    /* ── Risk preview bar ───────────────────────── */
    .risk-preview {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 18px 22px;
        display: flex; align-items: center; gap: 20px;
        margin-top: 4px;
    }
    .risk-preview-main { flex: 1; }
    .risk-preview-label {
        font-size: 0.7rem; font-weight: 600; color: #9ca3af;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;
    }
    .risk-preview-value {
        font-size: 2rem; font-weight: 700; line-height: 1;
        font-family: 'JetBrains Mono', monospace;
    }
    .risk-preview-bar-wrap {
        background: #f3f4f6; border-radius: 100px;
        height: 5px; margin-top: 10px; overflow: hidden; width: 100%;
    }
    .risk-preview-bar {
        height: 100%; border-radius: 100px;
        transition: width 0.3s ease;
    }
    .risk-preview-meta {
        font-size: 0.75rem; color: #9ca3af; margin-top: 6px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Step card ──────────────────────────────── */
    .step-card {
        display: flex; align-items: flex-start; gap: 11px;
        background: #ffffff; border: 1px solid #e5e7eb;
        border-left: 3px solid #4f46e5; border-radius: 6px;
        padding: 11px 15px; margin: 5px 0;
    }
    .step-num {
        background: #4f46e5; color: #ffffff;
        min-width: 23px; height: 23px; border-radius: 5px;
        font-size: 0.7rem; font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex; align-items: center;
        justify-content: center; flex-shrink: 0; margin-top: 1px;
    }
    .step-body { flex: 1; min-width: 0; }
    .step-action { font-weight: 600; color: #111827; font-size: 0.875rem; }
    .step-detail {
        color: #9ca3af; font-size: 0.74rem; margin-top: 3px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── State box ──────────────────────────────── */
    .state-box {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 18px 20px;
    }
    .state-box-hdr {
        display: flex; align-items: center; gap: 6px;
        font-size: 0.69rem; font-weight: 600; color: #9ca3af;
        text-transform: uppercase; letter-spacing: 0.09em;
        margin-bottom: 12px; padding-bottom: 10px;
        border-bottom: 1px solid #f3f4f6;
    }
    .state-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 7px 0; border-bottom: 1px solid #f9fafb;
    }
    .state-row:last-child { border-bottom: none; }
    .s-label { color: #6b7280; font-size: 0.83rem; }
    .s-val {
        color: #111827; font-weight: 600;
        font-family: 'JetBrains Mono', monospace; font-size: 0.83rem;
    }
    .s-val-right { display: flex; align-items: center; gap: 8px; }

    /* ── Risk badges ────────────────────────────── */
    .badge-high {
        display: inline-flex; align-items: center; gap: 3px;
        background: #fef2f2; color: #dc2626; font-size: 0.67rem;
        font-weight: 600; padding: 2px 7px; border-radius: 100px;
        border: 1px solid #fecaca;
    }
    .badge-low {
        display: inline-flex; align-items: center; gap: 3px;
        background: #f0fdf4; color: #16a34a; font-size: 0.67rem;
        font-weight: 600; padding: 2px 7px; border-radius: 100px;
        border: 1px solid #bbf7d0;
    }

    /* ── Comparison table ───────────────────────── */
    .comp-wrap {
        border: 1px solid #e5e7eb; border-radius: 8px;
        overflow: hidden; margin: 8px 0;
    }
    .comp-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    .comp-table th {
        background: #f9fafb; color: #6b7280; font-weight: 600;
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.07em;
        padding: 11px 16px; text-align: left; border-bottom: 1px solid #e5e7eb;
    }
    .comp-table td {
        padding: 11px 16px; border-bottom: 1px solid #f3f4f6;
        font-family: 'JetBrains Mono', monospace; color: #374151;
    }
    .comp-table tr:last-child td { border-bottom: none; }
    .comp-table tr:hover td { background: #fafafa; }
    .td-name { color: #111827 !important; font-weight: 600; font-family: 'Inter', sans-serif !important; }
    .td-best { color: #16a34a !important; font-weight: 700; }
    .td-goal-y { display: inline-flex; align-items: center; gap: 5px; color: #16a34a; font-weight: 600; font-family: 'Inter', sans-serif !important; }
    .td-goal-n { display: inline-flex; align-items: center; gap: 5px; color: #dc2626; font-weight: 600; font-family: 'Inter', sans-serif !important; }
    .td-muted { color: #9ca3af !important; }

    /* ── What-if cards ──────────────────────────── */
    .wi-card {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 15px 18px; margin: 7px 0;
    }
    .wi-title {
        display: flex; align-items: center; gap: 8px;
        font-weight: 600; color: #374151; font-size: 0.875rem; margin-bottom: 6px;
    }
    .wi-stat {
        display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
        font-family: 'JetBrains Mono', monospace; color: #6b7280; font-size: 0.8rem;
    }
    .wi-stat b { color: #111827; font-weight: 600; }
    .wi-delta-up { display: inline-flex; align-items: center; gap: 3px; color: #dc2626; font-size: 0.75rem; }
    .wi-delta-dn { display: inline-flex; align-items: center; gap: 3px; color: #16a34a; font-size: 0.75rem; }
    .wi-infeasible {
        display: inline-flex; align-items: center; gap: 6px;
        color: #dc2626; font-weight: 600; font-size: 0.875rem;
        font-family: 'Inter', sans-serif;
    }

    /* ── Section header ─────────────────────────── */
    .sec-hdr {
        display: flex; align-items: center; gap: 7px;
        font-size: 0.69rem; font-weight: 600; color: #9ca3af;
        text-transform: uppercase; letter-spacing: 0.09em; margin: 22px 0 12px 0;
    }
    .divider { height: 1px; background: #e5e7eb; margin: 20px 0; }

    /* ── Goal banner ────────────────────────────── */
    .goal-banner {
        display: flex; align-items: center; gap: 10px;
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 8px; padding: 12px 18px; margin-top: 16px;
        font-size: 0.875rem; color: #166534; font-weight: 500;
    }
    .goal-banner strong { color: #15803d; }

    /* ── Empty state ────────────────────────────── */
    .empty-state { text-align: center; padding: 64px 20px; }
    .empty-icon-wrap {
        width: 52px; height: 52px; border-radius: 12px; background: #f3f4f6;
        display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;
    }
    .empty-state h3 { font-size: 1.05rem; font-weight: 600; color: #374151; margin: 0 0 8px 0; }
    .empty-state p { font-size: 0.875rem; color: #9ca3af; max-width: 360px; margin: 0 auto; }

    /* ── Analysis block ─────────────────────────── */
    .analysis-block {
        background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;
        padding: 16px 20px; font-size: 0.875rem; color: #374151; line-height: 1.8;
    }
    .analysis-block p { margin: 0 0 8px 0; }
    .analysis-block p:last-child { margin-bottom: 0; }
    .analysis-block strong { color: #111827; }

    /* ── Slider tweaks ──────────────────────────── */
    [data-testid="stSlider"] label {
        font-size: 0.83rem !important; font-weight: 500 !important;
        color: #374151 !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] {
        font-size: 0.72rem !important; color: #9ca3af !important;
    }

    /* ── Tabs ───────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent; gap: 0;
        border-bottom: 1px solid #e5e7eb; padding: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 0;
        color: #6b7280 !important; padding: 10px 20px;
        font-size: 0.875rem; font-weight: 500;
        border-bottom: 2px solid transparent; margin-bottom: -1px;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #4f46e5 !important;
        border-bottom-color: #4f46e5 !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 22px; }

    /* ── Buttons ────────────────────────────────── */
    .stButton > button {
        background-color: #f3f4f6 !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important; font-size: 0.875rem !important;
        border-radius: 6px !important;
        transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #1e293b !important;
    }
    button[data-testid="stBaseButton-primary"] {
        background-color: #eef2ff !important;
        color: #4338ca !important;
        border: 1px solid #c7d2fe !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #4338ca !important;
        color: #ffffff !important;
        border-color: #4338ca !important;
    }

    /* ── Select box ─────────────────────────────── */
    [data-baseweb="select"] > div:first-child {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important; border-radius: 6px !important;
    }
    /* Every piece of text inside the select control */
    [data-baseweb="select"] * { color: #111827 !important; }
    [data-baseweb="select"] > div:first-child { background-color: #ffffff !important; }
    [data-baseweb="select"] svg { fill: #6b7280 !important; stroke: none !important; }
    /* Dropdown popup */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div { background-color: #ffffff !important; }
    [data-baseweb="menu"] {
        background-color: #ffffff !important; border: 1px solid #e5e7eb !important;
        border-radius: 8px !important; box-shadow: 0 4px 16px rgba(0,0,0,.08) !important;
    }
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] { color: #111827 !important; background-color: #ffffff !important; }
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover { background-color: #f3f4f6 !important; }

    /* ── All native inputs — belt-and-suspenders ─ */
    input, input[type="text"], input[type="number"], input[type="search"],
    textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    /* BaswUI input wrapper */
    [data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important; border-radius: 6px !important;
    }
    [data-baseweb="input"] > div { background-color: #ffffff !important; }
    [data-baseweb="input"] input { background-color: transparent !important; color: #111827 !important; }
    [data-testid="stNumberInput"] button {
        background: transparent !important; color: #6b7280 !important;
        border: none !important; box-shadow: none !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: #f3f4f6 !important; color: #111827 !important; border: none !important;
    }
    [data-baseweb="textarea"] {
        background-color: #ffffff !important; border: 1px solid #d1d5db !important;
        border-radius: 6px !important; color: #111827 !important;
    }

    /* ── Labels / captions ──────────────────────── */
    .stSelectbox label, .stNumberInput label, .stCheckbox label,
    .stFileUploader label, .stTextInput label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important; color: #374151 !important;
    }
    .stCaption { font-size: 0.8rem !important; color: #9ca3af !important; }

    /* ── File uploader ──────────────────────────── */
    [data-testid="stFileUploader"] button {
        background: #f3f4f6 !important; color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: #1e293b !important; color: #ffffff !important;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ===================== SESSION STATE =====================
if "df"                 not in st.session_state: st.session_state.df = None
if "results"            not in st.session_state: st.session_state.results = {}
if "last_source"        not in st.session_state: st.session_state.last_source = None
if "last_selected_idx"  not in st.session_state: st.session_state.last_selected_idx = None
if "last_run_scope"     not in st.session_state: st.session_state.last_run_scope = None
# Slider / input defaults (updated when a CSV/sample student is selected)
if "inp_name"           not in st.session_state: st.session_state.inp_name = "New Student"
if "inp_attendance"     not in st.session_state: st.session_state.inp_attendance = 60.0
if "inp_score"          not in st.session_state: st.session_state.inp_score = 55.0
if "inp_missing"        not in st.session_state: st.session_state.inp_missing = 3
if "inp_lms"            not in st.session_state: st.session_state.inp_lms = 40.0
if "inp_study_hours"    not in st.session_state: st.session_state.inp_study_hours = 10.0
if "inp_days"           not in st.session_state: st.session_state.inp_days = 14
if "inp_fatigue"        not in st.session_state: st.session_state.inp_fatigue = 0.0
if "wi_hours"           not in st.session_state: st.session_state.wi_hours = 4
if "wi_deadline"        not in st.session_state: st.session_state.wi_deadline = 5
if "wi_no_tutor"        not in st.session_state: st.session_state.wi_no_tutor = False
if "whatif_results"     not in st.session_state: st.session_state.whatif_results = None
if "selected_algo"      not in st.session_state: st.session_state.selected_algo = "A* Search"


# ===================== HELPERS =====================
_ALGO_KEYS = {"A* Search": "astar", "Greedy Best-First": "greedy", "Uniform Cost Search": "ucs"}

def run_single_algorithm(start, algo_name, actions=None):
    if actions is None:
        actions = ALL_ACTIONS
    if algo_name == "A* Search":
        path, cost, final, met = a_star_search(start, actions, heuristic, is_goal)
    elif algo_name == "Greedy Best-First":
        path, cost, final, met = greedy_search(start, actions, heuristic, is_goal)
    else:
        path, cost, final, met = uniform_cost_search(start, actions, heuristic, is_goal)
    return _ALGO_KEYS[algo_name], {"path": path, "cost": cost, "final": final, "metrics": met}


def run_all_algorithms(start, actions=None):
    if actions is None:
        actions = ALL_ACTIONS
    path_a, cost_a, final_a, met_a = a_star_search(start, actions, heuristic, is_goal)
    path_g, cost_g, final_g, met_g = greedy_search(start, actions, heuristic, is_goal)
    path_u, cost_u, final_u, met_u = uniform_cost_search(start, actions, heuristic, is_goal)
    return {
        "astar":  {"path": path_a, "cost": cost_a, "final": final_a, "metrics": met_a},
        "greedy": {"path": path_g, "cost": cost_g, "final": final_g, "metrics": met_g},
        "ucs":    {"path": path_u, "cost": cost_u, "final": final_u, "metrics": met_u},
    }


def _delta(new_c, base_c):
    if new_c is None or base_c is None: return ""
    d = new_c - base_c
    if d > 0: return f'<span class="wi-delta-up">{_icon("arrow-up", 11, "#dc2626")} +{d:.2f}</span>'
    if d < 0: return f'<span class="wi-delta-dn">{_icon("arrow-down", 11, "#16a34a")} {d:.2f}</span>'
    return ""

def _case_body(path, cost, nodes, base_c):
    if not path:
        return f'<div class="wi-stat"><span class="wi-infeasible">{_icon("circle-x", 14, "#dc2626")} Infeasible</span></div>'
    return (
        f'<div class="wi-stat">'
        f'<span>Cost: <b>{cost:.2f}</b></span>'
        f'<span>Steps: <b>{len(path)}</b></span>'
        f'<span>Nodes: <b>{nodes}</b></span>'
        f'{_delta(cost, base_c)}'
        f'</div>'
    )

def render_metric(label, value, color="#111827", icon_name=None):
    ico = f'<span style="opacity:.55">{_icon(icon_name, 12, "#6b7280")}</span>' if icon_name else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{ico}{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
    </div>""", unsafe_allow_html=True)


def render_state(title, state, icon_name="map-pin"):
    risk = risk_score(state)
    rc = "#dc2626" if risk > RISK_THRESHOLD else "#16a34a"
    badge_cls = "badge-high" if risk > RISK_THRESHOLD else "badge-low"
    badge_lbl = "At Risk" if risk > RISK_THRESHOLD else "Safe"
    st.markdown(f"""
    <div class="state-box">
        <div class="state-box-hdr">{_icon(icon_name, 13)} {title}</div>
        <div class="state-row"><span class="s-label">Attendance</span><span class="s-val">{state.attendance:.0%}</span></div>
        <div class="state-row"><span class="s-label">Missing Submissions</span><span class="s-val">{state.missing}</span></div>
        <div class="state-row"><span class="s-label">Quiz Score</span><span class="s-val">{state.score:.0f}</span></div>
        <div class="state-row"><span class="s-label">LMS Activity</span><span class="s-val">{state.lms:.0%}</span></div>
        <div class="state-row"><span class="s-label">Study Hours / Week</span><span class="s-val">{state.study_hours:.0f}</span></div>
        <div class="state-row"><span class="s-label">Days to Deadline</span><span class="s-val">{state.days:.0f}</span></div>
        <div class="state-row">
            <span class="s-label">Risk Score</span>
            <span class="s-val-right">
                <span class="s-val" style="color:{rc}">{risk:.3f}</span>
                <span class="{badge_cls}">{badge_lbl}</span>
            </span>
        </div>
    </div>""", unsafe_allow_html=True)


_PLOT = dict(
    plot_bgcolor="white", paper_bgcolor="#f9fafb",
    font=dict(color="#374151", family="Inter, system-ui, sans-serif", size=12),
)

def _ax(title=""):
    return dict(
        gridcolor="#f3f4f6", linecolor="#e5e7eb", zerolinecolor="#e5e7eb",
        title=title, title_font=dict(color="#6b7280", size=11),
        tickfont=dict(color="#9ca3af", size=11),
    )


# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown(
        f'<div class="sb-label">{_icon("database", 13)} Data Input</div>',
        unsafe_allow_html=True,
    )
    st.caption("Load a CSV dataset or generate sample data.")

    c1, c2 = st.columns(2)
    with c1: load_csv   = st.button("Load CSV",         use_container_width=True)
    with c2: gen_sample = st.button("Generate Sample",  use_container_width=True)

    if gen_sample:
        st.session_state.df = generate_sample_data()
        st.session_state.results = {k: v for k, v in st.session_state.results.items() if k == "manual"}
        st.session_state.last_source = None
        st.session_state.last_run_scope = None
        st.session_state.last_selected_idx = None
        st.rerun()

    if load_csv:
        st.session_state.show_uploader = True

    if st.session_state.get("show_uploader", False):
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try:
                st.session_state.df = load_students_csv(uploaded)
                st.session_state.results = {k: v for k, v in st.session_state.results.items() if k == "manual"}
                st.session_state.last_source = None
                st.session_state.last_run_scope = None
                st.session_state.last_selected_idx = None
                st.session_state.show_uploader = False
                st.rerun()
            except ValueError as e:
                st.error(f"CSV error: {e}")
                st.caption("Required columns: attendance_rate, missing_submissions, avg_quiz_score, lms_activity, study_hours_per_week, days_to_deadline")

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    selected_idx = None

    if st.session_state.df is not None:
        df = st.session_state.df
        options = []
        for i, row in df.iterrows():
            s = state_from_row(row)
            r = risk_score(s)
            name = row.get("student_name", f"Student {i+1}")
            tag  = "HIGH" if r > RISK_THRESHOLD else "ok"
            options.append(f"{name} — {tag} ({r:.1f})")

        st.markdown(
            f'<div class="sb-label">{_icon("users", 13)} Select Student</div>',
            unsafe_allow_html=True,
        )
        selected_idx = st.selectbox(
            "Student", range(len(options)),
            format_func=lambda x: options[x],
            label_visibility="collapsed",
        )

        # Auto-fill sliders when selection changes
        if selected_idx != st.session_state.last_selected_idx:
            row = df.iloc[selected_idx]
            s   = state_from_row(row)
            st.session_state.inp_name        = row.get("student_name", f"Student {selected_idx+1}")
            st.session_state.inp_attendance  = round(float(s.attendance) * 100, 1)
            st.session_state.inp_score       = round(float(s.score), 1)
            st.session_state.inp_missing     = min(10, max(0, int(s.missing)))
            st.session_state.inp_lms         = round(float(s.lms) * 100, 1)
            st.session_state.inp_study_hours = min(20.0, max(0.0, round(float(s.study_hours), 1)))
            st.session_state.inp_days        = min(30, max(0, int(s.days)))
            st.session_state.inp_fatigue     = 0.0
            st.session_state.last_selected_idx = selected_idx
            st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: run_sel     = st.button("Run",     use_container_width=True, type="primary", key="run_selected_dataset")
        with c2: run_all_btn = st.button("Run All", use_container_width=True, key="run_all_dataset")

        clear_results = st.button("Clear Results", use_container_width=True, key="clear_dataset_results")
        if clear_results:
            st.session_state.results = {}
            st.session_state.last_source = None
            st.session_state.last_run_scope = None
            st.session_state.last_selected_idx = None
            st.session_state.whatif_results = None
            st.session_state._run_msg = None
            st.rerun()

        if run_sel:
            row   = df.iloc[selected_idx]
            start = state_from_row(row)
            name  = row.get("student_name", f"Student {selected_idx+1}")
            res   = run_all_algorithms(start)
            res["start"] = start
            res["name"]  = name
            st.session_state.results[selected_idx] = res
            st.session_state.last_source = "csv"
            st.session_state.last_run_scope = "single"
            st.rerun()

        if run_all_btn:
            for i, row in df.iterrows():
                start = state_from_row(row)
                name  = row.get("student_name", f"Student {i+1}")
                res   = run_all_algorithms(start)
                res["start"] = start
                res["name"]  = name
                st.session_state.results[i] = res
            st.session_state.last_source = "csv"
            st.session_state.last_run_scope = "all"
            st.rerun()



# ===================== MAIN CONTENT =====================
st.markdown(f"""
<div class="page-header">
    <div class="page-header-icon">
        {_icon("graduation-cap", 20, "#3b82f6", 2)}
    </div>
    <div class="page-header-text">
        <h1>Student At-Risk Recovery Planner</h1>
        <p><b>A* Search:</b> find the optimal recovery path for at-risk students</p>
    </div>
</div>""", unsafe_allow_html=True)

# Always-visible tabs
tab_input, tab_plan, tab_plots, tab_compare, tab_whatif_tab = st.tabs([
    "Student Input", "Plan Results", "Visualizations", "Algorithm Comparison", "What-If",
])

# ── TAB 1: STUDENT INPUT ─────────────────────────────────────────────────────
with tab_input:
    col_form, col_preview = st.columns([3, 2], gap="large")

    with col_form:
        # Student name
        st.markdown(
            f'<div class="input-section-title" style="margin-bottom:4px">'
            f'{_icon("user", 14, "#6b7280")} Student Identity</div>',
            unsafe_allow_html=True,
        )
        inp_name = st.text_input("Student name", key="inp_name", label_visibility="visible")

        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        # ── Academic Performance ──
        st.markdown(
            f'<div class="input-section-title">'
            f'{_icon("book-open", 14, "#6b7280")} Academic Performance</div>',
            unsafe_allow_html=True,
        )

        inp_attendance = st.slider(
            "Attendance Rate", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%",
            key="inp_attendance",
            help="Percentage of classes attended",
        )
        inp_score = st.slider(
            "Average Quiz Score", min_value=0.0, max_value=100.0, step=0.5, format="%.1f",
            key="inp_score",
            help="Current average score across all quizzes (0–100)",
        )
        inp_missing = st.slider(
            "Missing Submissions", min_value=0, max_value=10, step=1,
            key="inp_missing",
            help="Number of assignments not yet submitted (whole number)",
        )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        # ── Engagement & Workload ──
        st.markdown(
            f'<div class="input-section-title">'
            f'{_icon("trending-up", 14, "#6b7280")} Engagement & Workload</div>',
            unsafe_allow_html=True,
        )

        inp_lms = st.slider(
            "LMS Activity", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%",
            key="inp_lms",
            help="Percentage of LMS tasks completed (videos, readings, forums)",
        )
        inp_study_hours = st.slider(
            "Study Hours / Week", min_value=0.0, max_value=20.0, step=0.5, format="%.1f hrs",
            key="inp_study_hours",
            help="Average hours spent studying per week",
        )
        inp_days = st.slider(
            "Days to Deadline", min_value=0, max_value=30, step=1,
            key="inp_days",
            help="Days remaining until the next major deadline (whole number)",
        )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        # ── Student Condition ──
        st.markdown(
            f'<div class="input-section-title">'
            f'{_icon("battery-charging", 14, "#6b7280")} Student Condition</div>',
            unsafe_allow_html=True,
        )

        inp_fatigue = st.slider(
            "Fatigue Level", min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
            key="inp_fatigue",
            help="Current fatigue: 0.0 = fully rested, 10.0 = exhausted",
        )

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        algo_choice = st.selectbox(
            "Algorithm", ["A* Search", "Greedy Best-First", "Uniform Cost Search"],
            key="algo_choice",
        )
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            run_one = st.button("Run Selected", type="primary", use_container_width=True, key="run_selected_manual")
        with col_r2:
            run_all_btn = st.button("Run All", use_container_width=True, key="run_all_manual")

    # ── Live Risk Preview (right column) ──────────────────────────────────────
    with col_preview:
        preview_state = State(
            attendance  = inp_attendance / 100,
            missing     = inp_missing,
            score       = inp_score,
            lms         = inp_lms / 100,
            study_hours = inp_study_hours,
            days        = inp_days,
            fatigue     = inp_fatigue,
        )
        risk     = risk_score(preview_state)
        at_risk  = risk > RISK_THRESHOLD
        rcolor   = "#dc2626" if at_risk else "#16a34a"
        bcls     = "badge-high" if at_risk else "badge-low"
        blbl     = "At Risk" if at_risk else "Safe"
        bar_pct  = min(int(risk * 100 / RISK_THRESHOLD * 100), 100)  # pct toward threshold

        st.markdown(
            f'<div class="sec-hdr" style="margin-top:0">'
            f'{_icon("target", 13)} Live Risk Preview</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:22px 24px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <div>
                    <div style="font-size:0.69rem;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px;">Risk Score</div>
                    <div style="font-size:2.4rem;font-weight:700;font-family:'JetBrains Mono',monospace;color:{rcolor};line-height:1">{risk:.3f}</div>
                </div>
                <span class="{bcls}" style="font-size:0.8rem;padding:5px 12px">{blbl}</span>
            </div>
            <div style="background:#f3f4f6;border-radius:100px;height:6px;overflow:hidden;margin-bottom:8px;">
                <div style="background:{rcolor};width:{bar_pct}%;height:100%;border-radius:100px;transition:width .3s"></div>
            </div>
            <div style="font-size:0.72rem;color:#9ca3af;font-family:'JetBrains Mono',monospace;">
                threshold: {RISK_THRESHOLD} &nbsp;|&nbsp; current: {risk:.4f}
            </div>
        </div>""", unsafe_allow_html=True)

        # Mini state summary
        st.markdown(
            f'<div class="sec-hdr">{_icon("scan-line", 13)} Input Summary</div>',
            unsafe_allow_html=True,
        )
        rows = [
            ("Attendance",       f"{inp_attendance:.1f}%"),
            ("Quiz Score",       f"{inp_score:.1f}"),
            ("Missing",          f"{inp_missing}"),
            ("LMS Activity",     f"{inp_lms:.1f}%"),
            ("Study Hrs / Wk",   f"{inp_study_hours:.1f}"),
            ("Days to Deadline", f"{inp_days}"),
            ("Fatigue",          f"{inp_fatigue:.1f} / 10"),
        ]
        rows_html = "".join(
            f'<div class="state-row"><span class="s-label">{lbl}</span><span class="s-val">{val}</span></div>'
            for lbl, val in rows
        )
        st.markdown(f'<div class="state-box">{rows_html}</div>', unsafe_allow_html=True)

    # Handle button clicks
    if run_one or run_all_btn:
        try:
            # Preserve existing results, only overwrite what was just run
            existing = st.session_state.results.get("manual", {})
            for k in ["astar", "greedy", "ucs"]:
                if k not in existing:
                    existing[k] = {"path": None, "cost": None, "final": None,
                                   "metrics": {"expanded_nodes": 0, "runtime": 0.0}}

            if run_all_btn:
                fresh = run_all_algorithms(preview_state)
                existing.update(fresh)
            else:
                k, res = run_single_algorithm(preview_state, st.session_state.algo_choice)
                existing[k] = res

            existing["start"] = preview_state
            existing["name"]  = inp_name.strip() or "Manual Student"
            st.session_state.results["manual"] = existing
            st.session_state.last_source = "manual"
            st.session_state.last_run_scope = "manual"

            _has_path = any(existing[k]["path"] for k in ["astar", "greedy", "ucs"])
            if _has_path:
                st.session_state._run_msg = "success"
            elif is_goal(preview_state):
                st.session_state._run_msg = "safe"
            else:
                st.session_state._run_msg = "infeasible"
            st.rerun()
        except Exception as e:
            import traceback
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

    # Show run result message (persisted across rerun)
    msg = st.session_state.get("_run_msg")
    if msg == "success":
        st.success("Done. Switch to **Plan Results** to view the recovery plan.")
    elif msg == "safe":
        st.info("Student is already below the risk threshold — no recovery plan needed.")
    elif msg == "infeasible":
        st.warning("No recovery plan found. The student may have too few days remaining, or try **Run All** to compare all algorithms.")

    # ── What-If Scenarios ─────────────────────────────────────────────────────
    st.markdown('<div class="divider" style="margin-top:24px"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sec-hdr">{_icon("flask-conical", 13)} What-If Scenarios (Optional)</div>',
        unsafe_allow_html=True,
    )
    st.caption("Simulate how recovery changes under different constraints using the current slider values as the starting point.")

    wi_col1, wi_col2, wi_col3 = st.columns([1, 1, 1])
    with wi_col1:
        wi_hours    = st.number_input("Max study hours",          min_value=1, max_value=20, key="wi_hours")
    with wi_col2:
        wi_deadline = st.number_input("Override deadline (days)", min_value=1, max_value=30, key="wi_deadline")
    with wi_col3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        wi_no_tutor = st.checkbox("Tutor unavailable", key="wi_no_tutor")

    run_whatif_btn = st.button("Run What-If", use_container_width=True, key="run_whatif_btn")

    if run_whatif_btn:
        so = preview_state
        po, co, fo, mo = a_star_search(so, ALL_ACTIONS, heuristic, is_goal)

        s1 = State(so.attendance, so.missing, so.score, so.lms,
                   min(so.study_hours, wi_hours), so.days, so.fatigue)
        p1, c1x, f1, m1 = a_star_search(s1, ALL_ACTIONS, heuristic, is_goal)

        s2 = State(so.attendance, so.missing, so.score, so.lms,
                   so.study_hours, wi_deadline, 0)
        p2, c2x, f2, m2 = a_star_search(s2, ALL_ACTIONS, heuristic, is_goal)

        restricted = [a for a in ALL_ACTIONS if a.__name__ != "meet_tutor"] if wi_no_tutor else ALL_ACTIONS
        p3, c3x, f3, m3 = a_star_search(so, restricted, heuristic, is_goal)

        st.session_state.whatif_results = {
            "baseline": {"path": po, "cost": co, "nodes": mo["expanded_nodes"]},
            "case1":    {"path": p1, "cost": c1x, "nodes": m1["expanded_nodes"],
                         "label": f"Max {wi_hours}h study"},
            "case2":    {"path": p2, "cost": c2x, "nodes": m2["expanded_nodes"],
                         "label": f"{wi_deadline}-day deadline"},
            "case3":    {"path": p3, "cost": c3x, "nodes": m3["expanded_nodes"],
                         "label": "No tutor" if wi_no_tutor else "With tutor"},
        }

    wr = st.session_state.whatif_results
    if wr:
        co   = wr["baseline"]["cost"]
        po   = wr["baseline"]["path"]
        c1x  = wr["case1"]["cost"]
        p1   = wr["case1"]["path"]
        c2x  = wr["case2"]["cost"]
        p2   = wr["case2"]["path"]
        c3x  = wr["case3"]["cost"]
        p3   = wr["case3"]["path"]

        if po:
            st.markdown(f"""
            <div class="wi-card" style="border-left:3px solid #4f46e5">
                <div class="wi-title">{_icon("bookmark", 14, "#4f46e5")} Baseline (no constraints)</div>
                <div class="wi-stat">
                    <span>Cost: <b>{co:.2f}</b></span>
                    <span>Steps: <b>{len(po)}</b></span>
                    <span>Nodes: <b>{wr["baseline"]["nodes"]}</b></span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("sliders-horizontal", 14, "#374151")} Case 1 — {wr["case1"]["label"]}</div>
            {_case_body(p1, c1x, wr["case1"]["nodes"], co)}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("clock", 14, "#374151")} Case 2 — {wr["case2"]["label"]}</div>
            {_case_body(p2, c2x, wr["case2"]["nodes"], co)}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("users", 14, "#374151")} Case 3 — {wr["case3"]["label"]}</div>
            {_case_body(p3, c3x, wr["case3"]["nodes"], co)}
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Cost Comparison</div>',
            unsafe_allow_html=True,
        )
        scenarios  = ["Baseline", wr["case1"]["label"], wr["case2"]["label"], wr["case3"]["label"]]
        cost_vals  = [co or 0, c1x or 0, c2x or 0, c3x or 0]
        bar_colors = ["#4f46e5",
                      "#22c55e" if c1x else "#ef4444",
                      "#22c55e" if c2x else "#ef4444",
                      "#22c55e" if c3x else "#ef4444"]
        fig_w = go.Figure(go.Bar(
            x=scenarios, y=cost_vals, marker_color=bar_colors,
            marker_line_width=0, opacity=0.88,
            text=[f"{c:.2f}" if c else "N/A" for c in [co, c1x, c2x, c3x]],
            textposition="outside", textfont=dict(color="#6b7280", size=11),
        ))
        fig_w.update_layout(
            height=300, **_PLOT,
            yaxis=_ax("Total Cost"), xaxis=_ax(),
            margin=dict(t=30, b=30, l=50, r=20),
        )
        st.plotly_chart(fig_w, use_container_width=True, key="fig_w_cost_comparison")


# ── Determine active result for the remaining tabs ────────────────────────────
active_res = None
if st.session_state.last_source == "manual":
    active_res = st.session_state.results.get("manual")
elif st.session_state.last_source == "csv" and selected_idx is not None and selected_idx in st.session_state.results:
    active_res = st.session_state.results[selected_idx]
elif selected_idx is not None and selected_idx in st.session_state.results:
    active_res = st.session_state.results[selected_idx]
elif "manual" in st.session_state.results:
    active_res = st.session_state.results.get("manual")

if active_res:
    start = active_res["start"]
    name  = active_res["name"]


# ── TAB 2: PLAN RESULTS ──────────────────────────────────────────────────────
with tab_plan:
    if not active_res:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon-wrap">{_icon("list-checks", 24, "#9ca3af")}</div>
            <h3>No results yet</h3>
            <p>Enter student data in <strong>Student Input</strong> and click
            <strong>Run Selected</strong> or <strong>Run All</strong>.</p>
        </div>""", unsafe_allow_html=True)
    else:
        _label_map   = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "Uniform Cost Search"}
        _algo_colors = {"astar": "#4f46e5",    "greedy": "#f59e0b",           "ucs": "#0891b2"}
        _ran = [k for k in ["astar", "greedy", "ucs"] if active_res.get(k, {}).get("path") is not None]

        if not _ran:
            st.warning("No algorithm has produced a result yet. Run one from **Student Input**.")
        else:
            # ── Shared starting state ─────────────────────────────────────────
            render_state("Starting State", start, "map-pin")
            rs = risk_score(start)

            # ── One section per algorithm ─────────────────────────────────────
            for _k in _ran:
                _r     = active_res[_k]
                _met   = _r["metrics"]
                _color = _algo_colors[_k]
                _label = _label_map[_k]
                rf     = risk_score(_r["final"])

                st.markdown(
                    f'<div class="sec-hdr" style="margin-top:28px">'
                    f'<span style="color:{_color};font-size:0.8rem">&#9679;</span>'
                    f'&nbsp;{_label}</div>',
                    unsafe_allow_html=True,
                )

                c1, c2, c3, c4, c5, c6 = st.columns(6)
                with c1: render_metric("Risk Before", f"{rs:.3f}",                "#dc2626", "activity")
                with c2: render_metric("Risk After",  f"{rf:.3f}",                "#16a34a", "target")
                with c3: render_metric("Total Cost",  f"{_r['cost']:.2f}",        _color,    "route")
                with c4: render_metric("Steps",       str(len(_r["path"])),       "#374151", "list-checks")
                with c5: render_metric("Nodes",       str(_met["expanded_nodes"]), "#374151", "cpu")
                with c6: render_metric("Runtime",     f"{_met['runtime']*1000:.1f} ms", "#374151", "clock")

                st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
                render_state("Final State", _r["final"], "flag")

                st.markdown(
                    f'<div class="sec-hdr" style="margin-top:14px">'
                    f'{_icon("list-checks", 13)} Recovery Steps</div>',
                    unsafe_allow_html=True,
                )
                for i, (act, state) in enumerate(_r["path"], 1):
                    desc = ACTION_DESCRIPTIONS.get(act, act)
                    st.markdown(f"""
                    <div class="step-card" style="border-left-color:{_color}">
                        <span class="step-num" style="background:{_color}">{i}</span>
                        <div class="step-body">
                            <div class="step-action">{desc}</div>
                            <div class="step-detail">att={state.attendance:.0%} &nbsp;|&nbsp; miss={state.missing} &nbsp;|&nbsp; score={state.score:.0f} &nbsp;|&nbsp; fatigue={state.fatigue:.1f}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="goal-banner">
                    {_icon("circle-check", 18, "#16a34a")}
                    <span>Risk reduced from <strong style="color:#dc2626">{rs:.3f}</strong>
                    to <strong style="color:#16a34a">{rf:.3f}</strong>
                    in {len(_r["path"])} steps</span>
                </div>""", unsafe_allow_html=True)

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ── TAB 3: VISUALIZATIONS ────────────────────────────────────────────────────
with tab_plots:
    def _any_path(v):
        return any(v.get(k, {}).get("path") is not None for k in ["astar", "greedy", "ucs"])
    def _best_final(v):
        candidates = []
        for k in ["astar", "greedy", "ucs"]:
            r = v.get(k, {})
            if r.get("final") is not None and r.get("cost") is not None:
                candidates.append((r["cost"], r["final"]))
        if candidates:
            return min(candidates, key=lambda item: item[0])[1]
        for k in ["astar", "greedy", "ucs"]:
            if v.get(k, {}).get("final") is not None:
                return v[k]["final"]
        return None

    if st.session_state.last_source == "manual":
        solved = {
            "manual": st.session_state.results.get("manual")
        } if _any_path(st.session_state.results.get("manual", {})) else {}
    elif st.session_state.last_source == "csv":
        if st.session_state.last_run_scope == "single" and selected_idx is not None and selected_idx in st.session_state.results:
            solved = {selected_idx: st.session_state.results[selected_idx]}
        else:
            solved = {
                k: v for k, v in st.session_state.results.items()
                if isinstance(k, int) and _any_path(v)
            }
    else:
        solved = {k: v for k, v in st.session_state.results.items() if _any_path(v)}

    if not solved:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon-wrap">{_icon("bar-chart-2", 24, "#9ca3af")}</div>
            <h3>No data to visualize</h3>
            <p>Run an analysis first to see charts here.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Risk Score Before vs After — Per Algorithm</div>',
            unsafe_allow_html=True,
        )
        if active_res and _any_path(active_res):
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            _algo_colors = {"astar": "#4f46e5", "greedy": "#f59e0b", "ucs": "#0891b2"}
            _algo_labels = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "UCS"}

            if st.session_state.last_source == "csv" and st.session_state.last_run_scope == "all":
                # Dataset-wide per-algorithm graphs
                for _k, _color in _algo_colors.items():
                    names = []
                    before_vals = []
                    after_vals = []
                    for key in sorted(solved, key=str):
                        result = solved[key]
                        algo = result.get(_k, {})
                        if algo.get("path") is None:
                            continue
                        names.append(result["name"])
                        before_vals.append(risk_score(result["start"]))
                        after_vals.append(risk_score(algo["final"]))

                    if not names:
                        st.markdown(f"<p style='color:#6b7280;margin-bottom:16px;'>No dataset results available for {_algo_labels[_k]}.</p>", unsafe_allow_html=True)
                        continue

                    fig_algo = go.Figure()
                    fig_algo.add_trace(go.Bar(name="Before", x=names, y=before_vals, marker_color="#ef4444", marker_line_width=0, opacity=0.82, width=0.25))
                    fig_algo.add_trace(go.Bar(name="After",  x=names, y=after_vals,  marker_color="#22c55e", marker_line_width=0, opacity=0.82, width=0.25))
                    fig_algo.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                        line_width=1.5,
                        annotation_text=f"Threshold ({RISK_THRESHOLD})",
                        annotation_font_color="#f59e0b", annotation_font_size=11)
                    fig_algo.update_layout(
                        title={"text": f"{_algo_labels[_k]} — Before vs After", "x": 0.01, "xanchor": "left"},
                        height=320, **_PLOT,
                        barmode="group",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                        xaxis=_ax("Student"), yaxis=_ax("Risk Score"),
                        margin=dict(t=50, b=40, l=50, r=20),
                    )
                    st.plotly_chart(fig_algo, use_container_width=True, key=f"fig_before_after_{_k}")
            else:
                # Single result / manual run per-algorithm graph
                for _k, _color in _algo_colors.items():
                    _r = active_res.get(_k, {})
                    if _r.get("path") is None:
                        st.markdown(f"<p style='color:#6b7280;margin-bottom:16px;'>{_algo_labels[_k]} did not produce a recovery path.</p>", unsafe_allow_html=True)
                        continue

                    before_risk = risk_score(start)
                    after_risk = risk_score(_r["final"])
                    fig_algo = go.Figure()
                    fig_algo.add_trace(go.Bar(name="Before", x=[_algo_labels[_k]], y=[before_risk], marker_color="#ef4444", marker_line_width=0, opacity=0.82, width=0.4))
                    fig_algo.add_trace(go.Bar(name="After",  x=[_algo_labels[_k]], y=[after_risk],  marker_color="#22c55e", marker_line_width=0, opacity=0.82, width=0.4))
                    fig_algo.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                        line_width=1.5,
                        annotation_text=f"Threshold ({RISK_THRESHOLD})",
                        annotation_font_color="#f59e0b", annotation_font_size=11)
                    fig_algo.update_layout(
                        height=300, **_PLOT,
                        barmode="group",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                        xaxis=_ax("Algorithm"), yaxis=_ax("Risk Score"),
                        margin=dict(t=40, b=40, l=50, r=20),
                    )
                    st.plotly_chart(fig_algo, use_container_width=True, key=f"fig_before_after_{_k}")

            # ── Action Distribution ───────────────────────────────────────────
            _best_key = next(k for k in ["astar", "greedy", "ucs"] if active_res.get(k, {}).get("path"))
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="sec-hdr">{_icon("activity", 13)} Action Distribution — {_algo_labels[_best_key]}</div>',
                unsafe_allow_html=True,
            )
            path   = active_res[_best_key]["path"]
            counts = Counter(a for a, _ in path)
            labels = [ACTION_DESCRIPTIONS.get(a, a) for a in counts]
            values = list(counts.values())
            palette = ["#4f46e5", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#7c3aed"]
            fig2 = go.Figure(go.Bar(
                x=values, y=labels, orientation="h",
                marker=dict(color=palette[:len(labels)], line_width=0), opacity=0.88,
                text=values, textposition="outside",
                textfont=dict(color="#6b7280", size=11),
            ))
            fig2.update_layout(
                height=max(240, len(labels) * 52), **_PLOT,
                xaxis=_ax("Count"), yaxis=_ax(),
                margin=dict(t=20, b=30, l=190, r=60),
            )
            st.plotly_chart(fig2, use_container_width=True, key="fig2_scatter")


# ── TAB 4: ALGORITHM COMPARISON ──────────────────────────────────────────────
with tab_compare:
    if not active_res:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon-wrap">{_icon("git-compare-arrows", 24, "#9ca3af")}</div>
            <h3>No comparison data</h3>
            <p>Run an analysis first to compare A*, Greedy, and UCS.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="sec-hdr">{_icon("git-compare-arrows", 13)} A* vs Greedy vs UCS</div>',
            unsafe_allow_html=True,
        )
        best_cost = min(
            (active_res[k]["cost"] for k in ["astar", "greedy", "ucs"] if active_res[k]["cost"] is not None),
            default=None,
        )
        rows_html = ""
        for label, key in [("A* Search", "astar"), ("Greedy Best-First", "greedy"), ("Uniform Cost Search", "ucs")]:
            r = active_res[key]
            if r["path"] is not None:
                cost_cls = ' class="td-best"' if r["cost"] == best_cost else ""
                goal_td  = f'<span class="td-goal-y">{_icon("circle-check", 14, "#16a34a")} Yes</span>'
                rows_html += (
                    f"<tr><td class='td-name'>{label}</td>"
                    f"<td{cost_cls}>{r['cost']:.2f}</td>"
                    f"<td>{len(r['path'])}</td>"
                    f"<td>{r['metrics']['expanded_nodes']}</td>"
                    f"<td>{r['metrics']['runtime']*1000:.3f} ms</td>"
                    f"<td>{goal_td}</td></tr>"
                )
            else:
                goal_td  = f'<span class="td-goal-n">{_icon("circle-x", 14, "#dc2626")} No</span>'
                rows_html += (
                    f"<tr><td class='td-name'>{label}</td>"
                    f"<td class='td-muted'>N/A</td><td class='td-muted'>—</td>"
                    f"<td>{r['metrics']['expanded_nodes']}</td>"
                    f"<td>{r['metrics']['runtime']*1000:.3f} ms</td>"
                    f"<td>{goal_td}</td></tr>"
                )

        st.markdown(f"""
        <div class="comp-wrap"><table class="comp-table">
        <thead><tr>
            <th>Method</th><th>Cost</th><th>Steps</th>
            <th>Nodes</th><th>Runtime</th><th>Goal</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
        </table></div>""", unsafe_allow_html=True)

        # Threshold degradation comparison chart
        if active_res and _any_path(active_res):
            _algo_labels = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "UCS"}
            algo_labels = []
            before_vals = []
            after_vals = []
            for key in ["astar", "greedy", "ucs"]:
                algo = active_res.get(key, {})
                if algo.get("path") is None:
                    continue
                algo_labels.append(_algo_labels[key])
                before_vals.append(risk_score(active_res["start"]))
                after_vals.append(risk_score(algo["final"]))

            if algo_labels:
                fig_thr = go.Figure()
                fig_thr.add_trace(go.Bar(name="Before", x=algo_labels, y=before_vals, marker_color="#ef4444", marker_line_width=0, opacity=0.82, width=0.35))
                fig_thr.add_trace(go.Bar(name="After",  x=algo_labels, y=after_vals,  marker_color="#22c55e", marker_line_width=0, opacity=0.82, width=0.35))
                fig_thr.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                    line_width=1.5,
                    annotation_text=f"Threshold ({RISK_THRESHOLD})",
                    annotation_font_color="#f59e0b", annotation_font_size=11)
                fig_thr.update_layout(
                    title={"text": "Threshold Degradation — Before vs After", "x": 0.01, "xanchor": "left", "y": 0.95},
                    height=360, **_PLOT,
                    barmode="group",
                    legend=dict(orientation="h", x=0, xanchor="left", y=-0.18, yanchor="top",
                        bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                    xaxis=_ax("Algorithm"), yaxis=_ax("Risk Score"),
                    margin=dict(t=80, b=70, l=50, r=20),
                )
                st.plotly_chart(fig_thr, use_container_width=True, key="fig_threshold_degradation")

            # Combined risk progression line chart for all algorithms
            fig_thr_prog = go.Figure()
            marker_symbols = {"astar": "circle", "greedy": "square", "ucs": "diamond"}
            line_styles = {"astar": "solid", "greedy": "dash", "ucs": "dot"}
            for key, color in [("astar", "#4f46e5"), ("greedy", "#f59e0b"), ("ucs", "#0891b2")]:
                algo = active_res.get(key, {})
                if algo.get("path") is None:
                    continue
                progression = [risk_score(active_res["start"])] + [risk_score(s) for _, s in algo["path"]]
                fig_thr_prog.add_trace(go.Scatter(
                    x=list(range(len(progression))), y=progression,
                    name=_algo_labels[key], mode="lines+markers",
                    line=dict(color=color, width=3, dash=line_styles[key]),
                    marker=dict(size=8, color=color, symbol=marker_symbols[key], line=dict(width=1, color="white")),
                ))
            if fig_thr_prog.data:
                fig_thr_prog.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                    line_width=1.5,
                    annotation_text=f"Threshold ({RISK_THRESHOLD})",
                    annotation_font_color="#f59e0b", annotation_font_size=11,
                    annotation_position="top right")
                fig_thr_prog.update_layout(
                    title={"text": "Risk Progression — All Algorithms", "x": 0.01, "xanchor": "left", "y": 0.95},
                    height=360, **_PLOT,
                    legend=dict(orientation="h", x=0, xanchor="left", y=-0.18, yanchor="top",
                        bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                    xaxis=_ax("Step"), yaxis=_ax("Risk Score"),
                    margin=dict(t=80, b=70, l=50, r=20),
                )
                st.plotly_chart(fig_thr_prog, use_container_width=True, key="fig_threshold_progression")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("info", 13)} Analysis</div>',
            unsafe_allow_html=True,
        )
        lines = []
        ac, gc, uc = active_res["astar"]["cost"], active_res["greedy"]["cost"], active_res["ucs"]["cost"]
        if ac is not None and gc is not None:
            lines.append(
                "<strong>A*</strong> found an equal or lower cost plan than <strong>Greedy</strong>, confirming its optimality."
                if ac <= gc else
                "<strong>Greedy</strong> found a cheaper path, but it may not always be optimal."
            )
        if ac is not None and uc is not None:
            an, un = active_res["astar"]["metrics"]["expanded_nodes"], active_res["ucs"]["metrics"]["expanded_nodes"]
            lines.append(f"<strong>A*</strong> expanded <strong>{an}</strong> nodes vs UCS's <strong>{un}</strong> nodes.")
            if an < un:
                lines.append(f"The heuristic saved A* from expanding <strong>{un - an}</strong> unnecessary nodes.")
        lines.append("<strong>Key takeaway:</strong> A* combines UCS's optimality with Greedy's speed via an informed heuristic.")
        st.markdown(
            f'<div class="analysis-block">{"".join(f"<p>{l}</p>" for l in lines)}</div>',
            unsafe_allow_html=True,
        )


# ── TAB 5: WHAT-IF ───────────────────────────────────────────────────────────
with tab_whatif_tab:
    wr5 = st.session_state.whatif_results
    if wr5:
        st.markdown(
            f'<div class="sec-hdr">{_icon("flask-conical", 13)} What-If Results</div>',
            unsafe_allow_html=True,
        )
        co5  = wr5["baseline"]["cost"]
        po5  = wr5["baseline"]["path"]
        c1x5 = wr5["case1"]["cost"]
        p1x5 = wr5["case1"]["path"]
        c2x5 = wr5["case2"]["cost"]
        p2x5 = wr5["case2"]["path"]
        c3x5 = wr5["case3"]["cost"]
        p3x5 = wr5["case3"]["path"]

        if po5:
            st.markdown(f"""
            <div class="wi-card" style="border-left:3px solid #4f46e5">
                <div class="wi-title">{_icon("bookmark", 14, "#4f46e5")} Baseline (no constraints)</div>
                <div class="wi-stat">
                    <span>Cost: <b>{co5:.2f}</b></span>
                    <span>Steps: <b>{len(po5)}</b></span>
                    <span>Nodes: <b>{wr5["baseline"]["nodes"]}</b></span>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("sliders-horizontal", 14, "#374151")} Case 1 — {wr5["case1"]["label"]}</div>
            {_case_body(p1x5, c1x5, wr5["case1"]["nodes"], co5)}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("clock", 14, "#374151")} Case 2 — {wr5["case2"]["label"]}</div>
            {_case_body(p2x5, c2x5, wr5["case2"]["nodes"], co5)}
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wi-card">
            <div class="wi-title">{_icon("users", 14, "#374151")} Case 3 — {wr5["case3"]["label"]}</div>
            {_case_body(p3x5, c3x5, wr5["case3"]["nodes"], co5)}
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Cost Comparison</div>',
            unsafe_allow_html=True,
        )
        scenarios5  = ["Baseline", wr5["case1"]["label"], wr5["case2"]["label"], wr5["case3"]["label"]]
        cost_vals5  = [co5 or 0, c1x5 or 0, c2x5 or 0, c3x5 or 0]
        bar_colors5 = ["#4f46e5",
                       "#22c55e" if c1x5 else "#ef4444",
                       "#22c55e" if c2x5 else "#ef4444",
                       "#22c55e" if c3x5 else "#ef4444"]
        fig_w5 = go.Figure(go.Bar(
            x=scenarios5, y=cost_vals5, marker_color=bar_colors5,
            marker_line_width=0, opacity=0.88,
            text=[f"{c:.2f}" if c else "N/A" for c in [co5, c1x5, c2x5, c3x5]],
            textposition="outside", textfont=dict(color="#6b7280", size=11),
        ))
        fig_w5.update_layout(
            height=300, **_PLOT,
            yaxis=_ax("Total Cost"), xaxis=_ax(),
            margin=dict(t=30, b=30, l=50, r=20),
        )
        st.plotly_chart(fig_w5, use_container_width=True, key="fig_w5_cost_comparison")
    else:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon-wrap">{_icon("flask-conical", 24, "#9ca3af")}</div>
            <h3>No What-If results yet</h3>
            <p>Go to <strong>Student Input</strong>, set constraints at the bottom, and click <strong>Run What-If</strong>.</p>
        </div>""", unsafe_allow_html=True)

