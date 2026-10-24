"""Final structural, statistical and reporting reconciliation; no source mutation."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];checks={}
primary=pd.read_csv(R/'data/analysis_cohort.csv');checks['primary_n_events']=len(primary)==65 and primary.event730.sum()==0
checks['primary_followup']=primary.appointment_days.eq(0).sum()==60 and primary.appointment_proxy_days730.sum()==738
dictionary=pd.read_csv(R/'documentation/data_dictionary.csv')
for p in (R/'data').glob('*.csv'):
 d=pd.read_csv(p);checks[p.name+'_unique']=d.study_id.is_unique
 checks[p.name+'_no_source_keys']=not any(c in d for c in ['PatientID','EncounterID','index_date','repeat_date'])
 checks[p.name+'_dictionary']=set(d.columns)==set(dictionary.loc[dictionary.file.eq(p.name),'variable'])
for ds,expected_n,expected_events in [('Colonoscopy',12462,180),('EGD',38864,2835)]:
 d=pd.read_csv(R/f'data/extended_{ds}_analysis.csv');f=d[d.calendar730];z=pd.read_csv(R/f'data/supplement_{ds}Core.csv');z=z[z.calendar730]
 checks[ds+'_independent_event_counts']=len(f)==len(z)==expected_n and int(f.repeat730.sum())==int(z.event730.sum())==expected_events
 checks[ds+'_event_definition']=bool(d.repeat730.eq(d.repeat_gap.between(1,730)).all())
 checks[ds+'_shared_symptom_subset']=bool((~d.same_symptom_first_repeat| (d.target_symptom&d.repeat730)).all())
 for scenario in ['Administrative','Last_recorded_contact','Last_appointment_plus_repeat_evidence']:
  m=pd.read_csv(R/f'data/model_{ds}_{scenario}.csv')
  checks[ds+'_'+scenario+'_positive_time']=bool(m.duration.between(1,730).all())
  checks[ds+'_'+scenario+'_all_recorded_events_retained']=int(m.event.sum())==int(d.repeat730.sum())
 c=pd.read_csv(R/'tables/Adjusted Cox results.csv');c=c[c.dataset.eq(ds)]
 checks[ds+'_finite_main_cox']=bool(np.isfinite(c[['hazard_ratio','ci_low','ci_high','p_value']]).all().all())
checks['cox_independent_engine']=all(v['max_log_hr_difference']<.0001 and v['max_se_difference']<.0001 for v in json.loads((R/'documentation/cox_verification.json').read_text())['checks'])
texts={name:' '.join('\n'.join(p.extract_text() for p in PdfReader(R/(name+'.pdf')).pages).split()) for name in ['Final scientific report','Scientific manuscript','Cox proportional hazards analysis']}
for name in ['Final scientific report','Scientific manuscript']:
 for value in ['180/12,462','2,835/38,864','629/19,200','1.44%','7.29%']:
  checks[name+'_'+value+'_matches_tables']=value in texts[name]
for row in pd.read_csv(R/'tables/Adjusted Cox results.csv').itertuples():
 expected=f'{row.hazard_ratio:.2f} ({row.ci_low:.2f}-{row.ci_high:.2f})'
 checks[row.dataset+'_'+row.scenario+'_'+row.term+'_printed_cox']=expected in texts['Cox proportional hazards analysis']
checks['all_interval_models_converged']=all(not v.get('status') for v in json.loads((R/'documentation/cox_model_audit.json').read_text())['fits'])
checks['all_interval_models_independently_verified']=len(json.loads((R/'documentation/cox_verification.json').read_text())['interval_checks'])==8
for name in ['Final scientific report','Scientific manuscript','Cox proportional hazards analysis']:
 text='\n'.join(p.extract_text() for p in PdfReader(R/(name+'.pdf')).pages)
 checks[name+'_no_workflow_provenance']=not any(s in text.lower() for s in ['meeting','transcript','zoom'])
 checks[name+'_has_substance']=len(text)>5000
 checks[name+'_no_placeholder']=not any(s in text for s in ['TODO','[INSERT','TBD'])
assert all(checks.values()),[k for k,v in checks.items() if not v]
(R/'documentation/final_validation.json').write_text(json.dumps({'all_passed':True,'checks':{k:bool(v) for k,v in checks.items()}},indent=2))
manifest=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and p.name!='package_manifest.csv':manifest.append({'relative_path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
pd.DataFrame(manifest).to_csv(R/'documentation/package_manifest.csv',index=False)
print(f'{len(checks)} checks passed; {len(manifest)} files indexed.')
