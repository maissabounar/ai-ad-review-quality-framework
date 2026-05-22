-- ============================================================
-- 05_bpo_calibration_analysis.sql
-- Identify BPO teams and reviewer tenure groups that need
-- calibration based on human accuracy, error patterns,
-- and appeal reversal rates.
-- ============================================================

-- 1. Human accuracy by BPO team
SELECT
    bpo_team,
    COUNT(*)                              AS total_cases,
    ROUND(AVG(is_human_correct::INT), 4) AS human_accuracy,
    ROUND(1 - AVG(is_human_correct::INT), 4) AS error_rate,
    ROUND(AVG(is_human_ai_agreement::INT), 4) AS human_ai_agreement,
    ROUND(AVG(review_time_seconds), 1)   AS avg_review_time_sec
FROM ad_reviews
GROUP BY bpo_team
ORDER BY human_accuracy ASC;

-- 2. Error rate by reviewer tenure
SELECT
    reviewer_tenure,
    COUNT(*)                                    AS total_cases,
    ROUND(AVG(is_human_correct::INT), 4)        AS human_accuracy,
    ROUND(1 - AVG(is_human_correct::INT), 4)   AS error_rate,
    ROUND(AVG(is_human_ai_agreement::INT), 4)  AS human_ai_agreement,
    ROUND(AVG(review_time_seconds), 1)          AS avg_review_time_sec
FROM ad_reviews
GROUP BY reviewer_tenure
ORDER BY error_rate DESC;

-- 3. Appeal reversal rate by BPO team
SELECT
    bpo_team,
    SUM(appeal_submitted::INT)   AS total_appeals,
    SUM(is_appeal_reversed::INT) AS reversals,
    ROUND(
        SUM(is_appeal_reversed::INT) * 1.0
        / NULLIF(SUM(appeal_submitted::INT), 0),
        4
    )                            AS reversal_rate
FROM ad_reviews
GROUP BY bpo_team
ORDER BY reversal_rate DESC;

-- 4. Policy categories where new reviewers struggle most
SELECT
    policy_category,
    COUNT(*)                                    AS total_new_reviewer_cases,
    ROUND(AVG(is_human_correct::INT), 4)        AS accuracy,
    ROUND(1 - AVG(is_human_correct::INT), 4)   AS error_rate
FROM ad_reviews
WHERE reviewer_tenure = 'new'
GROUP BY policy_category
ORDER BY error_rate DESC;

-- 5. Teams with highest human-golden disagreement
-- (i.e., teams most divergent from the expert reference label)
SELECT
    bpo_team,
    reviewer_tenure,
    COUNT(*)                                    AS total_cases,
    ROUND(AVG(is_human_correct::INT), 4)        AS human_accuracy,
    ROUND(1 - AVG(is_human_correct::INT), 4)   AS error_rate,
    SUM(is_high_risk_approval_miss::INT)        AS high_risk_misses_in_team
FROM ad_reviews
GROUP BY bpo_team, reviewer_tenure
ORDER BY error_rate DESC;

-- 6. BPO team performance split by risk level
SELECT
    bpo_team,
    risk_level,
    COUNT(*)                             AS total_cases,
    ROUND(AVG(is_human_correct::INT), 4) AS human_accuracy
FROM ad_reviews
GROUP BY bpo_team, risk_level
ORDER BY bpo_team, risk_level;

-- 7. Worst-performing reviewer cohort: new reviewers on high-risk cases
SELECT
    bpo_team,
    policy_category,
    COUNT(*)                             AS high_risk_new_cases,
    ROUND(AVG(is_human_correct::INT), 4) AS accuracy,
    SUM(is_appeal_reversed::INT)         AS appeal_reversals
FROM ad_reviews
WHERE reviewer_tenure = 'new'
  AND risk_level = 'high'
GROUP BY bpo_team, policy_category
HAVING COUNT(*) >= 5
ORDER BY accuracy ASC;
