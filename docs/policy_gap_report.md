# Policy Gap Report

Analysis of 5000 synthetic ad review cases across 10 policy categories and 8 markets.

The goal is to identify where quality issues come from: model weakness, reviewer calibration, unclear policy rules, or local market nuance.

---

## Gap 1: Health Claim

Health claims need clearer substantiation rules.

**What the data shows**

- AI accuracy is 65.1%, below the overall 71.1% benchmark.
- Both AI and human reviewers diverge from the golden label more often than expected.
- New reviewers struggle most in this category.
- Ambiguous cases are more frequent than in clearer policy areas.

**Risk**

Health claims sit in a sensitive space. Weak enforcement can let misleading claims through. Overly strict enforcement can block legitimate wellness products.

FR, DE, and IT carry higher regulatory sensitivity.

**Recommendation**

Define clearer substantiation thresholds.

Separate:

- soft lifestyle claims, such as “supports a balanced routine”
- evidence-based claims, such as “clinically proven”

Add approved and rejected examples for each level.

**Owner**

Policy Team + BPO Quality

---

## Gap 2: Financial Product Claim

Financial ads need stronger eligibility and disclosure standards.

**What the data shows**

- This is the weakest category for AI accuracy.
- Risk misses are elevated.
- The AI approves some ads that should be limited or rejected.
- Appeal reversals are above average.

**Risk**

Financial ads can misrepresent eligibility, fees, rates, or conditions. That creates regulatory exposure, especially in UK, FR, and DE.

**Recommendation**

Add clear examples of acceptable and unacceptable disclosure language.

Examples should cover:

- eligibility conditions
- rate claims
- fee disclosures
- limited-time offers
- misleading “guaranteed approval” language

**Owner**

Policy Team + Algorithm Team

---

## Gap 3: Political or Sensitive Content

Escalation rules are not consistent enough across markets.

**What the data shows**

- This category has the lowest Human-AI agreement.
- Both over-rejections and risk misses are elevated.
- Non-English markets show stronger disagreement patterns.

**Risk**

Weak escalation rules create two problems at once: legitimate civic content can be blocked, while risky political or sensitive content can pass.

**Recommendation**

Define market-specific escalation criteria.

Until local rules are stronger, sensitive content in non-English markets should default to escalation more often.

**Owner**

Global Policy + Regional Policy

---

## Gap 4: Landing Page Issue

The AI cannot reliably judge landing page risk from ad text alone.

**What the data shows**

- AI accuracy is around 59%, the second weakest category.
- Landing page mismatch errors are concentrated here.
- Human reviewers also show above-average error rates.

**Risk**

An ad can look compliant while the landing page contains the actual issue. If the model only reads ad text, it misses part of the user journey.

**Recommendation**

Add a dedicated landing page review step.

For Landing Page Issue and Misleading Claim, human review should be the default path when landing page context matters.

**Owner**

Algorithm Team + Ad Operations + Policy Team

---

## Gap 5: Misleading Claim

The policy needs a clearer standard for claim severity.

**What the data shows**

- AI accuracy is below average.
- Errors are split between over-rejection and risk misses.
- Ambiguity and appeal reversals are elevated.

**Risk**

Without a clear claim hierarchy, decisions become inconsistent across reviewers, teams, and markets.

**Recommendation**

Define a claim hierarchy:

1. factually incorrect
2. unverifiable superlative
3. ambiguous relative claim
4. compliant claim

Each level should include approved and rejected examples.

**Owner**

Policy Team

---

## Gap 6: Non-English Markets

Local policy calibration is not strong enough.

**Markets**

BR, IT, MX, DE, ES

**What the data shows**

- BR and IT show higher disagreement than US and UK.
- Market nuance errors are concentrated in non-English markets.
- Review time is higher, which suggests reviewers spend more time resolving uncertainty.

**Risk**

Generic policy guidance does not cover local nuance well enough. This creates both over-rejection and risk misses.

**Recommendation**

Create market-specific policy supplements for FR, DE, ES, IT, BR, and MX.

Add:

- local examples
- market-specific escalation rules
- BPO calibration sessions by market
- market-tagged examples for model feedback

**Owner**

Regional Policy + BPO Quality + Algorithm Team
