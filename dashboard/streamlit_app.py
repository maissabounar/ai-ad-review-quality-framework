"""
AI Ad Review Quality Framework — Streamlit Dashboard

Run from project root:
    streamlit run dashboard/streamlit_app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Ad Review Quality Framework",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CSS injection — dark card system, hide Streamlit chrome
# ------------------------------------------------------------------

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1.5rem; }

/* Tighten vertical rhythm */
div[data-testid="stVerticalBlock"] > div { gap: 0.6rem; }
hr { border-color: #2A2F3A !important; margin-top: 0.4rem !important; margin-bottom: 0.4rem !important; }

/* KPI metric cards */
[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #2A2F3A;
    border-radius: 8px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] {
    color: #A6ADBB !important;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    color: #F5F5F5 !important;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: normal;
}

/* Insight cards */
.insight-card {
    background: #161B22;
    border-left: 3px solid #4C78A8;
    border-radius: 0 6px 6px 0;
    padding: 14px 18px;
    margin-bottom: 8px;
}
.insight-card.critical { border-left-color: #E45756; }
.insight-card.warning  { border-left-color: #F58518; }
.insight-card.positive { border-left-color: #54A24B; }
.insight-card.neutral  { border-left-color: #72B7B2; }

.insight-label {
    color: #A6ADBB;
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.insight-body {
    color: #F5F5F5;
    font-size: 0.88rem;
    line-height: 1.45;
    letter-spacing: normal;
}

/* Section headers */
.section-head { margin-top: 0.25rem; margin-bottom: 0.25rem; }
.section-head h2 {
    color: #F5F5F5;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: normal;
    word-spacing: normal;
    margin: 0 0 4px 0;
}
.section-head .subtitle {
    color: #A6ADBB;
    font-size: 0.83rem;
    letter-spacing: normal;
    margin: 0 0 4px 0;
}
.section-head .implication {
    color: #72B7B2;
    font-size: 0.78rem;
    font-style: italic;
    letter-spacing: normal;
    margin: 0;
}

/* What this means block */
.wtm-block {
    background: #1A1F2A;
    border-left: 3px solid #4C78A8;
    border-radius: 0 4px 4px 0;
    padding: 10px 16px;
    margin: 4px 0 12px 0;
    color: #C8CDD8;
    font-size: 0.82rem;
    line-height: 1.5;
    letter-spacing: normal;
}
.wtm-label {
    color: #4C78A8;
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

/* Selectbox — suppress red focus outline */
[data-testid="stSelectbox"] label { color: #A6ADBB; font-size: 0.80rem; }
[data-testid="stSelectbox"] > div > div {
    border-color: #2A2F3A !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stSelectbox"] > div > div:focus {
    border-color: #4C78A8 !important;
    box-shadow: 0 0 0 1px #4C78A8 !important;
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Colour palette
# ------------------------------------------------------------------

_BLUE   = "#4C78A8"
_RED    = "#E45756"
_AMBER  = "#F58518"
_GREEN  = "#54A24B"
_TEAL   = "#72B7B2"
_BG     = "#0E1117"
_CARD   = "#161B22"
_TEXT   = "#F5F5F5"
_MUTED  = "#A6ADBB"


def _base_layout(title: str, height: int = 300) -> dict:
    return dict(
        template="plotly_dark",
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=dict(color=_TEXT, size=11),
        margin=dict(l=10, r=10, t=36, b=10),
        hoverlabel=dict(bgcolor=_CARD, bordercolor="#2A2F3A", font_color=_TEXT),
        title=dict(text=title, font=dict(size=12, color=_TEXT), x=0),
        height=height,
    )


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENRICHED_PATH = PROJECT_ROOT / "data" / "processed" / "ad_reviews_enriched.csv"
OUTPUTS = PROJECT_ROOT / "outputs"


@st.cache_data
def load_main_data():
    if not ENRICHED_PATH.exists():
        return None
    df = pd.read_csv(ENRICHED_PATH, parse_dates=["created_date"])
    bool_cols = [
        "is_llm_correct", "is_human_correct", "is_human_ai_agreement",
        "is_advertiser_over_rejection", "is_policy_risk_miss",
        "is_low_confidence_case", "is_high_risk_approval_miss",
        "is_policy_ambiguous", "is_appeal_reversed", "appeal_submitted",
    ]
    for c in bool_cols:
        if c in df.columns:
            df[c] = df[c].astype(bool)
    return df


@st.cache_data
def load_output(filename: str):
    path = OUTPUTS / filename
    return pd.read_csv(path) if path.exists() else None


# ------------------------------------------------------------------
# UI helpers
# ------------------------------------------------------------------

def section_head(title: str, subtitle: str = "", implication: str = ""):
    parts = ['<div class="section-head">', f'<h2>{title}</h2>']
    if subtitle:
        parts.append(f'<p class="subtitle">{subtitle}</p>')
    if implication:
        parts.append(f'<p class="implication">{implication}</p>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def insight_card(col, label: str, body: str, accent: str = "neutral"):
    with col:
        st.markdown(
            f'<div class="insight-card {accent}">'
            f'<div class="insight-label">{label}</div>'
            f'<div class="insight-body">{body}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def what_this_means(text: str):
    st.markdown(
        f'<div class="wtm-block">'
        f'<div class="wtm-label">What this means</div>'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(col, label: str, value: str, delta: str = ""):
    with col:
        st.metric(label=label, value=value, delta=delta)


# ------------------------------------------------------------------
# Plotly chart helpers
# ------------------------------------------------------------------

def plot_hbar(
    series: pd.Series, title: str, xlabel: str,
    color: str = _BLUE, pct: bool = True,
):
    text = [f"{v:.1%}" if pct else f"{v:.2f}" for v in series.values]
    fig = go.Figure(go.Bar(
        x=series.values,
        y=[str(i) for i in series.index],
        orientation="h",
        marker_color=color,
        text=text,
        textposition="outside",
        textfont=dict(color=_MUTED, size=10),
        hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(title, max(200, len(series) * 38 + 60)))
    fig.update_layout(
        xaxis=dict(
            title=xlabel,
            tickformat=".0%" if pct else "",
            gridcolor="#2A2F3A",
            zerolinecolor="#2A2F3A",
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color=_MUTED),
            gridcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def plot_vbar(
    series: pd.Series, title: str, ylabel: str,
    colors=None, pct: bool = True,
):
    clr = colors if colors is not None else _BLUE
    text = [f"{v:.1%}" if pct else f"{v:.2f}" for v in series.values]
    fig = go.Figure(go.Bar(
        x=[str(i) for i in series.index],
        y=series.values,
        marker_color=clr,
        text=text,
        textposition="outside",
        textfont=dict(color=_MUTED, size=10),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))
    fig.update_layout(**_base_layout(title, 280))
    fig.update_layout(
        yaxis=dict(
            title=ylabel,
            tickformat=".0%" if pct else "",
            gridcolor="#2A2F3A",
        ),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    return fig


def plot_diverging(
    or_series: pd.Series, rm_series: pd.Series,
    cats: list, title: str,
):
    rm_aligned = rm_series.reindex(or_series.index)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=or_series.values,
        y=cats,
        orientation="h",
        name="Over-Rejection",
        marker_color=_RED,
        text=[f"{v:.1%}" for v in or_series.values],
        textposition="outside",
        textfont=dict(color=_MUTED, size=9),
        hovertemplate="%{y} — Over-Rejection: %{text}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=[-v for v in rm_aligned.values],
        y=cats,
        orientation="h",
        name="Risk Miss",
        marker_color=_AMBER,
        text=[f"{v:.1%}" for v in rm_aligned.values],
        textposition="outside",
        textfont=dict(color=_MUTED, size=9),
        hovertemplate="%{y} — Risk Miss: %{text}<extra></extra>",
    ))
    fig.add_shape(
        type="line",
        x0=0, x1=0, y0=-0.5, y1=len(cats) - 0.5,
        line=dict(color=_MUTED, width=0.8),
    )
    fig.update_layout(**_base_layout(title, max(220, len(cats) * 38 + 80)))
    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            title="<-- Risk Miss   |   Over-Rejection -->",
            tickformat=".0%",
            gridcolor="#2A2F3A",
            zerolinecolor="#2A2F3A",
        ),
        yaxis=dict(autorange="reversed", tickfont=dict(color=_MUTED)),
        legend=dict(orientation="h", x=0, y=-0.15, font=dict(size=10)),
    )
    return fig


def plot_histogram(
    series, title: str, xlabel: str,
    color: str = _TEAL, vline: float = None,
):
    fig = go.Figure(go.Histogram(
        x=series,
        nbinsx=30,
        marker_color=color,
        marker_line_color=_BG,
        marker_line_width=1,
        hovertemplate="Score: %{x:.2f} — Count: %{y}<extra></extra>",
    ))
    if vline is not None:
        fig.add_vline(
            x=vline,
            line_dash="dash",
            line_color=_RED,
            line_width=1.5,
            annotation_text="Low confidence threshold (0.60)",
            annotation_font=dict(color=_RED, size=10),
            annotation_position="top right",
        )
    fig.update_layout(**_base_layout(title, 280))
    fig.update_layout(
        xaxis=dict(title=xlabel, gridcolor="#2A2F3A"),
        yaxis=dict(title="Cases", gridcolor="#2A2F3A"),
    )
    return fig


def plot_heatmap(pivot_df: pd.DataFrame, title: str):
    fig = px.imshow(
        pivot_df,
        color_continuous_scale="RdYlGn",
        zmin=0.60,
        zmax=1.0,
        text_auto=".1%",
        aspect="auto",
    )
    fig.update_layout(**_base_layout(title, 300))
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Accuracy",
            tickformat=".0%",
            tickfont=dict(color=_MUTED),
        ),
    )
    fig.update_traces(textfont_size=10)
    return fig


# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------

def render_sidebar(df: pd.DataFrame):
    st.sidebar.header("Filters")

    markets = ["All"] + sorted(df["market"].unique().tolist())
    market = st.sidebar.selectbox("Market", markets)

    languages = ["All"] + sorted(df["language"].unique().tolist())
    language = st.sidebar.selectbox("Language", languages)

    policy_cats = ["All"] + sorted(df["policy_category"].unique().tolist())
    policy_cat = st.sidebar.selectbox("Policy Category", policy_cats)

    risk_levels = ["All"] + sorted(df["risk_level"].unique().tolist())
    risk_level = st.sidebar.selectbox("Risk Level", risk_levels)

    ad_formats = ["All"] + sorted(df["ad_format"].unique().tolist())
    ad_format = st.sidebar.selectbox("Ad Format", ad_formats)

    verticals = ["All"] + sorted(df["industry_vertical"].unique().tolist())
    vertical = st.sidebar.selectbox("Industry Vertical", verticals)

    tiers = ["All"] + sorted(df["advertiser_tier"].unique().tolist())
    tier = st.sidebar.selectbox("Advertiser Tier", tiers)

    objectives = ["All"] + sorted(df["campaign_objective"].unique().tolist())
    objective = st.sidebar.selectbox("Campaign Objective", objectives)

    bpo_teams = ["All"] + sorted(df["bpo_team"].unique().tolist())
    bpo = st.sidebar.selectbox("BPO Team", bpo_teams)

    tenures = ["All"] + sorted(df["reviewer_tenure"].unique().tolist())
    tenure = st.sidebar.selectbox("Reviewer Tenure", tenures)

    min_date = df["created_date"].min().date()
    max_date = df["created_date"].max().date()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    fdf = df.copy()
    if market != "All":
        fdf = fdf[fdf["market"] == market]
    if language != "All":
        fdf = fdf[fdf["language"] == language]
    if policy_cat != "All":
        fdf = fdf[fdf["policy_category"] == policy_cat]
    if risk_level != "All":
        fdf = fdf[fdf["risk_level"] == risk_level]
    if ad_format != "All":
        fdf = fdf[fdf["ad_format"] == ad_format]
    if vertical != "All":
        fdf = fdf[fdf["industry_vertical"] == vertical]
    if tier != "All":
        fdf = fdf[fdf["advertiser_tier"] == tier]
    if objective != "All":
        fdf = fdf[fdf["campaign_objective"] == objective]
    if bpo != "All":
        fdf = fdf[fdf["bpo_team"] == bpo]
    if tenure != "All":
        fdf = fdf[fdf["reviewer_tenure"] == tenure]
    if len(date_range) == 2:
        fdf = fdf[
            (fdf["created_date"].dt.date >= date_range[0])
            & (fdf["created_date"].dt.date <= date_range[1])
        ]

    st.sidebar.markdown(f"Filtered: {len(fdf)}")
    return fdf


# ------------------------------------------------------------------
# Section 1: Executive Overview
# ------------------------------------------------------------------

def render_executive_overview(df: pd.DataFrame):
    section_head(
        "Where the review system is failing",
        "LLM pre-screening accuracy and human reviewer quality across all markets and policy categories.",
        "Use this view to track top-level risk exposure and prioritise where intervention will have the highest impact.",
    )

    total = len(df)
    if total == 0:
        st.warning("No data matches current filters.")
        return

    appealed = df["appeal_submitted"].sum()
    reversed_ = df["is_appeal_reversed"].sum()
    rev_rate = reversed_ / appealed if appealed > 0 else 0

    cols = st.columns(4)
    kpi_card(cols[0], "Ads reviewed", f"{total}")
    kpi_card(cols[1], "LLM accuracy", f"{df['is_llm_correct'].mean():.1%}")
    kpi_card(cols[2], "Human accuracy", f"{df['is_human_correct'].mean():.1%}")
    kpi_card(cols[3], "Agreement rate", f"{df['is_human_ai_agreement'].mean():.1%}")

    cols2 = st.columns(4)
    kpi_card(cols2[0], "Over-rejection rate", f"{df['is_advertiser_over_rejection'].mean():.1%}")
    kpi_card(cols2[1], "Risk miss rate", f"{df['is_policy_risk_miss'].mean():.1%}")
    kpi_card(cols2[2], "High-risk approval misses", f"{df['is_high_risk_approval_miss'].sum()}")
    kpi_card(cols2[3], "Appeal reversal rate", f"{rev_rate:.1%}")

    st.markdown("---")

    ic_cols = st.columns(4)
    insight_card(
        ic_cols[0], "Critical risk",
        "154 high-risk ads approved when they should have been limited, escalated, or rejected. "
        "Financial Product Claim (33) and Political Content (29) account for the majority.",
        "critical",
    )
    insight_card(
        ic_cols[1], "Model weakness",
        "LLM accuracy drops below 60% for Financial Product Claim (57%) and Landing Page Issue (59%). "
        "The dominant error is under-rejection: the model approves ads it should flag.",
        "warning",
    )
    insight_card(
        ic_cols[2], "Operational gap",
        "20% of LLM decisions fall below the 0.60 confidence threshold. "
        "These cases have materially higher error rates and are not currently routed to mandatory human review.",
        "warning",
    )
    insight_card(
        ic_cols[3], "Immediate action",
        "Route all decisions below 0.60 confidence to human review. "
        "This single change addresses the highest-density source of risk misses without a model change.",
        "neutral",
    )

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        acc = df.groupby("policy_category")["is_llm_correct"].mean().sort_values()
        fig = plot_hbar(
            acc,
            "Regulated categories score lowest — LLM accuracy by policy category",
            "Accuracy",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        or_rates = df.groupby("policy_category")["is_advertiser_over_rejection"].mean()
        rm_rates = df.groupby("policy_category")["is_policy_risk_miss"].mean()
        fig = plot_diverging(
            or_rates, rm_rates, list(or_rates.index),
            "Under-rejection dominates regulated categories",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    what_this_means(
        "The two highest-exposure categories — Financial Product Claim and Landing Page Issue — show the largest "
        "risk miss bars. Over-rejection is relatively contained, meaning the primary failure mode is ads passing "
        "through when they should not, not the reverse."
    )

    col_c, col_d = st.columns(2)

    with col_c:
        fig = plot_histogram(
            df["llm_confidence_score"],
            "1 in 5 decisions falls below the 0.60 confidence threshold",
            "LLM Confidence Score",
            vline=0.60,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        acc_market = df.groupby("market")["is_llm_correct"].mean().sort_values()
        fig = plot_hbar(
            acc_market,
            "Non-English markets trail US and UK — LLM accuracy by market",
            "Accuracy",
            color=_GREEN,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ------------------------------------------------------------------
# Section 2: Policy Category Analysis
# ------------------------------------------------------------------

def render_policy_analysis(df: pd.DataFrame):
    section_head(
        "Regulated categories drive most model risk",
        "LLM errors, human disagreement, and appeal reversals by policy category.",
        "Categories with high risk miss rates and low agreement are the first candidates for policy clarification and model retraining.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    policy_metrics = (
        df.groupby("policy_category")
        .agg(
            total_cases=("ad_id", "count"),
            llm_accuracy=("is_llm_correct", "mean"),
            human_accuracy=("is_human_correct", "mean"),
            agreement_rate=("is_human_ai_agreement", "mean"),
            over_rejection_rate=("is_advertiser_over_rejection", "mean"),
            risk_miss_rate=("is_policy_risk_miss", "mean"),
            high_risk_misses=("is_high_risk_approval_miss", "sum"),
            avg_llm_conf=("llm_confidence_score", "mean"),
        )
        .reset_index()
        .sort_values("llm_accuracy")
    )

    display = policy_metrics.copy()
    for col in ["llm_accuracy", "human_accuracy", "agreement_rate",
                "over_rejection_rate", "risk_miss_rate", "avg_llm_conf"]:
        display[col] = display[col].map(lambda x: f"{x:.1%}")

    st.dataframe(display, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        agr = df.groupby("policy_category")["is_human_ai_agreement"].mean().sort_values()
        fig = plot_hbar(
            agr,
            "Lowest agreement in Political Content and Financial Product Claim",
            "Agreement Rate",
            color=_TEAL,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        appealed = df[df["appeal_submitted"]]
        if len(appealed) > 0:
            rev = (
                appealed.groupby("policy_category")["is_appeal_reversed"]
                .mean()
                .sort_values(ascending=False)
            )
            fig = plot_hbar(
                rev,
                "High reversal rate confirms over-rejection — appeals by category",
                "Reversal Rate",
                color=_AMBER,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No appeals in filtered data.")

    what_this_means(
        "Categories with high reversal rates had decisions that were too strict relative to the golden label. "
        "High agreement rates paired with high error rates indicate the model and reviewer are both wrong in the same direction — "
        "a policy ambiguity problem, not a model problem alone."
    )


# ------------------------------------------------------------------
# Section 3: Market and Language Analysis
# ------------------------------------------------------------------

def render_market_analysis(df: pd.DataFrame):
    section_head(
        "Non-English markets have no consistent policy baseline",
        "Markets and languages with elevated disagreement or local calibration needs.",
        "BR, IT, DE, and ES show higher disagreement rates than US and UK, consistent with local regulatory context not reflected in current model training.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    market_metrics = (
        df.groupby(["market", "language"])
        .agg(
            total_cases=("ad_id", "count"),
            llm_accuracy=("is_llm_correct", "mean"),
            human_accuracy=("is_human_correct", "mean"),
            disagreement_rate=("is_human_ai_agreement", lambda x: 1 - x.mean()),
            over_rejection_rate=("is_advertiser_over_rejection", "mean"),
            risk_miss_rate=("is_policy_risk_miss", "mean"),
            avg_review_time=("review_time_seconds", "mean"),
        )
        .reset_index()
        .sort_values("disagreement_rate", ascending=False)
    )

    display = market_metrics.copy()
    for col in ["llm_accuracy", "human_accuracy", "disagreement_rate",
                "over_rejection_rate", "risk_miss_rate"]:
        display[col] = display[col].map(lambda x: f"{x:.1%}")
    display["avg_review_time"] = display["avg_review_time"].map(lambda x: f"{x:.0f}s")

    st.dataframe(display, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        market_acc = df.groupby("market")["is_llm_correct"].mean().sort_values()
        fig = plot_hbar(
            market_acc,
            "BR and IT trail the US and UK baseline — LLM accuracy by market",
            "Accuracy",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        lang_dis = (
            df.groupby("language")["is_human_ai_agreement"]
            .agg(lambda x: 1 - x.mean())
            .sort_values(ascending=False)
        )
        fig = plot_hbar(
            lang_dis,
            "Non-English languages show highest human-AI disagreement",
            "Disagreement Rate",
            color=_RED,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    what_this_means(
        "Higher disagreement in non-English markets reflects different local regulatory standards that neither "
        "the LLM training data nor the current BPO reviewer guidelines adequately cover. "
        "Market-specific policy supplements are needed before model updates alone can close these gaps."
    )


# ------------------------------------------------------------------
# Section 4: BPO Calibration Analysis
# ------------------------------------------------------------------

def render_bpo_analysis(df: pd.DataFrame):
    section_head(
        "New reviewers fail at more than twice the rate of experienced ones",
        "Reviewer teams and tenure groups that diverge most from golden labels.",
        "The 13.6 pp gap between new and experienced reviewers is concentrated in the same regulated categories where the LLM also struggles.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        team_acc = df.groupby("bpo_team")["is_human_correct"].mean().sort_values()
        fig = plot_hbar(
            team_acc,
            "BPO_D trails BPO_B by 8.9 pp — human accuracy by team",
            "Accuracy",
            color=_GREEN,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        tenure_err = (
            df.groupby("reviewer_tenure")["is_human_correct"]
            .agg(lambda x: 1 - x.mean())
            .reindex(["new", "intermediate", "experienced"])
        )
        fig = plot_vbar(
            tenure_err,
            "Error rate drops sharply with tenure — new vs experienced reviewers",
            "Error Rate",
            colors=[_RED, _AMBER, _GREEN],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    what_this_means(
        "The 8.9 pp team spread is not explained by category mix alone. BPO_D handles a similar category distribution "
        "to higher-performing teams, pointing to calibration and training differences. "
        "Monthly calibration sessions using reversed appeals and golden label disagreements would narrow this gap."
    )

    st.markdown("**Human accuracy by BPO team and reviewer tenure**")
    pivot = (
        df.groupby(["bpo_team", "reviewer_tenure"])["is_human_correct"]
        .mean()
        .unstack(fill_value=0)
    )
    col_order = [c for c in ["new", "intermediate", "experienced"] if c in pivot.columns]
    pivot = pivot[col_order]
    fig = plot_heatmap(pivot, "Regulated categories expose the largest accuracy gaps by tenure")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    new_errors = (
        df[df["reviewer_tenure"] == "new"]
        .groupby("policy_category")["is_human_correct"]
        .agg(lambda x: 1 - x.mean())
        .sort_values(ascending=False)
    )
    fig = plot_hbar(
        new_errors,
        "Financial Product Claim and Health Claim have the highest new reviewer error rates",
        "Error Rate",
        color=_RED,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ------------------------------------------------------------------
# Section 5: Human vs LLM Agreement
# ------------------------------------------------------------------

def render_agreement_analysis(df: pd.DataFrame):
    section_head(
        "Human vs LLM Agreement",
        "Where reviewers and the model agree or diverge, and how LLM confidence correlates with error rate.",
        "Cases where both are wrong in different directions flag policy ambiguity — neither training nor calibration sessions will fix them without policy changes first.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        agr_risk = (
            df.groupby("risk_level")["is_human_ai_agreement"]
            .mean()
            .reindex(["low", "medium", "high"])
        )
        fig = plot_vbar(
            agr_risk,
            "Agreement drops at high risk — human-AI agreement by risk level",
            "Agreement Rate",
            colors=[_GREEN, _AMBER, _RED],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        conf_groups = df.copy()
        conf_groups["confidence_tier"] = pd.cut(
            conf_groups["llm_confidence_score"],
            bins=[0, 0.60, 0.75, 1.0],
            labels=["Low (<0.60)", "Medium (0.60-0.75)", "High (>0.75)"],
        )
        err_by_conf = (
            conf_groups.groupby("confidence_tier", observed=True)["is_llm_correct"]
            .agg(lambda x: 1 - x.mean())
        )
        fig = plot_vbar(
            err_by_conf,
            "Low-confidence decisions drive a disproportionate share of errors",
            "LLM Error Rate",
            colors=[_RED, _AMBER, _GREEN],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("**LLM label vs golden label — diagonal = correct decisions**")
    confusion = (
        df.groupby(["golden_label", "llm_label"])
        .size()
        .unstack(fill_value=0)
    )
    label_order = ["approved", "approved_limited", "escalated", "rejected"]
    confusion = confusion.reindex(
        index=[l for l in label_order if l in confusion.index],
        columns=[l for l in label_order if l in confusion.columns],
        fill_value=0,
    )
    st.dataframe(
        confusion.style.background_gradient(cmap="Blues"),
        use_container_width=True,
    )
    st.caption("Rows = Golden label. Columns = LLM label.")


# ------------------------------------------------------------------
# Section 6: Appeal Reversal Analysis
# ------------------------------------------------------------------

def render_appeal_analysis(df: pd.DataFrame):
    section_head(
        "Appeal Reversal Analysis",
        "Appeal submission and reversal rates by policy category, advertiser tier, and BPO team.",
        "Reversal rate is the most direct signal of over-rejection — a reversed appeal is an original decision that was provably wrong.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    appealed = df[df["appeal_submitted"]].copy()
    if len(appealed) == 0:
        st.info("No appeals in filtered data.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        appeal_rate = (
            df.groupby("policy_category")["appeal_submitted"]
            .mean()
            .sort_values(ascending=False)
        )
        fig = plot_hbar(
            appeal_rate,
            "Rejected and limited ads drive most appeal submissions",
            "Appeal Rate",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        rev_rate = (
            appealed.groupby("policy_category")["is_appeal_reversed"]
            .mean()
            .sort_values(ascending=False)
        )
        fig = plot_hbar(
            rev_rate,
            "High reversal rate signals over-rejection — reversals by policy category",
            "Reversal Rate",
            color=_AMBER,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    col_c, col_d = st.columns(2)

    with col_c:
        appeal_tier = (
            df.groupby("advertiser_tier")["appeal_submitted"]
            .mean()
            .sort_values(ascending=False)
        )
        fig = plot_hbar(
            appeal_tier,
            "Enterprise advertisers appeal most — and succeed most",
            "Appeal Rate",
            color=_TEAL,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        bpo_rev = (
            appealed.groupby("bpo_team")["is_appeal_reversed"]
            .mean()
            .sort_values(ascending=False)
        )
        fig = plot_hbar(
            bpo_rev,
            "BPO teams with high reversal rates are the calibration priority",
            "Reversal Rate",
            color=_RED,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ------------------------------------------------------------------
# Section 7: Model Feedback Examples
# ------------------------------------------------------------------

def render_feedback_examples(df: pd.DataFrame):
    section_head(
        "Model Feedback Examples",
        "High-value cases for model retraining, policy clarification, or BPO calibration.",
        "High-confidence wrong decisions have the lowest annotation cost and the highest training signal — extract these monthly.",
    )

    if len(df) == 0:
        st.warning("No data matches current filters.")
        return

    mask = (
        (~df["is_llm_correct"])
        & (df["risk_level"].isin(["medium", "high"]))
        & (
            (df["llm_confidence_score"] > 0.72)
            | df["is_high_risk_approval_miss"]
            | df["is_appeal_reversed"]
            | df["is_policy_ambiguous"]
        )
    )
    candidates = df[mask].copy()

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        cats = ["All"] + sorted(candidates["policy_category"].unique().tolist())
        sel_cat = st.selectbox("Filter: Policy Category", cats, key="fb_cat")
    with col_f2:
        err_types = ["All"] + sorted(candidates["error_type"].unique().tolist())
        sel_err = st.selectbox("Filter: Error Type", err_types, key="fb_err")
    with col_f3:
        risks = ["All"] + sorted(candidates["risk_level"].unique().tolist())
        sel_risk = st.selectbox("Filter: Risk Level", risks, key="fb_risk")
    with col_f4:
        appeal_results = ["All"] + sorted(candidates["appeal_result"].unique().tolist())
        sel_appeal = st.selectbox("Filter: Appeal Result", appeal_results, key="fb_appeal")

    if sel_cat != "All":
        candidates = candidates[candidates["policy_category"] == sel_cat]
    if sel_err != "All":
        candidates = candidates[candidates["error_type"] == sel_err]
    if sel_risk != "All":
        candidates = candidates[candidates["risk_level"] == sel_risk]
    if sel_appeal != "All":
        candidates = candidates[candidates["appeal_result"] == sel_appeal]

    display_cols = [
        "ad_id", "ad_text", "policy_category", "risk_level", "market",
        "golden_label", "llm_label", "llm_confidence_score",
        "error_type", "appeal_result",
    ]
    st.markdown(f"{len(candidates)} examples match selected filters.")
    st.dataframe(
        candidates[display_cols].head(100).reset_index(drop=True),
        use_container_width=True,
    )


# ------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------

def main():
    st.markdown(
        '<h1 style="font-size:1.35rem;font-weight:700;color:#F5F5F5;'
        'letter-spacing:normal;word-spacing:normal;margin-bottom:0.15rem;">'
        "AI Ad Review Quality Framework</h1>"
        '<p style="color:#A6ADBB;font-size:0.85rem;letter-spacing:normal;'
        'margin-top:0;margin-bottom:0.75rem;">'
        "LLM pre-screening accuracy, human reviewer quality, policy gaps, and appeal reversals"
        " — 5000 cases, Jan–Dec 2024."
        "</p>",
        unsafe_allow_html=True,
    )

    df = load_main_data()

    if df is None:
        st.error(
            "Enriched data not found. Please run the pipeline first:\n\n"
            "```\n"
            "python src/generate_dataset.py\n"
            "python src/prepare_data.py\n"
            "python src/evaluate_quality.py\n"
            "```"
        )
        return

    fdf = render_sidebar(df)

    sections = [
        "Executive Overview",
        "Policy Category Analysis",
        "Market and Language Analysis",
        "BPO Calibration Analysis",
        "Human vs LLM Agreement",
        "Appeal Reversal Analysis",
        "Model Feedback Examples",
    ]
    section = st.selectbox("Navigate to section", sections)

    st.markdown("---")

    if section == "Executive Overview":
        render_executive_overview(fdf)
    elif section == "Policy Category Analysis":
        render_policy_analysis(fdf)
    elif section == "Market and Language Analysis":
        render_market_analysis(fdf)
    elif section == "BPO Calibration Analysis":
        render_bpo_analysis(fdf)
    elif section == "Human vs LLM Agreement":
        render_agreement_analysis(fdf)
    elif section == "Appeal Reversal Analysis":
        render_appeal_analysis(fdf)
    elif section == "Model Feedback Examples":
        render_feedback_examples(fdf)


if __name__ == "__main__":
    main()
