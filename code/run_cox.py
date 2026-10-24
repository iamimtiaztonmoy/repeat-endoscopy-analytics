from pathlib import Path
import sys,os,json,warnings
PACKAGE=Path(__file__).resolve().parents[1]
R=PACKAGE/'restricted/cox'
deps=PACKAGE.parent/'cox_analysis/dependencies'
if deps.exists():sys.path.insert(0,str(deps))
os.environ['MPLCONFIGDIR']=str(PACKAGE.parent/'shah_publication_qa/mpl')
import pandas as pd,numpy as np
from lifelines import CoxPHFitter,KaplanMeierFitter
from lifelines.statistics import proportional_hazard_test
from lifelines.exceptions import ConvergenceError
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=PACKAGE/'restricted/extended'
END=pd.Timestamp('2023-05-31')
last=pd.read_csv(R/'last_contacts.csv',parse_dates=['last_contact']).set_index('PatientID').last_contact
appt=pd.read_csv(R/'last_appointments.csv',parse_dates=['last_appointment']).set_index('PatientID').last_appointment
sources=json.loads((R/'contact_sources.json').read_text())
rows=[];diags=[];audits=[];intervals=[];kmrows=[];fitnotes=[]
fig,axes=plt.subplots(1,2,figsize=(12,5))
def savefit(m,terms,ds,scenario,period=None):
 omitted=[]
 if period:
  omitted=[t for t in terms if m[t].nunique()<2 or (m[t].nunique()==2 and any(m.loc[m[t].eq(v),'event'].sum()==0 for v in m[t].unique()))]
  terms=[t for t in terms if t not in omitted]
 cols=['duration','event']+terms+(['entry'] if period else [])
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter('always')
  try:
   fit=CoxPHFitter().fit(m[cols],duration_col='duration',event_col='event',entry_col='entry' if period else None,fit_options={'step_size':0.1} if period else None)
  except ConvergenceError as error:
   if not period:raise
   fitnotes.append({'dataset':ds,'scenario':scenario,'period':period,'status':'Not estimable: convergence failure','omitted_nonvarying_or_zero_event_terms':omitted,'error':str(error)})
   intervals.append(dict(dataset=ds,scenario=scenario,period=period,term='MODEL NOT ESTIMABLE',n=len(m),events=int(m.event.sum()),hazard_ratio=np.nan,ci_low=np.nan,ci_high=np.nan,p_value=np.nan))
   return None
 fitnotes.append({'dataset':ds,'scenario':scenario,'period':period,'omitted_nonvarying_or_zero_event_terms':omitted,'warnings':[str(w.message) for w in ws], 'log_likelihood':float(fit.log_likelihood_)})
 assert np.isfinite(fit.params_).all() and np.isfinite(fit.standard_errors_).all()
 for term,s in fit.summary.iterrows():
  row=dict(dataset=ds,scenario=scenario,term=term,n=len(m),events=int(m.event.sum()),hazard_ratio=s['exp(coef)'],ci_low=s['exp(coef) lower 95%'],ci_high=s['exp(coef) upper 95%'],p_value=s['p'])
  if period:row['period']=period;intervals.append(row)
  else:rows.append(row)
 return fit
