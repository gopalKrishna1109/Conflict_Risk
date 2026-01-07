import streamlit as st
from visuals.charts import plot_trend, plot_group_bar

def render_tabs(results_df, filters):
    if results_df.empty:
        st.warning("No results to display.")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Executive Overview",
        f"{filters['agg_level']} View",
        "Signal Drivers",
        "What This Means",
        "Recommended Actions"
    ])

    with tab1:
        st.subheader("Organization-Wide CRI Trend")
        plot_trend(results_df)

    with tab2:
        st.subheader(f"Current Risk Levels by {filters['agg_level']}")
        plot_group_bar(results_df)

    with tab3:
        st.dataframe(results_df.style.format({"CRI": "{:.1f}"}))

    with tab4:
        st.markdown("**Interpretation guide coming soon.**")

    with tab5:
        st.markdown("**Suggested interventions based on dominant signals will appear here.**")