"""Pre-registered randomized campaign experiment diagnostics (exploratory)."""
import numpy as np
from scipy.stats import norm

def two_proportions(y0,n0,y1,n1):
    p0=y0/n0;p1=y1/n1
    delta=p1-p0
    se=np.sqrt(p0*(1-p0)/n0+p1*(1-p1)/n1)
    z=delta/se if se else np.nan
    p=2*(1-norm.cdf(abs(z))) if se else None
    return {'control_conversion':round(p0,5),'test_conversion':round(p1,5),
      'absolute_percentage_point_lift':round(100*delta,3),
      'relative_lift_pct':round(100*delta/p0,2),
      'ci95_pp':[round(100*(delta-1.96*se),3),round(100*(delta+1.96*se),3)],
      'p_value_unadjusted':round(float(p),5),'caution':'Exploratory two-sided normal approximation; no multiple-comparison correction.'}

def approximate_sample_per_arm(baseline=.115,absolute_effect=.02,power=.8,alpha=.05):
    p0=baseline;p1=baseline+absolute_effect
    pa=(p0+p1)/2
    z1=norm.ppf(1-alpha/2);z2=norm.ppf(power)
    n=((z1*np.sqrt(2*pa*(1-pa))+z2*np.sqrt(p0*(1-p0)+p1*(1-p1)))**2)/(p1-p0)**2
    return int(np.ceil(n))
