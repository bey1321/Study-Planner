import streamlit as st
import plotly.graph_objects as go
from collections import Counter

from student_model import risk_score, RISK_THRESHOLD, ACTION_DESCRIPTIONS
from styles import _icon
from components import _PLOT, _ax


_ALGO_COLORS = {"astar": "#4f46e5", "greedy": "#f59e0b", "ucs": "#0891b2"}
_ALGO_LABELS = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "UCS"}


def _any_path(v):
    return any(v.get(k, {}).get("path") is not None for k in ["astar", "greedy", "ucs"])


def render_tab_plots(tab, active_res, selected_idx):
    with tab:
        if st.session_state.last_source == "manual":
            solved = (
                {"manual": st.session_state.results.get("manual")}
                if _any_path(st.session_state.results.get("manual", {})) else {}
            )
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
            return

        st.markdown(
            f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Risk Score Before vs After — Per Algorithm</div>',
            unsafe_allow_html=True,
        )

        if not (active_res and _any_path(active_res)):
            return

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        start = active_res["start"]

        if st.session_state.last_source == "csv" and st.session_state.last_run_scope == "all":
            for _k, _color in _ALGO_COLORS.items():
                names, before_vals, after_vals = [], [], []
                for key in sorted(solved, key=str):
                    result = solved[key]
                    algo = result.get(_k, {})
                    if algo.get("path") is None:
                        continue
                    names.append(result["name"])
                    before_vals.append(risk_score(result["start"]))
                    after_vals.append(risk_score(algo["final"]))

                if not names:
                    st.markdown(
                        f"<p style='color:#6b7280;margin-bottom:16px;'>No dataset results available for {_ALGO_LABELS[_k]}.</p>",
                        unsafe_allow_html=True,
                    )
                    continue

                fig = go.Figure()
                fig.add_trace(go.Bar(name="Before", x=names, y=before_vals, marker_color="#ef4444", marker_line_width=0, opacity=0.82, width=0.25))
                fig.add_trace(go.Bar(name="After",  x=names, y=after_vals,  marker_color="#22c55e", marker_line_width=0, opacity=0.82, width=0.25))
                fig.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                    line_width=1.5,
                    annotation_text=f"Threshold ({RISK_THRESHOLD})",
                    annotation_font_color="#f59e0b", annotation_font_size=11)
                fig.update_layout(
                    title={"text": f"{_ALGO_LABELS[_k]} — Before vs After", "x": 0.01, "xanchor": "left"},
                    height=320, **_PLOT,
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                    xaxis=_ax("Student"), yaxis=_ax("Risk Score"),
                    margin=dict(t=50, b=40, l=50, r=20),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"fig_before_after_{_k}")
        else:
            for _k, _color in _ALGO_COLORS.items():
                _r = active_res.get(_k, {})
                if _r.get("path") is None:
                    st.markdown(
                        f"<p style='color:#6b7280;margin-bottom:16px;'>{_ALGO_LABELS[_k]} did not produce a recovery path.</p>",
                        unsafe_allow_html=True,
                    )
                    continue

                before_risk = risk_score(start)
                after_risk  = risk_score(_r["final"])
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Before", x=[_ALGO_LABELS[_k]], y=[before_risk], marker_color="#ef4444", marker_line_width=0, opacity=0.82, width=0.4))
                fig.add_trace(go.Bar(name="After",  x=[_ALGO_LABELS[_k]], y=[after_risk],  marker_color="#22c55e", marker_line_width=0, opacity=0.82, width=0.4))
                fig.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                    line_width=1.5,
                    annotation_text=f"Threshold ({RISK_THRESHOLD})",
                    annotation_font_color="#f59e0b", annotation_font_size=11)
                fig.update_layout(
                    height=300, **_PLOT,
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                    xaxis=_ax("Algorithm"), yaxis=_ax("Risk Score"),
                    margin=dict(t=40, b=40, l=50, r=20),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"fig_before_after_{_k}")

        # ── Action Distribution ───────────────────────────────────────────────
        _best_key = next(k for k in ["astar", "greedy", "ucs"] if active_res.get(k, {}).get("path"))
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("activity", 13)} Action Distribution — {_ALGO_LABELS[_best_key]}</div>',
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
