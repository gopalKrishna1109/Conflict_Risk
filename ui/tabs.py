import streamlit as st
from visuals.charts import plot_trend, plot_group_bar, plot_radar
from io import BytesIO

def render_tabs(results_df, filters):
    if results_df.empty:
        st.warning("No results to display with current filters.")
        return

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Executive Overview",
        f"{filters['agg_level']} View",
        "Component Drivers",      
        "Signal Drivers",
        "What This Means",
        "Recommended Actions"
    ])

    with tab1:
        st.subheader("Executive Summary")

        if results_df.empty:
            st.info("Upload data and apply filters to see executive metrics.")
        else:
            # Get latest month data
            latest_month = results_df['month'].max()
            current = results_df[results_df['month'] == latest_month]

            # Previous month for trend
            months_sorted = sorted(results_df['month'].unique())
            prev_month = months_sorted[-2] if len(months_sorted) > 1 else None
            previous = results_df[results_df['month'] == prev_month] if prev_month else None

            # Calculations
            overall_cri = current['CRI'].mean()
            high_risk_count = len(current[current['CRI'] >= 70])
            medium_risk_count = len(current[(current['CRI'] >= 40) & (current['CRI'] < 70)])
            total_groups = len(current)

            # Trend calculation
            if previous is not None and not previous.empty:
                prev_avg = previous['CRI'].mean()
                curr_avg = overall_cri
                if abs(curr_avg - prev_avg) < 1:
                    trend = "→"
                    trend_text = "Stable"
                elif curr_avg > prev_avg:
                    trend = "↑"
                    trend_text = "Increasing"
                else:
                    trend = "↓"
                    trend_text = "Decreasing"
            else:
                trend = "→"
                trend_text = "No prior data"

            # Metric Cards using columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="Overall Average CRI",
                    value=f"{overall_cri:.1f}",
                    delta=None
                )

            with col2:
                st.metric(
                    label="High Risk Groups",
                    value=high_risk_count,
                    delta=f"{high_risk_count}/{total_groups} groups" if total_groups > 0 else None
                )

            with col3:
                st.metric(
                    label="Medium Risk Groups",
                    value=medium_risk_count,
                    delta=f"{medium_risk_count}/{total_groups} groups" if total_groups > 0 else None
                )

            with col4:
                st.metric(
                    label="Trend (MoM)",
                    value=trend_text,
                    delta=trend
                )

            # Trend chart below metrics
            st.markdown("### Organization-Wide CRI Trend")
            fig_trend = plot_trend(results_df)  # Now returns fig
            if fig_trend:
                buf = BytesIO()
                fig_trend.savefig(buf, format="png", bbox_inches='tight', dpi=200)
                buf.seek(0)
                st.download_button(
                    label="📥 Download Trend Chart",
                    data=buf,
                    file_name="cri_trend.png",
                    mime="image/png",
                    use_container_width=True
                )

    with tab2:
        st.subheader(f"Current Risk Levels by {filters['agg_level']}")
        fig_bar = plot_group_bar(results_df)  # Returns fig
        if fig_bar:
            buf = BytesIO()
            fig_bar.savefig(buf, format="png", bbox_inches='tight', dpi=200)
            buf.seek(0)
            st.download_button(
                label="📥 Download Risk Levels Chart",
                data=buf,
                file_name="risk_levels.png",
                mime="image/png",
                use_container_width=True
            )

    with tab3:  
        st.header("Component Drivers")
        st.markdown("""
        Visual breakdown of the five signals contributing to the highest current CRI.
        
        The larger the area, the stronger the contribution to workplace strain.
        """)

        if results_df.empty:
            st.info("Upload data and apply filters to see component drivers.")
        else:
            # Show radar for highest-risk group
            fig_radar = plot_radar(results_df)  # Returns fig
            if fig_radar:
                buf = BytesIO()
                fig_radar.savefig(buf, format="png", bbox_inches='tight', dpi=200)
                buf.seek(0)
                st.download_button(
                    label="📥 Download Radar Chart",
                    data=buf,
                    file_name="component_drivers.png",
                    mime="image/png",
                    use_container_width=True
                )

            # Table for exact values
            latest = results_df.sort_values('month').groupby('group').last()
            high_risk_row = latest.sort_values('CRI', ascending=False).iloc[0]
            group_name = high_risk_row.name

            st.markdown(f"#### Current Scores — **{group_name}**")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Polarization & Instability", f"{high_risk_row['vol_score']:.1f}")
            with col2:
                st.metric("Declining Trust & Safety", f"{high_risk_row['trust_score']:.1f}")
            with col3:
                st.metric("Communication Strain", f"{high_risk_row['comm_score']:.1f}")
            with col4:
                st.metric("HR Operational Stress", f"{high_risk_row['hr_score']:.1f}")
            with col5:
                st.metric("Rapid Change Impact", f"{high_risk_row['change_score']:.1f}")

    with tab4:
        st.subheader("Detailed Signal Data")

        display_df = results_df.copy()
        agg_col = filters["agg_level"].lower().replace(" ", "_")
        if agg_col in display_df.columns and 'group' in display_df.columns:
            if (display_df[agg_col] == display_df['group']).all():
                display_df = display_df.drop(columns=['group'])
        
        # Rename for consistency
        display_df = display_df.rename(columns={agg_col: "Group"})
        styled = display_df.style.format({
            "CRI": "{:.1f}",
            "vol_score": "{:.1f}",
            "trust_score": "{:.1f}",
            "comm_score": "{:.1f}",
            "hr_score": "{:.1f}",
            "change_score": "{:.1f}",
        })
        st.dataframe(styled, use_container_width=True)

    with tab5:
        st.header("What This Means")
        st.markdown("""
        This dashboard detects **early signals of workplace strain** — not failure, but opportunities for support.
        """)

        # Find highest risk group
        latest = results_df.sort_values('month').groupby('group').last()
        if not latest.empty:
            high_risk = latest.sort_values('CRI', ascending=False).iloc[0]
            group_name = high_risk.name
            cri = high_risk['CRI']
            risk_level = high_risk['risk_level']

            st.markdown(f"### Highest Signal: **{group_name}** (CRI {cri:.1f} — {risk_level})")

            # Rank components
            components = {
                "Polarization & Instability": high_risk['vol_score'],
                "Declining Trust & Safety": high_risk['trust_score'],
                "Communication Strain": high_risk['comm_score'],
                "HR Operational Stress": high_risk['hr_score'],
                "Rapid Change Impact": high_risk['change_score'],
            }
            top_components = sorted(components.items(), key=lambda x: x[1], reverse=True)[:2]

            st.markdown("**Dominant signals:**")
            for name, score in top_components:
                if score > 20:  # Only mention meaningful contributors
                    st.markdown(f"- **{name}** (contributing {score:.0f}% to CRI)")

            if cri <= 39:
                st.success("Overall low risk — healthy collaboration and stability detected. Continue monitoring.")
            elif cri <= 69:
                st.warning("Emerging strain detected. Patterns suggest growing friction that could escalate if unaddressed.")
            else:
                st.error("Elevated risk — multiple signals indicate significant strain. Proactive support recommended.")

    with tab6:
        st.header("Recommended Actions")
        st.markdown("Suggestions are **preventive and supportive**, focused on rebuilding connection and clarity.")

        if 'high_risk' not in locals():
            st.info("Upload data and apply filters to see tailored recommendations.")
        else:
            st.markdown(f"#### Focus Area: **{group_name}**")

            recs = []
            for name, score in top_components:
                if score <= 20:
                    continue
                if "Polarization" in name:
                    recs.append("• Host structured listening sessions to surface differing views safely")
                    recs.append("• Use anonymous pulse checks to reduce fear of speaking up")
                elif "Trust" in name:
                    recs.append("• Leadership roundtables to model vulnerability and transparency")
                    recs.append("• Reinforce psychological safety in team norms")
                elif "Communication" in name:
                    recs.append("• Improve meeting practices (e.g., clearer agendas, inclusive turn-taking)")
                    recs.append("• Cross-team syncs to reduce silos")
                elif "HR Operational" in name:
                    recs.append("• Review workload distribution and burnout indicators")
                    recs.append("• Offer flexible support (mental health days, EAP promotion)")
                elif "Change" in name:
                    recs.append("• Increase communication about ongoing changes and rationale")
                    recs.append("• Create feedback channels for change-related concerns")

            if recs:
                for rec in recs[:4]:  # Limit to top 4
                    st.markdown(rec)
            else:
                st.success("No urgent actions needed — maintain current supportive practices.")

            st.caption("All recommendations are general. Tailor to your organization's context with care and empathy.")