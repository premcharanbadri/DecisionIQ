"""Exact integer-programming benchmark for small acquisition batches.
Use a MILP to check regret of the fast greedy policy. Optional, not used in website.
"""
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix
from src.core import CONTACT_COST,margins

def exact_policy(df,pred,budget,max_contacts,time_limit_s=12):
    n=len(df)
    ap=(df.approval_assumption*df.activation_assumption).to_numpy()
    values=pred*margins(df)*ap[:,None]-CONTACT_COST[None,:]
    incremental=values[:,1:]-values[:,[0]]
    obj=-incremental.reshape(-1)
    # x_i1 + x_i2 <=1; total selected <= contacts; total contact cost <= budget
    rr=np.concatenate([np.repeat(np.arange(n),2),np.full(2*n,n),np.full(2*n,n+1)])
    cc=np.concatenate([np.arange(2*n),np.arange(2*n),np.arange(2*n)])
    vv=np.concatenate([np.ones(2*n),np.ones(2*n),np.tile(CONTACT_COST[1:],n)])
    A=coo_matrix((vv,(rr,cc)),shape=(n+2,2*n)).tocsr()
    lower=np.zeros(n+2); upper=np.concatenate([np.ones(n),[max_contacts,budget]])
    res=milp(c=obj,integrality=np.ones(2*n),bounds=Bounds(0,1),constraints=LinearConstraint(A,lower,upper),options={'time_limit':time_limit_s,'mip_rel_gap':.0001})
    if res.x is None:raise RuntimeError('MILP solver returned no feasible solution')
    x=res.x.reshape(n,2)
    policy=np.zeros(n,dtype=int)
    chosen=x.max(axis=1)>.5
    policy[chosen]=1+np.argmax(x[chosen],axis=1)
    gain=float(incremental[np.arange(n),np.maximum(policy-1,0)][policy>0].sum())
    return policy,{'objective':round(gain,2),'contacts':int(chosen.sum()),
         'budget_used':float(np.sum(CONTACT_COST[policy])),
         'optimal_certificate':res.status==0,'solver_status':int(res.status)}
