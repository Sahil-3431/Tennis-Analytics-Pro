import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import get_connection
from utils.global_filters import apply_global_filters
from utils.styling import (
    render_section_header,
    apply_chart_theme,
    render_dataframe
)

# =====================================================
# LOAD RANKING DATA
# =====================================================

@st.cache_data(show_spinner="Loading player rankings...")
def load_rankings():
    conn = get_connection()
    try:
        query = """
        SELECT
            c.competitor_id,
            c.competitor_name,
            c.abbreviation,
            c.country,
            c.country_code,
            d.rank,
            d.movement,
            d.points,
            d.competitions_played,
            d.ranking_snapshot_id,
            s.ranking_name,
            s.gender
        FROM DoublesRankings d
        INNER JOIN Competitors c
            ON d.competitor_id = c.competitor_id
        INNER JOIN RankingSnapshots s
            ON d.ranking_snapshot_id = s.ranking_snapshot_id
        ORDER BY d.rank ASC
        """
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # Numeric data validation
    for column in [
        "rank",
        "movement",
        "points",
        "competitions_played"
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )
    df["ranking_name"] = (
        df["ranking_name"]
        .fillna("Unknown")
        .astype(str)
        .str.upper()
    )
    df["competitor_name"] = (
        df["competitor_name"]
        .fillna("Unknown Player")
    )
    df["country_display"] = (
        df["country"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )
    return df

# =====================================================
# PLAYER RANKINGS PAGE
# =====================================================

def show():
    st.title("🏆 Player Rankings")
    st.markdown(
        """
        Explore and analyze player rankings across different categories, countries, and individual players."""
    )

    # =================================================
    # LOAD DATABASE
    # =================================================

    try:
        df = load_rankings()
    except Exception as e:
        st.error(f"Ranking data loading failed: {e}")
        st.stop()
    if df.empty:
        st.warning("No player ranking data available.")
        st.stop()

    # Apply global sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No ranking records match the global filters.")
        return
    
    # Remove invalid ranking rows
    df = df.dropna(subset=["rank", "points"]).copy()
    if df.empty:
        st.warning("No valid ranking records available.")
        st.stop()

    # =================================================
    # RANKING FILTERS
    # =================================================

    render_section_header(
        "Ranking Explorer",
        "Filter and explore player rankings by category, country and player name.",
        "🔎"
    )
    col1, col2, col3, col4 = st.columns(4)
    ranking_options = sorted(df["ranking_name"].unique().tolist())
    with col1:
        selected_type = st.selectbox(
            "Ranking Category",
            ranking_options,
            key="rank_category"
        )
    with col2:
        selected_limit = st.selectbox(
            "Leaderboard",
            ["Top 10", "Top 20", "Top 50", "All"],
            key="rank_limit"
        )
    ranking_df = df[df["ranking_name"] == selected_type].copy()
    country_options = ["All"] + sorted(ranking_df["country_display"].unique().tolist())
    with col3:
        selected_country = st.selectbox(
            "Country",
            country_options,
            key="rank_country"
        )
    with col4:
        search_player = st.text_input(
            "Search Player",
            placeholder="Enter player name...",
            key="rank_search"
        )

    # =================================================
    # APPLY FILTERS
    # =================================================

    if selected_country != "All":
        ranking_df = ranking_df[ranking_df["country_display"] == selected_country]
    if search_player.strip():
        ranking_df = ranking_df[
            ranking_df["competitor_name"]
            .str.contains(
                search_player.strip(),
                case=False,
                na=False
            )
        ]
    # Remove duplicate player records within snapshot
    ranking_df = (
        ranking_df.sort_values("rank")
        .drop_duplicates(
            subset=["ranking_snapshot_id", "competitor_id"]
        )
    )

    # =================================================
    # TOP N LEADERBOARD
    # =================================================

    if selected_limit != "All":
        limit = int(selected_limit.replace("Top ", ""))
        ranking_df = ranking_df.head(limit)
    ranking_df = ranking_df.sort_values(["rank", "points"],ascending=[True, False]).copy()
    st.divider()
    if ranking_df.empty:
        st.warning("No players found for the selected filters.")
        return

    # =================================================
    # KPI CALCULATIONS
    # =================================================

    total_players = ranking_df["competitor_id"].nunique()
    average_points = ranking_df["points"].mean()
    highest_points = ranking_df["points"].max()
    best_rank = ranking_df["rank"].min()
    total_competitions = ranking_df["competitions_played"].sum()

    # =================================================
    # KPI DISPLAY
    # =================================================

    render_section_header(
        f"{selected_type} Ranking Overview",
        "Key performance indicators for the selected ranking category.",
        "📊"
    )
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Players Displayed",
        f"{total_players:,}"
    )
    k2.metric(
        "Average Points",
        f"{average_points:,.1f}"
    )
    k3.metric(
        "Highest Points",
        f"{highest_points:,.0f}"
    )
    k4.metric(
        "Best Rank",
        f"#{best_rank:,.0f}"
    )
    st.divider()

    # =================================================
    # CHART THEME
    # =================================================

    theme = st.session_state.get("theme", "Dark")
    chart_template = (
        "plotly_dark"
        if theme == "Dark"
        else "plotly_white"
    )

    # =================================================
    # PLAYER POINTS COMPARISON
    # =================================================

    render_section_header(
        "Player Points Comparison",
        "Compare ranking points among the leading players.",
        "🏆"
    )
    top_chart = ranking_df.nsmallest(10,"rank").sort_values("points",ascending=True)
    fig = px.bar(
        top_chart,
        x="points",
        y="competitor_name",
        orientation="h",
        color="points",
        title=f"Top Players — {selected_type}",
        labels={
            "points": "Ranking Points",
            "competitor_name": "Player"
        },
        template=chart_template
    )
    fig.update_layout(
        height=450,
        showlegend=False,
        yaxis_title=None,
        margin=dict(t=60, b=30)
    )
    fig = apply_chart_theme(fig)
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.divider()

    # =================================================
    # RANKING MOVEMENT ANALYSIS
    # =================================================

    render_section_header(
        "Ranking Movement Analysis",
        "Explore the movement values recorded in the source database.",
        "📈"
    )
    movement_data = ranking_df.dropna(subset=["movement"]).copy()

    col1, col2 = st.columns(2)
    with col1:
        if not movement_data.empty:
            movement_summary = (
                movement_data["movement"]
                .value_counts()
                .sort_index()
                .reset_index()
            )
            movement_summary.columns = ["Movement","Players"]
            fig = px.bar(
                movement_summary,
                x="Movement",
                y="Players",
                title="Player Movement Distribution",
                labels={
                    "Movement": "Movement Value",
                    "Players": "Number of Players"
                },
                template=chart_template
            )
            fig.update_layout(
                height=370,
                margin=dict(t=55, b=30)
            )
            fig = apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Movement data is unavailable.")

    with col2:
        movement_zero = (
            movement_data["movement"] == 0
        ).sum()
        movement_nonzero = (
            movement_data["movement"] != 0
        ).sum()

        movement_summary = pd.DataFrame({
            "Movement Status": [
                "Zero Movement",
                "Non-zero Movement"
            ],
            "Players": [
                movement_zero,
                movement_nonzero
            ]
        })
        fig = px.pie(
            movement_summary,
            names="Movement Status",
            values="Players",
            hole=0.6,
            title="Movement Status Overview",
            template=chart_template
        )
        fig.update_layout(
            height=370,
            margin=dict(t=55, b=30)
        )
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig,use_container_width=True)
    st.caption(
        "Movement values are displayed as provided by the "
        "source database. Their direction is not assumed."
    )
    st.divider()

    # =================================================
    # COMPLETE RANKING LEADERBOARD
    # =================================================

    render_section_header(
        "Ranking Leaderboard",
        "Complete player ranking records with country, points and movement details.",
        "📋"
    )
    display_df = ranking_df[
        [
            "rank",
            "competitor_name",
            "country_display",
            "points",
            "movement",
            "competitions_played"
        ]
    ].rename(
        columns={
            "rank": "Rank",
            "competitor_name": "Player",
            "country_display": "Country",
            "points": "Points",
            "movement": "Movement",
            "competitions_played": "Competitions Played"
        }
    )
    render_dataframe(
        display_df,
        hide_index=True
    )

    # =================================================
    # PLAYER DETAILS
    # =================================================

    render_section_header(
        "Individual Player Details",
        "View detailed ranking information for an individual player.",
        "👤"
    )
    player_options = ranking_df["competitor_name"].drop_duplicates().tolist()
    selected_player = st.selectbox(
        "Select a Player",
        player_options,
        key="rank_player_detail"
    )
    player = ranking_df[ranking_df["competitor_name"] == selected_player].iloc[0]

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Player Rank",
        f"#{player['rank']:,.0f}"
    )
    p2.metric(
        "Ranking Points",
        f"{player['points']:,.0f}"
    )
    p3.metric(
        "Competitions Played",
        f"{player['competitions_played']:,.0f}"
        if pd.notna(player["competitions_played"])
        else "N/A"
    )
    p4.metric(
        "Movement Value",
        f"{player['movement']:,.0f}"
        if pd.notna(player["movement"])
        else "N/A"
    )
    st.write(f"**Country:** {player['country_display']}")
    st.write(
        f"**Abbreviation:** "
        f"{player['abbreviation'] if pd.notna(player['abbreviation']) else 'N/A'}"
    )

    # =================================================
    # CSV EXPORT
    # =================================================

    st.divider()
    render_section_header(
        "Download Ranking Report",
        "Export the filtered player leaderboard as a CSV report.",
        "📥"
    )
    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download Ranking Leaderboard CSV",
        data=csv_data,
        file_name=f"{selected_type.lower()}_rankings.csv",
        mime="text/csv"
    )
    st.caption(
        f"Ranking category: {selected_type} | "
        f"Players displayed: {total_players:,}"
    )
