"""
Calculate quality metrics and export CSV reports for all analytical dimensions.

Outputs written to outputs/:
  - overall_quality_summary.csv
  - policy_category_metrics.csv
  - market_language_metrics.csv
  - bpo_team_metrics.csv
  - appeal_reversal_analysis.csv
  - model_feedback_examples.csv

Run from project root:
    python src/evaluate_quality.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import PROJECT_ROOT, print_section

PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "ad_reviews_enriched.csv"
OUTPUTS = PROJECT_ROOT / "outputs"


# ------------------------------------------------------------------
# Loaders
# ------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Processed data not found: {PROCESSED_PATH}\n"
            "Run 'python src/prepare_data.py' first."
        )
    df = pd.read_csv(PROCESSED_PATH, parse_dates=["created_date"])
    bool_cols = [
        "is_llm_correct", "is_human_correct", "is_human_ai_agreement",
        "is_advertiser_over_rejection", "is_policy_risk_miss",
        "is_low_confidence_case", "is_high_risk_approval_miss",
        "is_policy_ambiguous", "is_appeal_reversed", "appeal_submitted",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    return df


# ------------------------------------------------------------------
# 1. Overall quality summary
# ------------------------------------------------------------------

def calc_overall_summary(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    appealed = df["appeal_submitted"].sum()
    reversed_ = df["is_appeal_reversed"].sum()

    summary = {
        "total_cases": total,
        "llm_accuracy": round(df["is_llm_correct"].mean(), 4),
        "human_accuracy": round(df["is_human_correct"].mean(), 4),
        "human_ai_agreement_rate": round(df["is_human_ai_agreement"].mean(), 4),
        "advertiser_over_rejection_rate": round(df["is_advertiser_over_rejection"].mean(), 4),
        "policy_risk_miss_rate": round(df["is_policy_risk_miss"].mean(), 4),
        "high_risk_approval_miss_count": int(df["is_high_risk_approval_miss"].sum()),
        "low_confidence_case_rate": round(df["is_low_confidence_case"].mean(), 4),
        "avg_llm_confidence": round(df["llm_confidence_score"].mean(), 4),
        "appeal_submission_rate": round(appealed / total, 4),
        "appeal_reversal_rate": round(reversed_ / appealed, 4) if appealed > 0 else 0.0,
        "avg_review_time_seconds": round(df["review_time_seconds"].mean(), 1),
        "policy_ambiguity_rate": round(df["is_policy_ambiguous"].mean(), 4),
    }
    return pd.DataFrame([summary])


# ------------------------------------------------------------------
# 2. Policy category metrics
# ------------------------------------------------------------------

def calc_policy_metrics(df: pd.DataFrame) -> pd.DataFrame:
    def agg_group(g):
        total = len(g)
        appealed = g["appeal_submitted"].sum()
        reversed_ = g["is_appeal_reversed"].sum()
        return pd.Series({
            "total_cases": total,
            "llm_accuracy": round(g["is_llm_correct"].mean(), 4),
            "human_accuracy": round(g["is_human_correct"].mean(), 4),
            "human_ai_agreement_rate": round(g["is_human_ai_agreement"].mean(), 4),
            "advertiser_over_rejection_rate": round(g["is_advertiser_over_rejection"].mean(), 4),
            "policy_risk_miss_rate": round(g["is_policy_risk_miss"].mean(), 4),
            "high_risk_approval_misses": int(g["is_high_risk_approval_miss"].sum()),
            "policy_ambiguity_rate": round(g["is_policy_ambiguous"].mean(), 4),
            "avg_llm_confidence": round(g["llm_confidence_score"].mean(), 4),
            "appeal_submission_rate": round(appealed / total, 4),
            "appeal_reversal_rate": round(reversed_ / appealed, 4) if appealed > 0 else 0.0,
            "avg_review_time_seconds": round(g["review_time_seconds"].mean(), 1),
        })

    return df.groupby("policy_category").apply(agg_group).reset_index()


# ------------------------------------------------------------------
# 3. Market and language metrics
# ------------------------------------------------------------------

def calc_market_language_metrics(df: pd.DataFrame) -> pd.DataFrame:
    def agg_group(g):
        total = len(g)
        appealed = g["appeal_submitted"].sum()
        reversed_ = g["is_appeal_reversed"].sum()
        return pd.Series({
            "total_cases": total,
            "llm_accuracy": round(g["is_llm_correct"].mean(), 4),
            "human_accuracy": round(g["is_human_correct"].mean(), 4),
            "human_ai_agreement_rate": round(g["is_human_ai_agreement"].mean(), 4),
            "advertiser_over_rejection_rate": round(g["is_advertiser_over_rejection"].mean(), 4),
            "policy_risk_miss_rate": round(g["is_policy_risk_miss"].mean(), 4),
            "avg_review_time_seconds": round(g["review_time_seconds"].mean(), 1),
            "appeal_reversal_rate": round(reversed_ / appealed, 4) if appealed > 0 else 0.0,
        })

    return df.groupby(["market", "language"]).apply(agg_group).reset_index()


# ------------------------------------------------------------------
# 4. BPO team and reviewer tenure metrics
# ------------------------------------------------------------------

def calc_bpo_metrics(df: pd.DataFrame) -> pd.DataFrame:
    def agg_group(g):
        total = len(g)
        appealed = g["appeal_submitted"].sum()
        reversed_ = g["is_appeal_reversed"].sum()

        # Identify top problem category for this group
        cat_errors = (
            g[~g["is_human_correct"]]
            .groupby("policy_category")
            .size()
        )
        top_problem_cat = cat_errors.idxmax() if len(cat_errors) > 0 else "N/A"

        return pd.Series({
            "total_cases": total,
            "human_accuracy": round(g["is_human_correct"].mean(), 4),
            "human_golden_agreement": round(g["is_human_correct"].mean(), 4),
            "human_ai_agreement": round(g["is_human_ai_agreement"].mean(), 4),
            "error_rate": round(1 - g["is_human_correct"].mean(), 4),
            "avg_review_time_seconds": round(g["review_time_seconds"].mean(), 1),
            "appeal_reversal_rate": round(reversed_ / appealed, 4) if appealed > 0 else 0.0,
            "top_error_policy_category": top_problem_cat,
        })

    # By BPO team
    by_team = df.groupby("bpo_team").apply(agg_group).reset_index()

    # By reviewer tenure
    by_tenure = df.groupby("reviewer_tenure").apply(agg_group).reset_index()

    # Combined: team x tenure
    by_team_tenure = df.groupby(["bpo_team", "reviewer_tenure"]).apply(agg_group).reset_index()

    return by_team, by_tenure, by_team_tenure


# ------------------------------------------------------------------
# 5. Appeal reversal analysis
# ------------------------------------------------------------------

def calc_appeal_analysis(df: pd.DataFrame) -> pd.DataFrame:
    appealed_df = df[df["appeal_submitted"]].copy()

    def appeal_agg(g):
        total = len(g)
        reversed_ = (g["appeal_result"] == "reversed").sum()
        return pd.Series({
            "total_appeals": total,
            "reversals": int(reversed_),
            "reversal_rate": round(reversed_ / total, 4) if total > 0 else 0.0,
        })

    by_policy = appealed_df.groupby("policy_category").apply(appeal_agg).reset_index()
    by_policy["dimension"] = "policy_category"
    by_policy = by_policy.rename(columns={"policy_category": "value"})

    by_llm_label = appealed_df.groupby("llm_label").apply(appeal_agg).reset_index()
    by_llm_label["dimension"] = "llm_label"
    by_llm_label = by_llm_label.rename(columns={"llm_label": "value"})

    by_bpo = appealed_df.groupby("bpo_team").apply(appeal_agg).reset_index()
    by_bpo["dimension"] = "bpo_team"
    by_bpo = by_bpo.rename(columns={"bpo_team": "value"})

    by_tier = appealed_df.groupby("advertiser_tier").apply(appeal_agg).reset_index()
    by_tier["dimension"] = "advertiser_tier"
    by_tier = by_tier.rename(columns={"advertiser_tier": "value"})

    by_vertical = appealed_df.groupby("industry_vertical").apply(appeal_agg).reset_index()
    by_vertical["dimension"] = "industry_vertical"
    by_vertical = by_vertical.rename(columns={"industry_vertical": "value"})

    combined = pd.concat(
        [by_policy, by_llm_label, by_bpo, by_tier, by_vertical],
        ignore_index=True
    )
    return combined[["dimension", "value", "total_appeals", "reversals", "reversal_rate"]]


# ------------------------------------------------------------------
# 6. Model feedback examples
# ------------------------------------------------------------------

WHY_IT_MATTERS = {
    "high_risk_approval_miss": (
        "High-risk ad approved by LLM despite policy violation — "
        "missed by model may reach live inventory."
    ),
    "over_rejection": (
        "LLM over-rejected a safe or low-risk ad — "
        "causes unnecessary advertiser friction and potential revenue loss."
    ),
    "policy_risk_miss": (
        "LLM missed a policy violation — "
        "risky ad may have been served without appropriate restriction."
    ),
    "claim_substantiation_issue": (
        "LLM failed to identify an unsubstantiated claim in a regulated category."
    ),
    "landing_page_mismatch": (
        "LLM decision did not reflect a policy issue visible only on the landing page."
    ),
    "market_nuance_error": (
        "LLM decision diverged due to local market or language policy nuance."
    ),
    "low_confidence_disagree": (
        "LLM made a decision with low confidence that disagreed with the golden label — "
        "should be routed to human review."
    ),
}

RECOMMENDED_ACTIONS = {
    "high_risk_approval_miss": "Add to model training set — high-risk false approval example.",
    "over_rejection": "Review policy threshold calibration — reduce false rejection rate.",
    "policy_risk_miss": "Add to model training set — policy violation missed by model.",
    "claim_substantiation_issue": "Flag for policy team — update claim substantiation guidelines.",
    "landing_page_mismatch": "Add to model training set — improve landing page signal detection.",
    "market_nuance_error": "Route to market policy team — local calibration needed.",
    "low_confidence_disagree": "Implement mandatory human review for low-confidence decisions.",
}


def calc_model_feedback(df: pd.DataFrame, n_min=50, n_max=100) -> pd.DataFrame:
    # High-value examples for the algorithm and policy teams
    mask = (
        (~df["is_llm_correct"])
        & (df["risk_level"].isin(["medium", "high"]))
        & (
            (df["llm_confidence_score"] > 0.72)      # High-confidence wrong
            | (df["is_high_risk_approval_miss"])       # HR approval miss
            | (df["is_appeal_reversed"])               # Reversed appeal
            | (df["is_policy_ambiguous"])              # Both LLM and human wrong
        )
    )

    candidates = df[mask].copy()

    # Sort by priority: high-risk approval misses first, then high confidence errors
    candidates["priority_score"] = (
        candidates["is_high_risk_approval_miss"].astype(int) * 3
        + (candidates["llm_confidence_score"] > 0.75).astype(int) * 2
        + candidates["is_appeal_reversed"].astype(int) * 2
        + (candidates["risk_level"] == "high").astype(int)
    )
    candidates = candidates.sort_values("priority_score", ascending=False)

    # Cap at n_max
    sample = candidates.head(n_max).copy()

    # Add explanatory fields
    sample["why_it_matters"] = sample["error_type"].map(WHY_IT_MATTERS).fillna(
        "LLM decision diverged from golden label on a medium-to-high risk case."
    )
    sample["recommended_action_detail"] = sample["error_type"].map(RECOMMENDED_ACTIONS).fillna(
        "Review and add to appropriate feedback pipeline."
    )

    output_cols = [
        "ad_id", "ad_text", "landing_page_claim", "market", "language",
        "industry_vertical", "policy_category", "risk_level", "advertiser_tier",
        "golden_label", "human_label", "llm_label", "llm_confidence_score",
        "error_type", "appeal_submitted", "appeal_result",
        "why_it_matters", "recommended_action_detail",
    ]
    return sample[output_cols].rename(columns={"recommended_action_detail": "recommended_action"})


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def run_evaluation():
    print_section("Loading data")
    df = load_data()
    print(f"  Loaded {len(df):,} records.")

    OUTPUTS.mkdir(parents=True, exist_ok=True)

    print_section("Overall quality summary")
    overall = calc_overall_summary(df)
    path = OUTPUTS / "overall_quality_summary.csv"
    overall.to_csv(path, index=False)
    print(f"  Saved: {path}")
    for col, val in overall.iloc[0].items():
        print(f"    {col}: {val}")

    print_section("Policy category metrics")
    policy = calc_policy_metrics(df)
    path = OUTPUTS / "policy_category_metrics.csv"
    policy.to_csv(path, index=False)
    print(f"  Saved: {path} ({len(policy)} categories)")

    print_section("Market and language metrics")
    market = calc_market_language_metrics(df)
    path = OUTPUTS / "market_language_metrics.csv"
    market.to_csv(path, index=False)
    print(f"  Saved: {path} ({len(market)} market-language pairs)")

    print_section("BPO team and reviewer tenure metrics")
    by_team, by_tenure, by_team_tenure = calc_bpo_metrics(df)
    path = OUTPUTS / "bpo_team_metrics.csv"
    by_team_tenure.to_csv(path, index=False)
    print(f"  Saved: {path} ({len(by_team_tenure)} BPO team x tenure combinations)")
    print("\n  Human accuracy by BPO team:")
    for _, row in by_team.iterrows():
        print(f"    {row['bpo_team']}: {row['human_accuracy']:.1%}")
    print("\n  Error rate by reviewer tenure:")
    for _, row in by_tenure.iterrows():
        print(f"    {row['reviewer_tenure']}: {row['error_rate']:.1%}")

    print_section("Appeal reversal analysis")
    appeals = calc_appeal_analysis(df)
    path = OUTPUTS / "appeal_reversal_analysis.csv"
    appeals.to_csv(path, index=False)
    print(f"  Saved: {path} ({len(appeals)} rows)")

    print_section("Model feedback examples")
    feedback = calc_model_feedback(df)
    path = OUTPUTS / "model_feedback_examples.csv"
    feedback.to_csv(path, index=False)
    print(f"  Saved: {path} ({len(feedback)} high-value examples)")

    print_section("Evaluation complete")
    print(f"  All outputs written to: {OUTPUTS}")


if __name__ == "__main__":
    run_evaluation()
