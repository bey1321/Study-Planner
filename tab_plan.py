import streamlit as st

from student_model import risk_score, RISK_THRESHOLD, ACTION_DESCRIPTIONS
from styles import _icon
from components import render_metric, render_state


_LABEL_MAP   = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "Uniform Cost Search"}
_ALGO_COLORS = {"astar": "#4f46e5",   "greedy": "#f59e0b",           "ucs": "#0891b2"}


def render_tab_plan(tab, active_res):
    with tab:
        if not active_res:
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-icon-wrap">{_icon("list-checks", 24, "#9ca3af")}</div>
                <h3>No results yet</h3>
                <p>Enter student data in <strong>Student Input</strong> and click
                <strong>Run Selected</strong> or <strong>Run All</strong>.</p>
            </div>""", unsafe_allow_html=True)
            return

        _ran = [k for k in ["astar", "greedy", "ucs"] if active_res.get(k, {}).get("path") is not None]
        if not _ran:
            st.warning("No algorithm has produced a result yet. Run one from **Student Input**.")
            return

        start = active_res["start"]
        render_state("Starting State", start, "map-pin")
        rs = risk_score(start)

        for _k in _ran:
            _r     = active_res[_k]
            _met   = _r["metrics"]
            _color = _ALGO_COLORS[_k]
            _label = _LABEL_MAP[_k]
            rf     = risk_score(_r["final"])

            st.markdown(
                f'<div class="sec-hdr" style="margin-top:28px">'
                f'<span style="color:{_color};font-size:0.8rem">&#9679;</span>'
                f'&nbsp;{_label}</div>',
                unsafe_allow_html=True,
            )

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: render_metric("Risk Before", f"{rs:.3f}",                 "#dc2626", "activity")
            with c2: render_metric("Risk After",  f"{rf:.3f}",                 "#16a34a", "target")
            with c3: render_metric("Total Cost",  f"{_r['cost']:.2f}",         _color,    "route")
            with c4: render_metric("Steps",       str(len(_r["path"])),        "#374151", "list-checks")
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
