# Recommendations

Based on analysis of 5000 ad review cases across 10 policy categories, 8 markets, and 5 BPO teams. Each recommendation targets a specific failure mode with a concrete action, owner, and success metric.

---

## 1. Route Low-Confidence LLM Decisions to Human Review

**Problem**: LLM decisions with confidence below 0.60 have significantly higher error rates than high-confidence decisions. They are currently treated identically.

**Action**: Implement an automatic routing rule: any LLM decision with `llm_confidence_score < 0.60` must be queued for human review before the decision is finalized.

**Expected impact**: Reduced policy risk misses and over-rejections on uncertain cases. Most benefit in Health Claim, Financial Product Claim, and Landing Page Issue.

**Owner**: Algorithm Team + Ad Operations

**Success metric**: Error rate for low-confidence cases decreases by ≥20% within 60 days.

---

## 2. BPO Calibration for High-Disagreement Categories

**Problem**: Human reviewers show elevated error rates in Health Claim, Financial Product Claim, Political Content, and Misleading Claim. New reviewers are worst affected in all four.

**Action**: Monthly calibration sessions on these four categories. Use reversed appeal cases and golden label disagreements as training material. Track error rates by reviewer cohort before and after.

**Expected impact**: Lower human reviewer error rate, especially for new and intermediate reviewers. More consistent scores across BPO teams.

**Owner**: BPO Quality Lead

**Success metric**: New reviewer error rate in target categories decreases by ≥15% within 90 days.

---

## 3. Extract High-Confidence Wrong LLM Decisions as Model Feedback

**Problem**: High-confidence wrong decisions are the most damaging LLM errors. They are not currently extracted for model improvement.

**Action**: Export monthly: cases where `llm_confidence_score > 0.75` AND `is_llm_correct == False` AND `risk_level in ['medium', 'high']`. Share with the algorithm team as a labelled feedback set with golden labels and error type annotations.

**Expected impact**: Model retraining on these cases reduces high-confidence errors in Health Claim, Financial Product Claim, and Landing Page Issue.

**Owner**: Algorithm Team + Quality Analyst

**Success metric**: High-confidence error rate decreases by ≥10% over two model release cycles.

---

## 4. Market-Specific Policy Calibration for Non-English Markets

**Problem**: BR, IT, DE, ES, and MX consistently show higher disagreement rates than US/UK. Local policy nuance is not reflected in current model training or reviewer guidelines.

**Action**:
- Develop market-specific policy supplements for each non-English market
- Translate key policy examples into local languages
- Add market-tagged training examples to the LLM feedback set
- Run calibration workshops with BPO teams assigned to these markets

**Expected impact**: Reduced market nuance errors and lower disagreement rates in non-English markets.

**Owner**: Regional Policy Team + BPO Quality

**Success metric**: Disagreement rate in BR and IT within 5 pp of the US/UK baseline within 6 months.

---

## 5. Weekly Monitoring of High-Risk Approval Misses

**Problem**: High-risk approval misses — high-risk ads approved by the LLM when they should have been limited, rejected, or escalated — are not systematically tracked.

**Action**: Weekly automated report surfacing all new high-risk approval misses. Senior policy or quality analyst review within 3 business days. Escalation threshold to legal or compliance for severe cases.

**Expected impact**: Faster detection and remediation. Reduced risk of non-compliant content reaching live inventory.

**Owner**: Ad Operations + Quality Lead

**Success metric**: Time-to-detection for high-risk approval misses ≤3 business days.

---

## 6. Review Over-Rejection Patterns to Reduce Advertiser Friction

**Problem**: A meaningful share of rejected or limited ads were classified more strictly than the golden label warrants. Many generate appeals, and a significant proportion of those are reversed.

**Action**:
- Review policy thresholds for the Safe Ad category (most affected by over-rejection)
- Audit over-rejection patterns by market and advertiser tier
- Use reversed appeals to recalibrate decision thresholds
- Quarterly review where policy and operations teams review the over-rejection rate together

**Expected impact**: Lower appeal submission rate from legitimate advertisers. Improved advertiser trust.

**Owner**: Policy Team + Ad Operations

**Success metric**: Over-rejection rate decreases by ≥10% within 90 days.

---

## 7. Cross-Functional Quality Feedback Loop

**Problem**: Quality insights stay within each team. BPO quality observations do not systematically reach the policy team, and policy ambiguity cases are not fed back to the algorithm team.

**Action**: Monthly cross-functional quality review with representatives from:
- BPO Quality (calibration data)
- Policy Team (guideline updates)
- Algorithm Team (model feedback examples)
- Ad Operations (appeal reversal data)

Review the top 5 disagreement categories each session and assign follow-up actions. Track resolution.

**Owner**: Quality Lead (coordinator)

**Success metric**: All top-5 disagreement categories have an assigned action within 2 weeks of each monthly review.

---

## Summary

| # | Action | Owner | Priority |
|---|---|---|---|
| 1 | Route low-confidence LLM decisions to human review | Algorithm + Ad Ops | High |
| 2 | BPO calibration for high-disagreement categories | BPO Quality | High |
| 3 | Extract high-confidence wrong LLM decisions for model feedback | Algorithm | High |
| 4 | Market-specific policy calibration for non-English markets | Policy + BPO | Medium |
| 5 | Weekly monitoring of high-risk approval misses | Ad Ops + Quality | High |
| 6 | Review over-rejection patterns | Policy + Ad Ops | Medium |
| 7 | Cross-functional quality feedback loop | Quality Lead | Medium |
