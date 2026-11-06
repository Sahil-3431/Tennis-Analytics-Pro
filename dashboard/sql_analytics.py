import re
import sqlite3
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from database.connection import get_connection
from utils.styling import (
    render_section_header,
    apply_chart_theme,
    render_dataframe,
    render_kpi
)

# =========================================================
# READ-ONLY SQL EXECUTION
# =========================================================

def _read_only_authorizer(action, arg1, arg2, database_name, trigger_name):
    """
    Allow only read operations.
    Block database modifications, schema changes, PRAGMA,
    ATTACH, DETACH and other write operations.
    """

    allowed_actions = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_RECURSIVE,
    }

    if action not in allowed_actions:
        return sqlite3.SQLITE_DENY

    # Block potentially unsafe extension loading.
    if action == sqlite3.SQLITE_FUNCTION:
        function_name = (arg2 or arg1 or "").lower()

        if function_name == "load_extension":
            return sqlite3.SQLITE_DENY

    return sqlite3.SQLITE_OK


def validate_read_only_query(query):
    """
    Basic validation before executing a custom SQL query.
    SQLite authorizer provides the actual read-only protection.
    """

    if not query or not query.strip():
        raise ValueError("Please write a SQL query first.")

    cleaned_query = query.strip()

    # Remove SQL comments for initial validation.
    cleaned_query = re.sub(
        r"/\*.*?\*/",
        "",
        cleaned_query,
        flags=re.DOTALL
    )

    cleaned_query = re.sub(
        r"--[^\n]*",
        "",
        cleaned_query
    ).strip()

    if not cleaned_query:
        raise ValueError("The SQL query is empty.")

    if not re.match(
        r"^(SELECT|WITH)\b",
        cleaned_query,
        flags=re.IGNORECASE
    ):
        raise ValueError(
            "Only SELECT and WITH queries are allowed."
        )

    # Prevent multiple SQL statements.
    statement_without_trailing_semicolon = (
        cleaned_query.rstrip().rstrip(";").strip()
    )

    if ";" in statement_without_trailing_semicolon:
        raise ValueError(
            "Only one SQL statement can be executed at a time."
        )

    return query


def run_query(query):
    """
    Execute a read-only SQL query and return a DataFrame.
    """

    validate_read_only_query(query)

    conn = get_connection()

    try:
        conn.set_authorizer(_read_only_authorizer)

        result_df = pd.read_sql_query(query, conn)

        return result_df

    finally:
        conn.close()


# =========================================================
# SQL QUERY LIBRARY – 39 QUERIES
# =========================================================

