from pathlib import Path
import sys,json,os
PACKAGE=Path(__file__).resolve().parents[1]
SOURCE=PACKAGE.parents[1]
R=PACKAGE/'restricted/extended';R.mkdir(parents=True,exist_ok=True)
# Optional local fallback; otherwise install the versions recorded in requirements.txt.
localdeps=PACKAGE.parent/'repeat_endoscopy_analysis/dependencies'
if localdeps.exists(): sys.path.insert(0,str(localdeps))
os.environ['MPLCONFIGDIR']=str(PACKAGE.parent/'shah_publication_qa/mpl')
import pandas as pd,numpy as np
from statsmodels.stats.proportion import proportion_confint
import statsmodels.api as sm
import statsmodels.formula.api as smf
from functools import lru_cache
END=pd.Timestamp('2023-05-31');START=pd.Timestamp('2000-01-01');K=['PatientID','EncounterID']
@lru_cache(None)
def load(ds,t):
 print('Reading',ds,t,flush=True)
 return pd.read_excel(SOURCE/'Research Project/Drivers for Repeat Endoscopy'/f'{ds} dataset.xlsx',sheet_name=t)
proc=[]
for ds in ['Colonoscopy','EGD']:
 p=load(ds,'ProceduresProFee').copy();p['source']=ds;p['date']=pd.to_datetime(p.Date,errors='coerce').dt.normalize();p['code']=p.TermCodeMapped.astype(str).str.strip();proc.append(p)
allp=pd.concat(proc,ignore_index=True);allp=allp[allp.date.between(START,END)]
union=allp.drop_duplicates(K+['date','code'])
dxcol=pd.read_excel(SOURCE/'Research Project/colonoscopy dx everything icd code.xlsx',sheet_name='DiagnosesEverything')
dxegd=pd.concat(pd.read_excel(SOURCE/'Research Project/EGD diagnosis everything ICD code.xlsx',sheet_name=['DiagnosesEverything','DiagnosesEverything (part 2)']).values(),ignore_index=True)
dxegd=dxegd.rename(columns={'TermCodeMapped':'TermCodeSource'})
dx=pd.concat([dxcol,dxegd],ignore_index=True).drop_duplicates(K+['TermCodeSource','TermDescription'])
dx['code']=dx.TermCodeSource.fillna('').astype(str).str.strip().str.upper()
spec={'abdominal_pain':('R10','789.0'),'constipation':('K59.0','564.0'),'rectal_bleeding':('K62.5','569.3'),'heartburn':('R12','787.1'),'dysphagia':('R13','787.2'),'reflux':('K21','530.81'),'ibd':('K50','K51','555','556')}
for v,prefix in spec.items():dx[v]=dx.code.str.startswith(prefix)
for v,prefix in {'variable1':'K59.','variable2':'K62.5','variable3_any_other_code':'K62.','variable5':'R10.1','variable6':'R10.2','variable7':'R10.3'}.items():dx[v]=dx.code.str.startswith(prefix)
dx['variable3_any_other_code'] &= ~dx.code.str.startswith('K62.5')
dx['variable8']=dx.code.str.startswith(('R10.8','R10.9'))
ericbase=['variable1','variable2','variable3_any_other_code','variable5','variable6','variable7','variable8']
flags=dx.groupby(K)[list(spec)+ericbase].max().reset_index();flags['diagnosis_available']=True
flags['variable3']=flags.variable3_any_other_code & ~flags.variable2
flags['variable4']=flags[['variable1','variable2','variable3']].any(axis=1)
flags['variable9']=flags[['variable5','variable6','variable7','variable8']].any(axis=1)
ericvars=[f'variable{i}' for i in range(1,10)]+['variable3_any_other_code']
demo=pd.concat([load(ds,'DemographicInfo')[['PatientID','GenderCode']] for ds in ['Colonoscopy','EGD']]).drop_duplicates()
assert not demo.PatientID.duplicated().any()
results=[];models=[];details={};queues=[];eric_summary=[]
def summarize(ds,definition,d,outcome='repeat730'):
 n=len(d);e=int(d[outcome].sum());lo,hi=proportion_confint(e,n,method='wilson') if n else (np.nan,np.nan)
 results.append(dict(dataset=ds,definition=definition,n=n,events=e,proportion=e/n if n else None,ci_low=lo,ci_high=hi))
