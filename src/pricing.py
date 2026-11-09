"""Product-level pricing sensitivities -- research scenarios, NOT real bank prices."""
import numpy as np
from src.core import margins,CONTACT_COST

def fee_scenario(df,model_prob,annual_fee=0,conversion_penalty_per_100=0.012,
                 cashflow_cost=18,rewards_rate=.0012):
    """Uniform annual-fee scenario; assumes demand declines by specified absolute points per $100 fee.
    No evidence the elasticity assumption is true. No individualized APR/credit pricing.
    """
    fee=float(annual_fee)
    p=np.clip(model_prob-fee/100*conversion_penalty_per_100,0,1)
    m=margins(df,cashflow_cost,rewards_rate)+fee
    success=(df.approval_assumption*df.activation_assumption).to_numpy()
    value=p*m*success[:,None]-CONTACT_COST[None,:]
    return value