def get_query_library():

    return {

        # -------------------------------------------------
        # 1. DATABASE & SNAPSHOTS – 4 QUERIES
        # -------------------------------------------------

        "Database & Snapshots": {

            "01. Database Overview": """
                SELECT
                    'Competitors' AS Table_Name,
                    COUNT(*) AS Total_Records
                FROM Competitors

                UNION ALL

                SELECT
                    'DoublesRankings',
                    COUNT(*)
                FROM DoublesRankings

                UNION ALL

                SELECT
                    'RankingSnapshots',
                    COUNT(*)
                FROM RankingSnapshots;
            """,

            "02. Ranking Snapshot Details": """
                SELECT
                    ranking_snapshot_id,
                    ranking_name,
                    gender,
                    year,
                    week,
                    generated_at
                FROM RankingSnapshots
                ORDER BY year DESC, week DESC;
            """,

            "03. Records by Ranking Snapshot": """
                SELECT
                    s.ranking_name,
                    s.gender,
                    s.year,
                    s.week,
                    COUNT(d.competitor_id) AS Total_Players,
                    ROUND(AVG(d.points), 2) AS Average_Points,
                    ROUND(AVG(d.rank), 2) AS Average_Rank
                FROM RankingSnapshots s
                LEFT JOIN DoublesRankings d
                    ON s.ranking_snapshot_id =
                       d.ranking_snapshot_id
                GROUP BY
                    s.ranking_snapshot_id,
                    s.ranking_name,
                    s.gender,
                    s.year,
                    s.week
                ORDER BY s.year DESC, s.week DESC;
            """,

            "04. Latest Snapshot by Category": """
                SELECT
                    ranking_name,
                    gender,
                    year,
                    week,
                    generated_at,
                    ranking_snapshot_id
                FROM RankingSnapshots
                WHERE (ranking_name, gender, year, week) IN (
                    SELECT
                        ranking_name,
                        gender,
                        MAX(year),
                        MAX(week)
                    FROM RankingSnapshots
                    GROUP BY ranking_name, gender
                )
                ORDER BY ranking_name, gender;
            """,
        },


        # -------------------------------------------------
        # 2. PLAYERS & PERFORMANCE – 8 QUERIES
        # -------------------------------------------------

        "Players & Performance": {

            "05. Top 10 Players": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played,
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                ORDER BY d.rank ASC
                LIMIT 10;
            """,

            "06. Top 25 Players": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played,
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                ORDER BY d.rank ASC
                LIMIT 25;
            """,

            "07. Top 20 Players by Points": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.points AS Points,
                    d.rank AS Rank,
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                ORDER BY d.points DESC
                LIMIT 20;
            """,

            "08. Players with Most Competitions": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.competitions_played AS Competitions_Played,
                    d.points AS Points,
                    d.rank AS Rank
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                ORDER BY
                    d.competitions_played DESC
                LIMIT 20;
            """,

            "09. Player Ranking and Points Details": """
                SELECT
                    c.competitor_name AS Player,
                    c.abbreviation AS Abbreviation,
                    c.country AS Country,
                    c.country_code AS Country_Code,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played,
                    d.movement AS Recorded_Movement,
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                ORDER BY d.rank ASC;
            """,

            "10. Points per Competition": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played,
                    ROUND(
                        1.0 * d.points /
                        NULLIF(d.competitions_played, 0),
                        2
                    ) AS Points_Per_Competition
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                WHERE d.points IS NOT NULL
                  AND d.competitions_played > 0
                ORDER BY Points_Per_Competition DESC
                LIMIT 25;
            """,

            "11. Players with Zero Competitions": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                WHERE d.competitions_played = 0
                ORDER BY d.rank ASC;
            """,

            "12. Player Performance Summary": """
                SELECT
                    COUNT(DISTINCT d.competitor_id)
                        AS Total_Players,
                    ROUND(AVG(d.rank), 2)
                        AS Average_Rank,
                    MIN(d.rank)
                        AS Best_Rank,
                    MAX(d.rank)
                        AS Lowest_Rank,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points,
                    MAX(d.points)
                        AS Highest_Points,
                    ROUND(AVG(d.competitions_played), 2)
                        AS Average_Competitions
                FROM DoublesRankings d;
            """,
        },


        # -------------------------------------------------
        # 3. COUNTRIES & GEOGRAPHY – 7 QUERIES
        # -------------------------------------------------

        "Countries & Geography": {

            "13. Country-wise Performance": """
                SELECT
                    COALESCE(c.country, 'Unknown') AS Country,
                    COUNT(DISTINCT c.competitor_id)
                        AS Total_Players,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points,
                    ROUND(AVG(d.rank), 2)
                        AS Average_Rank,
                    SUM(d.points) AS Total_Points
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                GROUP BY c.country
                ORDER BY Total_Points DESC;
            """,

            "14. Top 10 Countries by Players": """
                SELECT
                    COALESCE(c.country, 'Unknown') AS Country,
                    COUNT(DISTINCT c.competitor_id)
                        AS Total_Players
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                GROUP BY c.country
                ORDER BY Total_Players DESC
                LIMIT 10;
            """,

            "15. Top 10 Countries by Total Points": """
                SELECT
                    COALESCE(c.country, 'Unknown') AS Country,
                    SUM(d.points) AS Total_Points,
                    COUNT(DISTINCT c.competitor_id)
                        AS Total_Players,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                GROUP BY c.country
                ORDER BY Total_Points DESC
                LIMIT 10;
            """,

            "16. Country-wise Best Ranked Player": """
                SELECT
                    c.country AS Country,
                    c.competitor_name AS Best_Ranked_Player,
                    d.rank AS Best_Rank,
                    d.points AS Player_Points
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                WHERE d.rank = (
                    SELECT MIN(d2.rank)
                    FROM DoublesRankings d2
                    JOIN Competitors c2
                        ON d2.competitor_id = c2.competitor_id
                    WHERE c2.country = c.country
                )
                ORDER BY d.rank ASC;
            """,

            "17. Country-wise Average Ranking": """
                SELECT
                    c.country AS Country,
                    COUNT(*) AS Ranked_Players,
                    ROUND(AVG(d.rank), 2)
                        AS Average_Rank,
                    MIN(d.rank) AS Best_Rank,
                    MAX(d.rank) AS Lowest_Rank
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                WHERE c.country IS NOT NULL
                GROUP BY c.country
                ORDER BY Average_Rank ASC;
            """,

            "18. Country-wise Gender Distribution": """
                SELECT
                    c.country AS Country,
                    s.gender AS Gender,
                    COUNT(DISTINCT c.competitor_id)
                        AS Total_Players,
                    SUM(d.points) AS Total_Points,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points
                FROM Competitors c
                JOIN DoublesRankings d
                    ON c.competitor_id = d.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                GROUP BY c.country, s.gender
                ORDER BY c.country, s.gender;
            """,

            "19. Country Code and Player Directory": """
                SELECT
                    c.country AS Country,
                    c.country_code AS Country_Code,
                    COUNT(DISTINCT c.competitor_id)
                        AS Total_Players,
                    GROUP_CONCAT(
                        c.competitor_name,
                        ', '
                    ) AS Player_Names
                FROM Competitors c
                GROUP BY c.country, c.country_code
                ORDER BY Total_Players DESC;
            """,
        },


        # -------------------------------------------------
        # 4. RANKING ANALYSIS – 6 QUERIES
        # -------------------------------------------------

        "Ranking Analysis": {

            "20. Ranking Category Analysis": """
                SELECT
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender,
                    COUNT(DISTINCT d.competitor_id)
                        AS Total_Players,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points,
                    ROUND(AVG(d.rank), 2)
                        AS Average_Rank
                FROM DoublesRankings d
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                GROUP BY s.ranking_name, s.gender
                ORDER BY Total_Players DESC;
            """,

            "21. Ranking Tier Distribution": """
                SELECT
                    CASE
                        WHEN rank <= 10 THEN 'Top 10'
                        WHEN rank <= 25 THEN '11-25'
                        WHEN rank <= 50 THEN '26-50'
                        WHEN rank <= 100 THEN '51-100'
                        WHEN rank <= 250 THEN '101-250'
                        WHEN rank <= 500 THEN '251-500'
                        ELSE 'Above 500'
                    END AS Ranking_Tier,
                    COUNT(*) AS Total_Players,
                    ROUND(AVG(points), 2)
                        AS Average_Points
                FROM DoublesRankings
                WHERE rank IS NOT NULL
                GROUP BY Ranking_Tier
                ORDER BY MIN(rank);
            """,

            "22. Top 10 Ranking Positions by Category": """
                SELECT
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender,
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                WHERE d.rank <= 10
                ORDER BY s.ranking_name, s.gender, d.rank;
            """,

            "23. Ranking Position Distribution": """
                SELECT
                    MIN(rank) AS Minimum_Rank,
                    MAX(rank) AS Maximum_Rank,
                    ROUND(AVG(rank), 2) AS Average_Rank,
                    ROUND(
                        1.0 * SUM(rank) / COUNT(rank),
                        2
                    ) AS Mean_Rank,
                    COUNT(*) AS Total_Ranked_Players
                FROM DoublesRankings
                WHERE rank IS NOT NULL;
            """,

            "24. Ranking Points by Tier": """
                SELECT
                    CASE
                        WHEN rank <= 10 THEN 'Top 10'
                        WHEN rank <= 25 THEN '11-25'
                        WHEN rank <= 50 THEN '26-50'
                        WHEN rank <= 100 THEN '51-100'
                        WHEN rank <= 250 THEN '101-250'
                        ELSE 'Above 250'
                    END AS Ranking_Tier,
                    COUNT(*) AS Total_Players,
                    MIN(points) AS Minimum_Points,
                    MAX(points) AS Maximum_Points,
                    ROUND(AVG(points), 2)
                        AS Average_Points,
                    SUM(points) AS Total_Points
                FROM DoublesRankings
                WHERE rank IS NOT NULL
                GROUP BY Ranking_Tier
                ORDER BY MIN(rank);
            """,

            "25. Rank vs Points Details": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                WHERE d.rank IS NOT NULL
                  AND d.points IS NOT NULL
                ORDER BY d.rank;
            """,
        },


        # -------------------------------------------------
        # 5. POINTS & COMPETITIONS – 4 QUERIES
        # -------------------------------------------------

        "Points & Competitions": {

            "26. Points Statistics": """
                SELECT
                    COUNT(points) AS Records_With_Points,
                    SUM(points) AS Total_Points,
                    ROUND(AVG(points), 2) AS Average_Points,
                    MIN(points) AS Minimum_Points,
                    MAX(points) AS Maximum_Points
                FROM DoublesRankings;
            """,

            "27. Competition Statistics": """
                SELECT
                    COUNT(competitions_played)
                        AS Records_With_Competition_Data,
                    SUM(competitions_played)
                        AS Total_Competition_Count,
                    ROUND(AVG(competitions_played), 2)
                        AS Average_Competitions,
                    MIN(competitions_played)
                        AS Minimum_Competitions,
                    MAX(competitions_played)
                        AS Maximum_Competitions
                FROM DoublesRankings;
            """,

            "28. Points vs Competitions": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.points AS Points,
                    d.competitions_played AS Competitions_Played,
                    d.rank AS Rank
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                WHERE d.points IS NOT NULL
                  AND d.competitions_played IS NOT NULL
                ORDER BY d.points DESC;
            """,

            "29. Players by Competition Participation": """
                SELECT
                    CASE
                        WHEN competitions_played <= 5
                            THEN '1-5 Competitions'
                        WHEN competitions_played <= 10
                            THEN '6-10 Competitions'
                        WHEN competitions_played <= 20
                            THEN '11-20 Competitions'
                        ELSE 'Above 20 Competitions'
                    END AS Participation_Group,
                    COUNT(*) AS Total_Players,
                    ROUND(AVG(points), 2)
                        AS Average_Points,
                    ROUND(AVG(rank), 2)
                        AS Average_Rank
                FROM DoublesRankings
                WHERE competitions_played IS NOT NULL
                GROUP BY Participation_Group
                ORDER BY MIN(competitions_played);
            """,
        },


        # -------------------------------------------------
        # 6. GENDER ANALYSIS – 3 QUERIES
        # -------------------------------------------------

        "Gender Analysis": {

            "30. Gender-wise Analysis": """
                SELECT
                    s.gender AS Gender,
                    COUNT(DISTINCT d.competitor_id)
                        AS Total_Players,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points,
                    ROUND(AVG(d.rank), 2)
                        AS Average_Rank,
                    ROUND(AVG(d.competitions_played), 2)
                        AS Average_Competitions,
                    SUM(d.points) AS Total_Points
                FROM DoublesRankings d
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                GROUP BY s.gender;
            """,

            "31. Gender-wise Ranking Distribution": """
                SELECT
                    s.gender AS Gender,
                    CASE
                        WHEN d.rank <= 10 THEN 'Top 10'
                        WHEN d.rank <= 50 THEN '11-50'
                        WHEN d.rank <= 100 THEN '51-100'
                        WHEN d.rank <= 250 THEN '101-250'
                        ELSE 'Above 250'
                    END AS Ranking_Tier,
                    COUNT(*) AS Total_Players
                FROM DoublesRankings d
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                WHERE d.rank IS NOT NULL
                GROUP BY s.gender, Ranking_Tier
                ORDER BY s.gender, MIN(d.rank);
            """,

            "32. Gender-wise Points Summary": """
                SELECT
                    s.gender AS Gender,
                    MIN(d.points) AS Minimum_Points,
                    MAX(d.points) AS Maximum_Points,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points,
                    SUM(d.points) AS Total_Points,
                    COUNT(d.points) AS Records_With_Points
                FROM DoublesRankings d
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                GROUP BY s.gender;
            """,
        },


        # -------------------------------------------------
        # 7. MOVEMENT ANALYSIS – 3 QUERIES
        # -------------------------------------------------

        "Movement Analysis": {

            "33. Ranking Movement Distribution": """
                SELECT
                    movement AS Recorded_Movement,
                    COUNT(*) AS Total_Records,
                    ROUND(AVG(points), 2)
                        AS Average_Points,
                    ROUND(AVG(rank), 2)
                        AS Average_Rank
                FROM DoublesRankings
                WHERE movement IS NOT NULL
                GROUP BY movement
                ORDER BY movement;
            """,

            "34. Players by Recorded Movement": """
                SELECT
                    c.competitor_name AS Player,
                    c.country AS Country,
                    d.rank AS Rank,
                    d.points AS Points,
                    d.movement AS Recorded_Movement
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                WHERE d.movement IS NOT NULL
                ORDER BY d.movement, d.rank;
            """,

            "35. Movement by Ranking Category": """
                SELECT
                    s.ranking_name AS Ranking_Category,
                    s.gender AS Gender,
                    d.movement AS Recorded_Movement,
                    COUNT(*) AS Total_Players,
                    ROUND(AVG(d.points), 2)
                        AS Average_Points
                FROM DoublesRankings d
                JOIN RankingSnapshots s
                    ON d.ranking_snapshot_id =
                       s.ranking_snapshot_id
                WHERE d.movement IS NOT NULL
                GROUP BY
                    s.ranking_name,
                    s.gender,
                    d.movement
                ORDER BY
                    s.ranking_name,
                    s.gender,
                    d.movement;
            """,
        },


        # -------------------------------------------------
        # 8. DATA QUALITY – 4 QUERIES
        # -------------------------------------------------

        "Data Quality": {

            "36. Data Quality Summary": """
                SELECT
                    COUNT(*) AS Total_Records,

                    SUM(
                        CASE WHEN competitor_id IS NULL
                        THEN 1 ELSE 0 END
                    ) AS Missing_Competitor_ID,

                    SUM(
                        CASE WHEN rank IS NULL
                        THEN 1 ELSE 0 END
                    ) AS Missing_Rank,

                    SUM(
                        CASE WHEN points IS NULL
                        THEN 1 ELSE 0 END
                    ) AS Missing_Points,

                    SUM(
                        CASE WHEN competitions_played IS NULL
                        THEN 1 ELSE 0 END
                    ) AS Missing_Competitions,

                    SUM(
                        CASE WHEN ranking_snapshot_id IS NULL
                        THEN 1 ELSE 0 END
                    ) AS Missing_Snapshot_ID

                FROM DoublesRankings;
            """,

            "37. Duplicate Ranking Records": """
                SELECT
                    ranking_snapshot_id,
                    competitor_id,
                    COUNT(*) AS Duplicate_Count
                FROM DoublesRankings
                GROUP BY
                    ranking_snapshot_id,
                    competitor_id
                HAVING COUNT(*) > 1
                ORDER BY Duplicate_Count DESC;
            """,

            "38. Competitors Missing Country": """
                SELECT
                    competitor_id,
                    competitor_name,
                    abbreviation,
                    country_code
                FROM Competitors
                WHERE country IS NULL
                   OR TRIM(country) = ''
                ORDER BY competitor_name;
            """,

            "39. Ranking Records with Invalid Values": """
                SELECT
                    competitor_id,
                    ranking_snapshot_id,
                    rank,
                    points,
                    competitions_played,
                    movement
                FROM DoublesRankings
                WHERE rank <= 0
                   OR points < 0
                   OR competitions_played < 0
                ORDER BY rank;
            """,
        },
        
        # -------------------------------------------------
        # 9. VENUES & COMPLEXES – 10 QUERIES
        # -------------------------------------------------

        "Venues & Complexes": {
            "40. Venue and Complex Database Overview": """
                SELECT
                    (SELECT COUNT(*) FROM Venues)
                        AS Total_Venues,
                    (SELECT COUNT(*) FROM Complexes)
                        AS Total_Complexes,
                    (SELECT COUNT(DISTINCT country_name)
                     FROM Venues)
                        AS Total_Countries,
                    (SELECT COUNT(DISTINCT city_name || ', ' || country_name)
                     FROM Venues)
                        AS Total_Cities;
            """,
            "41. Country-wise Venue Distribution": """
                SELECT
                    country_name AS Country,
                    country_code AS Country_Code,
                    COUNT(*) AS Total_Venues,
                    COUNT(DISTINCT city_name) AS Total_Cities,
                    COUNT(DISTINCT complex_id) AS Total_Complexes
                FROM Venues
                GROUP BY country_name, country_code
                ORDER BY Total_Venues DESC;
            """,
            "42. Top 20 Cities by Venue Count": """
                SELECT
                    city_name AS City,
                    country_name AS Country,
                    COUNT(*) AS Total_Venues,
                    COUNT(DISTINCT complex_id) AS Total_Complexes
                FROM Venues
                GROUP BY city_name, country_name
                ORDER BY Total_Venues DESC
                LIMIT 20;
            """,
            "43. Complex-wise Venue Distribution": """
                SELECT
                    c.complex_id AS Complex_ID,
                    c.complex_name AS Complex_Name,
                    COUNT(v.venue_id) AS Total_Venues,
                    COUNT(DISTINCT v.city_name) AS Total_Cities,
                    COUNT(DISTINCT v.country_name) AS Total_Countries
                FROM Complexes c
                LEFT JOIN Venues v
                    ON c.complex_id = v.complex_id
                GROUP BY c.complex_id, c.complex_name
                ORDER BY Total_Venues DESC;
            """,
            "44. Country-wise Complex Count": """
                SELECT
                    country_name AS Country,
                    COUNT(DISTINCT complex_id) AS Total_Complexes,
                    COUNT(venue_id) AS Total_Venues
                FROM Venues
                GROUP BY country_name
                ORDER BY Total_Complexes DESC;
            """,
            "45. Timezone-wise Venue Distribution": """
                SELECT
                    timezone AS Timezone,
                    COUNT(*) AS Total_Venues,
                    COUNT(DISTINCT country_name) AS Total_Countries,
                    COUNT(DISTINCT city_name) AS Total_Cities
                FROM Venues
                GROUP BY timezone
                ORDER BY Total_Venues DESC;
            """,
            "46. Complete Venue and Complex Details": """
                SELECT
                    v.venue_id AS Venue_ID,
                    v.venue_name AS Venue_Name,
                    v.city_name AS City,
                    v.country_name AS Country,
                    v.country_code AS Country_Code,
                    v.timezone AS Timezone,
                    c.complex_id AS Complex_ID,
                    c.complex_name AS Complex_Name
                FROM Venues v
                LEFT JOIN Complexes c
                    ON v.complex_id = c.complex_id
                ORDER BY v.country_name, v.city_name, v.venue_name;
            """,
            "47. Complexes with Multiple Venues": """
                SELECT
                    c.complex_id AS Complex_ID,
                    c.complex_name AS Complex_Name,
                    COUNT(v.venue_id) AS Total_Venues
                FROM Complexes c
                JOIN Venues v
                    ON c.complex_id = v.complex_id
                GROUP BY c.complex_id, c.complex_name
                HAVING COUNT(v.venue_id) > 1
                ORDER BY Total_Venues DESC;
            """,
            "48. Country-wise Venue and City Summary": """
                SELECT
                    country_name AS Country,
                    COUNT(DISTINCT venue_id) AS Total_Venues,
                    COUNT(DISTINCT city_name) AS Total_Cities,
                    COUNT(DISTINCT complex_id) AS Total_Complexes,
                    COUNT(DISTINCT timezone) AS Total_Timezones
                FROM Venues
                GROUP BY country_name
                ORDER BY Total_Venues DESC;
            """,
            "49. Venue and Complex Data Quality Check": """
                SELECT
                    (SELECT COUNT(*)
                     FROM Venues)
                        AS Total_Venues,
                    (SELECT COUNT(*)
                     FROM Venues
                     WHERE venue_id IS NULL
                        OR TRIM(venue_id) = '')
                        AS Missing_Venue_ID,
                    (SELECT COUNT(*)
                     FROM Venues
                     WHERE complex_id IS NULL
                        OR TRIM(complex_id) = '')
                        AS Missing_Complex_ID,
                    (SELECT COUNT(*)
                     FROM Venues v
                     LEFT JOIN Complexes c
                        ON v.complex_id = c.complex_id
                     WHERE c.complex_id IS NULL)
                        AS Unmatched_Complexes,
                    (SELECT COUNT(*)
                     FROM Complexes)
                        AS Total_Complexes,
                    (SELECT COUNT(*)
                     FROM (
                        SELECT venue_id
                        FROM Venues
                        GROUP BY venue_id
                        HAVING COUNT(*) > 1
                     ))
                        AS Duplicate_Venue_IDs,
                    (SELECT COUNT(*)
                     FROM (
                        SELECT complex_id
                        FROM Complexes
                        GROUP BY complex_id
                        HAVING COUNT(*) > 1
                     ))
                        AS Duplicate_Complex_IDs;
            """,
        },
    }

