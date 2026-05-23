# AI Ad Review Quality Framework

A senior analytics case study on monitoring AI-assisted ad review quality, policy risk, and human reviewer calibration.

Live dashboard: [Open the Streamlit app](https://ai-ad-review-quality-framework-bz2wtnfosysjofgbqvzsvx.streamlit.app/)

---

## Overview

This project simulates an ad review workflow where an AI model pre-screens ads before human reviewers make the final policy decision.

The goal is to answer three questions:

- Where does the AI create policy risk?
- Where do human reviewers need calibration?
- Which cases should be routed back into model feedback loops?

The project includes synthetic data, Python pipelines, SQL analysis, and an interactive Streamlit dashboard.

---

## Dashboard Preview

| Executive Overview | Policy Category Analysis |
|---|---|
| ![Executive Overview](dashboard/screenshots/executive_overview.png) | ![Policy Category Analysis](dashboard/screenshots/policy_category_analysis.png) |
| BPO Calibration | Model Feedback Examples |
| ![BPO Calibration](dashboard/screenshots/bpo_calibration.png) | ![Model Feedback Examples](dashboard/screenshots/model_feedback_examples.png) |

---

## Key Results

| Area | Finding |
|---|---|
| AI accuracy | 71.1% overall |
| Human accuracy | 83.5% overall |
| Agreement | 60.8% Human-AI agreement |
| Main risk | 154 high-risk approval misses |
| Weakest categories | Financial Product Claim, Landing Page Issue, Misleading Claim |
| Reviewer gap | New reviewers: 24.1% error rate vs. 10.5% for experienced reviewers |
| BPO gap | BPO_D at 78.4% accuracy vs. BPO_B at 87.3% |

---

## Main Insights

1. The AI performs well on clear-cut cases, but struggles with regulated or contextual categories.

2. The main risk is under-rejection: risky ads being approved or limited instead of escalated or rejected.

3. Low-confidence AI decisions below 0.60 should be routed to mandatory human review.

4. Reviewer quality is trainable. Tenure and BPO team explain a large part of human review variation.

5. The highest-value feedback examples are high-confidence wrong AI decisions, especially in regulated categories.

---

## Recommendations

| Priority | Action |
|---|---|
| High | Route AI decisions below 0.60 confidence to human review |
| High | Monitor high-risk approval misses weekly |
| High | Calibrate reviewers on Financial Product Claim and Health Claim |
| High | Send high-confidence wrong AI decisions to model retraining |
| Medium | Add market-specific policy guidance for BR, IT, DE, and ES |
| Medium | Audit categories with high appeal reversal rates |

---

## Tech Stack

| Tool | Use |
|---|---|
| Python | Data generation and evaluation |
| pandas | Data processing |
| DuckDB | SQL analysis |
| Plotly | Charts |
| Streamlit | Dashboard |
| GitHub | Documentation and project hosting |

---

## Project Structure

```text
data/          Synthetic raw and processed datasets
src/           Python generation and evaluation scripts
sql/           SQL analysis queries
dashboard/     Streamlit dashboard
docs/          Methodology and recommendations
outputs/       Final metric tables and summaries
