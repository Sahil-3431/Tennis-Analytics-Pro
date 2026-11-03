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

# ==========================================
# SYSTEM THEME DETECTION
# ==========================================

def get_system_theme():
    try:
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(
            registry_key,
            "AppsUseLightTheme"
        )
        winreg.CloseKey(registry_key)
        return "Light" if value == 1 else "Dark"
    except Exception:
        return "Dark"

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

if "current_page" not in st.session_state:
    st.session_state.current_page = "Executive Dashboard"
if "theme" not in st.session_state:
    st.session_state.theme = get_system_theme()

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

