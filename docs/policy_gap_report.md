# Policy Gap Report

Analysis of 5000 ad review cases across 10 policy categories and 8 markets. The patterns below affect both LLM and human reviewers, suggesting some issues originate from unclear policy guidelines rather than purely from model or reviewer error.

---

## Gap 1: Health Claim — Substantiation Thresholds Are Unclear

**Category**: Health Claim

**Evidence**:
- LLM accuracy is 65.1%, approximately 6 pp below the platform average of 71.1%
- Both LLM and human reviewers diverge from the golden label at elevated rates
- Policy ambiguity rate (both wrong in different directions) is among the highest for this category
- New reviewers show the highest error rate here

**Risk**: Inconsistent enforcement creates both over-rejection of legitimate wellness products and under-rejection of potentially misleading claims. FR, DE, and IT have elevated regulatory exposure.

**Recommendation**: Define explicit substantiation thresholds. Distinguish permissible lifestyle claims ("supports a balanced routine") from claims requiring clinical evidence ("clinically proven").

**Owner**: Policy Team + BPO Quality

---

## Gap 2: Financial Product Claim — Eligibility Disclosure Standards

**Category**: Financial Product Claim

**Evidence**:
- LLM accuracy among the lowest across all categories
- Policy risk miss rate is elevated — the model approves ads that should be limited or rejected
- Appeal reversal rate is above average

**Risk**: Financial ads misrepresenting eligibility, fees, or rates carry regulatory risk under consumer protection law in UK, FR, and DE.

**Recommendation**: Add explicit examples of acceptable and unacceptable disclosure language. Claim-level examples (e.g., "from X% APR" vs. "as low as X% APR subject to eligibility") help both model and reviewers calibrate.

**Owner**: Policy Team + Algorithm Team

---

## Gap 3: Political or Sensitive Content — Escalation Threshold Is Inconsistent

**Category**: Political or Sensitive Content

**Evidence**:
- Lowest human-AI agreement rate of any category
- Both over-rejection and risk misses occur at elevated rates — the LLM is uncertain rather than directionally biased
- Non-English markets (ES, IT, BR) show significantly higher disagreement

**Risk**: Inconsistent enforcement creates friction for legitimate civic platforms and risk misses for misleading or partisan content.

**Recommendation**: Define market-specific escalation criteria. The current policy does not account for local electoral law differences across FR, DE, ES, IT, BR, and MX. Default to escalation in non-English markets until local guidelines exist.

**Owner**: Policy Team (Global + Regional)

---

## Gap 4: Landing Page Issue — LLM Cannot Evaluate Landing Pages

**Category**: Landing Page Issue

**Evidence**:
- LLM accuracy of ~59%, second lowest across all categories (Financial Product Claim at 57% is the lowest overall)
- `landing_page_mismatch` errors are concentrated almost entirely here
- Human reviewers also show above-average error rates, suggesting a workflow gap

**Risk**: Ads with compliant copy but non-compliant landing pages can bypass screening. The LLM pre-screens ad text, not the full user journey.

**Recommendation**: Implement a dedicated landing page review step. For Landing Page Issue and Misleading Claim categories, human review should be the default rather than LLM-led.

**Owner**: Algorithm Team + Ad Operations + Policy Team

---

## Gap 5: Misleading Claim — No Consistent Standard

**Category**: Misleading Claim

**Evidence**:
- LLM accuracy below average with a roughly balanced split between over-rejection and risk miss
- Policy ambiguity rate is elevated — neither model nor human reviewers have a consistent interpretation
- Appeal reversal rate above average

**Risk**: Without a clear standard, enforcement will remain inconsistent. Advertisers face unpredictable decisions across markets and reviewer teams.

**Recommendation**: Define a claims hierarchy: (1) factually incorrect, (2) unverifiable superlative, (3) ambiguous relative claim, (4) compliant. Each level should have approved and rejected examples. Review quarterly.

**Owner**: Policy Team

---

## Gap 6: Non-English Markets Without Local Policy Calibration

**Markets**: BR, IT, MX, DE, ES

**Evidence**:
- Disagreement rates in BR and IT are significantly above the US/UK baseline
- `market_nuance_error` errors are concentrated in non-English markets
- Review time is higher in these markets, indicating reviewers spend more time on uncertain cases

**Risk**: Higher disagreement indicates neither the LLM nor human reviewers are consistently applying local policy context. Both over-rejection and risk misses are elevated.

**Recommendation**: Develop market-specific policy supplements for FR, DE, ES, IT, BR, and MX. Run calibration sessions for BPO teams assigned to these markets. Add market-tagged examples to the LLM training set.

**Owner**: Policy Team (Regional) + BPO Quality + Algorithm Team
