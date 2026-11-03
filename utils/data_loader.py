import streamlit as st
import pandas as pd
from database.connection import get_connection

# ==========================================
# LOAD COMPLETE TENNIS DATA
# ==========================================

@st.cache_data(show_spinner="Loading tennis database...")
def load_tennis_data():
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
            s.week,
            s.generated_at
        FROM DoublesRankings d
        INNER JOIN Competitors c
            ON d.competitor_id = c.competitor_id
        INNER JOIN RankingSnapshots s
            ON d.ranking_snapshot_id = s.ranking_snapshot_id
        ORDER BY
            s.ranking_name,
            d.rank ASC
        """
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # ======================================
    # DATA CLEANING
    # ======================================

    if df.empty:
        return df

    # Remove duplicate ranking records
    df = df.drop_duplicates(
        subset=[
            "ranking_snapshot_id",
            "competitor_id"
        ]
    )

    # Standardize text columns
    text_columns = [
        "competitor_name",
        "abbreviation",
        "country",
        "country_code",
        "ranking_name",
        "gender"
    ]
    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Handle missing text values
    df["country"] = df["country"].fillna("Unknown")
    df["country_code"] = (
        df["country_code"].fillna("UNK")
    )
    df["abbreviation"] = (
        df["abbreviation"].fillna("N/A")
    )

    # Convert numeric columns safely
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
            df[column],
            errors="coerce"
        )

    # Fill optional numeric values
    df["movement"] = df["movement"].fillna(0)
    df["points"] = df["points"].fillna(0)
    df["competitions_played"] = (
        df["competitions_played"].fillna(0)
    )
    # Sort records

    df = df.sort_values(
        by=["ranking_name", "rank"],
        ascending=[True, True]
    )
    df = df.reset_index(drop=True)
    return df

# ==========================================
# GET ATP DATA
# ==========================================

def get_atp_data(df):
    return df[
        df["ranking_name"].str.upper() == "ATP"
    ].copy()

# ==========================================
# GET WTA DATA
# ==========================================

def get_wta_data(df):
    return df[
        df["ranking_name"].str.upper() == "WTA"
    ].copy()

# ==========================================
# GET DATA QUALITY REPORT
# ==========================================

def get_data_quality(df):
    if df.empty:
        return {
            "total_records": 0,
            "duplicate_records": 0,
            "missing_values": {},
            "total_countries": 0
        }

    return {
        "total_records": len(df),
        "duplicate_records": int(
            df.duplicated(
                subset=[
                    "ranking_snapshot_id",
                    "competitor_id"
                ]
            ).sum()
        ),
        "missing_values": (
            df.isnull()
            .sum()
            .to_dict()
        ),
        "total_countries": int(
            df.loc[
                df["country"] != "Unknown",
                "country"
            ].nunique()
        )
    }

# ==========================================
# DATABASE DATA TEST
# ==========================================

if __name__ == "__main__":
    print("\n===================================")
    print("TENNIS DATA PROCESSING TEST")
    print("===================================")

    df = load_tennis_data()
    print("\nTotal Records:", len(df))
    print("\nAvailable Columns:")
    print(df.columns.tolist())
    print("\nRanking Distribution:")
    print(
        df["ranking_name"]
        .value_counts()
    )
    print("\nATP Records:", len(get_atp_data(df)))
    print("WTA Records:", len(get_wta_data(df)))
    print("\nData Quality Report:")
    print(get_data_quality(df))
    print("\nTop 5 Ranking Records:")
    print(
        df[
            [
                "competitor_name",
                "ranking_name",
                "country",
                "rank",
                "points"
            ]
        ].head()
    )
    print("\nDATA PROCESSING SUCCESSFUL!")
