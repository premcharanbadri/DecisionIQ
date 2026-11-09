# DecisionIQ — Product strategy and hypothesis-driven development brief

**Audience:** senior business analysts, growth product managers, small-business-card marketers, and strategy consultants. **Data:** entirely synthetic. **Product stage:** local MVP, not a production bank product.

## Customer problem / value proposition

A strategy analyst must often move between a funnel dashboard, separate Python experiments, a financial workbook and PowerPoint recommendations. This creates switching costs, inconsistent assumptions, and unsupported numeric claims. DecisionIQ centralizes the *question → evidence → decision* workflow, but it does not replace independent judgment.

**Primary hypothesis:** allowing an analyst to ask strategic questions and receive reproducible calculations alongside visible uncertainty will reduce analysis time **without making recommendations worse**.

**Alternative hypothesis:** a simple dashboard with fixed filters provides the same value at lower maintenance and compute cost. The product should be benchmarked against that baseline—not only against manual spreadsheets.

## Job-to-be-done

"When I need to decide which small-business acquisition offer to test, I want to compare segment response, financial economics and uncertainty using the same underlying assumptions, so I can defend my recommendation to Product, Finance, Risk and Marketing."

## Must/should/could prioritization

- **Must:** five validated tools, source identifiers, synthetic-only demo, financial assumptions, error states, repeatable output, private key handling.
- **Should:** authenticated frontier reasoning, exportable recommendation memo, tool-call provenance, per-user billing controls, human evaluation dashboard.
- **Could:** exact MILP optimization benchmark at larger scale, connected scenario workspace, data uploads, dashboard integration.
- **Won't in MVP:** real applicant data, automated underwriting/credit limits/APRs, live campaigns, unsolicited outreach, claim of measured revenue benefit.

## Decision rubric

For every recommendation, require:
1. Desired economic outcome and guardrail.
2. Observed data and cohort definition.
3. Hypothesis and alternative explanation.
4. Tools used and versioned assumptions.
5. Uncertainty, sensitivity and irreversible consequences.
6. Comparison with a simpler or lower-cost baseline.
7. Go / pilot / pause recommendation and measurement plan.

## Experiment to prove value of the copilot

Randomize 8–12 participating analysts across counterbalanced case scenarios. Compare traditional CardGrowth dashboards/workbook alone against DecisionIQ. Blinded reviewers rate correctness, tradeoff completeness, calibration of uncertainty, and financial defensibility. Record time and compute cost. Treat the project as unsuccessful if it improves speed but decreases recommendation quality.

## North-star and guardrail KPIs

North-star: **Verified quality-adjusted strategy analyses completed per analyst hour**.

Guardrails: 100% deterministic numeric parity on approved test cases; zero unsupported material numeric assertions on critical evals; analyst quality score at least non-inferior; cost per strategy task within budget; zero unauthorized customer-data transfer; traceability for every recommendation.

These are desired metrics, **not results measured in deployment**.

## Why this is the right next project for a Senior Business Analyst

It demonstrates user discovery (real workflow hypothesis), option assessment (rule-based vs frontier), financial model design, product requirements, applied ML/experiments, risk governance, cross-functional deployment planning, and decision-influencing communication. It is more credible than claiming a general-purpose autonomous financial advisor.
