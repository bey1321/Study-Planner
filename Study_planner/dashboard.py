"""
Student At-Risk Recovery Planner Dashboard
==========================================
CSAI 350 - Introduction to Artificial Intelligence
Spring 2026

Run with:  streamlit run dashboard.py
"""

import streamlit as st

from styles import _icon, apply_styles
from sidebar import render_sidebar
from tab_input import render_tab_input
from tab_plan import render_tab_plan
from tab_plots import render_tab_plots
from tab_compare import render_tab_compare
from tab_whatif import render_tab_whatif


# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Recovery Planner - A* Search",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()


# ===================== SESSION STATE =====================
if "df"                 not in st.session_state: st.session_state.df = None
if "results"            not in st.session_state: st.session_state.results = {}
if "last_source"        not in st.session_state: st.session_state.last_source = None
if "last_selected_idx"  not in st.session_state: st.session_state.last_selected_idx = None
if "last_run_scope"     not in st.session_state: st.session_state.last_run_scope = None
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
if "wi_max_classes"     not in st.session_state: st.session_state.wi_max_classes = 5
if "wi_max_fatigue"     not in st.session_state: st.session_state.wi_max_fatigue = 7
if "whatif_results"     not in st.session_state: st.session_state.whatif_results = None
if "selected_algo"      not in st.session_state: st.session_state.selected_algo = "A* Search"


# ===================== SIDEBAR =====================
selected_idx = render_sidebar()


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

tab_input, tab_plan, tab_plots, tab_compare, tab_whatif_tab = st.tabs([
    "Student Input", "Plan Results", "Visualizations", "Algorithm Comparison", "What-If",
])


# ===================== ACTIVE RESULT =====================
active_res = None
if st.session_state.last_source == "manual":
    active_res = st.session_state.results.get("manual")
elif st.session_state.last_source == "csv" and selected_idx is not None and selected_idx in st.session_state.results:
    active_res = st.session_state.results[selected_idx]
elif selected_idx is not None and selected_idx in st.session_state.results:
    active_res = st.session_state.results[selected_idx]
elif "manual" in st.session_state.results:
    active_res = st.session_state.results.get("manual")


# ===================== TABS =====================
render_tab_input(tab_input)
render_tab_plan(tab_plan, active_res)
render_tab_plots(tab_plots, active_res, selected_idx)
render_tab_compare(tab_compare, active_res)
render_tab_whatif(tab_whatif_tab)
