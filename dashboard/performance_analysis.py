import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import get_connection
from utils.global_filters import apply_global_filters
from utils.styling import (
    render_section_header,
    apply_chart_theme,
    render_dataframe,
    render_kpi
)

# --------------------------------------------------
# LOAD PERFORMANCE DATA
# --------------------------------------------------

@st.cache_data
def load_performance_data():
    conn = get_connection()
    query = """
        SELECT
            c.competitor_id,
            c.competitor_name,
            c.country,
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
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    numeric_columns = [
        "rank",
        "movement",
        "points",
        "competitions_played"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["competitor_name"] = (df["competitor_name"].fillna("Unknown"))
    df["country"] = df["country"].fillna("Unknown")
    df["ranking_name"] = (df["ranking_name"].fillna("Unknown").str.upper())
    df["gender"] = df["gender"].fillna("Unknown")
    return df

# --------------------------------------------------
# PERFORMANCE ANALYSIS PAGE
# --------------------------------------------------

def show():
    st.title("📈 Ranking Movement & Performance Analysis")
    st.markdown(
        "Analyze ranking movement, competitor points, "
        "ranking positions, and competition participation."
    )
    st.divider()
    try:
        df = load_performance_data()
    except Exception as e:
        st.error(f"Unable to load performance data: {e}")
        return
    if df.empty:
        st.warning("No performance records available.")
        return

    # Apply global sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No performance records match the global filters.")
        return

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    render_section_header(
        "Analysis Filters",
        "Filter performance data by ranking category and country.",
        "🔎"
    )
    col1, col2 = st.columns(2)
    ranking_options = sorted(df["ranking_name"].dropna().unique().tolist())
    with col1:
        selected_ranking = st.selectbox("Ranking Category",["All"] + ranking_options)
    with col2:
        country_options = sorted(df["country"].dropna().unique().tolist())
        selected_country = st.selectbox("Country",["All"] + country_options)
    filtered_df = df.copy()
    if selected_ranking != "All":
        filtered_df = filtered_df[filtered_df["ranking_name"] == selected_ranking]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country"] == selected_country]
    filtered_df = filtered_df.drop_duplicates(subset=["ranking_snapshot_id", "competitor_id"])
    if filtered_df.empty:
        st.warning("No records found for the selected filters.")
        return
    st.divider()

    # --------------------------------------------------
    # PERFORMANCE KPIs
    # --------------------------------------------------

    render_section_header(
        "Overall Performance Metrics",
        "Key performance indicators for the selected filter criteria.",
        "📊"
    )
    total_records = len(filtered_df)
    total_competitors = filtered_df["competitor_id"].nunique()
    average_rank = filtered_df["rank"].mean()
    average_points = filtered_df["points"].mean()
    average_movement = filtered_df["movement"].mean()
    average_competitions = filtered_df["competitions_played"].mean()

    # First KPI Row
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_kpi(
            "Ranking Records",
            f"{total_records:,}",
            "Total ranking records"
        )
    with col2:
        render_kpi(
            "Unique Competitors",
            f"{total_competitors:,}",
            "Distinct competitors"
        )
    with col3:
        render_kpi(
            "Average Rank",
            f"{average_rank:,.2f}" if pd.notna(average_rank) else "N/A",
            "Average ranking position"
        )
    # Second KPI Row
    col4, col5, col6 = st.columns(3, gap="large")
    with col4:
        render_kpi(
            "Average Points",
            f"{average_points:,.2f}" if pd.notna(average_points) else "N/A",
            "Average ranking points"
        )
    with col5:
        render_kpi(
            "Average Movement",
            f"{average_movement:,.2f}" if pd.notna(average_movement) else "N/A",
            "Average movement value"
        )
    with col6:
        render_kpi(
            "Avg. Competitions Played",
            f"{average_competitions:,.2f}" if pd.notna(average_competitions) else "N/A",
            "Average competitions played"
        )
    st.divider()

    # --------------------------------------------------
    # RANKING MOVEMENT DISTRIBUTION
    # --------------------------------------------------

    render_section_header(
        "Ranking Movement Distribution",
        "Visualize the distribution of ranking movement values among competitors.",
        "📉"
    )
    movement_data = filtered_df.dropna(subset=["movement"])
    if not movement_data.empty:
        movement_counts = (
            movement_data["movement"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        movement_counts.columns = [
            "Movement Value",
            "Number of Competitors"
        ]
        fig_movement = px.bar(
            movement_counts,
            x="Movement Value",
            y="Number of Competitors",
            title="Distribution of Ranking Movement Values",
            text="Number of Competitors"
        )
        fig_movement.update_traces(
        textposition="outside",
        texttemplate="%{y:,.0f}",
        textfont=dict(size=13),
        marker_line_width=1.2,
        hovertemplate=(
            "<b>Movement: %{x}</b><br>"
            "Competitors: %{y:,}"
            "<extra></extra>"
            )
        )
        fig_movement.update_layout(
            height=390,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Movement Value",
            yaxis_title="Number of Competitors",
            margin=dict(t=55, b=35, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_movement = apply_chart_theme(fig_movement)
        st.plotly_chart(
            fig_movement,
            use_container_width=True
        )
    else:
        st.info("Movement data is not available.")

    st.caption(
        "Movement values are displayed as stored in the source database. "
        "Their direction or meaning is not assumed."
    )
    st.divider()

    # --------------------------------------------------
    # POINTS VS RANK ANALYSIS
    # --------------------------------------------------

    render_section_header(
        "Ranking Position vs Ranking Points",
        "Explore the relationship between ranking positions and points.",
        "🎯"
    )
    rank_points = filtered_df.dropna(subset=["rank", "points"])

    if not rank_points.empty:
        fig_rank_points = px.scatter(
            rank_points,
            x="rank",
            y="points",
            color="ranking_name",
            hover_name="competitor_name",
            hover_data=["country", "movement"],
            title="Relationship Between Ranking Position and Points",
            labels={
                "rank": "Ranking Position",
                "points": "Ranking Points",
                "ranking_name": "Ranking Category"
            }
        )
        fig_rank_points.update_traces(
        marker=dict(
            size=11,
            opacity=0.82,
            line=dict(width=1.2)
            ),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Rank: %{x}<br>"
                "Points: %{y:,.0f}<br>"
                "Country: %{customdata[0]}<br>"
                "Movement: %{customdata[1]}"
                "<extra></extra>"
            )
        )
        fig_rank_points.update_layout(
            height=430,
            margin=dict(t=65, b=45, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.30,
                xanchor="left",
                x=0
            )
        )
        fig_rank_points= apply_chart_theme(fig_rank_points)
        st.plotly_chart(
            fig_rank_points,
            use_container_width=True
        )
    else:
        st.info("Ranking and points data is not available.")
    st.divider()

    # --------------------------------------------------
    # COMPETITIONS VS POINTS
    # --------------------------------------------------

    render_section_header(
        "Competitions Played vs Ranking Points",
        "Analyze how competition participation relates to ranking points.",
        "🏆"
    )
    competition_data = filtered_df.dropna(subset=["competitions_played", "points"])
    if not competition_data.empty:
        fig_competitions = px.scatter(
            competition_data,
            x="competitions_played",
            y="points",
            color="ranking_name",
            hover_name="competitor_name",
            hover_data=["rank", "country"],
            title="Competitions Played vs Ranking Points",
            labels={
                "competitions_played": "Competitions Played",
                "points": "Ranking Points"
            }
        )
        fig_competitions.update_traces(
            marker=dict(
                size=11,
                opacity=0.82,
                line=dict(width=1.2)
                ),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Competitions Played: %{x}<br>"
                "Ranking Points: %{y:,.0f}<br>"
                "Rank: %{customdata[0]}<br>"
                "Country: %{customdata[1]}"
                "<extra></extra>"
            )
        )
        fig_competitions.update_layout(
            height=430,
            margin=dict(t=65, b=45, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.30,
                xanchor="left",
                x=0
            )
        )
        fig_competitions = apply_chart_theme(fig_competitions)
        st.plotly_chart(
            fig_competitions,
            use_container_width=True
        )
    else:
        st.info("Competition participation data is not available.")
    st.divider()

    # --------------------------------------------------
    # TOP PERFORMERS
    # --------------------------------------------------

    render_section_header(
        "Top 10 Competitors by Ranking Points",
        "Identify the top performers based on their ranking points.",
        "🥇"
    )
    top_performers = (
        filtered_df.dropna(subset=["points"])
        .sort_values("points", ascending=False)
        .head(10)
    )
    if not top_performers.empty:
        fig_top = px.bar(
            top_performers,
            x="competitor_name",
            y="points",
            color="ranking_name",
            text="points",
            title="Top 10 Competitors by Points",
            labels={
                "competitor_name": "Competitor",
                "points": "Ranking Points"
            }
        )
        fig_top.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Ranking Points: %{y:,.0f}<br>"
                "Ranking: %{fullData.name}"
                "<extra></extra>"
            )
        )
        fig_top.update_layout(
            height=430,
            bargap=0.35,
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.35,
                xanchor="left",
                x=0
            ),
            xaxis_title="Competitor",
            yaxis_title="Ranking Points"
        )
        fig_top= apply_chart_theme(fig_top)
        st.plotly_chart(
            fig_top,
            use_container_width=True
        )
    else:
        st.info("No points data available.")
    st.divider()

    # --------------------------------------------------
    # PERFORMANCE SUMMARY TABLE
    # --------------------------------------------------

    render_section_header(
        "Performance Summary Table",
        "Comprehensive overview of competitor performance metrics.",
        "📑"
    )
    summary_columns = [
        "competitor_name",
        "country",
        "ranking_name",
        "rank",
        "points",
        "movement",
        "competitions_played"
    ]
    summary_df = filtered_df[summary_columns].copy()
    summary_df = summary_df.sort_values(
        "points",
        ascending=False
    )
    summary_df = summary_df.rename(columns={
        "competitor_name": "Competitor",
        "country": "Country",
        "ranking_name": "Ranking Category",
        "rank": "Rank",
        "points": "Ranking Points",
        "movement": "Movement",
        "competitions_played": "Competitions Played"
    })
    render_dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------

    render_section_header(
        "Download Performance Analysis",
        "Export the filtered performance summary as a CSV file.",
        "📥"
    )
    csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Performance Analysis CSV",
        data=csv,
        file_name="tennis_performance_analysis.csv",
        mime="text/csv"
    )
    st.caption(
        "Analysis is performed using the existing SQLite database. "
        "Original source data remains unchanged."
    )
