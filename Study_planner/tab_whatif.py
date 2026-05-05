import streamlit as st

from styles import _icon
from components import _render_whatif_table, render_whatif_chart


def render_tab_whatif(tab):
    with tab:
        wr = st.session_state.whatif_results
        if not wr:
            st.markdown(f"""
            <div class="empty-state">
                <div class="empty-icon-wrap">{_icon("flask-conical", 24, "#9ca3af")}</div>
                <h3>No What-If results yet</h3>
                <p>Go to <strong>Student Input</strong>, set constraints at the bottom, and click <strong>Run What-If</strong>.</p>
            </div>""", unsafe_allow_html=True)
            return

        st.markdown(
            f'<div class="sec-hdr">{_icon("flask-conical", 13)} What-If Results</div>',
            unsafe_allow_html=True,
        )
        _render_whatif_table(wr)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-hdr">{_icon("bar-chart-2", 13)} Cost Comparison</div>',
            unsafe_allow_html=True,
        )
        render_whatif_chart(wr, "fig_w5_cost_comparison")
