import streamlit as st
from utils.data_loader import load_tennis_data

def reset_global_filters():
    st.session_state["global_ranking"] = "All"
    st.session_state["global_country"] = "All"
    st.session_state["global_gender"] = "All"

PAGES = {
    "Executive Dashboard": "📊",
    "Data Quality": "🛡️",
    "Player Rankings": "🏆",
    "Performance Analysis": "📈",
    "Competitor Explorer": "🔍",
    "Venue & Complex Analytics":"🏟️",
    "Country Analytics": "🌍",
    "SQL Analytics": "🗄️",
    "Insights & Recommendations": "💡"
}

def render_sidebar():
    with st.sidebar:
        # BRANDING
        st.markdown(
            """
            <div class="brand-title">
                🎾 TENNIS PRO
            </div>
            <div class="brand-subtitle">
                GAME ANALYTICS PLATFORM
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")

        # ==========================================
        # COLOR THEME SELECTION
        # ==========================================

        st.markdown(
            """
            <div class="sidebar-section-title">
                <span>🎨</span> APPEARANCE SETTINGS
            </div>
            """,
            unsafe_allow_html=True
        )
        theme_options = [
            "Ocean Blue",
            "Pearl Light",
            "Aurora Teal",
            "Graphite Bronze",
            "Slate Mono"
        ]
        if "color_theme" not in st.session_state:
            st.session_state.color_theme = "Ocean Blue"
        with st.container(border=True):
            st.markdown("**Choose Your Theme**")
            st.selectbox(
                "Select Color Theme",
                theme_options,
                key="color_theme",
                label_visibility="collapsed"
            )
            st.caption("Customize your Tennis Analytics Pro experience.")
        st.markdown("---")
        st.caption("Page Navigation")

        # NAVIGATION
        for page, icon in PAGES.items():
            is_active = (st.session_state.get("current_page") == page)
            label = (
                f"● {icon} {page}"
                if is_active
                else f"{icon} {page}"
            )
            if st.button(
                label,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page
                st.rerun()
        st.markdown("---")

        # ==========================================
        # GLOBAL ANALYTICS FILTERS
        # ==========================================

        st.markdown(
            """
            <div class="sidebar-section-title">
                <span>⚙️</span> GLOBAL ANALYTICS FILTERS
            </div>
            """,
            unsafe_allow_html=True
        )
        global_df = load_tennis_data()
        if not global_df.empty:
            ranking_options = ["All"] + sorted(
                global_df["ranking_name"]
                .dropna()
                .unique()
                .tolist()
            )
            country_options = ["All"] + sorted(
                global_df["country"]
                .dropna()
                .unique()
                .tolist()
            )
            gender_options = ["All"] + sorted(
                global_df["gender"]
                .dropna()
                .unique()
                .tolist()
            )
            if "global_ranking" not in st.session_state:
                st.session_state["global_ranking"] = "All"
            if "global_country" not in st.session_state:
                st.session_state["global_country"] = "All"
            if "global_gender" not in st.session_state:
                st.session_state["global_gender"] = "All"

            with st.container(border=True):
                st.markdown("**🏆 Ranking Category**")
                st.selectbox(
                    "Ranking Category",
                    ranking_options,
                    key="global_ranking",
                    label_visibility="collapsed"
                )
                st.markdown("**🌍 Country**")
                st.selectbox(
                    "Country",
                    country_options,
                    key="global_country",
                    label_visibility="collapsed"
                )
                st.markdown("**👤 Gender**")
                st.selectbox(
                    "Gender",
                    gender_options,
                    key="global_gender",
                    label_visibility="collapsed"
                )
                st.button(
                    "↻ Reset Global Filters",
                    key="reset_global_filters",
                    on_click=reset_global_filters,
                    use_container_width=True,
                    type="secondary"
                )
        st.markdown("---")
        
        # FOOTER
        st.markdown(
            """
            <div style="font-size:12px; color:#94A3B8;">
                <b>Tennis Analytics Pro</b><br>
                Powered by SportRadar API<br><br>
                Project: Game Analytics<br>
                Team Project | 2026
            </div>
            """,
            unsafe_allow_html=True
        )
