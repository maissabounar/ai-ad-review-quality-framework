"""
Load raw synthetic ad reviews and produce an enriched analytical dataset.

New fields added:
  - Severity scores (llm, human, golden)
  - is_policy_ambiguous: both LLM and human diverge from golden in different directions
  - is_appeal_reversed: appeal was submitted and resulted in reversal

Existing boolean flags from the raw file are recalculated for consistency.

Run from project root:
    python src/prepare_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import SEVERITY_MAP, PROJECT_ROOT

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_ad_reviews.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "ad_reviews_enriched.csv"

REQUIRED_COLUMNS = [
    "ad_id", "created_date", "market", "language", "ad_format",
    "industry_vertical", "advertiser_tier", "campaign_objective",
    "policy_category", "risk_level", "ad_text", "landing_page_claim",
    "golden_label", "human_label", "llm_label",
    "llm_confidence_score", "human_confidence_score",
    "review_time_seconds", "appeal_submitted", "appeal_result",
    "bpo_team", "reviewer_tenure", "error_type",
]


def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print(f"  Column validation passed — {len(df.columns)} columns present.")


def add_severity_scores(df: pd.DataFrame) -> pd.DataFrame:
    df["llm_severity_score"] = df["llm_label"].map(SEVERITY_MAP)
    df["golden_severity_score"] = df["golden_label"].map(SEVERITY_MAP)
    df["human_severity_score"] = df["human_label"].map(SEVERITY_MAP)
    return df


def add_correctness_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["is_llm_correct"] = df["llm_label"] == df["golden_label"]
    df["is_human_correct"] = df["human_label"] == df["golden_label"]
    df["is_human_ai_agreement"] = df["llm_label"] == df["human_label"]
    return df


def add_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["is_advertiser_over_rejection"] = df["llm_severity_score"] > df["golden_severity_score"]
    df["is_policy_risk_miss"] = df["llm_severity_score"] < df["golden_severity_score"]
    df["is_low_confidence_case"] = df["llm_confidence_score"] < 0.60
    df["is_high_risk_approval_miss"] = (
        (df["risk_level"] == "high")
        & (df["golden_label"].isin(["approved_limited", "rejected", "escalated"]))
        & (df["llm_label"] == "approved")
    )
    return df


def add_policy_ambiguity_flag(df: pd.DataFrame) -> pd.DataFrame:
    # Cases where both LLM and human disagree with the golden label — suggests ambiguous policy
    df["is_policy_ambiguous"] = (
        (~df["is_llm_correct"])
        & (~df["is_human_correct"])
        & (df["llm_label"] != df["human_label"])
    )
    return df


def add_appeal_reversal_flag(df: pd.DataFrame) -> pd.DataFrame:
    df["is_appeal_reversed"] = (
        (df["appeal_submitted"].astype(bool))
        & (df["appeal_result"] == "reversed")
    )
    return df


def prepare_data() -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw data not found: {RAW_PATH}\n"
            "Run 'python src/generate_dataset.py' first."
        )

    print(f"[prepare_data] Loading {RAW_PATH} ...")
    df = pd.read_csv(RAW_PATH)
    print(f"  Loaded {len(df):,} records.")

    validate_columns(df)

    # Type coercions
    df["created_date"] = pd.to_datetime(df["created_date"])
    df["appeal_submitted"] = df["appeal_submitted"].astype(bool)

    # Enrichment pipeline
    df = add_severity_scores(df)
    df = add_correctness_flags(df)
    df = add_quality_flags(df)
    df = add_policy_ambiguity_flag(df)
    df = add_appeal_reversal_flag(df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    print(f"\n[prepare_data] Enriched data saved -> {PROCESSED_PATH}")
    print(f"  Total rows:               {len(df):,}")
    print(f"  Total columns:            {len(df.columns)}")
    print(f"  LLM accuracy:             {df['is_llm_correct'].mean():.1%}")
    print(f"  Human accuracy:           {df['is_human_correct'].mean():.1%}")
    print(f"  Human-AI agreement:       {df['is_human_ai_agreement'].mean():.1%}")
    print(f"  Over-rejections:          {df['is_advertiser_over_rejection'].sum():,}")
    print(f"  Policy risk misses:       {df['is_policy_risk_miss'].sum():,}")
    print(f"  High-risk approval miss:  {df['is_high_risk_approval_miss'].sum():,}")
    print(f"  Low-confidence cases:     {df['is_low_confidence_case'].sum():,}")
    print(f"  Policy ambiguous cases:   {df['is_policy_ambiguous'].sum():,}")
    print(f"  Appeal reversals:         {df['is_appeal_reversed'].sum():,}")
    return df


if __name__ == "__main__":
    prepare_data()
