import streamlit as st

def setup_page():
    st.set_page_config(
        page_title="Conflict Risk Early Warning Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def inject_css():
    st.markdown("""
    <style>
        /* Sidebar (keep your working styles) */
        section[data-testid="stSidebar"] > div:first-child {
            box-sizing: border-box !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {
            width: 6px !important;
        }
        section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }

        /* Main content */
        .block-container {
            max-width: 94% !important;
            padding-top: 2rem !important;
            padding-left: 4rem !important;
            padding-right: 4rem !important;
            padding-bottom: 100px !important;
        }

        /* Fixed footer - centered text, adjusts to main area */
        .custom-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: #0e1117;
            color: #aaa;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            border-top: 1px solid #333;
            z-index: 999;
            pointer-events: none;  /* Allows clicking through if needed */
        }

        /* When sidebar expanded: add left margin to footer to match main content */
        section[data-testid="stSidebar"]:not([aria-expanded="false"]) ~ [data-testid="stAppViewContainer"] .custom-footer,
        [data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stAppViewContainer"] .custom-footer {
            left: 360px !important;
            right: 0;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("<h1 style='text-align: center;'>Conflict Risk & Polarisation Early Warning Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #888;'>
    Audience: HR Directors, Chief People Officers, DEI Leaders<br>
    <strong>Core Value:</strong> Detect internal conflict before it escalates
    </p>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Important: Privacy & Purpose", expanded=False):
        st.info("All data is processed in aggregate only. Individual responses are never identified.")

    with st.expander("# 🚀 How to Use the Conflict Risk Early Warning Dashboard", expanded=False):
        
        st.markdown("""
        This tool helps HR leaders and people teams detect **early signals of workplace strain** using aggregated survey and HR data.

        **All data is processed anonymously and in aggregate only** — individual responses are never identified.
        """)

        st.info("Follow these steps to generate insights:")

        st.markdown("### Step 1: Download Templates")
        col1, col2, col3 = st.columns(3)
        with col1:
            with open("template_workplace_climate_survey.csv", "rb") as f:
                st.download_button(
                    "📄 Download Survey Template (CSV)",
                    f,
                    file_name="workplace_climate_survey_template.csv",
                    mime="text/csv"
                )
        with col2:
            with open("template_hr_operational_metrics.csv", "rb") as f:
                st.download_button(
                    "📊 Download HR Metrics Template (CSV)",
                    f,
                    file_name="hr_operational_metrics_template.csv",
                    mime="text/csv"
                )
        with col3:
            with open("survey_questions.txt", "rb") as f:
                st.download_button(
                    "❓ Download Survey Questions (TXT)",
                    f,
                    file_name="employee_survey_questions.txt",
                    mime="text/plain"
                )

        st.markdown("### Step 2: Collect Your Data")
        st.markdown("""
        - Use the **Survey Template** to collect anonymous employee responses collected using **survey questions** (1–5 scale).
        - Use the **HR Metrics Template** to input monthly operational data by department.
        - Refer to the **Survey Questions** file to ensure consistent wording.
        """)

        st.markdown("### Step 3: Upload Your Files")
        st.markdown("""
        Once ready:
        - Upload your filled **Workplace Climate Survey CSV** → top uploader
        - Upload your filled **HR Operational Metrics CSV** → bottom uploader

        The dashboard will instantly generate insights.
        """)

def render_footer():
    st.markdown("""
    <div class="custom-footer">
        Conflict Risk & Polarisation Early Warning Dashboard • January 2026 • A compassionate early warning system
    </div>
    """, unsafe_allow_html=True)
    