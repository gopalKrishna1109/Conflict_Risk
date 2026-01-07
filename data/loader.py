import pandas as pd
import streamlit as st

@st.cache_data
def load_data(survey_bytes, hr_bytes):
    # Fixed: Removed invalid bracket syntax
    survey = pd.read_csv(survey_bytes)
    hr = pd.read_csv(hr_bytes)

    # Convert timestamp and extract month
    survey['timestamp'] = pd.to_datetime(survey['timestamp'], errors='coerce')
    survey['month'] = survey['timestamp'].dt.to_period('M').astype(str)

    # Convert survey questions to numeric
    q_cols = [f'q{i}' for i in range(1, 19)]
    survey[q_cols] = survey[q_cols].apply(pd.to_numeric, errors='coerce')

    # Ensure HR month is string
    hr['month'] = hr['month'].astype(str)

    return survey, hr