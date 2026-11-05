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
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_quality_data():
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
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --------------------------------------------------
# DATA QUALITY DASHBOARD
# --------------------------------------------------

def show():
    st.title("🛡️ Data Quality & Validation Dashboard")
    st.markdown(
        "Check dataset completeness, duplicate records, "
        "missing values, invalid values, and data consistency."
    )
    st.divider()
    try:
        df = load_quality_data()
    except Exception as e:
        st.error(f"Unable to load data: {e}")
        return
    if df.empty:
        st.warning("No records available for quality analysis.")
        return

    # Apply global sidebar filters
    df = apply_global_filters(df)
    if df.empty:
        st.warning("No records match the global filters for quality analysis.")
        return

    # --------------------------------------------------
    # DATA PREPARATION
    # --------------------------------------------------

    numeric_columns = [
        "rank",
        "movement",
        "points",
        "competitions_played"
    ]
    text_columns = [
        "competitor_id",
        "competitor_name",
        "abbreviation",
        "country",
        "country_code",
        "ranking_name",
        "gender"
    ]
    original_df = df.copy()
    invalid_numeric = {}
    for col in numeric_columns:
        original_values = df[col].copy()
        converted = pd.to_numeric(original_values,errors="coerce")
        invalid_numeric[col] = (original_values.notna() & converted.isna()).sum()
        df[col] = converted

    # --------------------------------------------------
    # OVERALL DATA QUALITY METRICS
    # --------------------------------------------------

    total_records = len(df)
    total_columns = len(df.columns)
    total_cells = total_records * total_columns
    missing_cells = int(df.isna().sum().sum())
    complete_cells = total_cells - missing_cells
    completeness = (
        (complete_cells / total_cells) * 100
        if total_cells else 0
    )
    duplicate_records = int(df.duplicated().sum())
    duplicate_competitor_records = int(
        df.duplicated(
            subset=["ranking_snapshot_id", "competitor_id"]
        ).sum()
    )
    unique_competitors = df["competitor_id"].nunique()
    unique_countries = df["country"].nunique()
    render_section_header(
        "Overall Data Quality Overview",
        "Summary of key data quality metrics.",
        "📊"
    )
    # First KPI Row
    k1, k2, k3 = st.columns(3, gap="large")
    with k1:
        render_kpi(
            "Total Records",
            f"{total_records:,}",
            "Total database records"
        )
    with k2:
        render_kpi(
            "Total Columns",
            f"{total_columns:,}",
            "Total dataset columns"
        )
    with k3:
        render_kpi(
            "Completeness",
            f"{completeness:.2f}%",
            "Overall data completeness"
        )
    # Second KPI Row
    k4, k5, k6 = st.columns(3, gap="large")
    with k4:
        render_kpi(
            "Duplicate Rows",
            f"{duplicate_records:,}",
            "Exact duplicate records"
        )
    with k5:
        render_kpi(
            "Unique Competitors",
            f"{unique_competitors:,}",
            "Distinct competitors"
        )
    with k6:
        render_kpi(
            "Unique Countries",
            f"{unique_countries:,}",
            "Countries represented"
        )
    st.divider()

    # --------------------------------------------------
    # MISSING VALUE ANALYSIS
    # --------------------------------------------------

    render_section_header(
        "Missing Value Analysis",
        "Identify columns with missing values and their counts.",
        "🔍"
    )
    missing_summary = (
        original_df.isna()
        .sum()
        .reset_index()
    )
    missing_summary.columns = ["Column","Missing Values"]
    missing_summary["Missing Percentage"] = (
        missing_summary["Missing Values"]
        / total_records * 100
    ).round(2)
    missing_summary = missing_summary.sort_values("Missing Values",ascending=False)
    missing_summary = missing_summary[missing_summary["Missing Values"] > 0]
    if not missing_summary.empty:
        fig_missing = px.bar(
            missing_summary,
            x="Column",
            y="Missing Values",
            text="Missing Values",
            title="Missing Values by Column"
        ) 
        fig_missing.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            textfont=dict(size=13),
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Missing Values: %{y:,}"
                "<extra></extra>"
            )
        )
        fig_missing.update_layout(
            height=390,
            showlegend=False,
            bargap=0.35,
            xaxis_title="Column",
            yaxis_title="Missing Values",
            margin=dict(t=55, b=45, l=25, r=25),
            title=dict(
                font=dict(size=19),
                x=0.02,
                xanchor="left"
            ),
            hoverlabel=dict(font_size=13)
        )
        fig_missing = apply_chart_theme(fig_missing)
        st.plotly_chart(
            fig_missing,
            use_container_width=True
        )
        render_dataframe(
            missing_summary,
            hide_index=True
        )
    else:
        st.success("No missing values found in the joined dataset.")
    st.divider()

    # --------------------------------------------------
    # NUMERIC VALIDATION
    # --------------------------------------------------

    render_section_header(
        "Numeric Data Validation",
        "Review missing, invalid and valid numeric values.",
        "🔢"
    )
    numeric_validation = []
    for col in numeric_columns:
        invalid_count = int(invalid_numeric[col])
        missing_count = int(original_df[col].isna().sum())
        numeric_validation.append({
            "Column": col,
            "Missing Values": missing_count,
            "Invalid Numeric Values": invalid_count,
            "Valid Numeric Values": int(df[col].notna().sum())
        })
    numeric_validation_df = pd.DataFrame(numeric_validation)
    render_dataframe(
        numeric_validation_df,
        hide_index=True
    )
    st.divider()

    # --------------------------------------------------
    # VALUE RANGE VALIDATION
    # --------------------------------------------------

    render_section_header(
        "Value Range Validation",
        "Check numeric columns for invalid value ranges.",
        "📏"
    )
    range_checks = []
    range_conditions = {
        "rank": df["rank"] <= 0,
        "points": df["points"] < 0,
        "competitions_played": df["competitions_played"] < 0
    }
    for column, condition in range_conditions.items():
        invalid_count = int((condition & df[column].notna()).sum())
        range_checks.append({
            "Column": column,
            "Validation Rule": (
                "Must be greater than 0"
                if column == "rank"
                else "Must not be negative"
            ),
            "Invalid Records": invalid_count,
            "Status": "Pass" if invalid_count == 0 else "Review Required"
        })
    range_check_df = pd.DataFrame(range_checks)
    render_dataframe(
        range_check_df,
        hide_index=True
    )
    st.divider()

    # --------------------------------------------------
    # DUPLICATE ANALYSIS
    # --------------------------------------------------

    render_section_header(
        "Duplicate Record Analysis",
        "Identify exact duplicates and repeated competitor-snapshot records.",
        "📑"
    )
    duplicate_df = df[df.duplicated(keep=False)].copy()
    if not duplicate_df.empty:
        st.warning(f"{len(duplicate_df):,} rows are involved in exact duplicate groups.")
        render_dataframe(
            duplicate_df,
            hide_index=True
        )
    else:
        st.success("No exact duplicate rows found.")
    duplicate_ranking_df = df[
        df.duplicated(
            subset=["ranking_snapshot_id", "competitor_id"],
            keep=False
        )
    ].copy()
    if not duplicate_ranking_df.empty:
        st.warning("Duplicate competitor records exist within the same ranking snapshot.")
        render_dataframe(
            duplicate_ranking_df[
                [
                    "competitor_id",
                    "competitor_name",
                    "ranking_snapshot_id",
                    "ranking_name",
                    "rank",
                    "points"
                ]
            ],
            hide_index=True
        )
    else:
        st.success("No repeated competitor-snapshot combinations found.")
    st.divider()

    # --------------------------------------------------
    # TEXT COMPLETENESS
    # --------------------------------------------------

    render_section_header(
        "Text Column Completeness",
        "Review missing and blank values in text-based columns.",
        "📝"
    )
    text_quality = []
    for col in text_columns:
        missing_count = int(original_df[col].isna().sum())
        blank_count = int(
            original_df[col]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
            .sum()
        )
        text_quality.append({
            "Column": col,
            "Missing Values": missing_count,
            "Blank Values": blank_count,
            "Non-Missing Values": int(original_df[col].notna().sum())
        })
    text_quality_df = pd.DataFrame(text_quality)
    render_dataframe(
        text_quality_df,
        hide_index=True
    )
    st.divider()

    # --------------------------------------------------
    # QUALITY SUMMARY
    # --------------------------------------------------

    render_section_header(
        "Data Quality Summary",
        "Comprehensive overview of data quality metrics.",
        "📊"
    )
    summary = pd.DataFrame({
        "Quality Check": [
            "Total Records",
            "Missing Cells",
            "Exact Duplicate Rows",
            "Duplicate Competitor-Snapshot Records",
            "Invalid Rank Values",
            "Negative Points Values",
            "Negative Competition Values"
        ],
        "Result": [
            total_records,
            missing_cells,
            duplicate_records,
            duplicate_competitor_records,
            int(range_checks[0]["Invalid Records"]),
            int(range_checks[1]["Invalid Records"]),
            int(range_checks[2]["Invalid Records"])
        ]
    })
    render_dataframe(
        summary,
        hide_index=True
    )

    # --------------------------------------------------
    # EXPORT QUALITY REPORT
    # --------------------------------------------------

    st.divider()
    render_section_header(
        "Export Data Quality Report",
        "Download the validation summary as a CSV report.",
        "📥"
    )
    report = summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Data Quality Report",
        data=report,
        file_name="tennis_data_quality_report.csv",
        mime="text/csv"
    )
    st.caption(
        "This dashboard performs read-only checks on the joined dataset. "
        "No original database records are changed or deleted."
    )
