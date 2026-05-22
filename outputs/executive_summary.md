# Executive Summary

## AI-Assisted Ad Review Quality Framework

**Analysis period**: January 2024 – December 2024  
**Total cases reviewed**: 5000  
**Markets**: FR, UK, US, DE, ES, IT, BR, MX  
**Policy categories**: 10

---

## Overall Quality Metrics

| Metric | Value |
|---|---|
| LLM accuracy | 71.1% |
| Human accuracy | 83.5% |
| Agreement rate | 60.8% |
| Over-rejection rate | 13.2% |
| Risk miss rate | 15.7% |
| High-risk approval misses | 154 |
| Low-confidence LLM rate | 20.0% |
| Appeal reversal rate | 15.8% |
| Avg review time | 119s |

---

## Key Findings

### LLM Performance

1. **Best categories**: Safe Ad (85%) and Scam (79%). The model is well-calibrated on clear-cut cases where violations are unambiguous.

2. **Weakest categories**: Financial Product Claim (57%), Landing Page Issue (59%), and Misleading Claim (60%). These require contextual reasoning or landing page access that exceeds current LLM capabilities.

3. **Directional bias**: The LLM under-rejects on Financial Product Claim, Health Claim, and Political Content — approving or limiting ads that should be escalated or rejected. Over-rejection is concentrated in Safe Ad and Adult Content.

4. **Confidence calibration**: 20% of LLM decisions fall below the 0.60 confidence threshold and have materially higher error rates. Routing this group to human review is the fastest available fix without a model change.

### Human Reviewer Performance

5. **Tenure gap**: New reviewers have a 24.1% error rate vs. 10.5% for experienced reviewers — a 13.6 pp gap concentrated in Financial Product Claim, Health Claim, and Misleading Claim.

6. **BPO team variation**: Accuracy ranges from 78.4% (BPO_D) to 87.3% (BPO_B) — an 8.9 pp spread that is not explained by category mix alone, pointing to calibration differences between teams.

### Market and Language Patterns

7. **Non-English markets**: BR, IT, DE, and ES show higher disagreement rates than US/UK, consistent with local regulatory context not being reflected in current model training or reviewer guidelines.

8. **Review time**: Cases from non-English markets take longer on average, suggesting reviewers spend more time resolving policy uncertainty.

### Appeal Analysis

9. **Over-rejection drives appeals**: Submission rates concentrate in rejected and approved_limited decisions. Reversal rates are highest where the original decision was stricter than the golden label — 15.8% of submitted appeals were reversed.

10. **Enterprise and strategic accounts appeal most**: Higher-tier advertisers are more likely to appeal and more likely to succeed, suggesting they are better at identifying legitimate over-rejections.

---

## Priority Recommendations

1. **Low-confidence routing** — Route all LLM decisions below 0.60 confidence to mandatory human review. 20% of decisions qualify; this group drives a disproportionate share of risk misses.

2. **Weekly high-risk approval miss review** — 154 high-risk ads were approved when they should not have been. A weekly automated alert and 3-day remediation SLA should be standard.

3. **BPO calibration for regulated categories** — Monthly sessions for Financial Product Claim and Health Claim, using reversed appeals and golden label disagreements as training material.

4. **Model feedback extraction** — Export high-confidence wrong LLM decisions monthly. These are the highest-value examples for model retraining with the least annotation cost.

5. **Market-specific policy supplements** — BR, IT, and DE need locally adapted guidelines. Generic policy does not provide sufficient context for local regulatory nuance.

---

## Limitations

- All data is synthetic. Real platform metrics will differ.
- The golden label is treated as ground truth. Expert annotators also disagree on borderline cases.
- The LLM pre-screening system is simulated statistically, not via real API calls.
- Landing page content is a single text field. Real evaluation requires URL-level access.
