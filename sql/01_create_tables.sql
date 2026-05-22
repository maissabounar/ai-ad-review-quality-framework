-- ============================================================
-- 01_create_tables.sql
-- Load the enriched CSV into a DuckDB in-memory table.
--
-- Usage (from project root):
--   duckdb -c ".read sql/01_create_tables.sql"
--   or run queries interactively via duckdb Python API.
-- ============================================================

-- Drop and recreate the main table from the processed CSV
CREATE OR REPLACE TABLE ad_reviews AS
SELECT *
FROM read_csv_auto(
    'data/processed/ad_reviews_enriched.csv',
    header = true,
    auto_detect = true
);

-- Confirm load
SELECT
    COUNT(*)                          AS total_records,
    COUNT(DISTINCT policy_category)   AS policy_categories,
    COUNT(DISTINCT market)            AS markets,
    COUNT(DISTINCT bpo_team)          AS bpo_teams,
    MIN(created_date)                 AS earliest_date,
    MAX(created_date)                 AS latest_date
FROM ad_reviews;

-- Column summary
DESCRIBE ad_reviews;