# =========================================================
# QUERY HISTORY MANAGEMENT
# =========================================================

def save_query_history(query, source, result_df):
    if "sql_query_history" not in st.session_state:
        st.session_state["sql_query_history"] = []

    history_item = {
        "query": query.strip(),
        "source": source,
        "rows": len(result_df),
        "columns": len(result_df.columns),
        "executed_at": datetime.now().strftime(
            "%d %b %Y, %I:%M:%S %p"
        )
    }
    history = st.session_state["sql_query_history"]
    history.insert(0, history_item)

    # Keep only the latest 30 executions
    st.session_state["sql_query_history"] = history[:30]

def render_query_history():
    render_section_header(
        "SQL Query History",
        "Review previously executed SQL queries and their execution details.",
        "🕘"
    )
    history = st.session_state.get("sql_query_history", [])
    if not history:
        st.info(
            "No query history available yet. "
            "Execute a query from Query Library or Own SQL Query."
        )
        return
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_kpi(
            "Total Executions",
            f"{len(history):,}",
            "SQL queries executed"
        )
    with col2:
        render_kpi(
            "Unique Query Sources",
            f"{len(set(item['source'] for item in history)):,}",
            "Different query sources"
        )
    st.divider()
    if st.button(
        "Clear Query History",
        key="clear_sql_query_history"
    ):
        st.session_state["sql_query_history"] = []
        st.rerun()

    for index, item in enumerate(history):
        title = (
            f"{index + 1}. {item['source']} "
            f"• {item['executed_at']}"
        )
        with st.expander(title):
            metric_col1, metric_col2, metric_col3 = st.columns(3, gap="large")
            with metric_col1:
                render_kpi(
                    "Result Rows",
                    f"{item['rows']:,}",
                    "Records returned"
                )
            with metric_col2:
                render_kpi(
                    "Result Columns",
                    f"{item['columns']:,}",
                    "Columns returned"
                )
            with metric_col3:
                render_kpi(
                    "Source",
                    item["source"],
                    "Query execution source"
                )
            st.markdown("**Executed SQL Query**")
            st.code(
                item["query"],
                language="sql"
            )
            st.button(
                "Copy SQL Query",
                key=f"copy_history_{index}",
                on_click=lambda q=item["query"]: st.session_state.update(
                    {"history_copy_query": q}
                )
            )
            if st.session_state.get("history_copy_query") == item["query"]:
                st.caption(
                    "Query selected. You can copy it from the code block above."
                )

