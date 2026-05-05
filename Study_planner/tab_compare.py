import streamlit as st
import plotly.graph_objects as go

from student_model import risk_score, RISK_THRESHOLD
from styles import _icon
from components import _PLOT, _ax


_ALGO_LABELS = {"astar": "A* Search", "greedy": "Greedy Best-First", "ucs": "UCS"}
_ALGO_COLORS = {"astar": "#4f46e5",   "greedy": "#f59e0b",           "ucs": "#0891b2"}


def _any_path(v):
    return any(v.get(k, {}).get("path") is not None for k in ["astar", "greedy", "ucs"])


def render_tab_compare(tab, active_res):
    with tab:
        if not active_res:
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-icon-wrap">{_icon("git-compare-arrows", 24, "#9ca3af")}</div>
                <h3>No comparison data</h3>
                <p>Run an analysis first to compare A*, Greedy, and UCS.</p>
            </div>""", unsafe_allow_html=True)
            return

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

        if not _any_path(active_res):
            return

        # ── Before vs After bar chart ─────────────────────────────────────────
        algo_labels, before_vals, after_vals = [], [], []
        for key in ["astar", "greedy", "ucs"]:
            algo = active_res.get(key, {})
            if algo.get("path") is None:
                continue
            algo_labels.append(_ALGO_LABELS[key])
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

        # ── Risk progression line chart ───────────────────────────────────────
        fig_prog = go.Figure()
        marker_symbols = {"astar": "circle", "greedy": "square", "ucs": "diamond"}
        line_styles    = {"astar": "solid",  "greedy": "dash",   "ucs": "dot"}
        for key, color in [("astar", "#4f46e5"), ("greedy", "#f59e0b"), ("ucs", "#0891b2")]:
            algo = active_res.get(key, {})
            if algo.get("path") is None:
                continue
            progression = [risk_score(active_res["start"])] + [risk_score(s) for _, s in algo["path"]]
            fig_prog.add_trace(go.Scatter(
                x=list(range(len(progression))), y=progression,
                name=_ALGO_LABELS[key], mode="lines+markers",
                line=dict(color=color, width=3, dash=line_styles[key]),
                marker=dict(size=8, color=color, symbol=marker_symbols[key], line=dict(width=1, color="white")),
            ))
        if fig_prog.data:
            fig_prog.add_hline(y=RISK_THRESHOLD, line_dash="dot", line_color="#f59e0b",
                line_width=1.5,
                annotation_text=f"Threshold ({RISK_THRESHOLD})",
                annotation_font_color="#f59e0b", annotation_font_size=11,
                annotation_position="top right")
            fig_prog.update_layout(
                title={"text": "Risk Progression — All Algorithms", "x": 0.01, "xanchor": "left", "y": 0.95},
                height=360, **_PLOT,
                legend=dict(orientation="h", x=0, xanchor="left", y=-0.18, yanchor="top",
                    bgcolor="rgba(255,255,255,.85)", bordercolor="#e5e7eb", borderwidth=1),
                xaxis=_ax("Step"), yaxis=_ax("Risk Score"),
                margin=dict(t=80, b=70, l=50, r=20),
            )
            st.plotly_chart(fig_prog, use_container_width=True, key="fig_threshold_progression")

        # ── Analysis text ─────────────────────────────────────────────────────
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
            an = active_res["astar"]["metrics"]["expanded_nodes"]
            un = active_res["ucs"]["metrics"]["expanded_nodes"]
            lines.append(f"<strong>A*</strong> expanded <strong>{an}</strong> nodes vs UCS's <strong>{un}</strong> nodes.")
            if an < un:
                lines.append(f"The heuristic saved A* from expanding <strong>{un - an}</strong> unnecessary nodes.")
        lines.append("<strong>Key takeaway:</strong> A* combines UCS's optimality with Greedy's speed via an informed heuristic.")
        st.markdown(
            f'<div class="analysis-block">{"".join(f"<p>{l}</p>" for l in lines)}</div>',
            unsafe_allow_html=True,
        )
