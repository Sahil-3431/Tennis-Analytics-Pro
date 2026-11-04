import streamlit as st
from utils.styling import apply_theme
from utils.sidebar import render_sidebar
from dashboard import overview
from dashboard import rankings
from dashboard import competitor
from dashboard import country
from dashboard import insights
from dashboard import sql_analytics
from dashboard import performance_analysis
from dashboard import data_quality
from pathlib import Path
import streamlit.components.v1 as components

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Tennis Analytics Pro",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SYSTEM THEME DETECTION
# ==========================================

theme_detector = components.declare_component(
    "theme_detector",
    path=str(
        Path(__file__).parent
        / "components"
        / "theme_detector"
    )
)

# ==========================================
# SESSION STATE
# ==========================================

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "System"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Executive Dashboard"

# Get live browser / OS theme preference
detected_theme = theme_detector(
    default="Dark",
    key="system_theme_detector"
)
if detected_theme not in ["Light", "Dark"]:
    detected_theme = "Dark"
st.session_state.system_theme = detected_theme

# Apply manual or automatic theme
if st.session_state.theme_mode == "System":
    st.session_state.theme = detected_theme
else:
    st.session_state.theme = st.session_state.theme_mode

# ==========================================
# APPLY DESIGN
# ==========================================

apply_theme()

# ==========================================
# SIDEBAR
# ==========================================

render_sidebar()

# ==========================================
# PAGE ROUTING
# ==========================================

page = st.session_state.current_page

if page == "Executive Dashboard":
    overview.show()
elif page == "Player Rankings":
    rankings.show()
elif page == "Competitor Explorer":
    competitor.show()
elif page == "Country Analytics":
    country.show()
elif page == "Performance Analysis":
    performance_analysis.show()
elif page == "Data Quality":
    data_quality.show()
elif page == "Insights & Recommendations":
    insights.show()
elif page == "SQL Analytics":
    sql_analytics.show()

# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="dashboard-footer">
        Tennis Analytics Pro |
        Powered by SportRadar API |
        Team Project 2026
    </div>
    """,
    unsafe_allow_html=True
)
