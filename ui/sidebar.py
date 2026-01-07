import streamlit as st
from data.loader import load_data

def render_sidebar():
    with st.sidebar:
        st.header("📁 Data Upload")

        survey_file = st.file_uploader(
            "Workplace Climate Survey CSV",
            type=["csv"],
            key="survey"
        )
        hr_file = st.file_uploader(
            "HR Operational Metrics CSV",
            type=["csv"],
            key="hr"
        )

        if not survey_file or not hr_file:
            st.warning("Both files are required to generate insights.")
            st.stop()

        # Load full data (unfiltered)
        survey_df, hr_df = load_data(survey_file, hr_file)

        st.markdown("---")

        st.header("⚙️ Filters & Settings")

        # Get unique values from full data
        months = sorted(survey_df['month'].unique())
        departments = sorted(survey_df['department'].unique())
        roles = sorted(survey_df['role_level'].unique())
        locations = sorted(survey_df['location'].unique())

        selected_months = st.multiselect("Select months", months, default=months[-3:])  # last 3 by default
        selected_depts = st.multiselect("Departments", departments, default=departments)
        selected_roles = st.multiselect("Role Levels", roles, default=roles)
        selected_locations = st.multiselect("Locations", locations, default=locations)

        agg_level = st.radio("Aggregate results by", ["Department", "Role Level", "Location"], index=0)

    filters = {
        "months": selected_months,
        "departments": selected_depts,
        "roles": selected_roles,
        "locations": selected_locations,
        "agg_level": agg_level
    }

    # Apply filters only to survey data
    filtered_survey = survey_df[
        (survey_df['month'].isin(selected_months)) &
        (survey_df['department'].isin(selected_depts)) &
        (survey_df['role_level'].isin(selected_roles)) &
        (survey_df['location'].isin(selected_locations))
    ]

    if filtered_survey.empty:
        st.warning("No data matches your filters. Please adjust.")
        st.stop()

    # Return filtered survey + full hr 
    return filtered_survey, hr_df, filters