# =========================================================
# QUERY LIBRARY EXECUTION
# =========================================================

def render_query_result(result_df, key_prefix):

    if result_df.empty:
        st.info("No records returned by this query.")
        return

    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        render_kpi(
            "Result Rows",
            f"{len(result_df):,}",
            "Records returned"
        )
    with col2:
        render_kpi(
            "Result Columns",
            f"{len(result_df.columns):,}",
            "Columns returned"
        )
    with col3:
        render_kpi(
            "Memory Usage",
            f"{result_df.memory_usage(deep=True).sum() / 1024:.1f} KB",
            "Result DataFrame size"
        )
    render_section_header(
        "Query Result",
        "Data returned by the executed SQL statement.",
        "📊"
    )
    render_dataframe(
        result_df,
        hide_index=True,
        use_container_width=True
    )

    csv_data = result_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="tennis_sql_result.csv",
        mime="text/csv",
        key=f"{key_prefix}_download"
    )

    # Visualization
    numeric_columns = result_df.select_dtypes(
        include="number"
    ).columns.tolist()

    category_columns = result_df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if numeric_columns and category_columns:
        st.divider()
        render_section_header(
            "Result Visualization",
            "Create a chart using the returned query data.",
            "📈"
        )
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            category_column = st.selectbox(
                "Category Column",
                category_columns,
                key=f"{key_prefix}_category"
            )

        with chart_col2:
            value_column = st.selectbox(
                "Numeric Column",
                numeric_columns,
                key=f"{key_prefix}_value"
            )

        chart_type = st.selectbox(
            "Chart Type",
            ["Bar", "Line", "Scatter"],
            key=f"{key_prefix}_chart_type"
        )

        chart_df = result_df[
            [category_column, value_column]
        ].dropna().head(100)

        if not chart_df.empty:
            template = "plotly_dark"
            if chart_type == "Bar":
                fig = px.bar(
                    chart_df,
                    x=category_column,
                    y=value_column,
                    color=category_column,
                    title=f"{value_column} by {category_column}",
                    template=template
                )

            elif chart_type == "Line":
                fig = px.line(
                    chart_df,
                    x=category_column,
                    y=value_column,
                    markers=True,
                    title=f"{value_column} by {category_column}",
                    template=template
                )

            else:
                fig = px.scatter(
                    chart_df,
                    x=category_column,
                    y=value_column,
                    title=f"{value_column} by {category_column}",
                    template=template
                )
            fig.update_traces(
                marker_line_width=1.2,
                hoverlabel=dict(font_size=13)
            )
            fig.update_layout(
                height=450,
                showlegend=False,
                margin=dict(t=65, b=55, l=25, r=25),
                title=dict(
                    font=dict(size=19),
                    x=0.02,
                    xanchor="left"
                ),
                hoverlabel=dict(font_size=13)
            )
            fig = apply_chart_theme(fig)
            st.plotly_chart(
                fig,
                use_container_width=True
            )


