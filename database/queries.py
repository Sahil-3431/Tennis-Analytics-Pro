# ==========================================
# TENNIS ANALYTICS SQL QUERIES
# ==========================================

TOTAL_COMPETITORS = """
SELECT COUNT(DISTINCT competitor_id)
FROM Competitors;
"""

TOTAL_RANKING_RECORDS = """
SELECT COUNT(*)
FROM DoublesRankings;
"""

TOTAL_COUNTRIES = """
SELECT COUNT(DISTINCT country)
FROM Competitors
WHERE country IS NOT NULL
AND TRIM(country) != '';
"""

ATP_COMPETITORS = """
SELECT COUNT(*)
FROM DoublesRankings d
JOIN RankingSnapshots s
ON d.ranking_snapshot_id = s.ranking_snapshot_id
WHERE s.ranking_name = 'ATP';
"""

WTA_COMPETITORS = """
SELECT COUNT(*)
FROM DoublesRankings d
JOIN RankingSnapshots s
ON d.ranking_snapshot_id = s.ranking_snapshot_id
WHERE s.ranking_name = 'WTA';
"""

TOP_PLAYERS = """
SELECT
    c.competitor_name,
    c.country,
    d.rank,
    d.points,
    d.movement,
    s.ranking_name
FROM DoublesRankings d
JOIN Competitors c
ON d.competitor_id = c.competitor_id
JOIN RankingSnapshots s
ON d.ranking_snapshot_id = s.ranking_snapshot_id
ORDER BY d.points DESC
LIMIT 10;
"""

COUNTRY_DISTRIBUTION = """
SELECT
    country,
    COUNT(*) AS total_players
FROM Competitors
WHERE country IS NOT NULL
GROUP BY country
ORDER BY total_players DESC;
"""

RANKING_COMPARISON = """
SELECT
    s.ranking_name,
    COUNT(*) AS total_players,
    AVG(d.points) AS average_points,
    MAX(d.points) AS highest_points,
    MIN(d.points) AS lowest_points
FROM DoublesRankings d
JOIN RankingSnapshots s
ON d.ranking_snapshot_id = s.ranking_snapshot_id
GROUP BY s.ranking_name;
"""

COUNTRY_AVERAGE_POINTS = """
SELECT
    c.country,
    s.ranking_name,
    COUNT(*) AS total_players,
    ROUND(AVG(d.points), 2) AS average_points
FROM DoublesRankings d
JOIN Competitors c
ON d.competitor_id = c.competitor_id
JOIN RankingSnapshots s
ON d.ranking_snapshot_id = s.ranking_snapshot_id
WHERE c.country IS NOT NULL
GROUP BY
    c.country,
    s.ranking_name
ORDER BY average_points DESC;
"""
