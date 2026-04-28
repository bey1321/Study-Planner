import streamlit as st

from student_model import (
    generate_sample_data, load_students_csv, state_from_row,
    risk_score, RISK_THRESHOLD,
)
from styles import _icon
from runner import run_all_algorithms


def render_sidebar():
    """Render the sidebar and return the currently selected student index (or None)."""
    selected_idx = None

    with st.sidebar:
        st.markdown(
            f'<div class="sb-label">{_icon("database", 13)} Data Input</div>',
            unsafe_allow_html=True,
        )
        st.caption("Load a CSV dataset or generate sample data.")

        c1, c2 = st.columns(2)
        with c1:
            load_csv   = st.button("Load CSV",        use_container_width=True)
        with c2:
            gen_sample = st.button("Generate Sample", use_container_width=True)

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

        if st.session_state.df is not None:
            df = st.session_state.df
            options = []
            for i, row in df.iterrows():
                s    = state_from_row(row)
                r    = risk_score(s)
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
            with c1:
                run_sel     = st.button("Run",     use_container_width=True, type="primary", key="run_selected_dataset")
            with c2:
                run_all_btn = st.button("Run All", use_container_width=True, key="run_all_dataset")

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
                with st.spinner(f"Running A* for {name}..."):
                    res = run_all_algorithms(start)
                res["start"] = start
                res["name"]  = name
                st.session_state.results[selected_idx] = res
                st.session_state.last_source = "csv"
                st.session_state.last_run_scope = "single"
                st.rerun()

            if run_all_btn:
                with st.spinner("Running A* for all students..."):
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

    return selected_idx