# =========================================================
# QUERY LIBRARY PAGE
# =========================================================

def render_query_library():
    render_section_header(
        "Ready-made SQL Query Library",
        "Explore 49 predefined SQL analyses across eight categories.",
        "📚"
    )
    query_library = get_query_library()

    category = st.selectbox(
        "Select Query Category",
        list(query_library.keys()),
        key="sql_library_category"
    )

    selected_query_name = st.selectbox(
        "Select SQL Analysis",
        list(query_library[category].keys()),
        key="sql_library_query"
    )

    selected_query = query_library[category][selected_query_name]

    st.markdown("#### SQL Query")

    st.code(
        selected_query.strip(),
        language="sql"
    )

    if st.button(
        "▶ Execute Selected Query",
        type="primary",
        key="execute_library_query"
    ):
        try:
            with st.spinner("Executing SQL query..."):
                result_df = run_query(selected_query)
            st.session_state["sql_library_result"] = result_df
            st.session_state["sql_library_result_name"] = (selected_query_name)
            save_query_history(selected_query,f"Query Library-{selected_query_name}",result_df)

        except Exception as error:
            st.error(f"SQL execution failed: {error}")
            st.session_state.pop("sql_library_result", None)

    if "sql_library_result" in st.session_state:
        st.divider()
        st.markdown(
            f"### Results: "
            f"{st.session_state.get('sql_library_result_name', '')}"
        )
        render_query_result(
            st.session_state["sql_library_result"],
            "library_result"
        )

