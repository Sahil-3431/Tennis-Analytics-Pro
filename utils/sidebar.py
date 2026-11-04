import streamlit as st
from utils.data_loader import load_tennis_data

def reset_global_filters():
    st.session_state["global_ranking"] = "All"
    st.session_state["global_country"] = "All"
    st.session_state["global_gender"] = "All"

PAGES = {
    "Executive Dashboard": "📊",
    "Player Rankings": "🏆",
    "Competitor Explorer": "🔍",
    "Country Analytics": "🌍",
    "Performance Analysis": "📈",
    "Data Quality": "🛡️",
    "Insights & Recommendations": "💡",
    "SQL Analytics": "🗄️"
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
                use_container_width=True
            ):
                st.session_state.current_page = page
                st.rerun()
        st.markdown("---")

        # ==========================================
        # GLOBAL ANALYTICS FILTERS
        # ==========================================

        st.caption("GLOBAL ANALYTICS FILTERS")
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

            st.selectbox(
                "Ranking Category",
                ranking_options,
                key="global_ranking"
            )
            st.selectbox(
                "Country",
                country_options,
                key="global_country"
            )
            st.selectbox(
                "Gender",
                gender_options,
                key="global_gender"
            )
            st.button(
                "Reset Global Filters",
                key="reset_global_filters",
                on_click=reset_global_filters,
                use_container_width=True
            )
        st.markdown("---")

        # ==========================================
        # THEME SELECTION
        # ==========================================

        st.caption("APPEARANCE")
        current_theme = st.session_state.get("theme_mode", "System")
        theme_options = ["System", "Dark", "Light"]
        selected_theme = st.selectbox(
            "Select Theme",
            theme_options,
            index=theme_options.index(current_theme),
            key="theme_selector",
            help="System automatically follows your device appearance preference."
        )
        if selected_theme != current_theme:
            st.session_state.theme_mode = selected_theme
            if selected_theme == "System":
                detected = st.session_state.get("system_theme", "Dark")
                st.session_state.theme = detected
            else:
                st.session_state.theme = selected_theme
            st.rerun()
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
