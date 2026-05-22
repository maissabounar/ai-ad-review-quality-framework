-- ============================================================
-- 06_model_feedback_examples.sql
-- Identify high-value examples for algorithm and policy teams.
-- Priority: high-confidence wrong LLM decisions,
-- high-risk approval misses, and reversed appeals.
-- ============================================================

-- 1. High-confidence LLM errors (most valuable for retraining)
SELECT
    ad_id,
    ad_text,
    landing_page_claim,
    market,
    language,
    policy_category,
    risk_level,
    golden_label,
    llm_label,
    llm_confidence_score,
    error_type,
    'High-confidence wrong LLM decision — priority retraining candidate' AS why_it_matters
FROM ad_reviews
WHERE NOT is_llm_correct
  AND llm_confidence_score > 0.75
  AND risk_level IN ('medium', 'high')
ORDER BY llm_confidence_score DESC
LIMIT 30;

-- 2. High-risk approval misses
SELECT
    ad_id,
    ad_text,
    landing_page_claim,
    market,
    language,
    policy_category,
    risk_level,
    golden_label,
    llm_label,
    llm_confidence_score,
    error_type,
    'High-risk ad approved by LLM — potential live inventory risk' AS why_it_matters
FROM ad_reviews
WHERE is_high_risk_approval_miss
ORDER BY llm_confidence_score DESC;

-- 3. Reversed appeals (evidence that the original decision was wrong)
SELECT
    ad_id,
    ad_text,
    landing_page_claim,
    market,
    language,
    policy_category,
    risk_level,
    golden_label,
    human_label,
    llm_label,
    llm_confidence_score,
    appeal_result,
    error_type,
    'Appeal reversed — original decision was incorrect' AS why_it_matters
FROM ad_reviews
WHERE is_appeal_reversed
ORDER BY policy_category, risk_level DESC;

-- 4. Policy ambiguity examples: both LLM and human diverge from golden
SELECT
    ad_id,
    ad_text,
    landing_page_claim,
    policy_category,
    risk_level,
    golden_label,
    human_label,
    llm_label,
    llm_confidence_score,
    'Both LLM and human reviewer diverged from golden — possible policy ambiguity' AS why_it_matters
FROM ad_reviews
WHERE is_policy_ambiguous
  AND risk_level IN ('medium', 'high')
ORDER BY policy_category
LIMIT 20;

-- 5. Combined high-priority model feedback shortlist
SELECT
    ad_id,
    policy_category,
    market,
    risk_level,
    golden_label,
    llm_label,
    llm_confidence_score,
    error_type,
    CASE
        WHEN is_high_risk_approval_miss THEN 'high_risk_approval_miss'
        WHEN llm_confidence_score > 0.75 AND NOT is_llm_correct THEN 'high_conf_wrong'
        WHEN is_appeal_reversed THEN 'reversed_appeal'
        WHEN is_policy_ambiguous THEN 'policy_ambiguous'
        ELSE 'other'
    END AS feedback_reason,
    CASE
        WHEN is_high_risk_approval_miss THEN 3
        WHEN llm_confidence_score > 0.75 AND NOT is_llm_correct THEN 2
        WHEN is_appeal_reversed THEN 2
        ELSE 1
    END AS priority_tier
FROM ad_reviews
WHERE NOT is_llm_correct
  AND risk_level IN ('medium', 'high')
  AND (
      is_high_risk_approval_miss
      OR llm_confidence_score > 0.72
      OR is_appeal_reversed
      OR is_policy_ambiguous
  )
ORDER BY priority_tier DESC, llm_confidence_score DESC
LIMIT 100;
