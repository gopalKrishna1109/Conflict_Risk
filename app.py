import streamlit as st
from ui.layout import setup_page, render_header, render_footer, inject_css
from ui.sidebar import render_sidebar
from ui.tabs import render_tabs
from data.processor import process_data

# -----------------------------
# Page Setup
# -----------------------------
setup_page()
inject_css()
render_header()

# -----------------------------
# Fixed Footer - rendered early so it's always visible
# -----------------------------
render_footer()   

# -----------------------------
# Sidebar: Upload + Filters
# -----------------------------
survey_df, hr_df, filters = render_sidebar()

# -----------------------------
# Data Processing
# -----------------------------
results_df = process_data(
    survey_df=survey_df,
    hr_df=hr_df,
    agg_level=filters["agg_level"],
)


# -----------------------------
# Main Content
# -----------------------------
render_tabs(results_df, filters)