def days(p,codes):return p[p.code.isin(codes)][['PatientID','date']].drop_duplicates()
def make(ds,indexp,indexcodes,outp,outcodes):
 ev=indexp[indexp.code.isin(indexcodes)][K+['date']].drop_duplicates().merge(flags,on=K,how='left',validate='many_to_one')
 vv=list(spec)+ericvars+['diagnosis_available'];ev[vv]=ev[vv].fillna(False).astype(bool)
 ev=ev.groupby(['PatientID','date'])[vv].max().reset_index().sort_values(['PatientID','date'])
 ev['variable3']=ev.variable3_any_other_code & ~ev.variable2
 idx=ev.groupby('PatientID').head(1).rename(columns={'date':'index_date'})
 fut=days(outp,outcodes).merge(idx[['PatientID','index_date']],on='PatientID',validate='many_to_one');fut['gap']=(fut.date-fut.index_date).dt.days;fut=fut[fut.gap.gt(0)]
 first=fut.sort_values('gap').groupby('PatientID').head(1).set_index('PatientID')
 idx['repeat_gap']=idx.PatientID.map(first.gap) if len(first) else np.nan
 idx['repeat_date']=idx.PatientID.map(first.date) if len(first) else pd.NaT
 idx['repeat730']=idx.repeat_gap.between(1,730);idx['repeat_any']=idx.repeat_gap.notna();idx['calendar730']=idx.index_date+pd.Timedelta(days=730)<=END
 idx['repeat31to730']=idx.PatientID.isin(fut.loc[fut.gap.between(31,730),'PatientID'])
 idx['repeat31to730_first']=idx.repeat_gap.between(31,730)
 idx['n_later_days']=idx.PatientID.map(fut.groupby('PatientID').size()).fillna(0).astype(int)
 idx['index_year']=idx.index_date.dt.year
 return idx,fut,ev
