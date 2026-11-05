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

@st.cache_data
def load_insights_data():
    conn = get_connection()
    query = """
        SELECT
            c.competitor_id,
            c.competitor_name,
            c.country,
            c.country_code,
            d.rank,
            d.points,
            d.movement,
            d.competitions_played,
            d.ranking_snapshot_id,
            r.ranking_name,
            r.gender
        FROM DoublesRankings d
        JOIN Competitors c
            ON d.competitor_id = c.competitor_id
        JOIN RankingSnapshots r
            ON d.ranking_snapshot_id = r.ranking_snapshot_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    numeric_columns = [
        "rank",
        "points",
        "movement",
        "competitions_played"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )
    return df

def generate_recommendations(df):
    recommendations = []
    if df.empty:
        return recommendations
    total_players = df["competitor_id"].nunique()
    valid_rank = df.dropna(subset=["rank"])
    valid_points = df.dropna(subset=["points"])
    valid_competitions = df.dropna(subset=["competitions_played"])

    # Top player insight
    if not valid_rank.empty:
        top_player = valid_rank.loc[valid_rank["rank"].idxmin()]
        recommendations.append({
            "title": "Top Ranked Player",
            "insight": (
                f"{top_player['competitor_name']} currently holds "
                f"the highest position in this selected dataset "
                f"with rank {top_player['rank']:g}."
            ),
            "recommendation": (
                "Use this player as a reference point for further "
                "analysis of ranking points and competition participation."
            )
        })

    # Country representation
    country_data = (
        df.dropna(subset=["country"])
        .groupby("country")["competitor_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    if not country_data.empty:
        leading_country = country_data.index[0]
        leading_count = int(country_data.iloc[0])
        recommendations.append({
            "title": "Country Representation",
            "insight": (
                f"{leading_country} has the highest player "
                f"representation with {leading_count} players."
            ),
            "recommendation": (
                "Compare player representation with average rank "
                "and average points to understand differences in "
                "country-level ranking performance."
            )
        })

    # Ranking distribution
    if not valid_rank.empty:
        top_10_count = int((valid_rank["rank"] <= 10).sum())
        top_10_percentage = (top_10_count / len(valid_rank)) * 100
        recommendations.append({
            "title": "Top 10 Ranking Distribution",
            "insight": (
                f"{top_10_count} players, representing "
                f"{top_10_percentage:.2f}% of ranked players, "
                "are within the Top 10."
            ),
            "recommendation": (
                "Study the points gap between Top 10 players "
                "and the remaining ranking groups to understand "
                "ranking concentration."
            )
        })
    # Points analysis
    if not valid_points.empty:
        average_points = valid_points["points"].mean()
        median_points = valid_points["points"].median()
        recommendations.append({
            "title": "Ranking Points Analysis",
            "insight": (
                f"Average ranking points are {average_points:,.2f}, "
                f"while median points are {median_points:,.2f}."
            ),
            "recommendation": (
                "Compare the average and median to understand "
                "whether ranking points are concentrated among "
                "a smaller number of players."
            )
        })

    # Competition participation
    if not valid_competitions.empty:
        average_competitions = (valid_competitions["competitions_played"].mean())
        recommendations.append({
            "title": "Competition Participation",
            "insight": (
                f"Players have an average of "
                f"{average_competitions:.2f} competitions played."
            ),
            "recommendation": (
                "Compare competition participation across ranking "
                "groups to explore how participation relates to "
                "ranking points and position."
            )
        })

    # Data coverage
    recommendations.append({
        "title": "Data Coverage",
        "insight": (
            f"The selected dataset contains {total_players} unique "
            "players."
        ),
        "recommendation": (
            "For more detailed analysis, compare multiple verified "
            "ranking snapshots and include additional historical "
            "data when available."
        )
    })
    return recommendations

def show():
    st.title("💡 Tennis Insights & Recommendations")
    st.caption(
        "Discover important patterns and data-driven recommendations "
        "from tennis ranking records."
    )
    df = load_insights_data()
    if df.empty:
        st.warning("No ranking data available.")
        return
    
    # Apply global sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No records match the global sidebar filters.")
        return
    st.divider()

    # Filters
    render_section_header(
        "Select Analysis Dataset",
        "Choose the ranking category and snapshot for analysis.",
        "🔎"
    )
    col1, col2 = st.columns(2)
    with col1:
        categories = sorted(df["ranking_name"].dropna().unique())
        selected_category = st.selectbox("Ranking Category",categories)
    category_df = df[df["ranking_name"] == selected_category].copy()
    with col2:
        snapshots = sorted(category_df["ranking_snapshot_id"].dropna().unique())
        if not snapshots:
            st.warning("No snapshots available.")
            return
        selected_snapshot = st.selectbox(
            "Ranking Snapshot",
            snapshots,
            format_func=lambda x: str(x)
        )
    filtered_df = category_df[category_df["ranking_snapshot_id"] == selected_snapshot].copy()
    filtered_df = filtered_df.drop_duplicates(subset=["competitor_id"])
    genders = sorted(filtered_df["gender"].dropna().unique())
    if len(genders) > 1:
        selected_gender = st.selectbox("Gender",["All"] + genders)
        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
    if filtered_df.empty:
        st.warning("No records found for the selected filters.")
        return
    st.divider()

    # KPI Overview
    render_section_header(
        "Key Performance Indicators",
        "Overview of important metrics for the selected dataset.",
        "📊"
    )
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        render_kpi(
            "Total Players",
            f"{filtered_df['competitor_id'].nunique():,}",
            "Unique competitors"
        )
    with col2:
        render_kpi(
            "Countries",
            f"{filtered_df['country'].nunique():,}",
            "Countries represented"
        )
    with col3:
        average_points = filtered_df["points"].mean()
        render_kpi(
            "Average Points",
            f"{average_points:,.2f}" if pd.notna(average_points) else "N/A",
            "Average ranking points"
        )
    with col4:
        average_rank = filtered_df["rank"].mean()
        render_kpi(
            "Average Rank",
            f"{average_rank:,.2f}" if pd.notna(average_rank) else "N/A",
            "Average player ranking"
        )
    st.divider()

    # Top players
    render_section_header(
        "Top 10 Players",
        "List of the top 10 players based on their ranking.",
        "🏆"
    )
    top_players = (
        filtered_df.dropna(subset=["rank"])
        .sort_values("rank")
        .head(10)
    )
    if not top_players.empty:
        render_dataframe(
            top_players[
                [
                    "rank",
                    "competitor_name",
                    "country",
                    "points",
                    "competitions_played"
                ]
            ].rename(columns={
                "rank": "Rank",
                "competitor_name": "Player",
                "country": "Country",
                "points": "Points",
                "competitions_played": "Competitions Played"
            }),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Rank information is not available.")
    st.divider()

    # Country insights
    render_section_header(
        "Country-wise Insights",
        "Compare player representation and ranking performance across countries.",
        "🌍"
    )
    country_df = (
        filtered_df.dropna(subset=["country"])
        .groupby("country")
        .agg(
            Players=("competitor_id", "nunique"),
            Average_Points=("points", "mean"),
            Average_Rank=("rank", "mean")
        )
        .reset_index()
        .sort_values("Players", ascending=False)
    )
    if not country_df.empty:
        fig_country = px.bar(
            country_df.head(10),
            x="country",
            y="Players",
            color="Average_Points",
            title="Top 10 Countries by Player Representation",
            labels={
                "country": "Country",
                "Players": "Number of Players",
                "Average_Points": "Average Points"
            },
            template="plotly_dark"
        )
        fig_country.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Players: %{y:,.0f}<br>"
                "Average Points: %{marker.color:,.2f}"
                "<extra></extra>"
            )
        )
        fig_country.update_layout(
            height=420,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Country",
            yaxis_title="Number of Players",
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(font=dict(size=19), x=0.02, xanchor="left"),
            hoverlabel=dict(font_size=13)
        )
        fig_country = apply_chart_theme(fig_country)
        st.plotly_chart(fig_country,use_container_width=True)
        render_dataframe(
            country_df.rename(columns={
                "country": "Country",
                "Players": "Total Players",
                "Average_Points": "Average Points",
                "Average_Rank": "Average Rank"
            }).round(2),
            hide_index=True,
            use_container_width=True
        )
    st.divider()

    # Points and competitions relationship
    render_section_header(
        "Points vs Competition Participation",
        "Explore the relationship between competition participation and ranking points.",
        "🎯"
    )
    relationship_df = filtered_df.dropna(subset=["points", "competitions_played"])
    if not relationship_df.empty:
        fig_relationship = px.scatter(
            relationship_df,
            x="competitions_played",
            y="points",
            hover_name="competitor_name",
            color="country",
            title="Ranking Points vs Competitions Played",
            labels={
                "competitions_played": "Competitions Played",
                "points": "Ranking Points",
                "country": "Country"
            },
            template="plotly_dark"
        )
        fig_relationship.update_traces(
            marker=dict(
                size=11,
                opacity=0.82,
                line=dict(width=1.2)
            ),
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Competitions Played: %{x:,.0f}<br>"
                "Ranking Points: %{y:,.2f}<br>"
                "<extra></extra>"
            )
        )
        fig_relationship.update_layout(
            height=430,
            margin=dict(t=65, b=45, l=25, r=25),
            title=dict(font=dict(size=19), x=0.02, xanchor="left"),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="left",
                x=0
            )
        )
        fig_relationship = apply_chart_theme(fig_relationship)
        st.plotly_chart(fig_relationship, use_container_width=True)
    else:
        st.info("Insufficient data for this relationship chart.")
    st.divider()

    # Automatic recommendations
    render_section_header(
        "Automatic Insights & Recommendations",
        "Review observations and recommendations generated from the selected ranking data.",
        "💡"
    )
    recommendations = generate_recommendations(filtered_df)
    for index, item in enumerate(recommendations, start=1):
        with st.expander(
            f"{index}. {item['title']}",
            expanded=True
        ):
            st.markdown("**Observation**")
            st.write(item["insight"])

            st.markdown("**Recommendation**")
            st.write(item["recommendation"])
    st.caption(
        "Recommendations are generated from the selected ranking "
        "snapshot. They describe observed data patterns and do not "
        "establish causation or predict future performance."
    )
    st.divider()

    # Export
    render_section_header(
        "Download Insights Dataset",
        "Export the selected ranking insights and competitor records.",
        "📥"
    )
    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download Insights Data",
        data=csv_data,
        file_name="tennis_insights_recommendations.csv",
        mime="text/csv"
    )