def load_custom_sql_example():
    examples = {
        "Top 10 Players": """
        SELECT
            c.competitor_name,
            c.country,
            d.rank,
            d.points
        FROM DoublesRankings d
        JOIN Competitors c
            ON d.competitor_id = c.competitor_id
        ORDER BY d.rank
        LIMIT 10;
        """,
                "Country-wise Player Count": """
        SELECT
            country,
            COUNT(*) AS total_players
        FROM Competitors
        GROUP BY country
        ORDER BY total_players DESC;
        """,
                "Average Points by Gender": """
        SELECT
            s.gender,
            ROUND(AVG(d.points), 2) AS average_points
        FROM DoublesRankings d
        JOIN RankingSnapshots s
            ON d.ranking_snapshot_id = s.ranking_snapshot_id
        GROUP BY s.gender;
        """,
                "Player Search": """
        SELECT
            competitor_name,
            country,
            abbreviation
        FROM Competitors
        WHERE competitor_name LIKE '%Smith%';
        """
    }
    selected = st.session_state.get("custom_sql_example")
    if selected in examples:
        st.session_state["custom_sql_editor"] = examples[selected]

def clear_custom_sql_editor():
    st.session_state["custom_sql_editor"] = ""
    st.session_state.pop("custom_sql_result", None)

