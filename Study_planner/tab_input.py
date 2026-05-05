import streamlit as st
import plotly.graph_objects as go

from student_model import (
    State, risk_score, RISK_THRESHOLD, is_goal,
    ALL_ACTIONS, heuristic,
)
from search import a_star_search
from styles import _icon
from runner import run_all_algorithms, run_single_algorithm
from components import _render_whatif_table, _PLOT, _ax, render_whatif_chart


@st.fragment
def _input_preview():
    col_form, col_preview = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown(
            f'<div class="input-section-title" style="margin-bottom:4px">'
            f'{_icon("user", 14, "#6b7280")} Student Identity</div>',
            unsafe_allow_html=True,
        )
        inp_name = st.text_input("Student name", key="inp_name", label_visibility="visible")

        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

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
            "Algorithm", ["A* Search", "Greedy Best-First", "Uniform Cost Search", "Run All"],
            key="algo_choice",
        )
        run_one = st.button("Run", type="primary", use_container_width=True, key="run_selected_manual")

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
        risk    = risk_score(preview_state)
        at_risk = risk > RISK_THRESHOLD
        rcolor  = "#dc2626" if at_risk else "#16a34a"
        bcls    = "badge-high" if at_risk else "badge-low"
        blbl    = "At Risk" if at_risk else "Safe"
        bar_pct = min(int(risk * 100 / RISK_THRESHOLD * 100), 100)

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

    # Handle button click — "Run All" dropdown option triggers run_all_algorithms
    if run_one:
        try:
            if is_goal(preview_state):
                existing = {"already_safe": True, "start": preview_state,
                            "name": inp_name.strip() or "Manual Student"}
                st.session_state.results["manual"] = existing
                st.session_state.last_source = "manual"
                st.session_state.last_run_scope = "manual"
                st.session_state._run_msg = "safe"
                st.rerun()

            existing = st.session_state.results.get("manual", {})
            for k in ["astar", "greedy", "ucs"]:
                if k not in existing:
                    existing[k] = {"path": None, "cost": None, "final": None,
                                   "metrics": {"expanded_nodes": 0, "runtime": 0.0}}

            if st.session_state.algo_choice == "Run All":
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

            _has_path = not existing.get("already_safe") and any(existing.get(k, {}).get("path") for k in ["astar", "greedy", "ucs"])
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


