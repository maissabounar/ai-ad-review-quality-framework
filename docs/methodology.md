# Methodology

## Reference Label: The Golden Label

Each ad is assigned a golden label — the correct policy decision from an expert reviewer. All accuracy metrics compare LLM and human decisions against this reference.

| Label | Decision |
|---|---|
| `approved` | Complies with policy — can be served |
| `approved_limited` | Minor concerns — can be served with restrictions |
| `escalated` | Requires senior review before a decision |
| `rejected` | Policy violation — must not be served |

---

## Evaluation Dimensions

**LLM vs golden label** — primary measure of model quality.

```python
is_llm_correct = (llm_label == golden_label)
```

**Human vs golden label** — measures reviewer quality by BPO team, tenure, and category.

```python
is_human_correct = (human_label == golden_label)
```

**LLM vs human agreement** — measures alignment between the two systems, regardless of which is correct. High disagreement in a category indicates either policy ambiguity or a need for model recalibration.

```python
is_human_ai_agreement = (llm_label == human_label)
```

---

## Severity Scale and Directional Errors

Labels are ordered by severity to classify directional errors:

```
approved = 0 | approved_limited = 1 | escalated = 2 | rejected = 3
```

**Over-rejection**: `llm_severity > golden_severity`
The LLM applied a stricter label than warranted. Causes advertiser friction and avoidable appeals.

**Policy risk miss**: `llm_severity < golden_severity`
The LLM applied a more lenient label than warranted. Risky ads may reach live inventory.

**High-risk approval miss**:
```python
risk_level == 'high'
AND golden_label IN ['approved_limited', 'rejected', 'escalated']
AND llm_label == 'approved'
```
A policy risk miss on a high-risk ad — the most consequential error type.

---

## Confidence Threshold

Decisions with `llm_confidence_score < 0.60` are flagged as low-confidence. These cases show materially higher error rates and are candidates for mandatory human review routing.

---

## Appeal Reversal Signal

A reversal occurs when an advertiser appeals and the original decision is overturned. This is a downstream quality signal — reversal rates by category and team identify systematic enforcement errors.

```python
is_appeal_reversed = (appeal_submitted == True) AND (appeal_result == 'reversed')
```

---

## Policy Ambiguity Flag

Flagged when both LLM and human diverge from the golden label in different directions. High ambiguity rates in a category indicate the policy rule itself may need clarification, not just the model or reviewer.

```python
is_policy_ambiguous = (NOT is_llm_correct) AND (NOT is_human_correct) AND (llm_label != human_label)
```

---

## Metrics Reference

| Metric | Formula |
|---|---|
| LLM accuracy | `mean(is_llm_correct)` |
| Human accuracy | `mean(is_human_correct)` |
| Agreement rate | `mean(is_human_ai_agreement)` |
| Over-rejection rate | `mean(llm_severity > golden_severity)` |
| Risk miss rate | `mean(llm_severity < golden_severity)` |
| Appeal reversal rate | `sum(is_appeal_reversed) / sum(appeal_submitted)` |
| Low-confidence rate | `mean(llm_confidence_score < 0.60)` |