# =========================================================
# OWN SQL QUERY EDITOR
# =========================================================

def render_custom_sql_editor():
    render_section_header(
        "Write Your Own SQL Query",
        "Create and execute custom read-only queries using the tennis database.",
        "✍️"
    )
    st.caption(
        "Write and execute your own SQL queries. "
        "Only read-only SELECT and WITH queries are allowed."
    )

    with st.expander("🗂️ Database Schema Reference"):

        st.markdown("**Competitors**")
        st.code(
            "competitor_id, competitor_name, abbreviation, "
            "country, country_code",
            language="text"
        )

        st.markdown("**DoublesRankings**")
        st.code(
            "ranking_snapshot_id, competitor_id, rank, "
            "movement, points, competitions_played",
            language="text"
        )

        st.markdown("**RankingSnapshots**")
        st.code(
            "ranking_snapshot_id, ranking_type_id, ranking_name, "
            "year, week, gender, generated_at",
            language="text"
        )

        st.markdown("**Venues**")
        st.code(
            "venue_id, venue_name, city_name, country_name, "
            "country_code, timezone, complex_id",
            language="text"
        )

        st.markdown("**Complexes**")
        st.code(
            "complex_id, complex_name",
            language="text"
        )

        st.markdown("**Venue & Complex Relationship**")
        st.code(
            "Venues.complex_id = Complexes.complex_id",
            language="sql"
        )

        st.markdown("**Table Relationships**")
        st.code(
            "DoublesRankings.competitor_id = Competitors.competitor_id\n"
            "DoublesRankings.ranking_snapshot_id = "
            "RankingSnapshots.ranking_snapshot_id",
            language="sql"
        )

    examples = [
        "Choose an example",
        "Top 10 Players",
        "Country-wise Player Count",
        "Average Points by Gender",
        "Player Search"
    ]

    st.selectbox(
        "Load Example Query",
        examples,
        key="custom_sql_example"
    )

    st.button(
        "Load Example into Editor",
        on_click=load_custom_sql_example,
        key="load_custom_sql_example"
    )

    if "custom_sql_editor" not in st.session_state:
        st.session_state["custom_sql_editor"] = """
                SELECT
                    c.competitor_name,
                    c.country,
                    d.rank,
                    d.points
                FROM DoublesRankings d
                JOIN Competitors c
                    ON d.competitor_id = c.competitor_id
                ORDER BY d.rank
                LIMIT 20;
                """
    custom_query = st.text_area(
        "SQL Query Editor",
        key="custom_sql_editor",
        height=280
    )
    execute_col, clear_col = st.columns(2)
    with execute_col:
        execute_custom = st.button(
            "▶ Execute Custom Query",
            type="primary",
            use_container_width=True,
            key="execute_custom_sql"
        )
    with clear_col:
        st.button(
            "Clear Editor",
            use_container_width=True,
            key="clear_custom_sql",
            on_click=clear_custom_sql_editor
        )
    if execute_custom:
        try:
            with st.spinner("Executing your SQL query..."):
                result_df = run_query(custom_query)

            st.session_state["custom_sql_result"] = result_df
            save_query_history(custom_query,"Own SQL Query",result_df)
            st.success("SQL query executed successfully.")

        except Exception as error:
            st.session_state.pop("custom_sql_result", None)
            st.error(f"Query execution failed: {error}")

    if "custom_sql_result" in st.session_state:

        st.divider()
        render_section_header(
            "Custom Query Results",
            "Output generated by your custom SQL query.",
            "🧾"
        )
        render_query_result(
            st.session_state["custom_sql_result"],
            "custom_sql_result"
        )


