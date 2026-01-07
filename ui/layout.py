import streamlit as st

def setup_page():
    st.set_page_config(
        page_title="Conflict Risk Early Warning Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def inject_css():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 360px !important;
            min-width: 360px !important;
        }
        .upload-panel {
            border: 2px dashed #555;
            border-radius: 10px;
            padding: 1rem;
            background: #1e1f24;
            margin-bottom: 1.2rem;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: #0e1117;
            color: #aaa;
            text-align: center;
            padding: 12px;
            font-size: 0.9rem;
            border-top: 1px solid #333;
            z-index: 999;
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

    with st.expander("ℹ️ Important: Privacy & Purpose", expanded=True):
        st.info("All data is processed in aggregate only. Individual responses are never identified.")

def render_footer():
    st.markdown("""
    <div class="footer">
        Conflict Risk & Polarisation Early Warning Dashboard • January 2026 • A compassionate early warning system
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)  # Spacer