import pandas as pd
import streamlit as st

@st.cache_data
def load_data(survey_bytes, hr_bytes):
    try:
        survey = pd.read_csv(survey_bytes)
        hr = pd.read_csv(hr_bytes)
    except Exception as e:
        st.error(f"Error reading CSV files: {e}")
        st.stop()

    # === Survey Validation ===
    required_survey_cols = ['department', 'role_level', 'location'] + [f'q{i}' for i in range(1, 19)]
    missing_survey = [col for col in required_survey_cols if col not in survey.columns]
    if missing_survey:
        st.error(f"Survey CSV is missing required columns: {', '.join(missing_survey)}")
        st.stop()

    # Handle timestamp
    if 'timestamp' not in survey.columns:
        st.error("Survey CSV is missing 'timestamp' column.")
        st.stop()

    survey['timestamp'] = pd.to_datetime(survey['timestamp'], errors='coerce')
    if survey['timestamp'].isna().all():
        st.error("All timestamps are invalid. Please use format like YYYY-MM-DD or MM/DD/YYYY.")
        st.stop()

    survey['month'] = survey['timestamp'].dt.to_period('M').astype(str)

    # Convert q1-q18 to numeric, coerce errors
    q_cols = [f'q{i}' for i in range(1, 19)]
    survey[q_cols] = survey[q_cols].apply(pd.to_numeric, errors='coerce')

    # Count invalid entries per row
    invalid_per_row = survey[q_cols].isna().sum(axis=1)
    invalid_rows = (invalid_per_row > 0).sum()

    if invalid_rows > 0:
        st.warning(f"{invalid_rows} survey rows contain non-numeric scores (converted to NaN). "
               f"Check your data for text in question columns.")

    # Warn if many invalid responses
    invalid_responses = survey[q_cols].isna().all(axis=1).sum()
    if invalid_responses > 0:
        st.warning(f"{invalid_responses} survey rows have no valid scores and will be ignored.")

    survey = survey.dropna(subset=q_cols, how='all')  # Drop completely empty responses

    # === HR Validation ===
    required_hr_cols = ['department', 'month']
    missing_hr = [col for col in required_hr_cols if col not in hr.columns]
    if missing_hr:
        st.error(f"HR Metrics CSV is missing required columns: {', '.join(missing_hr)}")
        st.stop()

    hr['month'] = hr['month'].astype(str)

    # Optional: fill missing numeric metrics with 0 or warn
    numeric_cols = ['attrition_rate', 'absenteeism_rate', 'sick_days_avg', 'grievances_count', 'manager_escalations']
    for col in numeric_cols:
        if col in hr.columns:
            hr[col] = pd.to_numeric(hr[col], errors='coerce').fillna(0)

    st.success("Data loaded successfully!")
    return survey, hr