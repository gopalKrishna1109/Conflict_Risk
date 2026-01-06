import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# -----------------------------
# Page Config & Header
# -----------------------------
st.set_page_config(page_title="Conflict Risk Early Warning Dashboard", layout="wide")
st.title("Conflict Risk & Polarisation Early Warning Dashboard")

st.markdown("""
**Audience:** HR Directors, Chief People Officers, DEI Leaders, Employee Relations Teams  
**Core Value:** Detect internal conflict before it escalates into grievances, attrition, or legal exposure

This tool analyzes engagement survey responses and HR metrics to provide clear, department-level risk signals 
and preventive guidance — all in aggregate, with no individual identification.
""")

st.info("Responses are reviewed in aggregate only. The goal is learning and care, not judgment.")

# -----------------------------
# File Upload
# -----------------------------
st.header("Upload Your Data")

col1, col2 = st.columns(2)

with col1:
    survey_file = st.file_uploader(
        "Upload Survey Data",
        type=["csv"],
        help="File name: workplace_climate_survey.csv (with columns: response_id, department, timestamp, q1-q18, etc.)"
    )

with col2:
    hr_file = st.file_uploader(
        "Upload HR Metrics",
        type=["csv"],
        help="File name: hr_operational_metrics.csv (with columns: department, month, attrition_rate, etc.)"
    )

if not survey_file or not hr_file:
    st.warning("Please upload both CSV files to generate the dashboard.")
    st.stop()

# -----------------------------
# Load & Process Data
# -----------------------------
@st.cache_data
def load_and_process(survey_bytes, hr_bytes):
    survey_df = pd.read_csv(survey_bytes)
    hr_df = pd.read_csv(hr_bytes)

    # Survey preprocessing
    survey_df['timestamp'] = pd.to_datetime(survey_df['timestamp'])
    survey_df['month'] = survey_df['timestamp'].dt.to_period('M').astype(str)
    q_cols = [f'q{i}' for i in range(1, 19)]
    survey_df[q_cols] = survey_df[q_cols].apply(pd.to_numeric, errors='coerce')

    # Aggregations
    grouped = survey_df.groupby(['department', 'month'])
    agg_means = grouped[q_cols].mean()
    agg_stds = grouped[q_cols].std()

    volatility = agg_stds.mean(axis=1)
    trust_qs = ['q1','q2','q3','q4','q5','q15','q16','q17','q18']
    comm_qs = ['q6','q7','q8','q9','q10']
    change_qs = ['q11','q12','q13','q14']

    trust_mean = agg_means[trust_qs].mean(axis=1)
    comm_mean = agg_means[comm_qs].mean(axis=1)
    comm_std = agg_stds[comm_qs].mean(axis=1)
    change_mean = agg_means[change_qs].mean(axis=1)
    response_count = grouped.size()

    survey_agg = pd.concat([volatility, trust_mean, comm_mean, comm_std, change_mean, response_count], axis=1)
    survey_agg.columns = ['engagement_volatility','trust_mean','comm_mean','comm_std','change_mean','response_count']
    survey_agg = survey_agg.reset_index()

    # Merge HR
    hr_df['month'] = hr_df['month'].astype(str)
    full_df = pd.merge(survey_agg, hr_df, on=['department', 'month'], how='left')

    # CRI Components (simplified but aligned with logic)
    full_df['vol_score'] = np.interp(full_df['engagement_volatility'], 
                                    (full_df['engagement_volatility'].min(), full_df['engagement_volatility'].max()), (0, 100))
    full_df['trust_decline'] = full_df.groupby('department')['trust_mean'].diff().clip(upper=0).abs().fillna(0)
    full_df['trust_score'] = np.interp(full_df['trust_decline'], (0, full_df['trust_decline'].max()), (0, 100))
    full_df['comm_strain'] = (5 - full_df['comm_mean']) * full_df['comm_std']
    full_df['comm_score'] = np.interp(full_df['comm_strain'], (0, full_df['comm_strain'].max()), (0, 100))
    full_df['change_score'] = np.interp(full_df['change_mean'], (1, 5), (0, 100))

    hr_metrics = ['attrition_rate', 'absenteeism_rate', 'sick_days_avg', 'grievances_count', 'manager_escalations']
    for col in hr_metrics:
        full_df[col] = full_df[col].fillna(full_df[col].mean())
    full_df['hr_score'] = full_df[hr_metrics].mean(axis=1) / full_df[hr_metrics].max().max() * 100

    # Final CRI
    full_df['CRI'] = (
        full_df['vol_score'] * 0.30 +
        full_df['trust_score'] * 0.25 +
        full_df['comm_score'] * 0.20 +
        full_df['hr_score'] * 0.15 +
        full_df['change_score'] * 0.10
    ).round(1)

    def risk_level(cri):
        if cri <= 39: return "Low risk (Monitor)", "green"
        elif cri <= 69: return "Medium risk (Preventive attention recommended)", "orange"
        else: return "High risk (Support intervention advised)", "red"

    full_df['risk_level'], full_df['color'] = zip(*full_df['CRI'].apply(risk_level))
    return full_df

# Process data
with st.spinner("Processing data and calculating risk scores..."):
    results_df = load_and_process(survey_file, hr_file)

# -----------------------------
# Dashboard
# -----------------------------
st.header("Conflict Risk Dashboard")

# Latest scores
latest = results_df.sort_values('month').groupby('department').last().reset_index()
latest = latest.sort_values('CRI', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Department Risk Overview (Latest Period)")
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = latest['color'].map({"green": "#2e8540", "orange": "#ffb75d", "red": "#d93a3e"})
    bars = ax.barh(latest['department'], latest['CRI'], color=colors)
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.set_xlabel("Conflict Risk Index (CRI)")
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height()/2, f'{width}', va='center', fontweight='bold')
    st.pyplot(fig)

with col2:
    st.subheader("Latest Scores")
    display_table = latest[['department', 'month', 'CRI', 'risk_level', 'response_count']].copy()
    display_table = display_table.rename(columns={'response_count': 'Responses'})
    st.dataframe(display_table.style.format({'CRI': '{:.1f}'}), use_container_width=True)

# Trend
st.subheader("Organization-Wide CRI Trend Over Time")
trend = results_df.groupby('month')['CRI'].mean().reset_index()
fig2, ax2 = plt.subplots()
ax2.plot(trend['month'], trend['CRI'], marker='o', linewidth=3, color='#1f77b4')
ax2.set_ylim(0, 100)
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)

# -----------------------------
# Download Outputs
# -----------------------------
st.header("Download Results")

col1, col2 = st.columns(2)

with col1:
    csv = results_df.to_csv(index=False).encode()
    st.download_button(
        label="Download Detailed CRI Results (CSV)",
        data=csv,
        file_name=f"conflict_risk_results_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    # Placeholder for PDF report (can be expanded with ReportLab later)
    report_text = f"""
# Workplace Climate Support Summary – {datetime.now().strftime('%B %Y')}

**Organization Overview**  
Average CRI: {results_df['CRI'].mean():.1f}  
Departments monitored: {results_df['department'].nunique()}

**Highest Risk Department**: {latest.iloc[0]['department']} (CRI: {latest.iloc[0]['CRI']})  
Risk Level: {latest.iloc[0]['risk_level']}

Early attention can reduce downstream impacts on wellbeing and retention.
    """
    st.download_button(
        label="Download Executive Summary Report (TXT)",
        data=report_text,
        file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

st.success("Dashboard ready! All outputs are aggregated and non-identifying.")
st.caption("This positions the product as risk management, not culture war surveillance.")