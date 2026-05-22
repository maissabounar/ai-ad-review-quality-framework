"""
Shared utilities for the AI Ad Review Quality Framework.
"""

from pathlib import Path

# Severity order used throughout the project
SEVERITY_MAP = {
    "approved": 0,
    "approved_limited": 1,
    "escalated": 2,
    "rejected": 3,
}

REVERSE_SEVERITY_MAP = {v: k for k, v in SEVERITY_MAP.items()}

# Canonical label set
LABELS = ["approved", "approved_limited", "escalated", "rejected"]

# Project root (all scripts should run from project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"


def severity(label: str) -> int:
    """Return integer severity for a review label."""
    return SEVERITY_MAP.get(label, -1)


def is_over_rejection(llm_label: str, golden_label: str) -> bool:
    """Return True when the LLM decision is stricter than the golden label."""
    return severity(llm_label) > severity(golden_label)


def is_risk_miss(llm_label: str, golden_label: str) -> bool:
    """Return True when the LLM decision is more lenient than the golden label."""
    return severity(llm_label) < severity(golden_label)


def is_high_risk_approval_miss(risk_level: str, golden_label: str, llm_label: str) -> bool:
    """Return True when a high-risk ad that should be limited/rejected was approved by LLM."""
    return (
        risk_level == "high"
        and golden_label in ["approved_limited", "rejected", "escalated"]
        and llm_label == "approved"
    )


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
