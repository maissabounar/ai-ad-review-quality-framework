# Executive Summary

## AI-Assisted Ad Review Quality Framework

This project evaluates how well an AI pre-screening layer and human BPO reviewers handle digital ad policy decisions.

The analysis covers 5000 synthetic ad review cases across 8 markets and 10 policy categories.

---

## Quality Snapshot

| Metric | Value |
|---|---|
| AI accuracy | 71.1% |
| Human accuracy | 83.5% |
| Human-AI agreement | 60.8% |
| Over-rejection rate | 13.2% |
| Risk miss rate | 15.7% |
| High-risk approval misses | 154 |
| Low-confidence AI rate | 20.0% |
| Appeal reversal rate | 15.8% |
| Avg review time | 119s |

---

## What the Data Shows

### 1. The AI is weakest where policy context matters

The model performs well on clear cases:

- Safe Ad: 85%
- Scam: 79%

It struggles in categories that require judgment, disclosure checks, or landing page context:

- Financial Product Claim: 57%
- Landing Page Issue: 59%
- Misleading Claim: 60%

These are not random misses. They point to policy areas where the model needs better examples, clearer rules, or additional context.

---

### 2. The main model risk is under-rejection

The highest-risk pattern is not the AI being too strict.

It is the AI being too lenient in sensitive categories.

This creates policy exposure because ads that should be limited, escalated, or rejected move further into the review flow.

154 high-risk ads were approved when they should not have been.

The largest contributors are:

- Financial Product Claim
- Political or Sensitive Content
- Misleading Claim

---

### 3. Low-confidence decisions are the easiest operational fix

20.0% of AI decisions fall below the 0.60 confidence threshold.

These cases should not follow the same path as high-confidence decisions.

Routing them to mandatory human review would reduce avoidable risk without waiting for a model release.

---

### 4. Reviewer quality varies by experience and team

New reviewers have a 24.1% error rate.

Experienced reviewers are at 10.5%.

That gap is too large to ignore. It points to onboarding, calibration, and category-specific training needs.

There is also a clear BPO team gap:

- BPO_D: 78.4% accuracy
- BPO_B: 87.3% accuracy

The difference is not explained by category mix alone.

---

### 5. Local market context needs more attention

BR, IT, DE, and ES show higher disagreement than US and UK.

This suggests that generic policy guidance is not enough for non-English markets.

The issue is not only language. It is local policy interpretation.

---

## Priority Actions

| Priority | Action |
|---|---|
| High | Route AI decisions below 0.60 confidence to human review |
| High | Review high-risk approval misses every week |
| High | Calibrate reviewers on Financial Product Claim and Health Claim |
| High | Send high-confidence wrong AI decisions to the model team |
| Medium | Add market-specific policy guidance for BR, IT, DE, and ES |
| Medium | Use reversed appeals to reduce over-rejection |
| Medium | Run one monthly review across Policy, Algorithm, Ad Ops, and BPO Quality |

---

## Bottom Line

The AI is useful, but it should not be trusted equally across all categories.

It works best on clear-cut policy cases. It needs stronger controls for regulated, contextual, and local-market decisions.

The biggest opportunity is not building more dashboards.

It is setting up the right operating model:

- route low-confidence cases
- review high-risk misses fast
- calibrate reviewers by category
- feed the right errors back into the model
- localize policy guidance where disagreement is high

---

## Limitations

This is a synthetic portfolio project.

The data is designed to simulate realistic review patterns, not production benchmarks.

The AI system is statistically simulated, and the golden label is treated as the reference decision.
