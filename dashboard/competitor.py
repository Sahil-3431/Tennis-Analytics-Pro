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
# LOAD COMPETITOR DATA
# --------------------------------------------------

@st.cache_data
def load_competitor_data():
    conn = get_connection()
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
        ORDER BY c.competitor_name ASC
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
# COMPETITOR EXPLORER PAGE
# --------------------------------------------------

def show():
    st.title("🔎 Competitor Explorer")
    st.markdown(
        "Explore tennis competitors, analyze their ranking "
        "performance, and view individual player profiles."
    )
    st.divider()
    try:
        df = load_competitor_data()
    except Exception as e:
        st.error(f"Unable to load competitor data: {e}")
        return
    if df.empty:
        st.warning("No competitor records found in the database.")
        return

    # Apply global sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No competitors match the global sidebar filters.")
        return

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    render_section_header(
        "Competitor Filters",
        "Find competitors by ranking category, country and player name.",
        "🔎"
    )
    col1, col2, col3 = st.columns(3)
    ranking_options = sorted(df["ranking_name"].dropna().unique().tolist())
    with col1:
        selected_ranking = st.selectbox("Ranking Category",["All"] + ranking_options)
    with col2:
        country_options = sorted(df["country"].dropna().unique().tolist())
        selected_country = st.selectbox("Country",["All"] + country_options)
    with col3:
        search_name = st.text_input("Search Competitor",placeholder="Enter player name...")
    filtered_df = df.copy()

    if selected_ranking != "All":
        filtered_df = filtered_df[filtered_df["ranking_name"] == selected_ranking]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country"] == selected_country]
    if search_name.strip():
        filtered_df = filtered_df[
            filtered_df["competitor_name"].str.contains(
                search_name.strip(),
                case=False,
                na=False
            )
        ]
    filtered_df = filtered_df.drop_duplicates(subset=["ranking_snapshot_id", "competitor_id"])
    st.divider()

    # --------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------

    render_section_header(
        "Competitor Summary",
        "Overview of competitors, countries and ranking performance.",
        "📊"
    )
    total_players = filtered_df["competitor_id"].nunique()
    total_countries = filtered_df["country"].nunique()
    average_points = filtered_df["points"].mean()
    best_rank = filtered_df["rank"].min()
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_kpi(
            "Total Competitors",
            f"{total_players:,}",
            "Unique competitors"
        )
    with col2:
        render_kpi(
            "Countries",
            f"{total_countries:,}",
            "Represented countries"
        )
    with col3:
        render_kpi(
            "Average Points",
            f"{average_points:,.2f}" if pd.notna(average_points) else "N/A",
            "Average ranking points"
        )
    st.divider()

    # --------------------------------------------------
    # INDIVIDUAL PLAYER PROFILE
    # --------------------------------------------------

    render_section_header(
        "Individual Competitor Profile",
        "Explore detailed ranking information for a selected competitor.",
        "👤"
    )
    player_options = sorted(filtered_df["competitor_name"].dropna().unique().tolist())
    selected_player = st.selectbox("Select Competitor",player_options)
    player_data=filtered_df[filtered_df["competitor_name"]==selected_player].sort_values("rank",ascending=True)

    if not player_data.empty:
        player = player_data.iloc[0]
        st.markdown(f"### {player['competitor_name']}")
        p1, p2, p3, p4 = st.columns(4, gap="large")
        with p1:
            render_kpi(
                "Current Rank",
                f"{int(player['rank'])}" if pd.notna(player["rank"]) else "N/A",
                "Current ranking position"
            )
        with p2:
            render_kpi(
                "Ranking Points",
                f"{player['points']:,.0f}" if pd.notna(player["points"]) else "N/A",
                "Total ranking points"
            )
        with p3:
            render_kpi(
                "Movement",
                f"{player['movement']:,.0f}" if pd.notna(player["movement"]) else "N/A",
                "Ranking movement value"
            )
        with p4:
            render_kpi(
                "Competitions Played",
                f"{int(player['competitions_played'])}" if pd.notna(player["competitions_played"]) else "N/A",
                "Total competitions"
            )
        profile_col1, profile_col2 = st.columns(2)
        with profile_col1:
            st.write("**Competitor ID:**", player["competitor_id"])
            st.write("**Abbreviation:**", player["abbreviation"])
            st.write("**Country:**", player["country"])
        with profile_col2:
            st.write("**Country Code:**", player["country_code"])
            st.write("**Ranking Category:**", player["ranking_name"])
            st.write("**Gender:**", player["gender"])

        # ==========================================
        # ADVANCED PLAYER PERFORMANCE INSIGHTS
        # ==========================================

        render_section_header(
            "Advanced Player Performance Insights",
            "Evaluate player performance against ranking category benchmarks.",
            "📈"
        )
        # Compare only within the same ranking category
        category_df = df[df["ranking_name"] == player["ranking_name"]].drop_duplicates(subset=["competitor_id"]).copy()
        category_df = category_df.dropna(subset=["rank", "points"])
        category_total = len(category_df)
        player_rank = player["rank"]
        player_points = player["points"]
        player_competitions = player["competitions_played"]

        # Ranking percentile
        if category_total > 0 and pd.notna(player_rank):
            ranking_percentile = (
                (category_total - player_rank + 1)
                / category_total
            ) * 100
        else:
            ranking_percentile = None

        # Points per competition
        if (
            pd.notna(player_points)
            and pd.notna(player_competitions)
            and player_competitions > 0
        ):
            points_per_competition = (player_points / player_competitions)
        else:
            points_per_competition = None

        # Category benchmarks
        category_median_points = category_df["points"].median()
        category_median_rank = category_df["rank"].median()
        top_25_df = category_df[category_df["rank"] <= 25]
        top_25_median_points = (
            top_25_df["points"].median()
            if not top_25_df.empty
            else None
        )

        # Player comparison with category median
        if pd.notna(category_median_points):
            points_difference = (
                player_points - category_median_points
            )
        else:
            points_difference = None

        # ==========================================
        # ADVANCED KPI CARDS
        # ==========================================

        insight_col1, insight_col2, insight_col3 = st.columns(3, gap="large")
        with insight_col1:
            render_kpi(
                "Points per Competition",
                f"{points_per_competition:,.2f}"
                if points_per_competition is not None
                else "N/A",
                "Average points per competition"
            )
        with insight_col2:
            render_kpi(
                "Ranking Percentile",
                f"{ranking_percentile:.2f}%"
                if ranking_percentile is not None
                else "N/A",
                "Position within category"
            )
        with insight_col3:
            render_kpi(
                "Points vs Category Median",
                f"{points_difference:+,.0f}"
                if points_difference is not None
                else "N/A",
                "Difference from category median"
            )

        # ==========================================
        # CATEGORY BENCHMARK COMPARISON
        # ==========================================

        render_section_header(
            "Player vs Category Benchmarks",
            "Compare selected player points with category and Top 25 medians.",
            "⚖️"
        )
        benchmark_data = [
            {
                "Benchmark": "Selected Player",
                "Points": player_points
            },
            {
                "Benchmark": "Category Median",
                "Points": category_median_points
            }
        ]

        if top_25_median_points is not None:
            benchmark_data.append(
                {
                    "Benchmark": "Top 25 Median",
                    "Points": top_25_median_points
                }
            )
        benchmark_df = pd.DataFrame(benchmark_data)
        benchmark_df = benchmark_df.dropna(subset=["Points"])
        if not benchmark_df.empty:
            fig_benchmark = px.bar(
                benchmark_df,
                x="Benchmark",
                y="Points",
                color="Benchmark",
                text="Points",
                title="Ranking Points Benchmark Comparison",
                labels={
                    "Benchmark": "Comparison Group",
                    "Points": "Ranking Points"
                }
            )
            fig_benchmark.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
                textfont=dict(size=13),
                marker_line_width=1.2,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Ranking Points: %{y:,.0f}"
                    "<extra></extra>"
                )
            )
            fig_benchmark.update_layout(
                height=400,
                showlegend=False,
                bargap=0.35,
                yaxis_title="Ranking Points",
                xaxis_title="",
                margin=dict(t=60, b=35, l=25, r=25),
                title=dict(
                    font=dict(size=19),
                    x=0.02,
                    xanchor="left"
                ),
                hoverlabel=dict(font_size=13)
            )
            fig_benchmark = apply_chart_theme(fig_benchmark)
            st.plotly_chart(
                fig_benchmark,
                use_container_width=True
            )

        # ==========================================
        # AUTOMATED PLAYER INSIGHTS
        # ==========================================

        render_section_header(
            "Player Performance Summary",
            "Automated insights based on the available ranking snapshot.",
            "💡"
        )
        st.write(f"**Ranking Category:** {player['ranking_name']}")
        st.write(f"**Category Competitors:** {category_total:,}")
        st.write(
            f"**Category Median Rank:** "
            f"{category_median_rank:,.1f}"
            if pd.notna(category_median_rank)
            else "**Category Median Rank:** N/A"
        )
        if points_difference is not None:
            if points_difference > 0:
                st.success(
                    f"The selected player has "
                    f"{points_difference:,.0f} more points "
                    f"than the category median."
                )

            elif points_difference < 0:
                st.info(
                    f"The selected player has "
                    f"{abs(points_difference):,.0f} fewer points "
                    f"than the category median."
                )
            else:
                st.info(
                    "The selected player is exactly at "
                    "the category median points."
                )
        st.caption(
            "Percentile and benchmark values are calculated "
            "from the available ranking snapshot. "
            "They do not represent historical performance trends."
        )

    st.divider()

    # --------------------------------------------------
    # COUNTRY-WISE COMPETITOR DISTRIBUTION
    # --------------------------------------------------

    render_section_header(
        "Country-wise Competitor Distribution",
        "Explore the countries with the highest competitor representation.",
        "🌍"
    )
    country_data = (
        filtered_df.groupby("country")["competitor_id"]
        .nunique()
        .reset_index(name="competitors")
        .sort_values("competitors", ascending=False)
        .head(10)
    )
    if not country_data.empty:
        fig_country = px.bar(
            country_data,
            x="country",
            y="competitors",
            title="Top 10 Countries by Competitor Count",
            labels={
                "country": "Country",
                "competitors": "Number of Competitors"
            },
            text="competitors"
        )
        fig_country.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Competitors: %{y:,}"
                "<extra></extra>"
            )
        )
        fig_country.update_layout(
            height=420,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Country",
            yaxis_title="Competitors",
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_country = apply_chart_theme(fig_country)
        st.plotly_chart(fig_country, use_container_width=True)
    st.divider()

    # --------------------------------------------------
    # COMPETITOR POINTS DISTRIBUTION
    # --------------------------------------------------

    render_section_header(
        "Competitor Points Analysis",
        "Analyze the distribution of ranking points across competitors.",
        "📉"
    )
    points_data = filtered_df.dropna(subset=["points"])
    if not points_data.empty:
        fig_points = px.histogram(
            points_data,
            x="points",
            nbins=20,
            title="Distribution of Competitor Ranking Points",
            labels={"points": "Ranking Points"}
        )
        fig_points.update_traces(
            marker_line_width=1.2,
            hovertemplate=(
                "Ranking Points Range: %{x}<br>"
                "Number of Competitors: %{y:,}"
                "<extra></extra>"
            )
        )
        fig_points.update_layout(
            height=420,
            showlegend=False,
            bargap=0.08,
            xaxis_title="Ranking Points",
            yaxis_title="Number of Competitors",
            margin=dict(t=65, b=45, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_points = apply_chart_theme(fig_points)
        st.plotly_chart(fig_points, use_container_width=True)
    st.divider()

    # --------------------------------------------------
    # COMPETITOR DIRECTORY
    # --------------------------------------------------

    render_section_header(
        "Competitor Directory",
        "Browse the complete filtered competitor database.",
        "📋"
    )
    directory_columns = [
        "competitor_id",
        "competitor_name",
        "abbreviation",
        "country",
        "rank",
        "points",
        "movement",
        "competitions_played",
        "ranking_name"
    ]
    directory = filtered_df[directory_columns].copy()
    directory = directory.sort_values("rank",ascending=True)
    directory = directory.rename(columns={
        "competitor_id": "Competitor ID",
        "competitor_name": "Competitor",
        "abbreviation": "Abbreviation",
        "country": "Country",
        "rank": "Rank",
        "points": "Ranking Points",
        "movement": "Movement",
        "competitions_played": "Competitions Played",
        "ranking_name": "Ranking Category"
    })
    render_dataframe(
        directory,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------

    render_section_header(
        "Download Competitor Data",
        "Export competitor records for further analysis and reporting.",
        "📥"
    )
    csv = directory.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Competitor Data CSV",
        data=csv,
        file_name="competitor_explorer_data.csv",
        mime="text/csv"
    )
    st.caption(
        "Data is fetched from the existing SQLite database. "
        "No original database records are modified."
    )
