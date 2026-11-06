import streamlit as st
import pandas as pd
import plotly.express as px
from database.connection import get_connection
from utils.styling import (
    render_section_header,
    apply_chart_theme,
    render_dataframe,
    render_kpi
)

# =====================================================
# LOAD VENUE AND COMPLEX DATA
# =====================================================

@st.cache_data
def load_venue_complex_data():
    conn = get_connection()
    query = """
        SELECT
            v.venue_id,
            v.venue_name,
            v.city_name,
            v.country_name,
            v.country_code,
            v.timezone,
            v.complex_id,
            c.complex_name
        FROM Venues v
        LEFT JOIN Complexes c
            ON v.complex_id = c.complex_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    text_columns = [
        "venue_id",
        "venue_name",
        "city_name",
        "country_name",
        "country_code",
        "timezone",
        "complex_id",
        "complex_name"
    ]
    for col in text_columns:
        df[col] = df[col].fillna("Unknown").astype(str)
    return df

# =====================================================
# VENUE & COMPLEX ANALYTICS PAGE
# =====================================================

def show():
    st.title("🏟️ Venue & Complex Analytics")
    st.markdown(
        "Explore tennis venue locations, complex distribution, "
        "country-wise venue coverage, cities and timezones."
    )
    st.divider()

    # -------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------

    try:
        df = load_venue_complex_data()
    except Exception as e:
        st.error(f"Unable to load venue and complex data: {e}")
        return
    if df.empty:
        st.warning("No venue records available.")
        return

    # -------------------------------------------------
    # ANALYSIS FILTERS
    # -------------------------------------------------

    render_section_header(
        "Venue Analysis Filters",
        "Filter venues by country, city and complex.",
        "🔎"
    )
    col1, col2, col3 = st.columns(3)
    country_options = sorted(df["country_name"].unique().tolist())
    city_options = sorted(df["city_name"].unique().tolist())
    complex_options = sorted(df["complex_name"].unique().tolist())
    with col1:
        selected_country = st.selectbox(
            "Select Country",
            ["All"] + country_options,
            key="venue_country_filter"
        )
    with col2:
        selected_city = st.selectbox(
            "Select City",
            ["All"] + city_options,
            key="venue_city_filter"
        )
    with col3:
        selected_complex = st.selectbox(
            "Select Complex",
            ["All"] + complex_options,
            key="venue_complex_filter"
        )
    filtered_df = df.copy()

    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country_name"] == selected_country]
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["city_name"] == selected_city]
    if selected_complex != "All":
        filtered_df = filtered_df[filtered_df["complex_name"] == selected_complex]
    if filtered_df.empty:
        st.warning("No venues found for the selected filters.")
        return
    st.divider()

    # -------------------------------------------------
    # OVERVIEW KPIs
    # -------------------------------------------------

    render_section_header(
        "Venue & Complex Overview",
        "Key statistics for the selected venue records.",
        "📊"
    )
    total_venues = filtered_df["venue_id"].nunique()
    total_complexes = filtered_df["complex_id"].nunique()
    total_countries = filtered_df["country_name"].nunique()
    total_cities = (
        filtered_df[["city_name", "country_name"]]
        .drop_duplicates()
        .shape[0]
    )
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        render_kpi(
            "Total Venues",
            f"{total_venues:,}",
            "Available tennis venues"
        )
    with col2:
        render_kpi(
            "Total Complexes",
            f"{total_complexes:,}",
            "Associated complexes"
        )
    with col3:
        render_kpi(
            "Total Countries",
            f"{total_countries:,}",
            "Countries represented"
        )
    with col4:
        render_kpi(
            "Total Cities",
            f"{total_cities:,}",
            "Unique city-country pairs"
        )
    st.divider()

    # -------------------------------------------------
    # COUNTRY-WISE VENUE DISTRIBUTION
    # -------------------------------------------------

    render_section_header(
        "Country-wise Venue Distribution",
        "Identify countries with the highest number of tennis venues.",
        "🌍"
    )
    country_summary = (
        filtered_df.groupby("country_name")
        .agg(
            total_venues=("venue_id", "nunique"),
            total_complexes=("complex_id", "nunique"),
            total_cities=("city_name", "nunique")
        )
        .reset_index()
        .sort_values("total_venues", ascending=False)
    )
    top_countries = country_summary.head(15)
    if not top_countries.empty:
        fig_country = px.bar(
            top_countries,
            x="country_name",
            y="total_venues",
            text="total_venues",
            title="Top 15 Countries by Venue Count",
            labels={
                "country_name": "Country",
                "total_venues": "Number of Venues"
            }
        )
        fig_country.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            marker_line_width=1.2
        )
        fig_country.update_layout(
            height=430,
            showlegend=False,
            xaxis_title="Country",
            yaxis_title="Total Venues",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=75, l=25, r=25)
        )
        fig_country = apply_chart_theme(fig_country)
        st.plotly_chart(
            fig_country,
            use_container_width=True
        )
    st.divider()

    # -------------------------------------------------
    # CITY-WISE VENUE ANALYSIS
    # -------------------------------------------------

    render_section_header(
        "City-wise Venue Analysis",
        "Discover cities with the highest concentration of tennis venues.",
        "🏙️"
    )
    city_summary = (
        filtered_df.groupby(["city_name", "country_name"])
        .agg(
            total_venues=("venue_id", "nunique"),
            total_complexes=("complex_id", "nunique")
        )
        .reset_index()
        .sort_values("total_venues", ascending=False)
    )
    city_summary["city_location"] = (
        city_summary["city_name"]
        + ", "
        + city_summary["country_name"]
    )
    top_cities = city_summary.head(15)
    if not top_cities.empty:
        fig_city = px.bar(
            top_cities,
            x="city_location",
            y="total_venues",
            text="total_venues",
            title="Top 15 Cities by Venue Count",
            labels={
                "city_location": "City",
                "total_venues": "Number of Venues"
            }
        )
        fig_city.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            marker_line_width=1.2
        )
        fig_city.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="City",
            yaxis_title="Total Venues",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=100, l=25, r=25)
        )
        fig_city = apply_chart_theme(fig_city)
        st.plotly_chart(
            fig_city,
            use_container_width=True
        )
    st.divider()

    # -------------------------------------------------
    # COMPLEX ANALYSIS
    # -------------------------------------------------

    render_section_header(
        "Complex-wise Venue Analysis",
        "Analyze how venues are distributed across tennis complexes.",
        "🏟️"
    )
    complex_summary = (
        filtered_df.groupby(["complex_id", "complex_name"])
        .agg(
            total_venues=("venue_id", "nunique"),
            total_cities=("city_name", "nunique"),
            total_countries=("country_name", "nunique")
        )
        .reset_index()
        .sort_values("total_venues", ascending=False)
    )
    top_complexes = complex_summary.head(15)
    if not top_complexes.empty:
        fig_complex = px.bar(
            top_complexes,
            x="complex_name",
            y="total_venues",
            text="total_venues",
            title="Top 15 Complexes by Number of Venues",
            labels={
                "complex_name": "Complex",
                "total_venues": "Number of Venues"
            }
        )
        fig_complex.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            marker_line_width=1.2
        )
        fig_complex.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="Complex Name",
            yaxis_title="Total Venues",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=100, l=25, r=25)
        )
        fig_complex = apply_chart_theme(fig_complex)
        st.plotly_chart(
            fig_complex,
            use_container_width=True
        )
    st.divider()

    # -------------------------------------------------
    # TIMEZONE ANALYSIS
    # -------------------------------------------------

    render_section_header(
        "Timezone Distribution",
        "Explore venue coverage across different geographical timezones.",
        "🕒"
    )
    timezone_summary = (
        filtered_df.groupby("timezone")
        .agg(
            total_venues=("venue_id", "nunique"),
            total_countries=("country_name", "nunique")
        )
        .reset_index()
        .sort_values("total_venues", ascending=False)
        .head(15)
    )
    if not timezone_summary.empty:
        fig_timezone = px.bar(
            timezone_summary,
            x="timezone",
            y="total_venues",
            text="total_venues",
            title="Top 15 Timezones by Venue Count",
            labels={
                "timezone": "Timezone",
                "total_venues": "Number of Venues"
            }
        )
        fig_timezone.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            marker_line_width=1.2
        )
        fig_timezone.update_layout(
            height=450,
            showlegend=False,
            xaxis_title="Timezone",
            yaxis_title="Total Venues",
            xaxis_tickangle=-45,
            margin=dict(t=65, b=100, l=25, r=25)
        )
        fig_timezone = apply_chart_theme(fig_timezone)
        st.plotly_chart(
            fig_timezone,
            use_container_width=True
        )
    st.divider()

    # -------------------------------------------------
    # COUNTRY PERFORMANCE SUMMARY
    # -------------------------------------------------

    render_section_header(
        "Country-wise Venue Summary",
        "Detailed venue, complex and city statistics by country.",
        "📋"
    )
    render_dataframe(
        country_summary,
        hide_index=True,
        use_container_width=True
    )
    st.divider()

    # -------------------------------------------------
    # COMPLEX DIRECTORY
    # -------------------------------------------------

    render_section_header(
        "Complex Directory",
        "Browse complex identifiers and their associated venue statistics.",
        "🏟️"
    )
    render_dataframe(
        complex_summary,
        hide_index=True,
        use_container_width=True
    )
    st.divider()

    # -------------------------------------------------
    # VENUE DIRECTORY
    # -------------------------------------------------

    render_section_header(
        "Venue Directory",
        "Explore venue details, geographical information and complex associations.",
        "📑"
    )
    directory_columns = [
        "venue_id",
        "venue_name",
        "city_name",
        "country_name",
        "country_code",
        "timezone",
        "complex_id",
        "complex_name"
    ]
    venue_directory = filtered_df[directory_columns].copy()
    search_text = st.text_input(
        "Search Venue, City or Complex",
        placeholder="Enter venue, city or complex name..."
    )
    if search_text.strip():
        search_value = search_text.strip()
        search_mask = (
            venue_directory[directory_columns]
            .astype(str)
            .apply(
                lambda column: column.str.contains(
                    search_value,
                    case=False,
                    na=False,
                    regex=False
                )
            )
            .any(axis=1)
        )
        venue_directory = venue_directory[search_mask]
    render_dataframe(
        venue_directory,
        hide_index=True,
        use_container_width=True
    )
    st.caption(f"Showing {len(venue_directory):,} matching venue records.")
    st.divider()

    # -------------------------------------------------
    # CSV EXPORT
    # -------------------------------------------------

    render_section_header(
        "Download Venue & Complex Reports",
        "Export filtered venue, country and complex analysis reports.",
        "📥"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Venue Data",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="tennis_venue_analysis.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            "Download Country Summary",
            data=country_summary.to_csv(index=False).encode("utf-8"),
            file_name="tennis_venue_country_summary.csv",
            mime="text/csv"
        )
    with col3:
        st.download_button(
            "Download Complex Summary",
            data=complex_summary.to_csv(index=False).encode("utf-8"),
            file_name="tennis_complex_summary.csv",
            mime="text/csv"
        )
    st.caption(
        "Venue and complex analysis uses the existing SQLite database. "
        "Original source data and existing ranking tables are not modified."
    )
