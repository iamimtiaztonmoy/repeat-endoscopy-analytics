from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1]
deps=R.parent/'repeat_endoscopy_analysis/dependencies'
if deps.exists():sys.path.insert(0,str(deps))
import pandas as pd,numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
summ=[];models=[]
for ds in ['Colonoscopy','EGD']:
 d=pd.read_csv(R/f'data/extended_{ds}_analysis.csv');d=d[d.calendar730].copy()
 for scenario,mask in [('Primary broad model',pd.Series(True,index=d.index)),('Exclude index IBD codes',~d.ibd),('Known index diagnoses only',d.diagnosis_available)]:
  m=d[mask].copy();n=len(m);e=int(m.repeat730.sum());lo,hi=proportion_confint(e,n,method='wilson')
  summ.append(dict(cohort=ds,scenario=scenario,n=n,events=e,proportion=e/n,ci_low=lo,ci_high=hi,excluded=len(d)-n))
  syms=['abdominal_pain','constipation'] if ds=='Colonoscopy' else ['abdominal_pain','heartburn','dysphagia']
  m=m[m.GenderCode.isin(['F','M'])].copy();m['female']=m.GenderCode.eq('F').astype(int);m['era']=pd.cut(m.index_year,[1999,2011,2015,2023],labels=['2000_2011','2012_2015','2016_plus']);m['y']=m.repeat730.astype(int);m['unknown_dx']=(~m.diagnosis_available).astype(int)
  for v in syms:m[v]=m[v].astype(int)
  terms=['female','era']+syms+(['unknown_dx'] if m.unknown_dx.nunique()>1 else [])
  fit=smf.glm('y ~ '+' + '.join(terms),data=m,family=sm.families.Poisson()).fit(cov_type='HC0');ci=fit.conf_int()
  assert fit.converged
  if scenario=='Primary broad model':
   reference=pd.read_csv(R/'tables/Exploratory associations.csv');reference=reference[reference.dataset.eq(ds)].set_index('term')
   for term,row in reference.iterrows():assert abs(float(np.exp(fit.params[term]))-row.adjusted_recorded_probability_ratio)<1e-9
  for t in fit.params.index:
   if t=='Intercept':continue
   models.append(dict(cohort=ds,scenario=scenario,term=t,ratio=float(np.exp(fit.params[t])),ci_low=float(np.exp(ci.loc[t,0])),ci_high=float(np.exp(ci.loc[t,1])),p_value=float(fit.pvalues[t]),n=len(m),events=int(m.y.sum())))
  m[['study_id','female','era','y']+syms+(['unknown_dx'] if m.unknown_dx.nunique()>1 else [])].to_csv(R/'data'/f'robustness_{ds}_{scenario.replace(" ","_")}.csv',index=False)
pd.DataFrame(summ).to_csv(R/'tables/robustness_proportions.csv',index=False)
pd.DataFrame(models).to_csv(R/'tables/robustness_associations.csv',index=False)
print(pd.DataFrame(summ).to_string(index=False))
