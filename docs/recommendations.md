# Recommendations

These recommendations turn the quality analysis into actions for model teams, policy teams, Ad Ops, and BPO quality.

They focus on three priorities:

- reduce policy risk misses
- improve reviewer calibration
- create a usable feedback loop for model improvement

---

## 1. Route Low-Confidence AI Decisions to Human Review

**Issue**

AI decisions below 0.60 confidence have higher error rates, but they are currently treated like any other decision.

**Action**

Route every case below the confidence threshold to mandatory human review before final decisioning.

```python
llm_confidence_score < 0.60
```

**Why it matters**

This is the fastest operational fix. It reduces avoidable errors without waiting for a model update.

**Owner**

Algorithm Team + Ad Operations

**Success metric**

Low-confidence error rate down by 20% within 60 days.

---

## 2. Calibrate Reviewers on High-Disagreement Categories

**Issue**

Reviewer errors are concentrated in Health Claim, Financial Product Claim, Political Content, and Misleading Claim. New reviewers are the most exposed.

**Action**

Run monthly calibration sessions using:

- reversed appeals
- golden label disagreements
- high-risk approval misses
- ambiguous policy cases

Track error rates before and after by reviewer tenure and BPO team.

**Why it matters**

Reviewer quality is trainable. The gap between new and experienced reviewers points to onboarding and calibration, not only individual performance.

**Owner**

BPO Quality Lead

**Success metric**

New reviewer error rate in target categories down by 15% within 90 days.

---

## 3. Use High-Confidence Wrong AI Decisions for Model Feedback

**Issue**

The most useful model feedback cases are not all errors. They are the cases where the AI was wrong and confident.

**Action**

Export a monthly feedback set:

```python
llm_confidence_score > 0.75
and is_llm_correct == False
and risk_level in ["medium", "high"]
```

Include:

- golden label
- AI label
- policy category
- error type
- market
- appeal result when available

**Why it matters**

These cases show where the model is confidently wrong. They are more valuable for retraining than random error samples.

**Owner**

Algorithm Team + Quality Analyst

**Success metric**

High-confidence error rate down by 10% over two model releases.

---

## 4. Add Local Policy Calibration for Non-English Markets

**Issue**

BR, IT, DE, ES, and MX show higher disagreement than US and UK markets.

**Action**

Create market-specific policy supplements with:

- local examples
- translated policy guidance
- market-specific escalation rules
- market-tagged model feedback examples

Run calibration workshops with the BPO teams reviewing these markets.

**Why it matters**

Generic policy guidance misses local nuance. This creates both over-rejection and risk misses.

**Owner**

Regional Policy + BPO Quality

**Success metric**

BR and IT disagreement rates within 5 pp of the US/UK baseline within 6 months.

---

## 5. Monitor High-Risk Approval Misses Weekly

**Issue**

High-risk approval misses are the most severe failure mode: risky ads approved by the AI when they should have been limited, rejected, or escalated.

**Action**

Create a weekly report of all new high-risk approval misses.

Each case should be reviewed within 3 business days by a senior policy or quality analyst.

Severe cases should be escalated to legal or compliance.

**Why it matters**

These are the cases with the highest policy exposure. They need fast review, not monthly reporting.

**Owner**

Ad Operations + Quality Lead

**Success metric**

Time to detection below 3 business days.

---

## 6. Reduce Over-Rejection and Avoidable Appeals

**Issue**

Some ads are rejected or limited more strictly than the golden label supports. Many of these cases generate appeals, and some are reversed.

**Action**

Review over-rejection patterns by:

- policy category
- market
- advertiser tier
- appeal outcome

Use reversed appeals to recalibrate decision thresholds.

**Why it matters**

Over-rejection does not create policy exposure, but it damages advertiser trust and slows campaigns.

**Owner**

Policy Team + Ad Operations

**Success metric**

Over-rejection rate down by 10% within 90 days.

---

## 7. Create a Monthly Quality Feedback Loop

**Issue**

Quality signals are scattered across teams. Model errors, policy ambiguity, BPO calibration gaps, and appeal reversals need one shared review process.

**Action**

Run a monthly quality review with:

- BPO Quality
- Policy
- Algorithm
- Ad Operations

Review the top disagreement categories, assign owners, and track follow-up actions.

**Why it matters**

The same issues often appear across model, reviewer, and policy signals. Reviewing them together prevents isolated fixes.

**Owner**

Quality Lead

**Success metric**

Top 5 disagreement categories have assigned actions within 2 weeks.

---

## Summary

| Priority | Recommendation | Owner |
|---|---|---|
| High | Route low-confidence AI decisions to human review | Algorithm + Ad Ops |
| High | Calibrate reviewers on high-disagreement categories | BPO Quality |
| High | Use high-confidence wrong AI decisions for model feedback | Algorithm + Quality |
| High | Monitor high-risk approval misses weekly | Ad Ops + Quality |
| Medium | Add local policy calibration for non-English markets | Regional Policy + BPO Quality |
| Medium | Reduce over-rejection and avoidable appeals | Policy + Ad Ops |
| Medium | Create a monthly quality feedback loop | Quality Lead |
