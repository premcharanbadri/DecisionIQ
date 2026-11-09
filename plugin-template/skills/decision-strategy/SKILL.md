---
name: decision-strategy
summary: Evaluate synthetic small-business card marketing and pricing strategies with reproducible analytical tools.
description: Use when users ask about CardGrowth synthetic customer segmentation, A/B experiments, hypothetical uniform annual fees, campaign budget allocation or marketing funnel diagnostics. Never use these tools for real credit underwriting or individual price decisions.
---

# DecisionIQ Strategy Workflow

1. Identify the business decision, objective, controlled variables and constraints.
2. Call the **DecisionIQ MCP tools** instead of inventing calculations or assuming model outputs are causal evidence.
3. For marketing performance, use `diagnose_growth_tool` and `analyze_segments_tool`.
4. For randomized conversion experiments, use `evaluate_experiment_tool` and explain effect size, interval, multiple comparison caution, and the difference between conversions and profit.
5. For unit economics, use `simulate_pricing_tool`; explicitly label annual-fee elasticity as an untested hypothetical assumption.
6. For allocation, use `optimize_campaign_tool`; report budget, contact cap, modeled benefit, assumptions, and the unconstrained evidence gap.
7. Deliver a recommendation with a competing alternative, missing evidence, quality/risk guardrails, and the next valid test.

All data are synthetic. No bank-client attribution, observed revenue impact, individual APR or credit-limit adjustments, or automated lending decisions. If asked to perform individual credit decisions, explain the tool's boundary and decline. Tools are read-only.
