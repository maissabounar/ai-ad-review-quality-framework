# Error Taxonomy

This document defines the quality flags used in the analysis.

The goal is simple: separate model risk, reviewer error, advertiser friction, and policy ambiguity so each team knows what to fix.

---

## 1. LLM Incorrect Decision

The AI decision does not match the golden label.

**Field**: `is_llm_correct == False`

This includes over-rejections, risk misses, high-risk approval misses, and low-confidence disagreements.

**Why it matters**: Wrong AI decisions either block good advertisers or let risky ads move forward.

---

## 2. Human Reviewer Error

The human reviewer decision does not match the golden label.

**Field**: `is_human_correct == False`

Typical drivers include unclear policy guidance, weak category knowledge, local market nuance, or inconsistent escalation standards.

**Why it matters**: High error rates show where reviewers need calibration, training, or clearer policy examples.

---

## 3. Advertiser Over-Rejection

The AI applies a stricter decision than needed.

**Field**: `is_advertiser_over_rejection == True`

**Logic**: `llm_severity_score > golden_severity_score`

Examples:

```text
golden = approved
AI = approved_limited

golden = approved_limited
AI = rejected
```

**Why it matters**: Over-rejection creates advertiser friction, delays campaigns, and drives avoidable appeals.

---

## 4. Policy Risk Miss

The AI applies a more lenient decision than needed.

**Field**: `is_policy_risk_miss == True`

**Logic**: `llm_severity_score < golden_severity_score`

Examples:

```text
golden = rejected
AI = approved_limited

golden = approved_limited
AI = approved
```

**Why it matters**: Risk misses are the main policy exposure. They allow non-compliant ads to move further into the review flow.


---

## 5. High-Risk Approval Miss

A high-risk ad is approved by the AI when it should have been limited, rejected, or escalated.

**Field**: `is_high_risk_approval_miss == True`

**Logic**:

```text
risk_level == high
AND golden_label IN [approved_limited, rejected, escalated]
AND llm_label == approved
```

**Why it matters**: This is the highest-priority error. These cases should feed model retraining, quality monitoring, and weekly risk review.

---

## 6. Policy Ambiguity

Both the AI and the human reviewer miss the golden label, but in different ways.

**Field**: `is_policy_ambiguous == True`

**Logic**:

```text
is_llm_correct == False
AND is_human_correct == False
AND llm_label != human_label
```

**Why it matters**: These cases often point to unclear policy wording, not only model or reviewer failure. They should be reviewed by the policy team.

---

## 7. Landing Page Mismatch

The AI misses a policy issue linked to the landing page.

**Error type**: `landing_page_mismatch`

**Why it matters**: Some ad claims only become risky once the landing page is checked. A model that cannot evaluate landing page context will underperform in Landing Page Issue and Misleading Claim cases.

---

## 8. Claim Substantiation Issue

The AI fails to catch an unsupported claim in a regulated category.

**Error type**: `claim_substantiation_issue`

**Why it matters**: Unsupported claims in finance or health create legal, policy, and brand safety risk.


---

## 9. Market Nuance Error

The AI decision diverges from the golden label in a non-English or local-market context.

**Error type**: `market_nuance_error`

**Why it matters**: Local policy interpretation matters. These errors suggest that training examples or reviewer guidance do not cover regional nuance well enough.

---

## 10. Low-Confidence Escalation Needed

The AI is wrong and its confidence score is below 0.60.

**Fields**:

```text
is_low_confidence_case == True
AND is_llm_correct == False
```

**Error type**: `low_confidence_disagree`

**Why it matters**: These cases are easy to route. A mandatory human review rule for low-confidence decisions would reduce avoidable errors without changing the model.

---

## 11. Appeal Reversal

An advertiser appeal is accepted and the original decision is overturned.

**Field**: `is_appeal_reversed == True`

**Why it matters**: Reversals show where the system was too strict or poorly calibrated. They are useful for policy clarification, reviewer coaching, and model feedback.

---

## How to Use This Taxonomy

| Signal | Main owner | Action |
|---|---|---|
| Policy risk miss | Algorithm + Policy | Improve model examples and policy rules |
| High-risk approval miss | Ad Ops + Quality | Review weekly and remediate fast |
| Over-rejection | Policy + Ad Ops | Reduce unnecessary advertiser friction |
| Human reviewer error | BPO Quality | Calibrate reviewers and improve training |
| Policy ambiguity | Policy | Clarify rules and examples |
| Appeal reversal | Policy + Quality | Use reversals as feedback cases |
| Low-confidence disagreement | Algorithm + Ad Ops | Route to mandatory human review |