for ax,ds in zip(axes,['Colonoscopy','EGD']):
 d=pd.read_csv(B/f'{ds} patient cohort.csv',parse_dates=['index_date','repeat_date'])
 assert d.PatientID.is_unique
 d['admin_days']=np.minimum((END-d.index_date).dt.days,730)
 d['last_contact']=d.PatientID.map(last);d['last_appointment']=d.PatientID.map(appt)
 d['female']=d.GenderCode.eq('F').astype(int)
 d['era_2012_2015']=d.index_year.between(2012,2015).astype(int);d['era_2016_plus']=d.index_year.ge(2016).astype(int)
 d['unknown_dx']=(~d.diagnosis_available).astype(int)
 syms=['abdominal_pain','constipation'] if ds=='Colonoscopy' else ['abdominal_pain','heartburn','dysphagia']
 terms=['female','era_2012_2015','era_2016_plus']+syms+['unknown_dx']
 for v in syms:d[v]=d[v].astype(int)
 for scenario in ['Administrative','Last recorded contact','Last appointment plus repeat evidence']:
  m=d.copy();e=m.repeat_gap.between(1,730)&m.repeat_gap.le(m.admin_days)
  if scenario=='Administrative':c=m.admin_days
  else:
   date=m.last_contact if scenario=='Last recorded contact' else m.last_appointment
   # A documented subsequent procedure is itself evidence of observation on that date.
   date=pd.concat([date,m.repeat_date,m.index_date],axis=1).max(axis=1)
   c=np.minimum((date-m.index_date).dt.days,m.admin_days)
  m['event']=(e&m.repeat_gap.le(c)).astype(int)
  m['duration']=np.where(m.event.eq(1),m.repeat_gap,c)
  zero=m.duration.le(0)|m.duration.isna();gender=~m.GenderCode.isin(['F','M'])
  audits.append(dict(dataset=ds,scenario=scenario,starting_n=len(d),zero_followup=int(zero.sum()),unknown_gender_after_positive=int((~zero&gender).sum()),n=int((~zero&~gender).sum()),events=int(m.loc[~zero&~gender,'event'].sum()),person_years=float(m.loc[~zero&~gender,'duration'].sum()/365.25),median_days=float(m.loc[~zero&~gender,'duration'].median()),events_after_last_appointment=int((e&(m.last_appointment.isna()|m.repeat_date.gt(m.last_appointment))).sum())))
  m=m[~zero&~gender].copy().reset_index(drop=True)
  assert m.duration.between(1,730).all() and m.loc[m.event.eq(1),'duration'].eq(m.loc[m.event.eq(1),'repeat_gap']).all()
  assert m.event.sum()==d.repeat_gap.between(1,730).sum()
  fit=savefit(m,terms,ds,scenario)
  ph=proportional_hazard_test(fit,m[['duration','event']+terms],time_transform='rank')
  for term,s in ph.summary.iterrows():diags.append(dict(dataset=ds,scenario=scenario,term=term,test_statistic=s.test_statistic,p_value=s.p))
  km=KaplanMeierFitter().fit(m.duration,m.event,label=scenario)
  km.plot_cumulative_density(ax=ax,ci_show=False)
  for day in [30,90,365,730]:kmrows.append(dict(dataset=ds,scenario=scenario,day=day,at_risk=int(m.duration.ge(day).sum()),cumulative_repeat_estimate=float(1-km.predict(day))))
  m[['PatientID','index_date','repeat_date','last_contact','last_appointment','duration','event']+terms].to_csv(R/f'{ds} {scenario}.csv',index=False)
  # Prespecified descriptive early/late split to assess whether a constant HR hides changing associations.
  if scenario in ['Administrative','Last recorded contact']:
   for low,high,label in [(0,90,'Days 1-90'),(90,730,'Days 91-730')]:
    z=m[m.duration.gt(low)].copy();z['entry']=low;z['event']=(z.event.eq(1)&z.duration.le(high)).astype(int);z['duration']=z.duration.clip(upper=high)
    savefit(z,terms,ds,scenario,label)
  print(ds,scenario,len(m),int(m.event.sum()),'PH p<.05',int((ph.summary.p<.05).sum()),flush=True)
 ax.set(title=ds,xlabel='Days after first observed procedure',ylabel='Estimated probability of recorded repeat',xlim=(0,730))
 ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.suptitle('Repeat procedure estimates depend on the censoring assumption',fontsize=13)
fig.tight_layout();fig.savefig(R/'Censoring sensitivity.png',dpi=180)
for name,data in [('Adjusted Cox results',rows),('Proportional hazards checks',diags),('Follow-up audit',audits),('Early and late hazard ratios',intervals),('Survival estimates and risk sets',kmrows)]:pd.DataFrame(data).to_csv(R/f'{name}.csv',index=False)
(R/'model_audit.json').write_text(json.dumps({'sources':sources,'fits':fitnotes,'checks':'Unique patients, positive follow-up, event-time consistency, finite estimates, all eligible events retained'},indent=2))
(PACKAGE/'documentation/cox_model_audit.json').write_bytes((R/'model_audit.json').read_bytes())
print('COMPLETE',flush=True)


# Final model inputs use the same study IDs as the extended cohort files.
for ds in ['Colonoscopy','EGD']:
 link=pd.read_csv(PACKAGE/f'restricted/extended_{ds}_linkage.csv')[['PatientID','study_id']]
 for scenario in ['Administrative','Last recorded contact','Last appointment plus repeat evidence']:
  p=R/f'{ds} {scenario}.csv';d=pd.read_csv(p).merge(link,on='PatientID',validate='one_to_one')
  d.drop(columns=['PatientID','index_date','repeat_date','last_contact','last_appointment']).to_csv(PACKAGE/'data'/f'model_{ds}_{scenario.replace(" ","_")}.csv',index=False)
for name in ['Adjusted Cox results','Proportional hazards checks','Follow-up audit','Early and late hazard ratios','Survival estimates and risk sets']:
 (PACKAGE/'tables'/f'{name}.csv').write_bytes((R/f'{name}.csv').read_bytes())
