import streamlit as st
import plotly.graph_objects as go

from student_model import risk_score, RISK_THRESHOLD, ACTION_DESCRIPTIONS
from styles import _icon


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


def _delta(new_c, base_c):
    if new_c is None or base_c is None:
        return ""
    d = new_c - base_c
    if d > 0:
        return f'<span class="wi-delta-up">{_icon("arrow-up", 11, "#dc2626")} +{d:.2f}</span>'
    if d < 0:
        return f'<span class="wi-delta-dn">{_icon("arrow-down", 11, "#16a34a")} {d:.2f}</span>'
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


def _plan_preview(path):
    if not path:
        return f'{_icon("circle-x", 12, "#dc2626")} Infeasible'
    steps = [ACTION_DESCRIPTIONS.get(a, a) for a, _ in path]
    mono = "font-family:'JetBrains Mono',monospace;font-size:0.74rem"
    if len(steps) == 1:
        return f'<span style="{mono};color:#374151">{steps[0]}</span>'
    items = "".join(
        f'<div style="padding:2px 0;color:#374151;{mono}">{i+1}. {s}</div>'
        for i, s in enumerate(steps)
    )
    return (
        f'<details style="{mono}">'
        f'<summary style="cursor:pointer;color:#4f46e5;font-weight:600;list-style:none">'
        f'{steps[0]} <span style="color:#9ca3af;font-weight:400">+{len(steps)-1} more</span>'
        f'</summary>'
        f'<div style="margin-top:6px;padding-left:8px;border-left:2px solid #e5e7eb">'
        f'{items}'
        f'</div>'
        f'</details>'
    )


def _render_whatif_table(wr):
    all_keys = ["baseline", "case1", "case2", "case3"]
    if "case4" in wr:
        all_keys += ["case4", "case5"]
    label_map = {
        "baseline": "Baseline (no constraints)",
        "case1": wr["case1"]["label"],
        "case2": wr["case2"]["label"],
        "case3": wr["case3"]["label"],
    }
    if "case4" in wr:
        label_map["case4"] = wr["case4"]["label"]
        label_map["case5"] = wr["case5"]["label"]

    rows_html = ""
    for key in all_keys:
        c = wr[key]
        path, cost, final = c["path"], c["cost"], c.get("final")
        label = label_map[key]
        row_bg = "background:#f5f3ff;" if key == "baseline" else ""

        if path is not None and cost is not None:
            r_after = risk_score(final) if final else None
            r_color = "#dc2626" if r_after is not None and r_after > RISK_THRESHOLD else "#16a34a"
            r_str = (
                f'<span style="color:{r_color};font-weight:600;'
                f'font-family:\'JetBrains Mono\',monospace">{r_after:.3f}</span>'
                if r_after is not None else "—"
            )
            rows_html += (
                f"<tr style='{row_bg}'>"
                f"<td class='td-name'>{label}</td>"
                f"<td style=\"font-family:'JetBrains Mono',monospace\">{cost:.2f}</td>"
                f"<td>{r_str}</td>"
                f"<td style=\"font-family:'JetBrains Mono',monospace\">{len(path)}</td>"
                f"<td>{_plan_preview(path)}</td>"
                f"</tr>"
            )
        else:
            rows_html += (
                f"<tr>"
                f"<td class='td-name'>{label}</td>"
                f"<td class='td-muted'>N/A</td>"
                f"<td class='td-muted'>—</td>"
                f"<td class='td-muted'>—</td>"
                f"<td class='td-goal-n'>{_icon('circle-x', 12, '#dc2626')} Infeasible</td>"
                f"</tr>"
            )

    st.markdown(f"""
    <div class="comp-wrap">
        <table class="comp-table">
            <thead><tr>
                <th>Scenario</th><th>Cost</th><th>Risk After</th><th>Steps</th><th>Plan Preview</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)


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


def render_whatif_chart(wr, chart_key):
    wi_keys = ["baseline", "case1", "case2", "case3"] + (["case4", "case5"] if "case4" in wr else [])
    wi_labels = {
        "baseline": "Baseline",
        "case1": wr["case1"]["label"], "case2": wr["case2"]["label"],
        "case3": wr["case3"]["label"],
        **({} if "case4" not in wr else {
            "case4": wr["case4"]["label"], "case5": wr["case5"]["label"],
        }),
    }
    scenarios = [wi_labels[k] for k in wi_keys]
    costs     = [wr[k]["cost"] or 0 for k in wi_keys]
    colors    = ["#4f46e5"] + ["#22c55e" if wr[k]["cost"] else "#ef4444" for k in wi_keys[1:]]
    fig = go.Figure(go.Bar(
        x=scenarios, y=costs, marker_color=colors,
        marker_line_width=0, opacity=0.88,
        text=[f"{c:.2f}" if c else "N/A" for c in costs],
        textposition="outside", textfont=dict(color="#6b7280", size=11),
    ))
    fig.update_layout(
        height=300, **_PLOT,
        yaxis=_ax("Total Cost"), xaxis=_ax(),
        margin=dict(t=30, b=30, l=50, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, key=chart_key)
