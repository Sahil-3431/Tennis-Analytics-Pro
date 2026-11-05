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
# LOAD COUNTRY ANALYSIS DATA
# --------------------------------------------------

@st.cache_data
def load_country_data():
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
        "points",
        "movement",
        "competitions_played"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["competitor_name"] = (df["competitor_name"].fillna("Unknown"))
    df["country"] = df["country"].fillna("Unknown")
    df["country_code"] = (df["country_code"].fillna("Unknown"))
    df["ranking_name"] = (df["ranking_name"].fillna("Unknown").str.upper())
    df["gender"] = df["gender"].fillna("Unknown")
    return df

# --------------------------------------------------
# COUNTRY ANALYSIS PAGE
# --------------------------------------------------

def show():
    st.title("🌍 Country-wise Tennis Performance Analysis")
    st.markdown(
        "Explore country-wise competitor distribution, "
        "ranking points, average rankings, and performance."
    )
    st.divider()
    try:
        df = load_country_data()
    except Exception as e:
        st.error(f"Unable to load country data: {e}")
        return
    if df.empty:
        st.warning("No country records available.")
        return

    # Apply global filters for the main country analysis
    global_filtered_df = apply_global_filters(df)

    # Keep both genders available for gender comparison
    gender_comparison_base = apply_global_filters(
        df,
        include_gender=False
    )

    # --------------------------------------------------
    # FILTERS
    # --------------------------------------------------

    render_section_header(
        "Analysis Filters",
        "Filter country performance by ranking category, country and gender.",
        "🔎"
    )
    col1, col2, col3 = st.columns(3)
    ranking_options = sorted(df["ranking_name"].dropna().unique().tolist())
    country_options = sorted(df["country"].dropna().unique().tolist())
    gender_options = sorted(df["gender"].dropna().unique().tolist())
    with col1:
        selected_ranking = st.selectbox("Ranking Category",["All"] + ranking_options)
    with col2:
        selected_country = st.selectbox("Select Country",["All"] + country_options)
    with col3:
        selected_gender = st.selectbox("Select Gender",["All"] + gender_options)
    filtered_df = global_filtered_df.copy()

    if selected_ranking != "All":
        filtered_df = filtered_df[filtered_df["ranking_name"] == selected_ranking]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country"] == selected_country]
    if selected_gender != "All":
        filtered_df = filtered_df[filtered_df["gender"] == selected_gender]
    filtered_df = filtered_df.drop_duplicates(subset=["ranking_snapshot_id", "competitor_id"])

    if filtered_df.empty:
        st.warning("No records found for the selected filters.")
        return
    st.divider()

    # --------------------------------------------------
    # COUNTRY & GENDER COMPARATIVE INSIGHTS
    # --------------------------------------------------

    render_section_header(
        "Gender-wise Comparative Analysis",
        "Compare competitor representation, ranking points and average rankings across genders.",
        "⚖️"
    )

    # Use the selected ranking and country filters,
    # but keep both genders available for comparison.
    comparison_df = gender_comparison_base.copy()

    if selected_ranking != "All":
        comparison_df = comparison_df[comparison_df["ranking_name"] == selected_ranking]
    if selected_country != "All":
        comparison_df = comparison_df[comparison_df["country"] == selected_country]
    comparison_df = comparison_df.drop_duplicates(subset=["ranking_snapshot_id", "competitor_id"])
    gender_summary = (
        comparison_df.groupby("gender")
        .agg(
            total_competitors=("competitor_id", "nunique"),
            total_points=("points", "sum"),
            average_points=("points", "mean"),
            average_rank=("rank", "mean"),
            average_competitions=("competitions_played", "mean")
        )
        .reset_index()
    )
    if not gender_summary.empty:

        # Gender KPI cards
        gender_col1, gender_col2 = st.columns(2, gap="large")
        for _, gender_row in gender_summary.iterrows():
            gender_name = str(gender_row["gender"]).upper()
            if gender_name in ["MALE", "MEN"]:
                gender_col = gender_col1
            elif gender_name in ["FEMALE", "WOMEN"]:
                gender_col = gender_col2
            else:
                continue
            render_kpi(
                f"{gender_name} Competitors",
                f"{gender_row['total_competitors']:,}",
                "Total competitors"
            )
            render_kpi(
                f"{gender_name} Total Points",
                f"{gender_row['total_points']:,.0f}",
                "Combined ranking points"
            )

        # Competitor count comparison
        fig_gender_count = px.bar(
            gender_summary,
            x="gender",
            y="total_competitors",
            color="gender",
            text="total_competitors",
            title="Competitor Count by Gender",
            labels={
                "gender": "Gender",
                "total_competitors": "Number of Competitors"
            }
        )
        fig_gender_count.update_traces(
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
        fig_gender_count.update_layout(
            height=390,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Gender",
            yaxis_title="Number of Competitors",
            margin=dict(t=55, b=35, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_gender_count = apply_chart_theme(fig_gender_count)
        st.plotly_chart(
            fig_gender_count,
            use_container_width=True
        )

        # Total ranking points comparison
        fig_gender_points = px.bar(
            gender_summary,
            x="gender",
            y="total_points",
            color="gender",
            text="total_points",
            title="Total Ranking Points by Gender",
            labels={
                "gender": "Gender",
                "total_points": "Total Ranking Points"
            }
        )
        fig_gender_points.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Total Ranking Points: %{y:,.0f}"
                "<extra></extra>"
            )
        )
        fig_gender_points.update_layout(
            height=390,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Gender",
            yaxis_title="Total Ranking Points",
            margin=dict(t=55, b=35, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_gender_points = apply_chart_theme(fig_gender_points)
        st.plotly_chart(
            fig_gender_points,
            use_container_width=True
        )

        # Average ranking comparison
        fig_gender_rank = px.bar(
            gender_summary.dropna(subset=["average_rank"]),
            x="gender",
            y="average_rank",
            color="gender",
            text="average_rank",
            title="Average Ranking Position by Gender",
            labels={
                "gender": "Gender",
                "average_rank": "Average Ranking"
            }
        )
        fig_gender_rank.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Ranking: %{y:,.2f}"
                "<extra></extra>"
            )
        )
        fig_gender_rank.update_layout(
            height=390,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Gender",
            yaxis_title="Average Ranking Position",
            margin=dict(t=55, b=35, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_gender_rank = apply_chart_theme(fig_gender_rank)
        st.plotly_chart(
            fig_gender_rank,
            use_container_width=True
        )
        render_section_header(
            "Gender Performance Summary",
            "Summary of competitor counts, ranking points and performance by gender.",
            "📊"
        )
        render_dataframe(
            gender_summary.round(2),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Gender comparison data is not available.")

    # --------------------------------------------------
    # COUNTRY-WISE GENDER DISTRIBUTION
    # --------------------------------------------------

    render_section_header(
        "Country-wise Gender Distribution",
        "Explore gender representation across the leading countries.",
        "🌍"
    )
    country_gender = (
        comparison_df.groupby(["country", "gender"])
        .agg(
            competitors=("competitor_id", "nunique")
        )
        .reset_index()
    )
    if not country_gender.empty:
        top_countries = (
            country_gender.groupby("country")["competitors"]
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .index
        )
        country_gender_top = country_gender[country_gender["country"].isin(top_countries)]
        fig_country_gender = px.bar(
            country_gender_top,
            x="country",
            y="competitors",
            color="gender",
            barmode="group",
            title="Gender Distribution Across Top 15 Countries",
            labels={
                "country": "Country",
                "competitors": "Number of Competitors",
                "gender": "Gender"
            }
        )
        fig_country_gender.update_traces(
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Gender: %{fullData.name}<br>"
                "Competitors: %{y:,}"
                "<extra></extra>"
            )
        )
        fig_country_gender.update_layout(
            height=500,
            barmode="group",
            xaxis_title="Country",
            yaxis_title="Number of Competitors",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=100, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )
        fig_country_gender = apply_chart_theme(fig_country_gender)
        st.plotly_chart(
            fig_country_gender,
            use_container_width=True
        )
        country_gender_pivot = country_gender.pivot(
            index="country",
            columns="gender",
            values="competitors"
        ).fillna(0).reset_index()

        render_section_header(
            "Country × Gender Comparison",
            "Compare competitor counts across countries and gender categories.",
            "📋"
        )
        render_dataframe(
            country_gender_pivot,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Country-wise gender distribution is not available.")

    st.caption(
        "Gender comparison uses both genders for the selected ranking "
        "category and country. The Gender filter affects the existing "
        "country analysis below, not this comparison section. "
        "All comparisons use the available ranking records, not "
        "historical performance trends."
    )
    st.divider()

    # --------------------------------------------------
    # COUNTRY KPIs
    # --------------------------------------------------

    render_section_header(
        "Country Performance Overview",
        "Key statistics covering countries, competitors and ranking points.",
        "📈"
    )
    total_countries = filtered_df["country"].nunique()
    total_competitors = (filtered_df["competitor_id"].nunique())
    total_points = filtered_df["points"].sum()
    average_rank = filtered_df["rank"].mean()
    # Country KPIs
    col1,col2,col3,col4 = st.columns(4, gap="large")
    with col1:
        render_kpi(
            "Total Countries",
            f"{total_countries:,}",
            "Countries represented"
        )
    with col2:
        render_kpi(
            "Total Competitors",
            f"{total_competitors:,}",
            "Across all countries"
        )
    with col3:
        render_kpi(
            "Total Ranking Points",
            f"{total_points:,.0f}",
            "Combined ranking points"
        )
    with col4:
        render_kpi(
            "Average Ranking",
            f"{average_rank:,.2f}",
            "Average ranking position"
        )
    st.divider()

    # --------------------------------------------------
    # COUNTRY-WISE COMPETITOR COUNT
    # --------------------------------------------------

    render_section_header(
        "Competitor Distribution by Country",
        "Identify countries with the highest number of ranked competitors.",
        "🌐"
    )
    country_competitors = (
        filtered_df.groupby("country")
        .agg(
            competitors=("competitor_id", "nunique")
        )
        .reset_index()
        .sort_values("competitors", ascending=False)
        .head(15)
    )
    if not country_competitors.empty:
        fig_country_count = px.bar(
            country_competitors,
            x="country",
            y="competitors",
            text="competitors",
            title="Top 15 Countries by Competitor Count",
            labels={
                "country": "Country",
                "competitors": "Number of Competitors"
            }
        )
        fig_country_count.update_traces(
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
        fig_country_count.update_layout(
            height=420,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Country",
            yaxis_title="Number of Competitors",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_country_count = apply_chart_theme(fig_country_count)
        st.plotly_chart(
            fig_country_count,
            use_container_width=True
        )
    st.divider()

    # --------------------------------------------------
    # COUNTRY-WISE TOTAL POINTS
    # --------------------------------------------------

    render_section_header(
        "Country-wise Ranking Points",
        "Compare total ranking points accumulated by different countries.",
        "🏆"
    )
    country_points = (
        filtered_df.groupby("country")
        .agg(
            total_points=("points", "sum")
        )
        .reset_index()
        .sort_values("total_points", ascending=False)
        .head(15)
    )
    if not country_points.empty:
        fig_country_points = px.bar(
            country_points,
            x="country",
            y="total_points",
            text="total_points",
            title="Top 15 Countries by Total Ranking Points",
            labels={
                "country": "Country",
                "total_points": "Total Ranking Points"
            }
        )
        fig_country_points.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Total Ranking Points: %{y:,.0f}"
                "<extra></extra>"
            )
        )
        fig_country_points.update_layout(
            height=420,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Country",
            yaxis_title="Total Ranking Points",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_country_points = apply_chart_theme(fig_country_points)
        st.plotly_chart(
            fig_country_points,
            use_container_width=True
        )
    st.divider()

    # --------------------------------------------------
    # COUNTRY-WISE AVERAGE RANK
    # --------------------------------------------------

    render_section_header(
        "Country-wise Average Ranking",
        "Compare average ranking positions across countries.",
        "📊"
    )
    country_rank = (
        filtered_df.dropna(subset=["rank"])
        .groupby("country")
        .agg(
            average_rank=("rank", "mean"),
            competitors=("competitor_id", "nunique")
        )
        .reset_index()
        .sort_values("average_rank", ascending=True)
        .head(15)
    )
    if not country_rank.empty:
        fig_country_rank = px.bar(
            country_rank,
            x="country",
            y="average_rank",
            text="average_rank",
            title="15 Countries with Lowest Average Ranking Number",
            labels={
                "country": "Country",
                "average_rank": "Average Ranking"
            }
        )
        fig_country_rank.update_traces(
            textposition="outside",
            texttemplate="%{y:,.2f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Ranking: %{y:,.2f}"
                "<extra></extra>"
            )
        )
        fig_country_rank.update_layout(
            height=420,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Country",
            yaxis_title="Average Ranking Position",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=65, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_country_rank = apply_chart_theme(fig_country_rank)
        st.plotly_chart(
            fig_country_rank,
            use_container_width=True
        )
        st.caption(
            "A lower average ranking number represents a better "
            "average ranking position among the included competitors."
        )
    st.divider()

    # --------------------------------------------------
    # COUNTRY CONTRIBUTION
    # --------------------------------------------------

    render_section_header(
        "Country Contribution to Ranking Points",
        "Explore how the leading countries contribute to total ranking points.",
        "🥇"
    )
    if not country_points.empty:
        fig_country_pie = px.pie(
            country_points,
            names="country",
            values="total_points",
            title="Ranking Points Contribution – Top 15 Countries",
            hole=0.4
        )
        fig_country_pie.update_traces(
            hole=0.65,
            textposition="inside",
            textinfo="label+percent",
            textfont=dict(size=13),
            marker=dict(
                line=dict(width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Total Points: %{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )
        fig_country_pie.update_layout(
            height=600,
            margin=dict(t=65, b=140, l=35, r=35),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=13)
            )
        )
        fig_country_pie = apply_chart_theme(fig_country_pie)
        st.plotly_chart(
            fig_country_pie,
            use_container_width=True
        )
    st.divider()

    # --------------------------------------------------
    # COUNTRY PERFORMANCE TABLE
    # --------------------------------------------------

    render_section_header(
        "Country Performance Summary",
        "Detailed country-level performance metrics and statistics.",
        "📑"
    )
    country_summary = (
        filtered_df.groupby("country")
        .agg(
            total_competitors=("competitor_id", "nunique"),
            total_points=("points", "sum"),
            average_points=("points", "mean"),
            average_rank=("rank", "mean"),
            average_movement=("movement", "mean"),
            average_competitions=("competitions_played", "mean")
        )
        .reset_index()
    )
    country_summary = country_summary.sort_values("total_points",ascending=False)
    render_dataframe(
        country_summary.round(2),
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # COUNTRY PLAYER DIRECTORY
    # --------------------------------------------------

    st.divider()
    render_section_header(
        "Country Competitor Directory",
        "Browse competitor records with country and ranking information.",
        "👥"
    )
    directory_columns = [
        "competitor_name",
        "country",
        "country_code",
        "ranking_name",
        "rank",
        "points",
        "movement",
        "competitions_played"
    ]
    directory = filtered_df[directory_columns].copy()
    directory = directory.sort_values("rank",ascending=True)
    render_dataframe(
        directory,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------

    render_section_header(
        "Download Country Analysis Report",
        "Export the country performance summary as a CSV file.",
        "📥"
    )
    csv = country_summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Country Analysis CSV",
        data=csv,
        file_name="tennis_country_analysis.csv",
        mime="text/csv"
    )
    st.caption(
        "Country analysis uses existing database records. "
        "No original source data is modified."
    )
