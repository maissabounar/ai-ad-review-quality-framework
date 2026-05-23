# Methodology

This project evaluates two decisions for each ad:

- the AI pre-screening decision
- the human reviewer decision

Both are compared against a reference decision called the golden label.

---

## Golden Label

The golden label is the expected policy decision.

| Label | Meaning |
|---|---|
| `approved` | The ad complies with policy |
| `approved_limited` | The ad can run with restrictions |
| `escalated` | The ad needs senior review |
| `rejected` | The ad violates policy |

This label is used as the reference point for all accuracy metrics.

---

## Core Quality Checks

### AI accuracy

Measures whether the AI matched the golden label.

```python
is_llm_correct = llm_label == golden_label
```

### Human accuracy

Measures whether the human reviewer matched the golden label.

```python
is_human_correct = human_label == golden_label
```

### Human-AI agreement

Measures whether the AI and the human reviewer made the same decision.

```python
is_human_ai_agreement = llm_label == human_label
```

Agreement does not mean both were correct. It only shows alignment between the two review layers.

---

## Directional Errors

Policy decisions are ordered by severity.

```text
approved = 0
approved_limited = 1
escalated = 2
rejected = 3
```

This makes it possible to separate two very different problems.

### Over-rejection

The AI is stricter than the golden label.

```python
llm_severity_score > golden_severity_score
```

This creates advertiser friction, delays campaigns, and increases appeals.

### Risk miss

The AI is more lenient than the golden label.

```python
llm_severity_score < golden_severity_score
```

This is the main policy risk, because non-compliant ads move further into the review flow.

### High-risk approval miss

A high-risk ad is approved by the AI when it should have been limited, rejected, or escalated.

```python
risk_level == "high"
and golden_label in ["approved_limited", "rejected", "escalated"]
and llm_label == "approved"
```

This is the highest-priority error in the framework.

---

## Confidence Routing

AI decisions below 0.60 confidence are flagged as low-confidence.

```python
llm_confidence_score < 0.60
```

These cases are strong candidates for mandatory human review.

The logic is practical: low-confidence decisions are easier to route than to fix through model changes.

---

## Appeal Reversals

An appeal reversal happens when an advertiser challenges a decision and wins.

```python
is_appeal_reversed = appeal_submitted and appeal_result == "reversed"
```

Reversals are used as a downstream quality signal.

They help identify categories, reviewers, or teams where enforcement may be too strict or poorly calibrated.

---

## Policy Ambiguity

A case is flagged as ambiguous when both the AI and the human reviewer miss the golden label, but in different ways.

```python
is_policy_ambiguous = (
    not is_llm_correct
    and not is_human_correct
    and llm_label != human_label
)
```

These cases are useful for the policy team. They often point to unclear rules or missing examples.

---

## Metrics

| Metric | Formula |
|---|---|
| AI accuracy | `mean(is_llm_correct)` |
| Human accuracy | `mean(is_human_correct)` |
| Human-AI agreement | `mean(is_human_ai_agreement)` |
| Over-rejection rate | `mean(llm_severity_score > golden_severity_score)` |
| Risk miss rate | `mean(llm_severity_score < golden_severity_score)` |
| Low-confidence rate | `mean(llm_confidence_score < 0.60)` |
| Appeal reversal rate | `sum(is_appeal_reversed) / sum(appeal_submitted)` |
