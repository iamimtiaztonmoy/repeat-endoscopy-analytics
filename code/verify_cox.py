from pathlib import Path
import sys,json
PACKAGE=Path(__file__).resolve().parents[1]
R=PACKAGE/'restricted/cox'
deps=PACKAGE.parent/'repeat_endoscopy_analysis/dependencies'
if deps.exists():sys.path.insert(0,str(deps))
import pandas as pd,numpy as np
from statsmodels.duration.hazard_regression import PHReg
h=pd.read_csv(R/'Adjusted Cox results.csv');checks=[]
for ds in ['Colonoscopy','EGD']:
 for scenario in ['Administrative','Last recorded contact']:
  d=pd.read_csv(R/f'{ds} {scenario}.csv')
  q=h[h.dataset.eq(ds)&h.scenario.eq(scenario)].set_index('term')
  terms=list(q.index)
  f=PHReg(d.duration,d[terms],status=d.event,ties='efron').fit()
  error=float(np.max(np.abs(f.params-np.log(q.hazard_ratio))))
  se=np.sqrt(np.diag(f.cov_params()));refse=(np.log(q.ci_high)-np.log(q.ci_low))/(2*1.959963984540054)
  seerror=float(np.max(np.abs(se-refse)))
  assert error<1e-4 and seerror<1e-4
  checks.append(dict(dataset=ds,scenario=scenario,max_log_hr_difference=error,max_se_difference=seerror))
  print(ds,scenario,error,flush=True)
(R/'verification.json').write_text(json.dumps({'independent_engine':'statsmodels PHReg, Efron ties','checks':checks},indent=2))

intervals=pd.read_csv(R/'Early and late hazard ratios.csv');intervalchecks=[]
for ds in ['Colonoscopy','EGD']:
 for scenario in ['Administrative','Last recorded contact']:
  source=pd.read_csv(R/f'{ds} {scenario}.csv')
  for low,high,label in [(0,90,'Days 1-90'),(90,730,'Days 91-730')]:
   d=source[source.duration.gt(low)].copy();d['entry']=low;d['event']=(d.event.eq(1)&d.duration.le(high)).astype(int);d['duration']=d.duration.clip(upper=high)
   q=intervals[intervals.dataset.eq(ds)&intervals.scenario.eq(scenario)&intervals.period.eq(label)].set_index('term');terms=list(q.index)
   f=PHReg(d.duration,d[terms],status=d.event,entry=d.entry,ties='efron').fit(method='bfgs',gtol=1e-8,maxiter=1000)
   error=float(np.max(np.abs(f.params-np.log(q.hazard_ratio))))
   se=np.sqrt(np.diag(f.cov_params()));refse=(np.log(q.ci_high)-np.log(q.ci_low))/(2*1.959963984540054);seerror=float(np.max(np.abs(se-refse)))
   assert error<1e-4 and seerror<1e-4
   intervalchecks.append(dict(dataset=ds,scenario=scenario,period=label,max_log_hr_difference=error,max_se_difference=seerror))
(PACKAGE/'documentation/cox_verification.json').write_text(json.dumps({'independent_engine':'statsmodels PHReg, Efron ties','checks':checks,'interval_checks':intervalchecks},indent=2))
