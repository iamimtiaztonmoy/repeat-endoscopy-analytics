"""Rebuild the publication audit from original workbooks; no prior analytic files used."""
from pathlib import Path
import argparse, hashlib, json, platform
import pandas as pd
import numpy as np
import openpyxl

ap=argparse.ArgumentParser()
ap.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[3])
ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1])
a=ap.parse_args(); R=a.output; S=a.source_root
for folder in ['data','restricted','tables','figures','documentation']: (R/folder).mkdir(parents=True,exist_ok=True)
sources={'procedure':'Research Project/Drivers for Repeat Endoscopy/Colonoscopy dataset.xlsx','diagnosis':'Research Project/colonoscopy dx everything icd code.xlsx','clinic':'Dataset/colonoscopy clinic.xlsx'}
manifest=[]; sheets={}
needed={'procedure':['ProceduresProFee','EncounterAll','EncounterAnthropometricsBMI','PatientInfo','DemographicInfo','Orders','ClaritySocialHistory','ClarityMedicalHistory','Query Specifications'], 'diagnosis':['DiagnosesEverything'], 'clinic':['EncounterAll','DiagnosesEverything']}
for label,rel in sources.items():
 p=S/rel; manifest.append({'source':label,'relative_path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
 w=openpyxl.load_workbook(p,read_only=True,data_only=True)
 for name in needed[label]:
  rows=w[name].values
  if name=='Query Specifications':
   q=list(rows); evidence=[{'excel_row':i+1,'field':str(row[1]),'text':str(row[2])} for i,row in enumerate(q) if '569.3' in str(row)]
   (R/'documentation/query_exclusion_evidence.json').write_text(json.dumps(evidence,indent=2))
   continue
  d=pd.DataFrame(rows,columns=next(rows)); sheets[label,name]=d
  print(label,name,len(d),flush=True)
 w.close()
pd.DataFrame(manifest).to_csv(R/'documentation/source_manifest.csv',index=False)
def get(label,name): return sheets[label,name].copy()
def dates(s): return pd.to_datetime(s,errors='coerce').dt.normalize()
K=['PatientID','EncounterID']; cutoff=pd.Timestamp('2023-05-31')
p=get('procedure','ProceduresProFee'); p['date']=dates(p.Date);p['code']=p.TermCodeMapped.fillna('').astype(str).str.strip()
all_p=p.copy(); p=p[p.date.between('2000-01-01',cutoff)&p.code.eq('45378')].copy()
dx=get('diagnosis','DiagnosesEverything'); dx['code']=dx.TermCodeSource.fillna('').astype(str).str.strip().str.upper()
rules={'variable1':'K59.','variable2':'K62.5','variable3':'K62.','variable5':'R10.1','variable6':'R10.2','variable7':'R10.3'}
for v,code in rules.items(): dx[v]=dx.code.str.startswith(code)
dx['variable2']=dx.code.eq('K62.5')
dx['variable3'] &= ~dx.code.eq('K62.5')
dx['variable8']=dx.code.str.startswith(('R10.8','R10.9'))
vs=list(rules)+['variable8']; flags=dx.groupby(K)[vs].max().reset_index()
flags['variable4']=flags[['variable1','variable2','variable3']].any(axis=1)
flags['variable9']=flags[['variable5','variable6','variable7','variable8']].any(axis=1)
flags['variable3_exclusive']=flags.variable3 & ~flags.variable2
target=p[K+['date']].drop_duplicates()
j=target.merge(flags,on=K,how='left',validate='many_to_one')
eligible=j[j.variable2.eq(True)].sort_values(['PatientID','date','EncounterID'])
idx=eligible.groupby('PatientID').head(1).copy()
idx=idx.rename(columns={'EncounterID':'index_encounter_id','date':'index_date'})
days=p[['PatientID','date']].drop_duplicates()
rp=days.merge(idx[['PatientID','index_date']],on='PatientID',validate='many_to_one');rp['gap']=(rp.date-rp.index_date).dt.days
second=rp[rp.gap.gt(0)].sort_values(['PatientID','gap']).groupby('PatientID').head(1)
idx=idx.merge(second[['PatientID','date','gap']].rename(columns={'date':'repeat_date','gap':'repeat_gap_days'}),how='left',on='PatientID',validate='one_to_one')
clinic=get('clinic','EncounterAll');clinic['date']=dates(clinic.AppointmentTime)
enc=get('procedure','EncounterAll');enc['admit']=dates(enc.AdmitDate)
assert not enc.duplicated(K).any()
idx['latest_appointment_date']=idx.PatientID.map(clinic.groupby('PatientID').date.max())
idx['latest_admission_date']=idx.PatientID.map(enc.groupby('PatientID').admit.max())
idx=idx.merge(enc[K+['admit']].rename(columns={'EncounterID':'index_encounter_id','admit':'index_admission_date'}),on=['PatientID','index_encounter_id'],how='left',validate='one_to_one')
idx['appointment_days']=(idx.latest_appointment_date-idx.index_date).dt.days
idx['admission_days']=(idx.latest_admission_date-idx.index_date).dt.days
idx['both_admission_days']=(idx.latest_admission_date-idx.index_admission_date).dt.days
idx['calendar_days']=(cutoff-idx.index_date).dt.days
idx['event730']=idx.repeat_gap_days.between(1,730).astype(int);idx['censor']=1-idx.event730
idx['legacy_event_time']=idx.repeat_gap_days.where(idx.repeat_gap_days.le(730),731).where(idx.repeat_gap_days.notna())
idx['legacy_followup_days']=idx.legacy_event_time.fillna(idx.appointment_days)
# This is an unverified timestamp proxy, NOT validated observation time.
idx['appointment_proxy_days730']=idx[['appointment_days','calendar_days']].min(axis=1,skipna=False).clip(upper=730)
idx['admission_proxy_days730']=idx[['admission_days','calendar_days']].min(axis=1,skipna=False).clip(upper=730)
idx['both_admission_proxy_days730']=idx.both_admission_days.clip(upper=730)
idx['no_positive_appointment_followup']=idx.appointment_days.le(0).astype(int)
idx['calendar730_available']=idx.calendar_days.ge(730).astype(int)
idx['prior_observed45378']=idx.PatientID.isin(rp.loc[rp.gap.lt(0),'PatientID']).astype(int)
idx['index_year']=idx.index_date.dt.year
patient=get('procedure','PatientInfo').rename(columns={'AGE':'source_age_unanchored'})
idx=idx.merge(patient,on='PatientID',how='left',validate='one_to_one')
demo=get('procedure','DemographicInfo')
idx=idx.merge(demo[['PatientID','GenderCode','GenderName']],on='PatientID',how='left',validate='one_to_one')
idx['age_at_index']=np.nan
idx['female_recorded_gender']=idx.GenderCode.map({'F':1,'M':0})
basekeys=['PatientID','index_encounter_id']
bmi=get('procedure','EncounterAnthropometricsBMI').rename(columns={'EncounterID':'index_encounter_id','BMI':'index_bmi','HeightCM':'index_height_cm','WeightKG':'index_weight_kg'})
idx=idx.merge(bmi,on=basekeys,how='left',validate='one_to_one')
for col in ['index_bmi','index_height_cm','index_weight_kg']:idx[col]=pd.to_numeric(idx[col],errors='coerce')
idx['bmi_review_flag']=((idx.index_bmi.notna())&(~idx.index_bmi.between(10,80))).astype(int)
orders=get('procedure','Orders');orders['gi_proxy']=orders.OrderDepartment.fillna('').str.contains('GI liver|gastroenterology|txp|gi proc|med proc unit|hepatology',case=False,regex=True)
of=orders.groupby(K).gi_proxy.agg(['size','max']).reset_index().rename(columns={'EncounterID':'index_encounter_id','size':'index_order_rows','max':'gi_department_proxy'})
idx=idx.merge(of,on=basekeys,how='left',validate='one_to_one');idx['index_order_rows']=idx.index_order_rows.fillna(0).astype(int)
hist=get('procedure','ClarityMedicalHistory');hcounts=hist.groupby(K).size();idx['index_history_rows']=[int(hcounts.get((r.PatientID,r.index_encounter_id),0)) for r in idx.itertuples()]
soc=get('procedure','ClaritySocialHistory');soc=soc[soc.SmokingStatusMapped.isin(['Current','Former','Never'])]
sm=soc.groupby(K).SmokingStatusMapped.agg(lambda x:'|'.join(sorted(set(x)))).reset_index().rename(columns={'EncounterID':'index_encounter_id','SmokingStatusMapped':'index_smoking_status'})
idx=idx.merge(sm,on=basekeys,how='left',validate='one_to_one')
idx['ibd_code_any_export']=idx.PatientID.isin(dx.loc[dx.code.str.startswith(('K50','K51','555','556')),'PatientID']).astype(int)
for v in [f'variable{i}' for i in range(1,10)]:idx[v]=idx[v].astype(int)
idx=idx.sort_values('PatientID').reset_index(drop=True);idx.insert(0,'study_id',[f'RB{i:04d}' for i in range(1,len(idx)+1)])
idx['verified_observation_days']=np.nan
idx['analysis_disposition']='Descriptive only; follow-up unverified and no observed events'
datecols=['index_date','repeat_date','latest_appointment_date','latest_admission_date','index_admission_date']
idx[['study_id','PatientID','index_encounter_id']+datecols].to_csv(R/'restricted/linkage_and_dates.csv',index=False)
analysis=idx.drop(columns=['PatientID','index_encounter_id']+datecols)
analysis.to_csv(R/'data/analysis_cohort.csv',index=False)
idx.to_csv(R/'restricted/cohort_with_source_keys.csv',index=False)
# Rebuild broad procedure-only context separately with exactly the same procedure definition.
bp=days.sort_values(['PatientID','date']);bp['rank']=bp.groupby('PatientID').cumcount()
bf=bp[bp['rank'].eq(0)][['PatientID','date']].rename(columns={'date':'first_date'})
bs=bp[bp['rank'].eq(1)][['PatientID','date']].rename(columns={'date':'second_date'})
b=bf.merge(bs,on='PatientID',how='left',validate='one_to_one');b['gap']=(b.second_date-b.first_date).dt.days
flow=[('All professional fee rows',len(all_p)),('45378 rows in study window',len(p)),('Unique 45378 patient encounter keys',len(p[K].drop_duplicates())),('Distinct 45378 patient days',len(days)),('Patients with any 45378',p.PatientID.nunique()),('45378 encounter keys without coded diagnoses',len(p[K].drop_duplicates().merge(flags[K],on=K,how='left',indicator=True).query('_merge == "left_only"'))),('Qualifying bleeding procedure encounters',len(eligible)),('Earliest qualifying patients',len(idx)),('Observed repeat within 730 days',int(idx.event730.sum())),('Positive appointment proxy follow-up',int(idx.appointment_days.gt(0).sum()))]
pd.DataFrame(flow,columns=['stage','count']).to_csv(R/'tables/cohort_flow.csv',index=False)
def stat(s):
 s=s.dropna();return f'{s.median():.1f} ({s.quantile(.25):.1f}-{s.quantile(.75):.1f}); range {s.min():.1f}-{s.max():.1f}' if len(s) else 'Not available'
labels={1:'K59 family flag',2:'Rectal bleeding K62.5',3:'Other K62 family codes',4:'Any stool code composite',5:'Upper abdominal pain R10.1',6:'Pelvic pain R10.2',7:'Lower abdominal pain R10.3',8:'Other or unspecified abdominal pain R10.8 or R10.9',9:'Any abdominal pain code composite'}
tab=[]
for i in range(1,10):
 v=f'variable{i}';tab.append({'characteristic':labels[i],'value':f'{idx[v].sum()}/{len(idx)} ({100*idx[v].mean():.1f}%)','missing':0})
for col,label in [('index_bmi','BMI at index'),('source_age_unanchored','Source age with unverified reference date')]:tab.append({'characteristic':label,'value':stat(idx[col]),'missing':int(idx[col].isna().sum())})
tab += [{'characteristic':'Female recorded gender','value':f'{idx.female_recorded_gender.eq(1).sum()}/{len(idx)} ({100*idx.female_recorded_gender.eq(1).mean():.1f}%)','missing':int(idx.female_recorded_gender.isna().sum())},{'characteristic':'Verified age at index','value':'Unavailable','missing':len(idx)},{'characteristic':'Known smoking status at exact index encounter','value':str(idx.index_smoking_status.notna().sum()),'missing':int(idx.index_smoking_status.isna().sum())},{'characteristic':'GI department proxy among patients with index orders','value':f'{idx.gi_department_proxy.eq(True).sum()}/{idx.index_order_rows.gt(0).sum()}','missing':int(idx.index_order_rows.eq(0).sum())}]
pd.DataFrame(tab).to_csv(R/'tables/table1_baseline.csv',index=False)
sens=[]
for col,name in [('appointment_days','Billing index to latest appointment'),('admission_days','Billing index to latest admission'),('both_admission_days','Admission index to latest admission')]:
 sens.append({'definition':name,'patients':len(idx),'zero_days':int(idx[col].eq(0).sum()),'positive_days':int(idx[col].gt(0).sum()),'missing_days':int(idx[col].isna().sum()),'negative_days':int(idx[col].lt(0).sum()),'uncapped_days':int(idx[col].sum()),'capped730_proxy_days':int(idx[col].clip(upper=730).sum()),'observed_events730':int(idx.event730.sum())})
pd.DataFrame(sens).to_csv(R/'tables/table2_followup.csv',index=False)
idx.appointment_days.value_counts().sort_index().rename_axis('appointment_days').rename('patients').to_csv(R/'tables/followup_distribution.csv')
pd.DataFrame([{'variable':c,'missing_n':int(analysis[c].isna().sum()),'missing_percent':float(analysis[c].isna().mean()*100),'distinct_nonmissing':int(analysis[c].nunique())} for c in analysis]).to_csv(R/'tables/missingness.csv',index=False)
summary={'n':len(idx),'events730':int(idx.event730.sum()),'any_repeat':int(idx.repeat_gap_days.notna().sum()),'index_start':str(idx.index_date.min().date()),'index_end':str(idx.index_date.max().date()),'proxy_days':int(idx.appointment_proxy_days730.sum()),'verified_followup_available':0,'calendar730':int(idx.calendar730_available.sum()),'bmi_flagged':int(idx.bmi_review_flag.sum()),'strict_first_n':int(idx.prior_observed45378.eq(0).sum()),'broad':{'patients':len(b),'billing_rows':len(p),'distinct_days':len(days),'repeat_patients_anytime':int(b.gap.notna().sum()),'repeat730':int(b.gap.between(1,730).sum())},'diagnosis_rows':len(dx),'icd9_bleeding_rows':int(dx.code.eq('569.3').sum()),'ibd_any_export':int(idx.ibd_code_any_export.sum()),'flow':dict(flow)}
# Definition sensitivity and direct independent set checks.
bothkeys=set(map(tuple,dx.loc[dx.code.isin(['K62.5','569.3']),K].drop_duplicates().to_numpy()))
bothpat={r.PatientID for r in p.itertuples() if (r.PatientID,r.EncounterID) in bothkeys}
codekeys=set(map(tuple,dx.loc[dx.code.eq('K62.5'),K].drop_duplicates().to_numpy()))
direct={r.PatientID for r in p.itertuples() if (r.PatientID,r.EncounterID) in codekeys}
summary['icd9_sensitivity_n']=len(bothpat)
checks={'unique_patient_rows':not idx.PatientID.duplicated().any(),'independent_eligibility_set':set(idx.PatientID)==direct,'event_censor_complements':bool(idx.event730.add(idx.censor).eq(1).all()),'no_negative_appointment_durations':bool(idx.appointment_days.ge(0).all()),'constant_entry_flags':bool(idx.variable2.eq(1).all() and idx.variable4.eq(1).all()),'no_id_or_exact_dates_in_analysis_file':not any(c in analysis for c in ['PatientID','index_encounter_id']+datecols),'primary_event_recheck':sum(any(0<(dt-row.index_date).days<=730 for dt in days.loc[days.PatientID.eq(row.PatientID),'date']) for row in idx.itertuples())==idx.event730.sum()}
assert all(checks.values()),checks
(R/'documentation/validation.json').write_text(json.dumps({'checks':{k:bool(v) for k,v in checks.items()},'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'openpyxl':openpyxl.__version__},indent=2))
(R/'tables/results.json').write_text(json.dumps(summary,indent=2,default=int))
print(json.dumps(summary,indent=2,default=int))
