-- ============================================================
-- 02_quality_metrics.sql
-- Overall quality metrics: LLM accuracy, human accuracy,
-- agreement rates, over-rejection, risk misses, and appeal KPIs.
-- ============================================================

-- 1. Overall LLM accuracy
SELECT
    COUNT(*)                             AS total_cases,
    ROUND(AVG(is_llm_correct::INT), 4)  AS llm_accuracy,
    ROUND(AVG(CASE WHEN NOT is_llm_correct THEN 1 ELSE 0 END), 4) AS llm_error_rate
FROM ad_reviews;

-- 2. Human reviewer accuracy
SELECT
    ROUND(AVG(is_human_correct::INT), 4)   AS human_accuracy,
    ROUND(AVG(CASE WHEN NOT is_human_correct THEN 1 ELSE 0 END), 4) AS human_error_rate
FROM ad_reviews;

-- 3. Human-AI agreement rate
SELECT
    ROUND(AVG(is_human_ai_agreement::INT), 4) AS human_ai_agreement_rate,
    SUM(CASE WHEN NOT is_human_ai_agreement THEN 1 ELSE 0 END) AS disagreement_cases
FROM ad_reviews;

-- 4. Advertiser over-rejection rate
-- LLM applied a stricter label than the golden label
SELECT
    SUM(is_advertiser_over_rejection::INT)          AS over_rejection_count,
    ROUND(AVG(is_advertiser_over_rejection::INT), 4) AS over_rejection_rate
FROM ad_reviews;

-- 5. Policy risk miss rate
-- LLM applied a more lenient label than the golden label
SELECT
    SUM(is_policy_risk_miss::INT)          AS risk_miss_count,
    ROUND(AVG(is_policy_risk_miss::INT), 4) AS risk_miss_rate
FROM ad_reviews;

-- 6. Low-confidence LLM cases and their disagreement rate
SELECT
    SUM(is_low_confidence_case::INT)                 AS low_confidence_cases,
    ROUND(AVG(is_low_confidence_case::INT), 4)       AS low_confidence_rate,
    ROUND(
        AVG(CASE WHEN is_low_confidence_case AND NOT is_llm_correct THEN 1.0 ELSE 0 END)
        / NULLIF(AVG(is_low_confidence_case::INT), 0),
        4
    )                                                AS low_conf_error_rate
FROM ad_reviews;

-- 7. High-risk approval misses
SELECT
    SUM(is_high_risk_approval_miss::INT)   AS high_risk_approval_miss_count,
    policy_category,
    risk_level
FROM ad_reviews
WHERE is_high_risk_approval_miss
GROUP BY policy_category, risk_level
ORDER BY high_risk_approval_miss_count DESC;

-- 8. LLM confidence distribution summary
SELECT
    ROUND(MIN(llm_confidence_score), 3)    AS min_conf,
    ROUND(AVG(llm_confidence_score), 3)    AS avg_conf,
    ROUND(MEDIAN(llm_confidence_score), 3) AS median_conf,
    ROUND(MAX(llm_confidence_score), 3)    AS max_conf,
    ROUND(STDDEV(llm_confidence_score), 3) AS std_conf
FROM ad_reviews;

-- 9. Appeal submission and reversal rates
SELECT
    SUM(appeal_submitted::INT)                                        AS total_appeals,
    SUM(is_appeal_reversed::INT)                                      AS total_reversals,
    ROUND(AVG(appeal_submitted::INT), 4)                              AS appeal_rate,
    ROUND(
        SUM(is_appeal_reversed::INT)
        / NULLIF(SUM(appeal_submitted::INT), 0)::FLOAT,
        4
    )                                                                  AS reversal_rate
FROM ad_reviews;

-- 10. Average review time by decision complexity
SELECT
    golden_label,
    risk_level,
    ROUND(AVG(review_time_seconds), 1) AS avg_review_time_sec,
    COUNT(*)                           AS cases
FROM ad_reviews
GROUP BY golden_label, risk_level
ORDER BY avg_review_time_sec DESC;
