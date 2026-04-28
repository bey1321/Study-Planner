import streamlit as st


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


_CSS = """
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
    [data-baseweb="select"] * { color: #111827 !important; }
    [data-baseweb="select"] > div:first-child { background-color: #ffffff !important; }
    [data-baseweb="select"] svg { fill: #6b7280 !important; stroke: none !important; }
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

    /* ── All native inputs ───────────────────────── */
    input, input[type="text"], input[type="number"], input[type="search"],
    textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
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
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        min-width: 21.875rem !important;
        width: 21.875rem !important;
    }
    [data-testid="collapsedControl"] { display: none !important; }
"""


def apply_styles():
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
