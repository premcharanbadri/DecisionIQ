"""Five read-only, reproducible decision tools. All prospect data is synthetic.

Financial values are scenario outputs, not real profits, causal benefits, or advice
about lending decisions. The frontier LLM never performs the numerical math.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.core import ARMS, CONTACT_COST, margins, optimize
from src.experiment import approximate_sample_per_arm, two_proportions
from src.pricing import fee_scenario

ROOT = Path(__file__).resolve().parents[1]
SEGMENTS = ["All", "Cash-flow constrained", "Growth-focused", "Spend-intensive"]
OFFERS = ["All", *ARMS]
DISCLAIMER = "SYNTHETIC PORTFOLIO SIMULATION. No real customers, bank revenue, causal effect, or operational deployment. Not for underwriting or personalized credit decisions."

class DiagnoseArgs(BaseModel):
    segment: Literal["All", "Cash-flow constrained", "Growth-focused", "Spend-intensive"] = "All"

class SegmentArgs(BaseModel):
    offer: Literal["All", "Standard", "Cash-flow experience", "Rewards experience"] = "All"

class PricingArgs(BaseModel):
    annual_fee: float = Field(default=0, ge=0, le=300, description="Hypothetical uniform yearly card fee in USD; NOT individualized APR")
    conversion_penalty_per_100: float = Field(default=.012, ge=0, le=.1, description="Assumed absolute conversion-probability drop per $100 fee, not empirically estimated")
    rewards_rate: float = Field(default=.0012, ge=0, le=.02, description="Extra rewards expense per $1 in annual spending on reward offer")

class OptimizeArgs(BaseModel):
    budget: float = Field(default=2600, ge=0, le=20000, description="USD promotional contact budget for entire simulated holdout")
    max_contacts: int = Field(default=2600, ge=0, le=8000)
    segment: Literal["All", "Cash-flow constrained", "Growth-focused", "Spend-intensive"] = "All"

class ExperimentArgs(BaseModel):
    offer: Literal["Cash-flow experience", "Rewards experience"] = "Cash-flow experience"

SCHEMAS = {
    "diagnose_growth": DiagnoseArgs,
    "analyze_segments": SegmentArgs,
    "simulate_pricing": PricingArgs,
    "optimize_campaign": OptimizeArgs,
    "evaluate_experiment": ExperimentArgs,
}
DESCRIPTIONS = {
    "diagnose_growth": "Diagnose simulated applications, approval, activation and funnel bottlenecks by randomized offer; filter by a prospect segment.",
    "analyze_segments": "Compare simulated acquisition conversion and model-estimated offer response across small-business customer segments.",
    "simulate_pricing": "Evaluate an explicitly hypothetical, uniform annual card fee and rewards scenario using modeled first-year value; never make individual APR decisions.",
    "optimize_campaign": "Allocate synthetic marketing contacts between offers subject to a budget and contact cap; returns modeled economic value, not realized uplift.",
    "evaluate_experiment": "Evaluate randomized simulated application conversion for one offer versus Standard, with uncertainty and multiple-test caution.",
}

@lru_cache(maxsize=1)
def data():
    df = pd.read_csv(ROOT / "artifacts" / "holdout_offer_scoring.csv")
    with (ROOT / "artifacts" / "metrics.json").open() as f:
        metrics = json.load(f)
    prob = df[[f"estimate_application_arm{i}" for i in range(3)]].to_numpy(dtype=float)
    return df, metrics, prob


def _round(x, decimals=2):
    return round(float(x), decimals)


def diagnose_growth(segment="All"):
    df, _, _ = data()
    d = df if segment == "All" else df[df.segment == segment]
    records=[]
    for name in ARMS:
        g=d[d.assigned_offer == name]
        n=len(g); applications=int(g.applied.sum()); approvals=int(g.approved.sum()); active=int(g.activated.sum())
        records.append({"offer": name, "prospects":n, "applications":applications,
                        "application_conversion_pct":_round(100*applications/n),
                        "approval_given_application_pct":_round(100*approvals/max(1,applications)),
                        "activation_given_approval_pct":_round(100*active/max(1,approvals)),
                        "activated_accounts": active})
    bottleneck = min([("application",sum(x['applications'] for x in records)/max(1,sum(x['prospects'] for x in records))),
                      ("approval",sum(d.approved)/max(1,sum(d.applied))),
                      ("activation",sum(d.activated)/max(1,sum(d.approved)))],key=lambda x:x[1])[0]
    return {"tool":"diagnose_growth","segment":segment,"population":"Nov–Dec 2025 synthetic randomized test",
            "funnel_by_offer":records,"largest_percent_drop_step":bottleneck,
            "reasoning":"A low stage rate identifies where to investigate, not the causal reason for drop-off.",
            "next_analysis":"Test whether segment mix, channel, or product experience explains the difference; verify business-level net contribution.",
            "evidence":DISCLAIMER}


def analyze_segments(offer="All"):
    df, _, prob = data()
    d=df if offer=="All" else df[df.assigned_offer==offer]
    out=[]
    for name,part in d.groupby('segment',sort=True):
        idx=part.index.to_numpy(dtype=int)
        # Prediction differences are model estimates, NOT causal treatment effects.
        expected=(prob[idx,1:]-prob[idx,0][:,None]).mean(axis=0)
        out.append({"segment":name,"prospects":len(part),"observed_application_conversion_pct":_round(100*part.applied.mean()),
                    "model_estimated_cashflow_minus_standard_pp":_round(100*expected[0],3),
                    "model_estimated_rewards_minus_standard_pp":_round(100*expected[1],3),
                    "avg_synthetic_annual_spend_usd":_round(part.annual_spend.mean(),0)})
    return {"tool":"analyze_segments", "offer_filter":offer,"segments":out,
            "interpretation":"Predictive differences are not validated individual causal uplift. Segment response may be noisy.","evidence":DISCLAIMER}


def simulate_pricing(annual_fee=0,conversion_penalty_per_100=.012,rewards_rate=.0012):
    df,_,p=data()
    selected=df.recommended_marketing_arm.to_numpy(int)
    actual=fee_scenario(df,p,annual_fee=float(annual_fee),conversion_penalty_per_100=float(conversion_penalty_per_100),rewards_rate=float(rewards_rate))
    base=fee_scenario(df,p,annual_fee=0,conversion_penalty_per_100=float(conversion_penalty_per_100),rewards_rate=.0012)
    idx=np.arange(len(df))
    return {"tool":"simulate_pricing","prospects":len(df),
            "assumptions":{"uniform_annual_fee_usd":annual_fee,"absolute_conversion_penalty_per_100_fee":conversion_penalty_per_100,
                           "extra_rewards_cost_per_spend_dollar":rewards_rate,"strategy":"fixed previously selected marketing policy"},
            "scenario_expected_contribution_usd":_round(actual[idx,selected].sum()),
            "same_policy_base_case_usd":_round(base[idx,selected].sum()),
            "scenario_difference_usd":_round((actual[idx,selected]-base[idx,selected]).sum()),
            "counterfactual_standard_usd":_round(actual[:,0].sum()),
            "status":"HYPOTHETICAL elasticity assumptions; not a measured pricing experiment or credit APR recommendation.","evidence":DISCLAIMER}


def optimize_campaign(budget=2600,max_contacts=2600,segment="All"):
    df,metrics,pr=data()
    if segment!="All":
        filt=df.segment==segment
        d=df.loc[filt].reset_index(drop=True)
        p=pr[filt.to_numpy()]
    else:
        d=df.reset_index(drop=True);p=pr
    selected, details=optimize(d,p,budget=float(budget),max_contacts=int(max_contacts))
    n=len(d)
    rates={}
    for a,offer in enumerate(ARMS): rates[offer]=int((selected==a).sum())
    marginal_cost_per_selected=float(CONTACT_COST[selected].sum())
    return {"tool":"optimize_campaign","population":n,"segment":segment,
            "constraints":{"max_contacts":max_contacts,"budget_usd":budget},
            "policy":{"assignments":rates,"contacts":details['contacts'],"spend_usd":_round(marginal_cost_per_selected),
                      "model_predicted_incremental_first_year_contribution_usd":details['estimated_incremental'],
                      "estimated_incremental_per_prospect_usd":_round(details['estimated_incremental']/max(1,n))},
            "method":"Greedy constrained optimization on pretrained synthetic response-model scores; not guaranteed globally optimal.",
            "uncertainty":"Model-predicted value overestimated simulator-oracle value in the original CardGrowth evaluation. Do not treat as realized impact.",
            "benchmark_on_original_holdout":{"predicted_2600_contacts_usd":metrics['results']['test'][metrics['selected']]['policy']['estimated_incremental'],
                                            "randomized_off_policy_ci_usd": [metrics['results']['test'][metrics['selected']]['off_policy_ipw']['ci95_low'],metrics['results']['test'][metrics['selected']]['off_policy_ipw']['ci95_high']]},
            "evidence": DISCLAIMER}


def evaluate_experiment(offer="Cash-flow experience"):
    df,_,_=data()
    d0=df[df.assigned_offer=="Standard"]
    d1=df[df.assigned_offer==offer]
    calc=two_proportions(int(d0.applied.sum()),len(d0),int(d1.applied.sum()),len(d1))
    return {"tool":"evaluate_experiment","comparison":f"{offer} versus Standard",
            "counts":{"control_n":len(d0),"control_applications":int(d0.applied.sum()),
                      "treatment_n":len(d1),"treatment_applications":int(d1.applied.sum())},
            "statistics":calc,
            "two_offer_bonferroni_significant_at_fwer_5pct":bool(calc['p_value_unadjusted']<.025),
            "exploratory_power_n_per_arm_for_2pp_abs_lift":approximate_sample_per_arm(absolute_effect=.02),
            "decision":"Conversion significance alone does not demonstrate positive contribution, customer value, or credit performance. Run adequately powered economic validation.",
            "evidence":DISCLAIMER}

TOOL_HANDLERS={
    "diagnose_growth":diagnose_growth,"analyze_segments":analyze_segments,
    "simulate_pricing":simulate_pricing,"optimize_campaign":optimize_campaign,
    "evaluate_experiment":evaluate_experiment
}

def execute(name:str, params:dict|None=None):
    if name not in TOOL_HANDLERS: raise ValueError('Unrecognized tool')
    if params is None:params={}
    validated=SCHEMAS[name].model_validate(params)
    return TOOL_HANDLERS[name](**validated.model_dump())

def openai_tools():
    return [{"type":"function","name":name,"description":description,
             "parameters":model.model_json_schema(),"strict":False}
            for name,(description,model) in ((name,(DESCRIPTIONS[name],SCHEMAS[name])) for name in SCHEMAS)]
