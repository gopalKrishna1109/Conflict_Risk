import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def process_data(survey_df, hr_df, agg_level):
    group_key_map = {
        "Department": "department",
        "Role Level": "role_level",
        "Location": "location"
    }
    group_key = group_key_map[agg_level]

    q_all = [f"q{i}" for i in range(1, 19)]
    q_trust = ['q1','q2','q3','q4','q5','q15','q16','q17','q18']
    q_comm = ['q6','q7','q8','q9','q10']
    q_change = ['q11','q12','q13','q14']

    # Group and aggregate
    grouped = survey_df.groupby([group_key, 'month'])

    means = grouped[q_all].mean()
    stds = grouped[q_all].std()
    counts = grouped.size().rename("responses")

    agg_df = pd.concat([means.add_suffix('_mean'), stds.add_suffix('_std'), counts], axis=1)
    agg_df = agg_df.reset_index()

    # 1. Volatility
    agg_df["volatility_raw"] = agg_df[[f"{q}_std" for q in q_all]].mean(axis=1)
    agg_df["vol_score"] = np.clip((agg_df["volatility_raw"] - 1.0) / 1.0 * 100, 0, 100)

    # 2. Trust Decline (MoM per group)
    agg_df["trust_mean"] = agg_df[[f"{q}_mean" for q in q_trust]].mean(axis=1)
    agg_df = agg_df.sort_values([group_key, 'month'])
    agg_df["trust_delta"] = agg_df.groupby(group_key)["trust_mean"].diff()
    agg_df["trust_decline"] = (-agg_df["trust_delta"].clip(upper=0)).fillna(0)  # positive = decline
    agg_df["trust_score"] = np.clip(agg_df["trust_decline"] * 100, 0, 100)

    # 3. Communication Strain
    agg_df["comm_mean"] = agg_df[[f"{q}_mean" for q in q_comm]].mean(axis=1)
    agg_df["comm_std"] = agg_df[[f"{q}_std" for q in q_comm]].mean(axis=1)
    agg_df["comm_raw"] = (5 - agg_df["comm_mean"]) * agg_df["comm_std"]
    # Use fixed scale: max reasonable = (5-1)*2 = 8
    agg_df["comm_score"] = np.clip(agg_df["comm_raw"] / 8.0 * 100, 0, 100)

    # 4. HR Stress
    hr_metrics = ['attrition_rate', 'absenteeism_rate', 'sick_days_avg', 'grievances_count', 'manager_escalations']
    full_df = agg_df.copy()

    if agg_level == "Department" and 'department' in hr_df.columns:
        full_df = pd.merge(full_df, hr_df, left_on=['department', 'month'], right_on=['department', 'month'], how='left')

    # Fill with org-wide averages
    org_means = hr_df[hr_metrics].mean()
    org_stds = hr_df[hr_metrics].std()
    for col in hr_metrics:
        if col not in full_df.columns:
            full_df[col] = org_means.get(col, 0)
        full_df[col] = full_df[col].fillna(org_means.get(col, 0))

    # Z-scores
    full_df["hr_raw"] = 0
    for col in hr_metrics:
        z = (full_df[col] - org_means[col]) / (org_stds[col] + 1e-6)
        full_df["hr_raw"] += z / len(hr_metrics)
    full_df["hr_score"] = np.clip(full_df["hr_raw"] * 50, 0, 100)  # since avg z=0 → 0, +2 → 100

    # 5. Change Exposure
    full_df["change_mean"] = full_df[[f"{q}_mean" for q in q_change]].mean(axis=1)
    full_df["change_score"] = np.clip((full_df["change_mean"] - 2.0) / 2.0 * 100, 0, 100)

    # Final CRI
    full_df["CRI"] = (
        full_df["vol_score"] * 0.30 +
        full_df["trust_score"] * 0.25 +
        full_df["comm_score"] * 0.20 +
        full_df["hr_score"] * 0.15 +
        full_df["change_score"] * 0.10
    ).round(1)

    # Risk level
    def risk_level(cri):
        if cri <= 39:
            return "Low risk (Monitor)"
        elif cri <= 69:
            return "Medium risk (Preventive attention)"
        else:
            return "High risk (Intervention advised)"

    full_df["risk_level"] = full_df["CRI"].apply(risk_level)
    full_df["group"] = full_df[group_key]

    return full_df[[group_key, "group", "month", "responses", "CRI", "risk_level",
                    "vol_score", "trust_score", "comm_score", "hr_score", "change_score"]]