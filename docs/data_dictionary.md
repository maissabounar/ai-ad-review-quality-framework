# Data Dictionary

**Primary dataset**: `data/processed/ad_reviews_enriched.csv`  
**Source**: `data/raw/synthetic_ad_reviews.csv` enriched by `prepare_data.py`

---

## Identifier and Date Fields

| Column | Type | Description |
|---|---|---|
| `ad_id` | string | Unique case identifier. Format: `AD00001` to `AD05000` |
| `created_date` | date | Date the ad was submitted for review. Format: YYYY-MM-DD |

---

## Ad and Campaign Attributes

| Column | Type | Values | Description |
|---|---|---|---|
| `market` | string | FR, UK, US, DE, ES, IT, BR, MX | Country where the ad was reviewed |
| `language` | string | French, English, German, Spanish, Italian, Portuguese | Language of the ad content |
| `ad_format` | string | Search Ad, Display Ad, Video Ad, Social Feed Ad, Shopping Ad, App Install Ad | Ad unit format |
| `industry_vertical` | string | Beauty, Health and Wellness, Finance, E-commerce, Gaming, Travel, Education, Food and Beverage, Mobile Apps, Retail | Advertiser industry |
| `advertiser_tier` | string | small_business, mid_market, enterprise, strategic_account | Account size classification |
| `campaign_objective` | string | Traffic, Conversions, Lead Generation, App Installs, Brand Awareness, Sales, Retargeting | Campaign goal |
| `ad_text` | string | — | Synthetic ad copy |
| `landing_page_claim` | string | — | Key claim or disclaimer on the landing page |

---

## Policy Classification Fields

| Column | Type | Values | Description |
|---|---|---|---|
| `policy_category` | string | See below | Primary policy category assigned to the ad |
| `risk_level` | string | low, medium, high | Risk level based on policy category and content |

**Policy category values**:
- `Safe Ad` — No policy concern
- `Misleading Claim` — Claims that may be false or unverifiable
- `Financial Product Claim` — Regulated financial product claims
- `Health Claim` — Health-related claims requiring substantiation
- `Restricted Product` — Product category with platform restrictions
- `Political or Sensitive Content` — Civic, political, or sensitive social content
- `Adult or Suggestive Content` — Mature or suggestive content
- `Scam or Suspicious Offer` — Patterns associated with fraudulent offers
- `Brand Safety Risk` — Risk to brand safety or third-party reputation
- `Landing Page Issue` — Compliant ad copy, non-compliant landing page

---

## Review Decision Fields

| Column | Type | Values | Description |
|---|---|---|---|
| `golden_label` | string | approved, approved_limited, escalated, rejected | Expert reference decision — ground truth |
| `human_label` | string | approved, approved_limited, escalated, rejected | Human BPO reviewer decision |
| `llm_label` | string | approved, approved_limited, escalated, rejected | LLM pre-screening decision |
| `llm_confidence_score` | float | 0.10–0.99 | LLM confidence in its decision. Below 0.60 is flagged as low-confidence |
| `human_confidence_score` | float | 0.20–0.99 | Human reviewer confidence |
| `review_time_seconds` | integer | ≥20 | Time spent by the human reviewer in seconds |

---

## Appeal Fields

| Column | Type | Values | Description |
|---|---|---|---|
| `appeal_submitted` | boolean | True / False | Whether the advertiser submitted an appeal |
| `appeal_result` | string | not_submitted, upheld, reversed | Appeal outcome. `reversed` = original decision overturned |

---

## Reviewer and Team Fields

| Column | Type | Values | Description |
|---|---|---|---|
| `bpo_team` | string | BPO_A, BPO_B, BPO_C, BPO_D, BPO_E | BPO team responsible for the review |
| `reviewer_tenure` | string | new, intermediate, experienced | Experience level of the reviewer |

---

## Error Classification Field

| Column | Type | Values | Description |
|---|---|---|---|
| `error_type` | string | See below | Primary LLM error type. `none` when LLM is correct |

**Error type values**:
- `none` — LLM matches golden label
- `over_rejection` — LLM applied a stricter label than warranted
- `policy_risk_miss` — LLM applied a more lenient label than warranted
- `high_risk_approval_miss` — High-risk ad approved when it should have been limited or rejected
- `landing_page_mismatch` — LLM missed an issue visible only on the landing page
- `claim_substantiation_issue` — LLM failed to flag an unsubstantiated claim in a regulated category
- `market_nuance_error` — LLM diverged due to local market or language context
- `low_confidence_disagree` — Low-confidence LLM decision that disagreed with the golden label

---

## Derived Boolean Flags (Raw Dataset)

Generated in `generate_dataset.py` and recalculated in `prepare_data.py`.

| Column | Type | Description |
|---|---|---|
| `is_llm_correct` | boolean | True when LLM label matches golden label |
| `is_human_correct` | boolean | True when human label matches golden label |
| `is_human_ai_agreement` | boolean | True when LLM label matches human label |
| `is_advertiser_over_rejection` | boolean | True when LLM severity > golden severity |
| `is_policy_risk_miss` | boolean | True when LLM severity < golden severity |
| `is_low_confidence_case` | boolean | True when `llm_confidence_score < 0.60` |
| `is_high_risk_approval_miss` | boolean | True when risk = high AND golden label is limited/rejected/escalated AND LLM approved |
| `recommended_action` | string | Recommended handling based on error type and flags |

---

## Enriched Fields (Added by prepare_data.py)

| Column | Type | Description |
|---|---|---|
| `llm_severity_score` | integer | Numeric severity of LLM label: approved=0, approved_limited=1, escalated=2, rejected=3 |
| `golden_severity_score` | integer | Numeric severity of golden label |
| `human_severity_score` | integer | Numeric severity of human label |
| `is_policy_ambiguous` | boolean | True when both LLM and human disagree with golden, in different directions |
| `is_appeal_reversed` | boolean | True when appeal was submitted AND result is `reversed` |

---

## Recommended Action Values

| Value | Meaning |
|---|---|
| `escalate_to_human_review` | High-risk approval miss — requires immediate human review |
| `route_to_human_review` | Low-confidence LLM decision — route to human before finalizing |
| `add_to_model_feedback` | High-confidence wrong LLM decision — valuable retraining example |
| `review_policy_threshold` | Reversed appeal from an over-rejected ad — review decision threshold |
| `flag_for_calibration` | Human reviewer error — candidate for BPO calibration |
| `no_action_required` | Correct decision — no follow-up needed |
