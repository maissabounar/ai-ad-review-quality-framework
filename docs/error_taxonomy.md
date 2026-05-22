# Error Taxonomy

Error types and quality flags used in this framework. All teams — algorithm, policy, and BPO quality — use these definitions to interpret findings consistently.

---

## 1. LLM Incorrect Decision

The LLM's decision does not match the golden label.

**Field**: `is_llm_correct == False`

Sub-types: over-rejection, policy risk miss, high-risk approval miss, low-confidence disagree.

**Impact**: Wrong LLM decisions either create advertiser friction or allow non-compliant ads through.

---

## 2. Human Reviewer Error

The human BPO reviewer's decision does not match the golden label.

**Field**: `is_human_correct == False`

Common causes: policy knowledge gaps, local market nuance, policy wording ambiguity, inconsistent escalation thresholds across teams.

**Impact**: High reviewer error rates indicate calibration needs.

---

## 3. Advertiser Over-Rejection

The LLM applied a stricter label than warranted.

**Field**: `is_advertiser_over_rejection == True`

**Condition**: `llm_severity_score > golden_severity_score`

Examples: golden = `approved`, LLM = `approved_limited`. Golden = `approved_limited`, LLM = `rejected`.

**Impact**: Unnecessary advertiser friction, delayed campaigns, avoidable appeals.

---

## 4. Policy Risk Miss

The LLM applied a more lenient label than warranted.

**Field**: `is_policy_risk_miss == True`

**Condition**: `llm_severity_score < golden_severity_score`

Examples: golden = `rejected`, LLM = `approved_limited`. Golden = `approved_limited`, LLM = `approved`.

**Impact**: Non-compliant ads may reach inventory, exposing the platform to policy and regulatory risk.

---

## 5. High-Risk Approval Miss

A high-risk ad that should have been limited, rejected, or escalated was approved by the LLM.

**Field**: `is_high_risk_approval_miss == True`

**Condition**:
```
risk_level == 'high'
AND golden_label IN ['approved_limited', 'rejected', 'escalated']
AND llm_label == 'approved'
```

**Impact**: The most critical error type. These cases should be prioritized in model feedback and quality monitoring.

---

## 6. Policy Ambiguity

Both the LLM and the human reviewer diverged from the golden label in different directions. The policy rule itself may be unclear.

**Field**: `is_policy_ambiguous == True`

**Condition**:
```
is_llm_correct == False
AND is_human_correct == False
AND llm_label != human_label
```

**Impact**: Inconsistent enforcement. Cases flagged here are candidates for policy team review, not just model retraining.

---

## 7. Landing Page Mismatch

The LLM decision did not reflect a policy issue visible on the landing page.

**Error type**: `landing_page_mismatch`

**Impact**: LLMs that cannot evaluate landing page content are structurally limited for Landing Page Issue and Misleading Claim categories.

---

## 8. Claim Substantiation Issue

The LLM failed to identify an unsubstantiated claim in a regulated category.

**Error type**: `claim_substantiation_issue`

**Impact**: Unsubstantiated claims in health and finance carry legal and reputational risk.

---

## 9. Market Nuance Error

The LLM diverged from the golden label in a non-English market, suggesting a failure to apply local regulatory context.

**Error type**: `market_nuance_error`

**Impact**: Indicates training data does not adequately represent non-English markets.

---

## 10. Low-Confidence Escalation Needed

LLM made a wrong decision with confidence below 0.60.

**Fields**: `is_low_confidence_case == True` AND `is_llm_correct == False`

**Error type**: `low_confidence_disagree`

**Impact**: Routing low-confidence decisions to human review would materially reduce errors in this group.

---

## 11. Appeal Reversal

An advertiser appealed and the original decision was overturned.

**Field**: `is_appeal_reversed == True`

**Impact**: High reversal rates by category or team indicate systemic over-rejection or incorrect enforcement.