def render_tab_input(tab):
    with tab:
        _input_preview()

        # Reconstruct state from session state (for analyze button + What-If)
        _preview_state = State(
            attendance  = st.session_state.inp_attendance / 100,
            missing     = st.session_state.inp_missing,
            score       = st.session_state.inp_score,
            lms         = st.session_state.inp_lms / 100,
            study_hours = st.session_state.inp_study_hours,
            days        = st.session_state.inp_days,
            fatigue     = st.session_state.inp_fatigue,
        )

        # ── What-If Scenarios ─────────────────────────────────────────────────
        st.markdown('<div class="divider" style="margin-top:24px"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("flask-conical", 13)} What-If Scenarios (Optional)</div>',
            unsafe_allow_html=True,
        )
        st.caption("Simulate how recovery changes under different constraints using the current slider values as the starting point.")

        # Red-coloured What-If sliders
        st.markdown("""<style>
        /* Thumb circle */
        [data-testid="stSlider"]:has([aria-label="Max study hours"]) [role="slider"],
        [data-testid="stSlider"]:has([aria-label="Override deadline (days)"]) [role="slider"],
        [data-testid="stSlider"]:has([aria-label="Max classes to attend"]) [role="slider"],
        [data-testid="stSlider"]:has([aria-label="Max fatigue level"]) [role="slider"] {
            background: #dc2626 !important;
            border-color: #dc2626 !important;
        }
        /* Thumb value bubble */
        [data-testid="stSlider"]:has([aria-label="Max study hours"]) [data-testid="stSliderThumbValue"],
        [data-testid="stSlider"]:has([aria-label="Override deadline (days)"]) [data-testid="stSliderThumbValue"],
        [data-testid="stSlider"]:has([aria-label="Max classes to attend"]) [data-testid="stSliderThumbValue"],
        [data-testid="stSlider"]:has([aria-label="Max fatigue level"]) [data-testid="stSliderThumbValue"] {
            background: #dc2626 !important;
            color: #ffffff !important;
        }
        /* Filled track portion — Streamlit nests the active fill as the last child inside stSliderTrack > div */
        [data-testid="stSlider"]:has([aria-label="Max study hours"]) [data-testid="stSliderTrack"] > div > div,
        [data-testid="stSlider"]:has([aria-label="Override deadline (days)"]) [data-testid="stSliderTrack"] > div > div,
        [data-testid="stSlider"]:has([aria-label="Max classes to attend"]) [data-testid="stSliderTrack"] > div > div,
        [data-testid="stSlider"]:has([aria-label="Max fatigue level"]) [data-testid="stSliderTrack"] > div > div {
            background: #dc2626 !important;
        }
        /* Label text */
        [data-testid="stSlider"]:has([aria-label="Max study hours"]) label,
        [data-testid="stSlider"]:has([aria-label="Override deadline (days)"]) label,
        [data-testid="stSlider"]:has([aria-label="Max classes to attend"]) label,
        [data-testid="stSlider"]:has([aria-label="Max fatigue level"]) label {
            color: #dc2626 !important;
            font-weight: 600 !important;
        }
        </style>""", unsafe_allow_html=True)

        wi_form_col, _ = st.columns([3, 2], gap="large")
        with wi_form_col:
            st.markdown(
                f'<div class="input-section-title">'
                f'{_icon("calendar", 14, "#dc2626")} Time &amp; Schedule</div>',
                unsafe_allow_html=True,
            )
            wi_hours    = st.slider("Max study hours",          min_value=1, max_value=20, key="wi_hours",
                                    help="Cap the student's available study hours")
            wi_deadline = st.slider("Override deadline (days)", min_value=1, max_value=30, key="wi_deadline",
                                    help="Shrink the deadline to this many days")

            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="input-section-title">'
                f'{_icon("sliders-horizontal", 14, "#dc2626")} Activity Limits</div>',
                unsafe_allow_html=True,
            )
            wi_max_classes = st.slider("Max classes to attend", min_value=0, max_value=20, key="wi_max_classes",
                                       help="Limit how many class sessions can be attended")
            wi_max_fatigue = st.slider("Max fatigue level",    min_value=1, max_value=10, key="wi_max_fatigue",
                                       help="Block any action that would push fatigue above this")

            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="input-section-title">'
                f'{_icon("users", 14, "#dc2626")} Support</div>',
                unsafe_allow_html=True,
            )
            wi_no_tutor = st.checkbox("Tutor unavailable", key="wi_no_tutor")

            st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
            run_whatif_btn = st.button("Run What-If", type="primary", use_container_width=True, key="run_whatif_btn")

        if run_whatif_btn:
            with st.spinner("Running What-If scenarios — please wait..."):
                so = _preview_state
                po, co, fo, mo = a_star_search(so, ALL_ACTIONS, heuristic, is_goal)

                # Case 1: cap study hours
                s1 = State(so.attendance, so.missing, so.score, so.lms,
                           min(so.study_hours, wi_hours), so.days, so.fatigue)
                p1, c1x, f1, m1 = a_star_search(s1, ALL_ACTIONS, heuristic, is_goal)

                # Case 2: override deadline
                s2 = State(so.attendance, so.missing, so.score, so.lms,
                           so.study_hours, wi_deadline, 0)
                p2, c2x, f2, m2 = a_star_search(s2, ALL_ACTIONS, heuristic, is_goal)

                # Case 3: no tutor
                restricted = [a for a in ALL_ACTIONS if a.__name__ != "meet_tutor"] if wi_no_tutor else ALL_ACTIONS
                p3, c3x, f3, m3 = a_star_search(so, restricted, heuristic, is_goal)

                # Case 4: max classes to attend
                _orig_attend = next(a for a in ALL_ACTIONS if a.__name__ == "attend_class")
                _att_cap = min(1.0, so.attendance + wi_max_classes * 0.05)
                def _attend_capped(s, _orig=_orig_attend, _cap=_att_cap):
                    if s.attendance >= _cap:
                        return None
                    return _orig(s)
                _attend_capped.__name__ = "attend_class"
                actions4 = [_attend_capped if a.__name__ == "attend_class" else a for a in ALL_ACTIONS]
                p4, c4x, f4, m4 = a_star_search(so, actions4, heuristic, is_goal)

                # Case 5: max fatigue
                def _make_fatigue_capped(actions, max_f):
                    capped = []
                    for act in actions:
                        def _w(s, _a=act, _mf=max_f):
                            res = _a(s)
                            if res is None:
                                return None
                            ns, cost = res
                            return None if ns.fatigue > _mf else (ns, cost)
                        _w.__name__ = act.__name__
                        capped.append(_w)
                    return capped
                actions5 = _make_fatigue_capped(ALL_ACTIONS, wi_max_fatigue)
                p5, c5x, f5, m5 = a_star_search(so, actions5, heuristic, is_goal)

                st.session_state.whatif_results = {
                    "baseline": {"path": po, "cost": co, "final": fo, "nodes": mo["expanded_nodes"]},
                    "case1":    {"path": p1, "cost": c1x, "final": f1, "nodes": m1["expanded_nodes"],
                                 "label": f"Max {wi_hours}h study"},
                    "case2":    {"path": p2, "cost": c2x, "final": f2, "nodes": m2["expanded_nodes"],
                                 "label": f"{wi_deadline}-day deadline"},
                    "case3":    {"path": p3, "cost": c3x, "final": f3, "nodes": m3["expanded_nodes"],
                                 "label": "No tutor" if wi_no_tutor else "With tutor"},
                    "case4":    {"path": p4, "cost": c4x, "final": f4, "nodes": m4["expanded_nodes"],
                                 "label": f"Max {wi_max_classes} classes"},
                    "case5":    {"path": p5, "cost": c5x, "final": f5, "nodes": m5["expanded_nodes"],
                                 "label": f"Max fatigue {wi_max_fatigue}"},
                }

        wr = st.session_state.whatif_results
        if wr:
            st.markdown(
                f'<div class="sec-hdr" style="margin-top:12px">'
                f'{_icon("git-compare-arrows", 13)} Scenario Comparison</div>',
                unsafe_allow_html=True,
            )
            _render_whatif_table(wr)
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Cost Comparison</div>',
                unsafe_allow_html=True,
            )
            render_whatif_chart(wr, "fig_w_cost_comparison")
