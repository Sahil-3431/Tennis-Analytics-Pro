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
# LOAD DATA FROM SQLITE DATABASE
# =====================================================

@st.cache_data(show_spinner="Loading tennis analytics...")
def get_dashboard_data():
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
            s.gender,
            s.year,
            s.week
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

    # Numeric conversions
    numeric_columns = [
        "rank",
        "movement",
        "points",
        "competitions_played",
        "year",
        "week"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    # Handle missing display values
    df["country_display"] = (
        df["country"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )
    df["competitor_name"] = (
        df["competitor_name"]
        .fillna("Unknown Player")
    )
    df["ranking_name"] = (
        df["ranking_name"]
        .fillna("Unknown")
        .astype(str)
        .str.upper()
    )
    return df

# =====================================================
# EXECUTIVE DASHBOARD
# =====================================================

def show():
    st.title("📊 Executive Dashboard")
    st.markdown(
        "Overview of Tennis Competitor Rankings and Performance Metrics"
    )

    # Load database
    try:
        df = get_dashboard_data()
    except Exception as e:
        st.error(f"Unable to load database: {e}")
        st.stop()
    if df.empty:
        st.warning("No ranking records found.")
        st.stop()

    # Apply shared sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No records match the global sidebar filters.")
        return

    # =================================================
    # GLOBAL FILTERS
    # =================================================

    render_section_header(
        "Analytics Filters",
        "Refine the dashboard view with these filters.",
        "⚙️"
    )
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        ranking_options = ["All"] + sorted(
            df["ranking_name"].dropna().unique().tolist()
        )
        selected_ranking = st.selectbox(
            "Ranking Type",
            ranking_options,
            key="overview_ranking"
        )
    with f2:
        country_options = ["All"] + sorted(
            df["country_display"].unique().tolist()
        )
        selected_country = st.selectbox(
            "Country",
            country_options,
            key="overview_country"
        )
    min_rank = max(
        1,
        int(df["rank"].min())
    )
    max_rank = max(
        min_rank,
        int(df["rank"].max())
    )
    with f3:
        rank_min = int(df["rank"].min())
        rank_max = int(df["rank"].max())
        if rank_min < rank_max:
            rank_range = st.slider(
                "Rank Range",
                min_value=rank_min,
                max_value=rank_max,
                value=(rank_min, rank_max),
                key="overview_rank_range"
            )
        else:
            rank_range = (rank_min, rank_max)
            st.info(f"Only one ranking position is available: {rank_min}")
    max_points = int(
        df["points"].max()
    ) if df["points"].notna().any() else 0
    with f4:
        min_points = st.number_input(
            "Minimum Points",
            min_value=0,
            max_value=max(0, max_points),
            value=0,
            step=100,
            key="overview_min_points"
        )

    # =================================================
    # APPLY FILTERS
    # =================================================

    filtered_df = df.copy()
    if selected_ranking != "All":
        filtered_df = filtered_df[filtered_df["ranking_name"] == selected_ranking]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country_display"] == selected_country]
    filtered_df = filtered_df[
        filtered_df["rank"].between(
            rank_range[0],
            rank_range[1]
        )
    ]
    filtered_df = filtered_df[filtered_df["points"] >= min_points]
    st.divider()
    if filtered_df.empty:
        st.warning(
            "No records match the selected filters. "
            "Please adjust your filters."
        )
        return

    
    # =================================================
    # GLOBAL PLOTLY CHART THEME
    # =================================================

    theme = st.session_state.get("theme", "Dark")
    chart_template = (
        "plotly_dark"
        if theme == "Dark"
        else "plotly_white"
    )
    # Apply theme to all Plotly Express charts
    px.defaults.template = chart_template

    # =================================================
    # KPI CALCULATIONS
    # =================================================

    total_competitors = (filtered_df["competitor_id"].nunique())
    total_countries = (filtered_df["country_display"].nunique())
    total_records = len(filtered_df)
    highest_points = (
        filtered_df["points"].max()
        if filtered_df["points"].notna().any()
        else 0
    )
    atp_count = (
        filtered_df[
            filtered_df["ranking_name"] == "ATP"
        ]["competitor_id"].nunique()
    )
    wta_count = (
        filtered_df[
            filtered_df["ranking_name"] == "WTA"
        ]["competitor_id"].nunique()
    )
    average_points = (
        filtered_df["points"].mean()
        if filtered_df["points"].notna().any()
        else 0
    )

    # =================================================
    # KPI CARDS
    # =================================================

    render_section_header(
        "Performance Overview",
        "Key metrics summarizing the tennis ranking data.",
        "📊"
    )
    k1, k2, k3 = st.columns(3)
    k1.metric(
        "Total Competitors",
        f"{total_competitors:,}"
    )
    k2.metric(
        "Countries Represented",
        f"{total_countries:,}"
    )
    k3.metric(
        "Ranking Records",
        f"{total_records:,}"
    )
    k4, k5, k6 = st.columns(3)
    k4.metric(
        "ATP Competitors",
        f"{atp_count:,}"
    )
    k5.metric(
        "WTA Competitors",
        f"{wta_count:,}"
    )
    
    k6.metric(
        "Highest Ranking Points",
        f"{highest_points:,.0f}"
    )

    # =================================================
    # ADVANCED KPI ANALYTICS
    # =================================================

    st.divider()
    render_section_header(
        "Advanced Performance Indicators",
        "Detailed metrics providing deeper insights into the tennis ranking data.",
        "📈"
    )

    # Median ranking position
    median_rank = filtered_df["rank"].median()

    # Median ranking points
    median_points = filtered_df["points"].median()

    # Average competitions played
    avg_competitions = filtered_df[
        "competitions_played"
    ].mean()

    # Top 10 points contribution
    valid_points = filtered_df[
        filtered_df["points"].notna()
    ].sort_values(
        "points",
        ascending=False
    )

    total_points = valid_points["points"].sum()

    top_10_points = valid_points.head(10)["points"].sum()

    top_10_share = (
        (top_10_points / total_points) * 100
        if total_points > 0
        else 0
    )

    # Most represented country
    country_counts = (
        filtered_df[
            ~filtered_df["country_display"].isin(
                ["Unknown", "Neutral"]
            )
        ]
        .groupby("country_display")["competitor_id"]
        .nunique()
        .sort_values(ascending=False)
    )

    if not country_counts.empty:
        leading_country = country_counts.index[0]
        leading_country_count = int(country_counts.iloc[0])
    else:
        leading_country = "N/A"
        leading_country_count = 0

    # Highest points competitor
    if not valid_points.empty:
        top_competitor = valid_points.iloc[0]
        top_competitor_name = top_competitor["competitor_name"]
        top_competitor_points = top_competitor["points"]
    else:
        top_competitor_name = "N/A"
        top_competitor_points = 0

    # Advanced KPI Cards
    a1, a2, a3 = st.columns(3)

    a1.metric(
        "Median Ranking Position",
        f"{median_rank:,.1f}"
        if pd.notna(median_rank) else "N/A"
    )

    a2.metric(
        "Median Ranking Points",
        f"{median_points:,.0f}"
        if pd.notna(median_points) else "N/A"
    )

    a3.metric(
        "Average Competitions Played",
        f"{avg_competitions:,.2f}"
        if pd.notna(avg_competitions) else "N/A"
    )

    a4, a5, a6 = st.columns(3)

    a4.metric(
        "Top 10 Points Share",
        f"{top_10_share:.2f}%"
    )

    a5.metric(
        "Leading Country",
        leading_country,
        help="Country with the highest number of unique competitors."
    )

    a6.metric(
        "Leading Country Competitors",
        f"{leading_country_count:,}"
    )

    render_section_header(
        "Highest Points Competitor",
        "The competitor with the most ranking points in the current filtered data.",
        "🏅"
    )

    st.info(
        f"🏆 **{top_competitor_name}** "
        f"has the highest ranking points in the current filtered data: "
        f"**{top_competitor_points:,.0f} points**."
    )

    st.caption(
        "Advanced indicators are calculated dynamically "
        "using the selected dashboard filters."
    )

    st.divider()

    # =================================================
    # EXECUTIVE DATA STORY
    # =================================================

    render_section_header(
        "Executive Data Story",
        "A quick overview of the current tennis ranking landscape.",
        "📊"
    )
    top_country_row = (
        filtered_df["country_display"]
        .value_counts()
        .head(1)
    )
    top_country = (
        top_country_row.index[0]
        if not top_country_row.empty
        else "N/A"
    )
    top_country_count = (
        int(top_country_row.iloc[0])
        if not top_country_row.empty
        else 0
    )
    median_points = filtered_df["points"].median()
    median_rank = filtered_df["rank"].median()
    story_col1, story_col2 = st.columns(2)
    with story_col1:
        st.info(
            f"""
            **🌍 Global Representation**

            The selected data represents **{total_competitors:,} competitors**
            across **{total_countries:,} countries**.

            **{top_country}** has the highest representation
            with **{top_country_count:,} competitors**.
            """
        )
    with story_col2:
        st.info(
            f"""
            **🎾 Ranking Performance**

            The median ranking position is
            **{median_rank:,.0f}**.

            The median ranking points are
            **{median_points:,.0f}**.

            The highest recorded points are
            **{highest_points:,.0f}**.
            """
        )
    st.caption("Insights are calculated dynamically from the currently selected filters.")
    st.divider()

    # =================================================
    # AUTOMATED COUNTRY INSIGHTS
    # =================================================

    render_section_header(
        "Country Performance Insights",
        "Explore country-wise competitor representation and performance.",
        "🌍"
    )
    country_insights = (
        filtered_df.groupby("country_display")
        .agg(
            Competitors=("competitor_id", "count"),
            Average_Points=("points", "mean"),
            Median_Rank=("rank", "median")
        )
        .reset_index()
    )
    country_insights = country_insights.dropna(subset=["Average_Points", "Median_Rank"])
    if not country_insights.empty:
        top_countries = country_insights.nlargest(5, "Competitors")
        best_points_country = country_insights.loc[country_insights["Average_Points"].idxmax()]
        best_rank_country = country_insights.loc[country_insights["Median_Rank"].idxmin()]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🏆 Top 5 Countries by Representation**")
            render_dataframe(
                top_countries[
                    ["country_display", "Competitors"]
                ].rename(
                    columns={"country_display": "Country"}
                ),
                use_container_width=True,
                hide_index=True
            )
        with col2:
            st.markdown("**📈 Country Performance Highlights**")
            st.success(
                f"Highest average points: "
                f"**{best_points_country['country_display']}** "
                f"({best_points_country['Average_Points']:.2f})"
            )
            st.info(
                f"Best median ranking position: "
                f"**{best_rank_country['country_display']}** "
                f"({best_rank_country['Median_Rank']:.0f})"
            )
    else:
        st.warning("No country-level insights available.")
    st.divider()

    # =================================================
    # RANKING DISTRIBUTION STORY
    # =================================================

    render_section_header(
        "Ranking Distribution Story",
        "Understand how competitors are distributed across ranking tiers.",
        "🏅"
    )
    ranking_distribution = pd.DataFrame({
        "Ranking Category": [
            "Top 10",
            "11–25",
            "26–50",
            "51–100",
            "101–500",
            "Above 500"
        ],
        "Competitors": [
            (filtered_df["rank"] <= 10).sum(),
            ((filtered_df["rank"] > 10) & (filtered_df["rank"] <= 25)).sum(),
            ((filtered_df["rank"] > 25) & (filtered_df["rank"] <= 50)).sum(),
            ((filtered_df["rank"] > 50) & (filtered_df["rank"] <= 100)).sum(),
            ((filtered_df["rank"] > 100) & (filtered_df["rank"] <= 500)).sum(),
            (filtered_df["rank"] > 500).sum()
        ]
    })
    ranking_distribution = ranking_distribution[ranking_distribution["Competitors"] > 0]
    if not ranking_distribution.empty:
        col1, col2 = st.columns([1.2, 1])
        with col1:
            fig = px.bar(
                ranking_distribution,
                x="Ranking Category",
                y="Competitors",
                color="Ranking Category",
                text="Competitors",
                title="Competitor Distribution Across Ranking Tiers"
            )
            fig.update_layout(showlegend=False)
            apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        with col2:
            total_ranked = int(ranking_distribution["Competitors"].sum())
            top_100 = int(
                ranking_distribution[
                    ranking_distribution["Ranking Category"].isin(
                        ["Top 10", "11–25", "26–50", "51–100"]
                    )
                ]["Competitors"].sum()
            )
            top_100_percentage = (
                (top_100 / total_ranked) * 100
                if total_ranked > 0 else 0
            )
            st.metric("Total Competitors", total_ranked)
            st.metric(
                "Top 100 Competitors",
                top_100,
                f"{top_100_percentage:.1f}% of total"
            )
            render_dataframe(
                ranking_distribution,
                hide_index=True
            )
    else:
        st.info("No ranking distribution data available.")
    st.divider()

    # =================================================
    # GENDER-WISE PERFORMANCE STORY
    # =================================================

    render_section_header(
        "Gender-wise Performance Story",
        "Compare competitor representation and ranking points across categories.",
        "⚖️"
    )
    gender_story = (
        filtered_df.groupby("gender")
        .agg(
            Competitors=("competitor_id", "count"),
            Average_Points=("points", "mean"),
            Median_Rank=("rank", "median"),
            Highest_Points=("points", "max")
        )
        .reset_index()
    )
    if not gender_story.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                gender_story,
                x="gender",
                y="Competitors",
                color="gender",
                text="Competitors",
                title="Competitor Count by Gender"
            )
            fig.update_layout(showlegend=False)
            apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        with col2:
            fig = px.bar(
                gender_story,
                x="gender",
                y="Average_Points",
                color="gender",
                text_auto=".2f",
                title="Average Ranking Points by Gender"
            )
            fig.update_layout(showlegend=False)
            apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        render_dataframe(
            gender_story,
            hide_index=True
        )
        highest_points_gender = gender_story.loc[gender_story["Highest_Points"].idxmax()]
        st.info(
            f"**Performance Highlight:** "
            f"{highest_points_gender['gender']} has the highest "
            f"recorded ranking points "
            f"({highest_points_gender['Highest_Points']:,.0f}) "
            f"in the currently selected data."
        )
    else:
        st.info("Gender-wise data is not available.")
    st.divider()

    # =================================================
    # AUTOMATED EXECUTIVE RECOMMENDATIONS
    # =================================================

    render_section_header(
        "Executive Recommendations",
        "Data-driven observations based on the currently selected records.",
        "💡"
    )
    recommendations = []
    total_players = len(filtered_df)
    if total_players > 0:
        # Country representation
        country_share = (
            filtered_df["country_display"]
            .value_counts(normalize=True)
        )
        if not country_share.empty:
            highest_country_share = country_share.iloc[0] * 100
            if highest_country_share > 40:
                recommendations.append(
                    "🌍 Competitors are concentrated in a single country. "
                    "Explore country-wise representation to understand "
                    "the geographical distribution."
                )

        # Ranking concentration
        top_100_count = (
            filtered_df["rank"] <= 100
        ).sum()
        top_100_share = (
            top_100_count / total_players
        ) * 100
        if top_100_share < 20:
            recommendations.append(
                "🏅 A relatively small share of competitors is within "
                "the Top 100. Review ranking-tier distribution "
                "for a deeper performance analysis."
            )

        # Gender representation
        if "gender" in filtered_df.columns:
            gender_counts = (
                filtered_df["gender"]
                .value_counts(normalize=True)
            )
            if len(gender_counts) >= 2:
                gender_gap = (
                    gender_counts.iloc[0] -
                    gender_counts.iloc[1]
                ) * 100
                if gender_gap > 20:
                    recommendations.append(
                        "⚖️ Gender representation differs considerably. "
                        "Compare ATP and WTA datasets separately "
                        "for more meaningful insights."
                    )

        # Ranking points variation
        points_std = filtered_df["points"].std()
        if pd.notna(points_std) and points_std > 0:
            recommendations.append(
                "📊 Ranking points show variation across competitors. "
                "Use the Statistical Analysis page to examine "
                "distribution, median and outliers."
            )
    if recommendations:
        for recommendation in recommendations:
            st.info(recommendation)
    else:
        st.success(
            "The current selection does not trigger any predefined "
            "recommendation rules."
        )
    st.caption(
        "Recommendations are rule-based observations from the current "
        "dataset, not predictions or causal conclusions."
    )
    st.divider()

    # =================================================
    # ATP VS WTA COMPARISON
    # =================================================

    render_section_header(
        "ATP vs WTA Comparison",
        "Comparison of performance metrics between ATP and WTA rankings.",
        "🆚"
    )
    ranking_summary = (
        filtered_df.groupby("ranking_name")
        .agg(
            total_players=("competitor_id", "nunique"),
            average_points=("points", "mean")
        )
        .reset_index()
    )
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            ranking_summary,
            names="ranking_name",
            values="total_players",
            hole=0.65,
            title="Competitor Distribution",
            template=chart_template
        )
        fig.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )
        fig.update_layout(height=350,margin=dict(t=55, b=20, l=20, r=20))
        apply_chart_theme(fig)
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        fig = px.bar(
            ranking_summary,
            x="ranking_name",
            y="average_points",
            color="ranking_name",
            title="Average Ranking Points",
            labels={
                "ranking_name": "Ranking Type",
                "average_points": "Average Points"
            },
            template=chart_template
        )
        fig.update_layout(
            height=350,
            showlegend=False,
            margin=dict(t=55, b=20)
        )
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig,use_container_width=True)
    st.divider()

    # =================================================
    # COUNTRY DISTRIBUTION
    # =================================================

    render_section_header(
        "Global Tennis Representation",
        "Distribution of tennis competitors across different countries.",
        "🌍"
    )
    country_summary = (
        filtered_df.groupby("country_display")
        .agg(
            total_players=("competitor_id", "nunique"),
            average_points=("points", "mean")
        )
        .reset_index()
        .sort_values(
            "total_players",
            ascending=False
        )
        .head(10)
    )
    if not country_summary.empty:
        fig = px.bar(
            country_summary.sort_values(
                "total_players",
                ascending=True
            ),
            x="total_players",
            y="country_display",
            orientation="h",
            color="total_players",
            title="Top 10 Countries by Competitor Count",
            labels={
                "total_players": "Total Competitors",
                "country_display": "Country"
            },
            template=chart_template
        )
        fig.update_layout(
            height=430,
            showlegend=False,
            yaxis_title=None,
            margin=dict(t=55, b=30)
        )
        apply_chart_theme(fig)
        st.plotly_chart(fig,use_container_width=True)
    st.divider()

    # =================================================
    # RANKING POINTS DISTRIBUTION
    # =================================================

    render_section_header(
        "Ranking Points Distribution",
        "Visualizing the spread of ranking points among competitors.",
        "📊"
    )
    points_df = filtered_df.dropna(subset=["points"])
    if not points_df.empty:
        fig = px.histogram(
            points_df,
            x="points",
            color="ranking_name",
            nbins=30,
            barmode="overlay",
            opacity=0.75,
            title="Distribution of Ranking Points",
            labels={
                "points": "Ranking Points",
                "count": "Number of Players"
            },
            template=chart_template
        )
        fig.update_layout(height=400,margin=dict(t=55, b=30))
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig,use_container_width=True)
    st.divider()

    # =================================================
    # ADVANCED RANKING DISTRIBUTION
    # =================================================

    render_section_header(
        "Advanced Ranking Distribution",
        "Detailed analysis of competitor rankings across different tiers.",
        "📈"
    )

    ranking_analysis_df = filtered_df.dropna(
        subset=["rank", "points"]
    ).copy()

    if not ranking_analysis_df.empty:

        # ---------------------------------------------
        # CREATE RANKING TIERS
        # ---------------------------------------------

        ranking_bins = [0, 10, 25, 50, 100, 250, 500, float("inf")]
        ranking_labels = [
            "Top 10",
            "11–25",
            "26–50",
            "51–100",
            "101–250",
            "251–500",
            "Above 500"
        ]
        ranking_analysis_df["ranking_tier"] = pd.cut(
            ranking_analysis_df["rank"],
            bins=ranking_bins,
            labels=ranking_labels,
            include_lowest=True
        )

        # ---------------------------------------------
        # RANKING TIER SUMMARY
        # ---------------------------------------------

        tier_summary = (
            ranking_analysis_df
            .groupby(
                "ranking_tier",
                observed=False
            )
            .agg(
                total_competitors=(
                    "competitor_id",
                    "nunique"
                ),
                average_points=(
                    "points",
                    "mean"
                ),
                median_points=(
                    "points",
                    "median"
                )
            )
            .reset_index()
        )
        tier_summary = tier_summary[tier_summary["total_competitors"] > 0]

        # ---------------------------------------------
        # CHART 1: RANKING TIER DISTRIBUTION
        # ---------------------------------------------

        st.markdown("#### 1. Competitor Distribution by Ranking Tier")

        if not tier_summary.empty:

            fig = px.bar(
                tier_summary,
                x="ranking_tier",
                y="total_competitors",
                color="total_competitors",
                text="total_competitors",
                title="Competitors Across Ranking Tiers",
                labels={
                    "ranking_tier": "Ranking Tier",
                    "total_competitors": "Total Competitors"
                },
                template=chart_template
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Ranking Tier",
                yaxis_title="Number of Competitors",
                margin=dict(t=60, b=30)
            )
            fig = apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ---------------------------------------------
        # CHART 2: POINTS DISTRIBUTION BY TIER
        # ---------------------------------------------

        st.markdown("#### 2. Ranking Tier vs Points Analysis")

        fig = px.box(
            ranking_analysis_df,
            x="ranking_tier",
            y="points",
            color="ranking_tier",
            points="outliers",
            title="Ranking Points Distribution Across Tiers",
            labels={
                "ranking_tier": "Ranking Tier",
                "points": "Ranking Points"
            },
            template=chart_template
        )

        fig.update_layout(
            height=430,
            showlegend=False,
            xaxis_title="Ranking Tier",
            yaxis_title="Ranking Points",
            margin=dict(t=60, b=30)
        )
        apply_chart_theme(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------------------------------------
        # CHART 3: RANK VS POINTS RELATIONSHIP
        # ---------------------------------------------

        st.markdown("#### 3. Ranking Position vs Ranking Points")

        fig = px.scatter(
            ranking_analysis_df,
            x="rank",
            y="points",
            color="ranking_name",
            hover_name="competitor_name",
            hover_data={
                "country_display": True,
                "competitions_played": True,
                "rank": True,
                "points": True
            },
            title="Relationship Between Ranking Position and Points",
            labels={
                "rank": "Ranking Position",
                "points": "Ranking Points",
                "ranking_name": "Ranking Type"
            },
            template=chart_template
        )

        fig.update_layout(
            height=450,
            xaxis_title="Ranking Position",
            yaxis_title="Ranking Points",
            margin=dict(t=60, b=30)
        )
        apply_chart_theme(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ---------------------------------------------
        # RANKING TIER STATISTICS TABLE
        # ---------------------------------------------

        st.markdown("#### Ranking Tier Statistical Summary")

        display_tier_summary = tier_summary.rename(
            columns={
                "ranking_tier": "Ranking Tier",
                "total_competitors": "Competitors",
                "average_points": "Average Points",
                "median_points": "Median Points"
            }
        )

        display_tier_summary[
            ["Average Points", "Median Points"]
        ] = display_tier_summary[
            ["Average Points", "Median Points"]
        ].round(2)

        render_dataframe(
            display_tier_summary,
            hide_index=True
        )

    else:
        st.warning(
            "Insufficient ranking and points data "
            "for advanced ranking analysis."
        )

    st.divider()

    # =================================================
    # TOP 10 PLAYER LEADERBOARD
    # =================================================

    render_section_header(
        "Top 10 Player Leaderboard",
        "Top performers based on their ranking positions and points.",
        "🏆"
    )
    leaderboard = (
        filtered_df.sort_values(
            ["rank", "points"],
            ascending=[True, False]
        )
        .drop_duplicates(
            subset=["ranking_snapshot_id", "competitor_id"]
        )
        .head(10)
        [[
            "rank",
            "competitor_name",
            "country_display",
            "ranking_name",
            "points",
            "movement",
            "competitions_played"
        ]]
        .rename(
            columns={
                "rank": "Rank",
                "competitor_name": "Player",
                "country_display": "Country",
                "ranking_name": "Ranking Type",
                "points": "Points",
                "movement": "Movement",
                "competitions_played": "Competitions Played"
            }
        )
    )
    render_dataframe(
        leaderboard,
        hide_index=True
    )

    # =================================================
    # DATA EXPORT
    # =================================================

    render_section_header(
        "Download Filtered Data",
        "Export the filtered tennis analytics data as a CSV file.",
        "💾"
    )
    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download Filtered Data (CSV)",
        data=csv_data,
        file_name="tennis_analytics_report.csv",
        mime="text/csv",
        use_container_width=False
    )
    st.caption(
        f"Showing {len(filtered_df):,} records "
        "from the connected tennis rankings database."
    )