for ds,core,wide,syms in [('Colonoscopy',['45378','45380'],['45378','45379','45380','45381','45382','45383','45384','45385','45386','45388','45390','45391'],['abdominal_pain','constipation','rectal_bleeding']),('EGD',['43235','43239'],['43233','43234','43235','43236','43237','43238','43239','43240','43241','43242','43243','43244','43245','43246','43247','43248','43249','43250','43251','43253','43254','43255','43256','43258','43259','43266','43270'],['abdominal_pain','heartburn','dysphagia'])]:
 if ds=='Colonoscopy':wide+=['44388','44389','44392','44394','G0105','G0121']
 p=allp[allp.source.eq(ds)]
 local,_,_=make(ds,p,core,p,core)
 idx,fut,ev=make(ds,p,core,union,core)
 broad,_,_=make(ds,p,core,union,wide)
 pooled,_,_=make(ds,union,core,union,core)
 idx['target_symptom']=idx[syms].any(axis=1)
 # Match the first subsequent core procedure date to diagnoses from every core encounter on that day.
 followflags=union[union.code.isin(core)][K+['date']].drop_duplicates().merge(flags,on=K,how='left',validate='many_to_one')
 vv=list(spec)+['diagnosis_available'];followflags[vv]=followflags[vv].fillna(False).astype(bool)
 followflags=followflags.groupby(['PatientID','date'])[vv].max().reset_index()
 idx=idx.merge(followflags.rename(columns={'date':'repeat_date',**{v:'repeat_'+v for v in vv}}),on=['PatientID','repeat_date'],how='left',validate='one_to_one')
 idx['same_symptom_first_repeat']=False
 for v in syms:idx['same_symptom_first_repeat'] |= idx[v]&idx['repeat_'+v].fillna(False).astype(bool)&idx.repeat730
 full=idx[idx.calendar730].copy()
 for v in ericvars:
  known=full[full.diagnosis_available];sub=known[known[v]]
  eric_summary.append(dict(dataset=ds,variable=v,index_positive=int(sub.shape[0]),known_index_diagnoses=len(known),unknown_index_diagnoses=int((~full.diagnosis_available).sum()),repeat_events=int(sub.repeat730.sum())))
 # Export exact encounter-level flags; unknown diagnoses remain blank rather than negative.
 ef=p[p.code.isin(core)][K+['date']].drop_duplicates().merge(flags[K+ericvars+['diagnosis_available']],on=K,how='left',validate='many_to_one')
 for v in ericvars:ef[v]=ef[v].astype('Int64')
 ef.to_csv(R/(ds+' encounter variables.csv'),index=False)
 summarize(ds,'Original source only; core codes; first repeat within 730; calendar opportunity',local[local.calendar730])
 summarize(ds,'Both source workbooks; core codes; first repeat within 730; calendar opportunity',full)
 summarize(ds,'Both sources; broader procedure family at follow-up; calendar opportunity',broad[broad.calendar730])
 summarize(ds,'Core codes; first repeat at any observed time; all index patients',idx,'repeat_any')
 summarize(ds,'Core codes; observed repeat within 730; all index patients including shorter calendar opportunity',idx)
 summarize(ds,'All available core index patients pooled across both sources; calendar opportunity',pooled[pooled.calendar730])
 summarize(ds,'Core codes; any procedure days 31–730; calendar opportunity',full,'repeat31to730')
 summarize(ds,'Core codes; first repeat occurs days 31–730; calendar opportunity',full,'repeat31to730_first')
 summarize(ds,'Symptom-positive first core index; any core repeat; calendar opportunity',full[full.target_symptom])
 summarize(ds,'Symptom-positive first core index; first repeat shares coded symptom; calendar opportunity',full[full.target_symptom],'same_symptom_first_repeat')
 for v in syms+(['reflux'] if ds=='EGD' else []):summarize(ds,'Index diagnosis: '+v+'; core repeat; calendar opportunity',full[full[v]])
 for lower,upper,name in [(2000,2011,'2000–2011'),(2012,2015,'2012–2015'),(2016,2021,'2016 onward')]:summarize(ds,'Index era '+name+'; core repeat; calendar opportunity',full[full.index_year.between(lower,upper)])
 for h in [30,90,365,730]:
  tmp=idx[idx.index_date+pd.Timedelta(days=h)<=END].copy();tmp['eventh']=tmp.repeat_gap.between(1,h);summarize(ds,f'Core codes; first repeat within {h} days; matching calendar opportunity',tmp,'eventh')
 details[ds]={'index_patients':len(idx),'index_patientdays':len(ev),'same_day_rows_collapsed':len(p[p.code.isin(core)])-len(ev),'source_only_events730_full':int(local.loc[local.calendar730,'repeat730'].sum()),'union_events730_full':int(full.repeat730.sum()),'additional_patients_with_events_from_other_workbook':int((full.repeat730&~full.PatientID.isin(local.loc[local.repeat730,'PatientID'])).sum()),'full_calendar_patients':len(full),'missing_index_diagnoses':int((~idx.diagnosis_available).sum()),'repeat_cases_missing_repeat_diagnoses':int((full.repeat730&~full.repeat_diagnosis_available.fillna(False).astype(bool)).sum()),'median_gap_among_730_events':float(full.loc[full.repeat730,'repeat_gap'].median()),'core_codes':core,'broad_followup_codes':wide,'symptoms':syms,'unique_repeat_cases_anytime':int(idx.repeat_any.sum())}
 idx=idx.merge(demo,on='PatientID',how='left',validate='one_to_one')
 export=idx.copy()
 for v in ericvars:export[v]=export[v].astype('Int64').where(export.diagnosis_available)
 export.to_csv(R/(ds+' patient cohort.csv'),index=False)
 # Reproducible exploratory models of recorded repeat probability, not a survival model.
 m=idx[idx.calendar730&idx.GenderCode.isin(['F','M'])].copy();m['y']=m.repeat730.astype(int);m['female']=m.GenderCode.eq('F').astype(int);m['unknown_dx']=(~m.diagnosis_available).astype(int);m['era']=pd.cut(m.index_year,[1999,2011,2015,2023],labels=['2000_2011','2012_2015','2016_plus'])
 terms=['female','era']+[v for v in syms if m[v].nunique()>1 and m.loc[m[v],'y'].sum()>0 and m.loc[~m[v],'y'].sum()>0]
 details[ds]['model_omitted_zero_event_symptom_terms']=[v for v in syms if v not in terms]
 if m.unknown_dx.nunique()>1:terms+=['unknown_dx']
 for v in syms:m[v]=m[v].astype(int)
 if m.y.sum()>=50:
  fit=smf.glm('y ~ '+' + '.join(terms),data=m,family=sm.families.Poisson()).fit(cov_type='HC0')
  ci=fit.conf_int()
  for term in fit.params.index:
   if term=='Intercept':continue
   models.append(dict(dataset=ds,term=term,adjusted_recorded_probability_ratio=float(np.exp(fit.params[term])),ci_low=float(np.exp(ci.loc[term,0])),ci_high=float(np.exp(ci.loc[term,1])),p_value=float(fit.pvalues[term]),n=len(m),events=int(m.y.sum())))
  details[ds]['model_converged']=bool(fit.converged);details[ds]['model_max_fitted_probability']=float(fit.fittedvalues.max());details[ds]['model_excluded_unknown_gender']=int(idx.calendar730.sum()-len(m))
 # Local case queue prioritizes symptom-overlap repeats; no adjudication assumed.
 q=idx[idx.repeat730].copy();q['dataset']=ds;q['review_priority']=np.where(q.same_symptom_first_repeat,'1 - shared symptom on first repeat',np.where(q.target_symptom,'2 - symptom index','3 - other indication'));queues.append(q)
 if ds=='Colonoscopy':
  strictlocal,_,_=make(ds,p,['45378'],p,['45378']);summarize(ds,'45378 only, any indication, original source; calendar opportunity',strictlocal[strictlocal.calendar730])
  strict,_,_=make(ds,p,['45378'],union,['45378']);summarize(ds,'45378 only, any index indication; calendar opportunity',strict[strict.calendar730])
  bleed=flags[flags.rectal_bleeding][K]; bp=p[p.code.eq('45378')].merge(bleed,on=K)
  bi,_,_=make(ds,bp,['45378'],union,['45378']);summarize(ds,'45378 index with bleeding in either ICD system; calendar opportunity',bi[bi.calendar730]);details[ds]['bleeding_index_n']=len(bi)
