-- ============================================================
-- 03_policy_gap_analysis.sql
-- Identify policy categories with the highest disagreement,
-- over-rejection, risk misses, and appeal reversal rates.
-- These signal where policy clarity or model retraining is needed.
-- ============================================================

-- 1. LLM and human accuracy by policy category
SELECT
    policy_category,
    COUNT(*)                              AS total_cases,
    ROUND(AVG(is_llm_correct::INT), 4)   AS llm_accuracy,
    ROUND(AVG(is_human_correct::INT), 4) AS human_accuracy,
    ROUND(AVG(llm_confidence_score), 3)  AS avg_llm_confidence
FROM ad_reviews
GROUP BY policy_category
ORDER BY llm_accuracy ASC;

-- 2. Human-AI disagreement by policy category
SELECT
    policy_category,
    COUNT(*)                                    AS total_cases,
    SUM(CASE WHEN NOT is_human_ai_agreement THEN 1 ELSE 0 END) AS disagreement_count,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4) AS disagreement_rate
FROM ad_reviews
GROUP BY policy_category
ORDER BY disagreement_rate DESC;

-- 3. Advertiser over-rejection by policy category
SELECT
    policy_category,
    SUM(is_advertiser_over_rejection::INT)          AS over_rejection_count,
    ROUND(AVG(is_advertiser_over_rejection::INT), 4) AS over_rejection_rate,
    COUNT(*)                                         AS total_cases
FROM ad_reviews
GROUP BY policy_category
ORDER BY over_rejection_rate DESC;

-- 4. Policy risk misses by category
SELECT
    policy_category,
    SUM(is_policy_risk_miss::INT)          AS risk_miss_count,
    ROUND(AVG(is_policy_risk_miss::INT), 4) AS risk_miss_rate,
    COUNT(*)                                AS total_cases
FROM ad_reviews
GROUP BY policy_category
ORDER BY risk_miss_rate DESC;

-- 5. High-risk approval misses by category
SELECT
    policy_category,
    SUM(is_high_risk_approval_miss::INT) AS high_risk_misses,
    COUNT(*)                             AS total_cases,
    ROUND(
        SUM(is_high_risk_approval_miss::INT) * 1.0 / COUNT(*),
        4
    )                                    AS high_risk_miss_rate
FROM ad_reviews
GROUP BY policy_category
ORDER BY high_risk_misses DESC;

-- 6. Appeal reversal rate by policy category
SELECT
    policy_category,
    SUM(appeal_submitted::INT)             AS total_appeals,
    SUM(is_appeal_reversed::INT)           AS reversals,
    ROUND(
        SUM(is_appeal_reversed::INT) * 1.0
        / NULLIF(SUM(appeal_submitted::INT), 0),
        4
    )                                      AS reversal_rate
FROM ad_reviews
GROUP BY policy_category
ORDER BY reversal_rate DESC;

-- 7. Policy ambiguity: categories where both LLM and human diverge from golden
SELECT
    policy_category,
    SUM(is_policy_ambiguous::INT)          AS ambiguous_cases,
    ROUND(AVG(is_policy_ambiguous::INT), 4) AS ambiguity_rate,
    COUNT(*)                               AS total_cases
FROM ad_reviews
GROUP BY policy_category
ORDER BY ambiguity_rate DESC;

-- 8. Combined risk signal: categories needing immediate attention
-- (high disagreement AND high risk miss AND low LLM accuracy)
SELECT
    policy_category,
    ROUND(AVG(is_llm_correct::INT), 4)               AS llm_accuracy,
    ROUND(1 - AVG(is_human_ai_agreement::INT), 4)    AS disagreement_rate,
    ROUND(AVG(is_policy_risk_miss::INT), 4)          AS risk_miss_rate,
    ROUND(AVG(is_advertiser_over_rejection::INT), 4) AS over_rejection_rate,
    SUM(is_high_risk_approval_miss::INT)             AS high_risk_misses,
    COUNT(*)                                         AS total_cases
FROM ad_reviews
GROUP BY policy_category
ORDER BY disagreement_rate DESC, risk_miss_rate DESC;
