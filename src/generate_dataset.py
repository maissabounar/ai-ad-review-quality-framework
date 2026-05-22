"""
Generate a synthetic dataset of 5,000 digital ad review cases.

Simulates a realistic LLM pre-screening + human BPO reviewer workflow.
Each row represents one ad reviewed by an LLM system, a human reviewer,
and assigned an expert golden label.

Run from project root:
    python src/generate_dataset.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import SEVERITY_MAP, LABELS, PROJECT_ROOT

RANDOM_SEED = 42
N_RECORDS = 5000
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "synthetic_ad_reviews.csv"

# ------------------------------------------------------------------
# Reference data
# ------------------------------------------------------------------

MARKETS = ["FR", "UK", "US", "DE", "ES", "IT", "BR", "MX"]

MARKET_LANGUAGE_MAP = {
    "FR": "French",
    "UK": "English",
    "US": "English",
    "DE": "German",
    "ES": "Spanish",
    "IT": "Italian",
    "BR": "Portuguese",
    "MX": "Spanish",
}

AD_FORMATS = [
    "Search Ad", "Display Ad", "Video Ad", "Social Feed Ad", "Shopping Ad", "App Install Ad"
]

INDUSTRY_VERTICALS = [
    "Beauty", "Health and Wellness", "Finance", "E-commerce", "Gaming",
    "Travel", "Education", "Food and Beverage", "Mobile Apps", "Retail"
]

ADVERTISER_TIERS = ["small_business", "mid_market", "enterprise", "strategic_account"]

CAMPAIGN_OBJECTIVES = [
    "Traffic", "Conversions", "Lead Generation", "App Installs",
    "Brand Awareness", "Sales", "Retargeting"
]

POLICY_CATEGORIES = [
    "Misleading Claim", "Financial Product Claim", "Health Claim",
    "Restricted Product", "Political or Sensitive Content", "Adult or Suggestive Content",
    "Scam or Suspicious Offer", "Brand Safety Risk", "Landing Page Issue", "Safe Ad"
]

BPO_TEAMS = ["BPO_A", "BPO_B", "BPO_C", "BPO_D", "BPO_E"]
REVIEWER_TENURES = ["new", "intermediate", "experienced"]

# ------------------------------------------------------------------
# Accuracy and bias configuration
# ------------------------------------------------------------------

# LLM accuracy per policy category (probability of matching golden label)
LLM_ACCURACY = {
    "Safe Ad": 0.95,                 # raised: offsets additional over-rejections from bias adjustments below
    "Scam or Suspicious Offer": 0.87,
    "Restricted Product": 0.82,
    "Brand Safety Risk": 0.79,
    "Adult or Suggestive Content": 0.76,
    "Political or Sensitive Content": 0.69,
    "Misleading Claim": 0.67,
    "Health Claim": 0.69,            # raised from 0.65: still clearly weakest regulated category
    "Financial Product Claim": 0.68, # raised from 0.64
    "Landing Page Issue": 0.60,      # raised from 0.58: structural limit (no landing page access)
}

# Human reviewer accuracy per tenure (pre-adjustment base rates)
HUMAN_ACCURACY = {
    "experienced": 0.95,   # experienced reviewers are highly reliable
    "intermediate": 0.90,  # clear gap vs new reviewers
    "new": 0.82,           # new reviewers make meaningful errors, especially on regulated categories
}

# BPO team calibration difficulty (>1.0 = team needs calibration)
# Kept intentionally narrow: real teams differ, but not by 14 percentage points
BPO_DIFFICULTY = {
    "BPO_A": 1.00,
    "BPO_B": 0.98,
    "BPO_C": 1.04,
    "BPO_D": 1.08,
    "BPO_E": 1.03,
}

# LLM market difficulty — model struggles more with non-English regulatory context
MARKET_DIFFICULTY = {
    "FR": 1.10, "UK": 1.00, "US": 1.00,
    "DE": 1.15, "ES": 1.12, "IT": 1.18,
    "BR": 1.20, "MX": 1.15,
}

# Human reviewer market difficulty — smaller effect than for LLM because BPO teams
# handling non-English markets receive local policy training and are native speakers
HUMAN_MARKET_DIFFICULTY = {
    "FR": 1.04, "UK": 1.00, "US": 1.00,
    "DE": 1.05, "ES": 1.04, "IT": 1.06,
    "BR": 1.08, "MX": 1.05,
}

# LLM directional bias when making an error
LLM_BIAS = {
    "Safe Ad": "over_reject",
    "Scam or Suspicious Offer": "over_reject",
    "Adult or Suggestive Content": "over_reject",
    "Health Claim": "under_reject",
    "Financial Product Claim": "under_reject",
    "Political or Sensitive Content": "under_reject",
    "Landing Page Issue": "under_reject",
    "Misleading Claim": "mixed",
    "Restricted Product": "mixed",
    "Brand Safety Risk": "mixed",
}

# How strongly the directional bias is applied when LLM is wrong (1.0 = always, <1.0 = partial)
# Under_reject categories set below 1.0 so a fraction of errors fall back to any wrong label,
# reducing the over-concentration of risk misses in regulated categories.
LLM_BIAS_STRENGTH = {
    "Health Claim": 0.70,
    "Financial Product Claim": 0.70,
    "Landing Page Issue": 0.75,
}

# Golden label distribution per policy category
GOLDEN_DIST = {
    "Safe Ad":                     {"approved": 0.75, "approved_limited": 0.20, "rejected": 0.03, "escalated": 0.02},
    "Scam or Suspicious Offer":    {"approved": 0.05, "approved_limited": 0.10, "rejected": 0.70, "escalated": 0.15},
    "Health Claim":                {"approved": 0.20, "approved_limited": 0.45, "rejected": 0.25, "escalated": 0.10},
    "Financial Product Claim":     {"approved": 0.25, "approved_limited": 0.40, "rejected": 0.25, "escalated": 0.10},
    "Misleading Claim":            {"approved": 0.10, "approved_limited": 0.35, "rejected": 0.40, "escalated": 0.15},
    "Restricted Product":          {"approved": 0.15, "approved_limited": 0.30, "rejected": 0.45, "escalated": 0.10},
    "Political or Sensitive Content": {"approved": 0.30, "approved_limited": 0.30, "rejected": 0.20, "escalated": 0.20},
    "Adult or Suggestive Content": {"approved": 0.15, "approved_limited": 0.35, "rejected": 0.35, "escalated": 0.15},
    "Brand Safety Risk":           {"approved": 0.20, "approved_limited": 0.40, "rejected": 0.25, "escalated": 0.15},
    "Landing Page Issue":          {"approved": 0.30, "approved_limited": 0.40, "rejected": 0.20, "escalated": 0.10},
}

# Risk level distribution per policy category
RISK_DIST = {
    "Safe Ad":                     {"low": 0.75, "medium": 0.22, "high": 0.03},
    "Scam or Suspicious Offer":    {"low": 0.05, "medium": 0.25, "high": 0.70},
    "Health Claim":                {"low": 0.20, "medium": 0.50, "high": 0.30},
    "Financial Product Claim":     {"low": 0.20, "medium": 0.45, "high": 0.35},
    "Misleading Claim":            {"low": 0.15, "medium": 0.45, "high": 0.40},
    "Restricted Product":          {"low": 0.10, "medium": 0.40, "high": 0.50},
    "Political or Sensitive Content": {"low": 0.25, "medium": 0.40, "high": 0.35},
    "Adult or Suggestive Content": {"low": 0.15, "medium": 0.45, "high": 0.40},
    "Brand Safety Risk":           {"low": 0.25, "medium": 0.45, "high": 0.30},
    "Landing Page Issue":          {"low": 0.35, "medium": 0.45, "high": 0.20},
}

# ------------------------------------------------------------------
# Ad text and landing page claim templates
# ------------------------------------------------------------------

AD_TEXTS = {
    "Safe Ad": [
        "Get 20% off your first skincare order today",
        "Summer sale now on — limited time only",
        "Free delivery on orders over 30 EUR",
        "Shop the new collection — fresh arrivals weekly",
        "Discover our latest seasonal offers",
        "Try our award-winning customer service",
        "Join over 500,000 happy customers worldwide",
        "New styles added daily — shop now",
        "Download our app and track your order in real time",
        "Explore thousands of products at unbeatable prices",
        "This course helps beginners learn data analytics",
        "New meal delivery plan for busy professionals",
        "Premium beauty bundle with customer reviews",
        "Try our gaming app with exclusive starter rewards",
        "Book your summer getaway with flexible cancellation",
    ],
    "Health Claim": [
        "Natural supplement to support your daily routine",
        "Clinically inspired formula for daily wellness",
        "Support your energy levels with our daily capsules",
        "Plant-based ingredients for a balanced lifestyle",
        "Daily nutrition designed for active adults",
        "Gentle formula to support digestive comfort",
        "Premium vitamins developed with nutrition experts",
        "Wellness supplements crafted from natural extracts",
        "Boost your morning routine with our daily blend",
        "Formulated to support healthy joints and mobility",
    ],
    "Financial Product Claim": [
        "Compare flexible loan options in minutes",
        "Low-interest personal finance solutions available now",
        "Apply for a business credit line with no hidden fees",
        "Find the best savings rate for your goals",
        "Fast approval personal loans — apply today",
        "Compare mortgage options across top lenders",
        "Open a savings account and start earning today",
        "No-fee investment accounts for new members",
        "Refinance your loan and lower your monthly payment",
        "Credit options tailored to your financial situation",
    ],
    "Misleading Claim": [
        "Results guaranteed or full refund — no questions asked",
        "The only product that truly delivers on its promise",
        "Scientifically proven to work in just one week",
        "Double your savings with our exclusive method",
        "Outperforms every competitor in independent tests",
        "No other solution comes close to our results",
        "Earn passive income with our proven system",
        "One simple approach to improve your outcomes fast",
        "Trusted by experts — see why customers switch",
        "Stop wasting money — our solution pays for itself",
    ],
    "Scam or Suspicious Offer": [
        "Win a free gift card after completing a quick survey",
        "You have been selected for an exclusive prize",
        "Claim your free device — only 3 slots remaining",
        "Limited slots available — register before midnight",
        "Enter your details to unlock your mystery reward",
        "You are the lucky visitor — collect your voucher",
        "Exclusive offer — act now or lose your spot",
        "Free product trial — no card required — act fast",
        "Congratulations — you qualify for a special offer",
        "Verify your account to receive your free reward",
    ],
    "Restricted Product": [
        "Premium vaping accessories for adult users",
        "Licensed lottery tickets available in your region",
        "Online pharmacy with prescription delivery service",
        "Age-verified adult subscription platform",
        "Same-day alcohol delivery in select areas",
        "Regulated gambling platform — play responsibly",
        "Sports betting — new member welcome offer",
        "Tobacco accessories shop — ID verification required",
        "Cannabis products for eligible medical use",
        "Adult entertainment content — 18 years and over",
    ],
    "Political or Sensitive Content": [
        "Support our movement for local community change",
        "Join the conversation about fair representation",
        "Civic engagement platform — your voice matters",
        "Register to participate in local elections",
        "Community forum for policy discussions",
        "Support awareness for human rights education",
        "Non-profit initiative for fair public services",
        "Advocacy campaign for environmental protection",
        "Sign the petition for transparent public spending",
        "Engage with your local elected representatives",
    ],
    "Adult or Suggestive Content": [
        "Meet new people near you — dating app for adults",
        "Premium lifestyle subscription for adult users",
        "Lingerie and intimate wear — discreet delivery",
        "Adult social platform — age verification required",
        "Romance and mature content — 18 plus only",
        "Dating service for singles — create your profile",
        "Mature content platform — verified adult access",
        "Exclusive member content for adult subscribers",
        "Lifestyle subscription — for consenting adults only",
        "Premium intimate product collection — discreet packaging",
    ],
    "Brand Safety Risk": [
        "Unbranded alternatives — same quality, lower price",
        "Compare brand prices before you buy",
        "Off-brand gadgets with comparable performance",
        "Independent reviews of popular consumer products",
        "Generic alternatives at a fraction of the cost",
        "Budget alternatives for expensive branded goods",
        "Aggregated reviews for popular consumer brands",
        "Side-by-side comparisons of competing products",
        "Switch and save — see how alternatives stack up",
        "Consumer comparison tool for popular categories",
    ],
    "Landing Page Issue": [
        "Best deal online — click here to learn more",
        "Exclusive offer — see our website for full details",
        "Limited time pricing — available on our site only",
        "Special rate unlocked — visit landing page now",
        "Click to reveal your personalized offer",
        "Your custom quote is ready — click to view",
        "See full terms on our website before applying",
        "Pricing varies — visit site for accurate information",
        "Offer subject to eligibility — check website",
        "Details not shown here — view on our landing page",
    ],
}

LANDING_PAGE_CLAIMS = [
    "Clinically inspired formula",
    "Rates may vary by eligibility",
    "Results depend on individual use",
    "No purchase required",
    "Terms and conditions apply",
    "Limited availability",
    "Customer testimonials shown",
    "Subscription renews monthly",
    "Check local rules before applying",
    "Product information updated regularly",
    "Individual results may vary",
    "Offer valid while stocks last",
    "Age verification required",
    "Subject to regulatory approval",
    "Free trial followed by monthly subscription",
    "Pricing subject to change",
    "Not available in all regions",
    "Professional advice recommended",
    "Standard delivery times apply",
    "Promotional pricing for new customers only",
]

# ------------------------------------------------------------------
# Generation helpers
# ------------------------------------------------------------------

def _make_llm_label(golden_label, policy_cat, llm_acc, market_diff, rng):
    """Generate LLM label with category-specific directional bias on errors."""
    if rng.random() < llm_acc / market_diff:
        return golden_label

    bias = LLM_BIAS.get(policy_cat, "mixed")
    bias_strength = LLM_BIAS_STRENGTH.get(policy_cat, 1.0)
    golden_sev = SEVERITY_MAP[golden_label]

    if bias == "over_reject":
        options = [l for l in LABELS if SEVERITY_MAP[l] > golden_sev]
        if options:
            return rng.choice(options)
    elif bias == "under_reject":
        options = [l for l in LABELS if SEVERITY_MAP[l] < golden_sev]
        if options and rng.random() < bias_strength:
            return rng.choice(options)

    # Fall back to any wrong label
    wrong = [l for l in LABELS if l != golden_label]
    return rng.choice(wrong)


def _make_human_label(golden_label, tenure, bpo_team, human_market_diff, rng):
    """Generate human reviewer label with tenure, BPO team, and market effects.

    Uses HUMAN_MARKET_DIFFICULTY (softer than LLM market difficulty) — BPO teams
    serving non-English markets receive local policy training, so the market
    penalty on humans is meaningfully smaller than on the LLM.
    """
    base_acc = HUMAN_ACCURACY[tenure]
    team_diff = BPO_DIFFICULTY[bpo_team]
    adjusted = base_acc / (human_market_diff * team_diff)

    if rng.random() < adjusted:
        return golden_label

    wrong = [l for l in LABELS if l != golden_label]
    return rng.choice(wrong)


def _make_llm_confidence(llm_label, golden_label, rng):
    """Confidence: correct predictions are generally more confident,
    but some wrong predictions carry falsely high confidence."""
    if llm_label == golden_label:
        conf = rng.beta(8, 2) * 0.40 + 0.60
    else:
        if rng.random() < 0.28:
            # High-confidence wrong prediction (most valuable for model feedback)
            conf = rng.beta(6, 2) * 0.25 + 0.72
        else:
            conf = rng.beta(4, 6) * 0.60 + 0.18
    return round(float(np.clip(conf, 0.10, 0.99)), 3)


def _make_human_confidence(human_label, golden_label, tenure, rng):
    if human_label == golden_label:
        conf = rng.beta(7, 2) * 0.35 + 0.65
    else:
        conf = rng.beta(3, 5) * 0.50 + 0.30
    return round(float(np.clip(conf, 0.20, 0.99)), 3)


def _make_review_time(risk_level, policy_cat, tenure, golden_label, rng):
    base = {"low": 45, "medium": 90, "high": 150}[risk_level]
    cat_mult = {
        "Safe Ad": 0.70, "Scam or Suspicious Offer": 1.10,
        "Health Claim": 1.30, "Financial Product Claim": 1.35,
        "Misleading Claim": 1.20, "Restricted Product": 1.15,
        "Political or Sensitive Content": 1.40, "Adult or Suggestive Content": 1.00,
        "Brand Safety Risk": 1.10, "Landing Page Issue": 1.25,
    }.get(policy_cat, 1.0)
    tenure_mult = {"experienced": 0.85, "intermediate": 1.00, "new": 1.35}[tenure]

    base = base * cat_mult * tenure_mult
    if golden_label in ["escalated", "rejected"]:
        base *= 1.2
    noise = rng.normal(0, base * 0.25)
    return max(int(base + noise), 20)


def _make_appeal(human_label, golden_label, advertiser_tier, rng):
    base_rate = {"rejected": 0.35, "approved_limited": 0.15}.get(human_label, 0.03)
    tier_mult = {"strategic_account": 1.50, "enterprise": 1.30, "mid_market": 1.00, "small_business": 0.70}
    rate = base_rate * tier_mult[advertiser_tier]
    submitted = rng.random() < rate

    if not submitted:
        return False, "not_submitted"

    h_sev = SEVERITY_MAP[human_label]
    g_sev = SEVERITY_MAP[golden_label]
    if h_sev > g_sev:
        # Original decision was stricter than warranted — appeal likely to succeed,
        # but not overwhelmingly; platform review processes add friction
        reversal_rate = 0.52
    elif h_sev == g_sev:
        reversal_rate = 0.12
    else:
        reversal_rate = 0.05

    result = "reversed" if rng.random() < reversal_rate else "upheld"
    return True, result


def _make_error_type(llm_label, golden_label, risk_level, policy_cat, llm_conf, market):
    if llm_label == golden_label:
        return "none"

    l_sev = SEVERITY_MAP[llm_label]
    g_sev = SEVERITY_MAP[golden_label]

    if l_sev > g_sev:
        return "over_rejection"

    if l_sev < g_sev:
        if risk_level == "high" and golden_label in ["approved_limited", "rejected", "escalated"] and llm_label == "approved":
            return "high_risk_approval_miss"
        if policy_cat == "Landing Page Issue":
            return "landing_page_mismatch"
        if policy_cat in ["Health Claim", "Financial Product Claim"]:
            return "claim_substantiation_issue"
        if MARKET_LANGUAGE_MAP.get(market) not in ["English"]:
            return "market_nuance_error"
        return "policy_risk_miss"

    # Same severity level but different label
    if llm_conf < 0.60:
        return "low_confidence_disagree"
    return "policy_risk_miss"


def _make_recommended_action(is_high_risk_miss, is_low_conf, is_llm_correct, llm_conf,
                              is_over_reject, appeal_result, is_human_correct):
    if is_high_risk_miss:
        return "escalate_to_human_review"
    if is_low_conf and not is_llm_correct:
        return "route_to_human_review"
    if not is_llm_correct and llm_conf > 0.75:
        return "add_to_model_feedback"
    if is_over_reject and appeal_result == "reversed":
        return "review_policy_threshold"
    if not is_human_correct:
        return "flag_for_calibration"
    return "no_action_required"


# ------------------------------------------------------------------
# Main generation function
# ------------------------------------------------------------------

def generate_dataset(n_records=N_RECORDS):
    rng = np.random.default_rng(RANDOM_SEED)

    # Draw base attributes
    market_probs = [0.12, 0.14, 0.16, 0.12, 0.11, 0.10, 0.13, 0.12]
    markets = rng.choice(MARKETS, n_records, p=market_probs)
    languages = [MARKET_LANGUAGE_MAP[m] for m in markets]

    format_probs = [0.20, 0.18, 0.15, 0.22, 0.15, 0.10]
    ad_formats = rng.choice(AD_FORMATS, n_records, p=format_probs)

    industry_verticals = rng.choice(INDUSTRY_VERTICALS, n_records)
    advertiser_tiers = rng.choice(ADVERTISER_TIERS, n_records, p=[0.40, 0.30, 0.20, 0.10])
    campaign_objectives = rng.choice(CAMPAIGN_OBJECTIVES, n_records)

    policy_probs = [0.10, 0.09, 0.09, 0.08, 0.07, 0.07, 0.10, 0.08, 0.08, 0.24]
    policy_categories = rng.choice(POLICY_CATEGORIES, n_records, p=policy_probs)

    bpo_teams = rng.choice(BPO_TEAMS, n_records)
    reviewer_tenures = rng.choice(REVIEWER_TENURES, n_records, p=[0.25, 0.40, 0.35])

    start_date = pd.Timestamp("2024-01-01")
    random_days = rng.integers(0, 365, n_records)

    records = []

    for i in range(n_records):
        policy_cat = policy_categories[i]
        market = markets[i]
        tenure = reviewer_tenures[i]
        bpo = bpo_teams[i]
        advertiser_tier = advertiser_tiers[i]
        llm_market_diff = MARKET_DIFFICULTY[market]
        human_market_diff = HUMAN_MARKET_DIFFICULTY[market]

        # Golden label
        g_dist = GOLDEN_DIST[policy_cat]
        golden_label = rng.choice(list(g_dist.keys()), p=list(g_dist.values()))

        # Risk level
        r_dist = RISK_DIST[policy_cat]
        risk_level = rng.choice(list(r_dist.keys()), p=list(r_dist.values()))

        # LLM and human labels (each uses its own market difficulty)
        llm_label = _make_llm_label(golden_label, policy_cat, LLM_ACCURACY[policy_cat], llm_market_diff, rng)
        llm_conf = _make_llm_confidence(llm_label, golden_label, rng)
        human_label = _make_human_label(golden_label, tenure, bpo, human_market_diff, rng)
        human_conf = _make_human_confidence(human_label, golden_label, tenure, rng)

        review_time = _make_review_time(risk_level, policy_cat, tenure, golden_label, rng)
        appeal_submitted, appeal_result = _make_appeal(human_label, golden_label, advertiser_tier, rng)

        # Derived flags
        is_llm_correct = llm_label == golden_label
        is_human_correct = human_label == golden_label
        is_human_ai_agreement = llm_label == human_label
        is_over_rej = SEVERITY_MAP[llm_label] > SEVERITY_MAP[golden_label]
        is_risk_miss = SEVERITY_MAP[llm_label] < SEVERITY_MAP[golden_label]
        is_low_conf = llm_conf < 0.60
        is_hr_miss = (
            risk_level == "high"
            and golden_label in ["approved_limited", "rejected", "escalated"]
            and llm_label == "approved"
        )

        error_type = _make_error_type(llm_label, golden_label, risk_level, policy_cat, llm_conf, market)
        recommended_action = _make_recommended_action(
            is_hr_miss, is_low_conf, is_llm_correct, llm_conf,
            is_over_rej, appeal_result, is_human_correct
        )

        # Ad text and landing page claim (cycle through templates)
        texts = AD_TEXTS[policy_cat]
        ad_text = texts[i % len(texts)]
        landing_page_claim = LANDING_PAGE_CLAIMS[i % len(LANDING_PAGE_CLAIMS)]

        created_date = (start_date + pd.Timedelta(days=int(random_days[i]))).strftime("%Y-%m-%d")

        records.append({
            "ad_id": f"AD{str(i + 1).zfill(5)}",
            "created_date": created_date,
            "market": market,
            "language": languages[i],
            "ad_format": ad_formats[i],
            "industry_vertical": industry_verticals[i],
            "advertiser_tier": advertiser_tier,
            "campaign_objective": campaign_objectives[i],
            "policy_category": policy_cat,
            "risk_level": risk_level,
            "ad_text": ad_text,
            "landing_page_claim": landing_page_claim,
            "golden_label": golden_label,
            "human_label": human_label,
            "llm_label": llm_label,
            "llm_confidence_score": llm_conf,
            "human_confidence_score": human_conf,
            "review_time_seconds": review_time,
            "appeal_submitted": appeal_submitted,
            "appeal_result": appeal_result,
            "bpo_team": bpo,
            "reviewer_tenure": tenure,
            "error_type": error_type,
            "is_llm_correct": is_llm_correct,
            "is_human_correct": is_human_correct,
            "is_human_ai_agreement": is_human_ai_agreement,
            "is_advertiser_over_rejection": is_over_rej,
            "is_policy_risk_miss": is_risk_miss,
            "is_low_confidence_case": is_low_conf,
            "is_high_risk_approval_miss": is_hr_miss,
            "recommended_action": recommended_action,
        })

    df = pd.DataFrame(records)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"[generate_dataset] Dataset created: {len(df):,} records -> {OUTPUT_PATH}")
    print(f"  LLM accuracy:     {df['is_llm_correct'].mean():.1%}")
    print(f"  Human accuracy:   {df['is_human_correct'].mean():.1%}")
    print(f"  H-AI agreement:   {df['is_human_ai_agreement'].mean():.1%}")
    print(f"  Over-rejections:  {df['is_advertiser_over_rejection'].sum():,}")
    print(f"  Risk misses:      {df['is_policy_risk_miss'].sum():,}")
    print(f"  HR approval miss: {df['is_high_risk_approval_miss'].sum():,}")
    return df


if __name__ == "__main__":
    generate_dataset()