pd.DataFrame(results).to_csv(R/'Repeat estimates.csv',index=False)
pd.DataFrame(models).to_csv(R/'Exploratory associations.csv',index=False)
pd.DataFrame(eric_summary).to_csv(R/'Nine variables summary.csv',index=False)
queue=pd.concat(queues,ignore_index=True).sort_values(['review_priority','dataset','repeat_gap'])
for v in ericvars:queue[v]=queue[v].astype('Int64').where(queue.diagnosis_available)
queue.to_csv(R/'Repeat cases for chart review.csv',index=False)
(R/'analysis_results.json').write_text(json.dumps({'details':details,'estimates':results,'models':models,'eric_variables':eric_summary},indent=2))
print(json.dumps(details,indent=2));print(pd.DataFrame(results).to_string(index=False))

# Export restricted raw linkage separately from prepared pseudonymous analytic data.
public=PACKAGE/'data'; tables=PACKAGE/'tables'
for ds in ['Colonoscopy','EGD']:
 d=pd.read_csv(R/(ds+' patient cohort.csv'))
 d=d.sort_values('PatientID').reset_index(drop=True)
 d.insert(0,'study_id',[f'{ds}_{i:06d}' for i in range(1,len(d)+1)])
 d[['study_id','PatientID','index_date','repeat_date']].to_csv(PACKAGE/f'restricted/extended_{ds}_linkage.csv',index=False)
 d.drop(columns=['PatientID','index_date','repeat_date']).to_csv(public/f'extended_{ds}_analysis.csv',index=False)
for name in ['Repeat estimates.csv','Exploratory associations.csv','Nine variables summary.csv']:
 (tables/name).write_bytes((R/name).read_bytes())
(PACKAGE/'tables/extended_results.json').write_bytes((R/'analysis_results.json').read_bytes())