# =========================================================
# SQL CONCEPTS
# =========================================================

def render_sql_learning():
    render_section_header(
        "SQL Concepts Reference",
        "Understand SQL commands and concepts used in this analytics workspace.",
        "📖"
    )
    concepts = [
        (
            "SELECT",
            "Retrieve records from database tables."
        ),
        (
            "WHERE",
            "Filter records using specified conditions."
        ),
        (
            "JOIN",
            "Combine related tables using common keys."
        ),
        (
            "GROUP BY",
            "Group records for aggregate calculations."
        ),
        (
            "HAVING",
            "Filter grouped results after aggregation."
        ),
        (
            "ORDER BY",
            "Sort query results in ascending or descending order."
        ),
        (
            "LIMIT",
            "Restrict the number of returned records."
        ),
        (
            "COUNT()",
            "Count records or unique values."
        ),
        (
            "SUM()",
            "Calculate the total of numeric values."
        ),
        (
            "AVG()",
            "Calculate the average of numeric values."
        ),
        (
            "MIN() and MAX()",
            "Find minimum and maximum values."
        ),
        (
            "CASE WHEN",
            "Apply conditional logic inside SQL queries."
        ),
        (
            "NULLIF()",
            "Return NULL when two expressions are equal; useful for avoiding division by zero."
        ),
        (
            "GROUP_CONCAT()",
            "Combine values from multiple rows into a single string in SQLite."
        ),
        (
            "UNION ALL",
            "Combine result sets while retaining duplicate rows."
        ),
        (
            "Subqueries",
            "Use one query result inside another SQL query."
        ),
        (
            "Common Table Expressions (CTE)",
            "Create a temporary named result using WITH."
        ),
    ]

    for concept, description in concepts:

        with st.expander(concept):
            st.write(description)


# =========================================================
# MAIN SQL ANALYTICS PAGE
# =========================================================

def show():
    st.title("🗄️ Advanced SQL Analytics")
    st.caption(
        "Explore tennis ranking data with 49 predefined SQL analyses "
        "or write and execute your own read-only SQL queries."
    )
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📚 Query Library",
            "✍️ Own SQL Query",
            "📖 SQL Learning",
            "🕘 Query History"
        ]
    )

    with tab1:
        render_query_library()
    with tab2:
        render_custom_sql_editor()
    with tab3:
        render_sql_learning()
    with tab4:
        render_query_history()

