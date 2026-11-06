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
from dashboard import venue_complex

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
# SESSION STATE
# ==========================================

if "color_theme" not in st.session_state:
    st.session_state.color_theme = "Ocean Blue"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Executive Dashboard"

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
elif page == "Data Quality":
    data_quality.show()
elif page == "Player Rankings":
    rankings.show()
elif page == "Performance Analysis":
    performance_analysis.show()
elif page == "Competitor Explorer":
    competitor.show()
elif page == "Country Analytics":
    country.show()
elif page == "SQL Analytics":
    sql_analytics.show()
elif page == "Insights & Recommendations":
    insights.show()
elif page == "Venue & Complex Analytics":
    venue_complex.show()

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
