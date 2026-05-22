-- ============================================================
-- 04_market_language_analysis.sql
-- Identify markets and languages with elevated disagreement,
-- higher error rates, or local policy calibration needs.
-- ============================================================

-- 1. LLM and human accuracy by market
SELECT
    market,
    language,
    COUNT(*)                              AS total_cases,
    ROUND(AVG(is_llm_correct::INT), 4)   AS llm_accuracy,
    ROUND(AVG(is_human_correct::INT), 4) AS human_accuracy,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4) AS disagreement_rate,
    ROUND(AVG(review_time_seconds), 1)   AS avg_review_time_sec
FROM ad_reviews
GROUP BY market, language
ORDER BY disagreement_rate DESC;

-- 2. LLM accuracy by language
SELECT
    language,
    COUNT(*)                             AS total_cases,
    ROUND(AVG(is_llm_correct::INT), 4)  AS llm_accuracy,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4) AS disagreement_rate
FROM ad_reviews
GROUP BY language
ORDER BY llm_accuracy ASC;

-- 3. Human-AI disagreement by market and language
SELECT
    market,
    language,
    SUM(CASE WHEN NOT is_human_ai_agreement THEN 1 ELSE 0 END) AS disagreement_count,
    COUNT(*)                                                    AS total_cases,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4)              AS disagreement_rate,
    ROUND(AVG(is_advertiser_over_rejection::INT), 4)           AS over_rejection_rate,
    ROUND(AVG(is_policy_risk_miss::INT), 4)                    AS risk_miss_rate
FROM ad_reviews
GROUP BY market, language
ORDER BY disagreement_rate DESC;

-- 4. Review time by market and language
SELECT
    market,
    language,
    ROUND(AVG(review_time_seconds), 1)   AS avg_review_time_sec,
    ROUND(MEDIAN(review_time_seconds), 1) AS median_review_time_sec,
    MAX(review_time_seconds)             AS max_review_time_sec
FROM ad_reviews
GROUP BY market, language
ORDER BY avg_review_time_sec DESC;

-- 5. Top problematic market x policy category pairs
-- (highest disagreement rate by combination)
SELECT
    market,
    policy_category,
    COUNT(*)                                       AS total_cases,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4) AS disagreement_rate,
    ROUND(AVG(is_llm_correct::INT), 4)            AS llm_accuracy,
    SUM(is_high_risk_approval_miss::INT)          AS high_risk_misses
FROM ad_reviews
GROUP BY market, policy_category
HAVING COUNT(*) >= 10
ORDER BY disagreement_rate DESC
LIMIT 20;

-- 6. Appeal reversal rate by market
SELECT
    market,
    SUM(appeal_submitted::INT)   AS total_appeals,
    SUM(is_appeal_reversed::INT) AS reversals,
    ROUND(
        SUM(is_appeal_reversed::INT) * 1.0
        / NULLIF(SUM(appeal_submitted::INT), 0),
        4
    )                            AS reversal_rate
FROM ad_reviews
GROUP BY market
ORDER BY reversal_rate DESC;

-- 7. Markets with highest policy risk miss rate
SELECT
    market,
    language,
    ROUND(AVG(is_policy_risk_miss::INT), 4)          AS risk_miss_rate,
    ROUND(AVG(is_advertiser_over_rejection::INT), 4) AS over_rejection_rate,
    COUNT(*)                                         AS total_cases
FROM ad_reviews
GROUP BY market, language
ORDER BY risk_miss_rate DESC;
