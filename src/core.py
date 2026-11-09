"""CardGrowth AI: all leads, outcomes, and revenue are synthetic.
Demo of randomized multi-arm acquisition, response uplift, and constrained allocation.
NEVER use this toy model for real credit or customer decisions.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

SEED=1926
ARMS=['Standard','Cash-flow experience','Rewards experience']
CONTACT_COST=np.array([0.,.70,1.10])
CASHFLOW_SERVICE_COST=18.
REWARD_RATE=.0012
FEATURES=['segment','channel','industry','firm_age_years','annual_revenue','annual_spend','expense_volatility','cashflow_need','digital_intent','prior_interest']
CATEGORICAL=['segment','channel','industry']
NUMERIC=[v for v in FEATURES if v not in CATEGORICAL]

def sigmoid(x):return 1/(1+np.exp(-np.clip(x,-30,30)))

def simulate(n_monthly=4000, seed=SEED):
    rng=np.random.default_rng(seed)
    n=12*n_monthly
    month=np.repeat(np.arange(1,13),n_monthly)
    seg=rng.choice(['Cash-flow constrained','Growth-focused','Spend-intensive'],n,p=[.38,.32,.30])
    channel=rng.choice(['Direct','Partner','Search'],n,p=[.35,.20,.45])
    industry=rng.choice(['Retail','Professional services','Construction','Hospitality','Other'],n,p=[.25,.26,.18,.16,.15])
    age=np.clip(rng.gamma(2.6,2.15,n),.3,28)
    rev=np.clip(rng.lognormal(np.log(270000),.73,n),30000,2500000)
    multiplier=np.where(seg=='Spend-intensive',.30,np.where(seg=='Growth-focused',.20,.13))
    spend=np.clip(rev*multiplier*rng.lognormal(0,.22,n),12000,300000)
    volatility=np.clip(rng.beta(2.1,4.4,n)*1.9,0,1)
    need=np.clip(rng.beta(2.0,2.5,n)+.23*(seg=='Cash-flow constrained'),0,1)
    intent=rng.beta(2.7,2.1,n)
    prior=rng.binomial(1,sigmoid(-1.5+1.9*intent))
    assigned=rng.integers(0,3,n)
    base_logit=-2.75+.68*intent+.34*prior+.21*(channel=='Direct')+.25*(seg=='Growth-focused')-.15*volatility+.13*np.log1p(rev/250000)
    p0=sigmoid(base_logit)
    uplift_cash=.004+.036*(seg=='Cash-flow constrained')+.005*(seg=='Growth-focused')+.008*need+.004*(channel=='Direct')
    uplift_rewards=.004+.040*(seg=='Spend-intensive')+.007*(seg=='Growth-focused')+.007*(spend>110000)+.003*intent
    p1=np.clip(p0+uplift_cash,.001,.65)
    p2=np.clip(p0+uplift_rewards,.001,.65)
    pmat=np.column_stack([p0,p1,p2])
    applied=rng.binomial(1,pmat[np.arange(n),assigned])
    approval_p=np.clip(.78-.17*volatility-.08*(age<2)-.05*(rev<100000),.38,.88)
    active_p=np.clip(.78+.1*intent-.05*volatility,.55,.94)
    approved=applied*rng.binomial(1,approval_p)
    activated=approved*rng.binomial(1,active_p)
    # First-year net yield per active card: spend*net interchange yield less servicing and risk proxy.
    base_margin=np.clip(.0082*spend-72-45*volatility,55,1650)
    margins=np.column_stack([base_margin,base_margin-CASHFLOW_SERVICE_COST,base_margin-REWARD_RATE*spend])
    contribution=activated*margins[np.arange(n),assigned]-CONTACT_COST[assigned]
    return pd.DataFrame({'lead_id':np.arange(n)+1,'month':[f'2025-{x:02d}' for x in month],
          'month_id':month,'segment':seg,'channel':channel,'industry':industry,
          'firm_age_years':np.round(age,3),'annual_revenue':np.round(rev,2),'annual_spend':np.round(spend,2),
          'expense_volatility':np.round(volatility,5),'cashflow_need':np.round(need,5),
          'digital_intent':np.round(intent,5),'prior_interest':prior,
          'assigned_arm':assigned,'assigned_offer':[ARMS[a] for a in assigned],
          'assignment_propensity':1/3,'applied':applied,'approved':approved,'activated':activated,
          'approval_assumption':np.round(approval_p,6),'activation_assumption':np.round(active_p,6),
          'base_margin':np.round(base_margin,2),'observed_net_contribution':np.round(contribution,2),
          'oracle_p0':p0,'oracle_p1':p1,'oracle_p2':p2})

def splits(df):
    return (df[df.month_id<=8].copy(),df[df.month_id.between(9,10)].copy(),df[df.month_id>=11].copy())

def create_model(kind):
    if kind=='logistic':
        proc=ColumnTransformer([('numeric',StandardScaler(),NUMERIC),('categories',OneHotEncoder(handle_unknown='ignore'),CATEGORICAL)])
        est=LogisticRegression(max_iter=500,C=.65)
    elif kind=='boosting':
        proc=ColumnTransformer([('numeric','passthrough',NUMERIC),('categories',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CATEGORICAL)],sparse_threshold=0)
        est=HistGradientBoostingClassifier(max_iter=95,learning_rate=.065,max_leaf_nodes=11,min_samples_leaf=140,l2_regularization=7,random_state=SEED)
    else:raise ValueError(kind)
    return Pipeline([('preprocess',proc),('model',est)])

def fit_models(train,kind):
    out={}
    for a in range(3):
        part=train[train.assigned_arm==a]
        m=create_model(kind)
        m.fit(part[FEATURES],part.applied)
        out[a]=m
    return out

def predict(models,df):return np.column_stack([models[a].predict_proba(df[FEATURES])[:,1] for a in range(3)])

def margins(df,cashflow=CASHFLOW_SERVICE_COST,rewards=REWARD_RATE):
    m=df.base_margin.to_numpy(float)
    return np.column_stack([m,m-cashflow,m-rewards*df.annual_spend.to_numpy(float)])

def optimize(df,prob,budget=2600,max_contacts=2600,cost_mult=1.,cashflow=CASHFLOW_SERVICE_COST,rewards=REWARD_RATE):
    """Select per-lead offer maximizing estimated incremental first-year contribution.
    Greedy under cardinality and spending limits; exact binary integer model optional.
    """
    costs=CONTACT_COST*cost_mult
    success=(df.approval_assumption*df.activation_assumption).to_numpy()
    ev=prob*margins(df,cashflow,rewards)*success[:,None]-costs[None,:]
    diff=ev[:,1:]-ev[:,[0]]
    winner=1+np.argmax(diff,axis=1)
    gain=diff[np.arange(len(df)),winner-1]
    policy=np.zeros(len(df),dtype=np.int8)
    expense=0.; used=0
    for i in np.argsort(-gain,kind='stable'):
        a=winner[i]
        if gain[i]<=0 or used>=max_contacts:break
        if expense+costs[a]>budget:continue
        policy[i]=a;expense+=costs[a];used+=1
    return policy,{'contacts':used,'budget_spent':round(expense,2),
                   'estimated_incremental':round(float((ev[np.arange(len(df)),policy]-ev[:,0]).sum()),2),
                   'cashflow_selected':int((policy==1).sum()),'rewards_selected':int((policy==2).sum())}

def oracle_evaluation(df,policy,cost_mult=1.,cashflow=CASHFLOW_SERVICE_COST,rewards=REWARD_RATE):
    """Simulation diagnostic ONLY: inaccessible in real business data."""
    true_p=df[['oracle_p0','oracle_p1','oracle_p2']].to_numpy(float)
    success=(df.approval_assumption*df.activation_assumption).to_numpy()
    ev=true_p*margins(df,cashflow,rewards)*success[:,None]-cost_mult*CONTACT_COST[None,:]
    baseline=float(ev[:,0].sum()); chosen=float(ev[np.arange(len(df)),policy].sum())
    return {'baseline':round(baseline,2),'selected':round(chosen,2),'incremental':round(chosen-baseline,2)}

def ipw_evaluation(df,policy):
    """Horvitz-Thompson randomized off-policy estimate with normal-based CI.
    Exploratory: no cluster adjustment or variance reduction.
    """
    assigned=df.assigned_arm.to_numpy()
    reward=df.observed_net_contribution.to_numpy()
    influence=3*reward*((assigned==policy).astype(float)-(assigned==0).astype(float))
    est=float(influence.sum());se=float(influence.std(ddof=1)*np.sqrt(len(influence)))
    return {'estimate':round(est,2),'standard_error':round(se,2),'ci95_low':round(est-1.96*se,2),'ci95_high':round(est+1.96*se,2)}
