"""Independent descriptive broad-cohort sensitivity; no diagnosis restriction or regression."""
from pathlib import Path
import argparse, json, hashlib, math
import pandas as pd
import openpyxl
ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();S=a.source_root;R=a.output
data={};meta=[]
for name in ['Colonoscopy','EGD']:
 p=S/'Research Project/Drivers for Repeat Endoscopy'/f'{name} dataset.xlsx'
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);rows=w['ProceduresProFee'].values;d=pd.DataFrame(rows,columns=next(rows));w.close()
 d['date']=pd.to_datetime(d.Date,errors='coerce').dt.normalize();d['code']=d.TermCodeMapped.fillna('').astype(str).str.strip();d=d[d.date.between('2000-01-01','2023-05-31')]
 data[name]=d;meta.append({'source':name,'relative_path':str(p.relative_to(S)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
pool=pd.concat(data.values(),ignore_index=True);results=[]
for name,origin,codes in [('Colonoscopy45378','Colonoscopy',['45378']),('ColonoscopyCore','Colonoscopy',['45378','45380']),('EGDCore','EGD',['43235','43239'])]:
 d=data[origin];ix=d[d.code.isin(codes)].sort_values(['PatientID','date','EncounterID']).groupby('PatientID').head(1)[['PatientID','date']].rename(columns={'date':'index_date'})
 ix=ix.sort_values('PatientID').reset_index(drop=True);ix.insert(0,'study_id',[f'{name}_{i:06d}' for i in range(1,len(ix)+1)])
 for search,procs in [('Original procedure workbook',d),('Both procedure workbooks',pool)]:
  z=procs[procs.code.isin(codes)][['PatientID','date']].drop_duplicates().merge(ix[['PatientID','index_date']],on='PatientID',validate='many_to_one');z['gap']=(z.date-z.index_date).dt.days
  nxt=z[z.gap.gt(0)].sort_values(['PatientID','gap']).groupby('PatientID').head(1)
  m=ix.merge(nxt[['PatientID','gap']],on='PatientID',how='left',validate='one_to_one');m['event730']=m.gap.between(1,730).astype(int);m['calendar730']=(pd.Timestamp('2023-05-31')-m.index_date).dt.days.ge(730)
  for population in ['All index patients','730 calendar days available']:
   v=m if population.startswith('All') else m[m.calendar730];n=len(v);x=int(v.event730.sum());ph=x/n;zz=1.959963984540054;center=(ph+zz*zz/(2*n))/(1+zz*zz/n);half=zz*math.sqrt(ph*(1-ph)/n+zz*zz/(4*n*n))/(1+zz*zz/n)
   results.append({'cohort':name,'index_codes':'/'.join(codes),'followup_search':search,'population':population,'n':n,'observed_first_repeat730':x,'observed_percent':ph*100,'wilson_low_percent':100*(center-half),'wilson_high_percent':100*(center+half),'interpretation':'Recorded-event proportion; continuous observation unverified'})
  if search.startswith('Both'):
   m[['study_id','PatientID','index_date']].to_csv(R/f'restricted/{name}_linkage.csv',index=False);m['index_year']=m.index_date.dt.year
   m[['study_id','index_year','gap','event730','calendar730']].to_csv(R/f'data/supplement_{name}.csv',index=False)
 # Cross-source check in the primary cohort, without changing its index.
 if name=='Colonoscopy45378':
  primary=pd.read_csv(R/'restricted/cohort_with_source_keys.csv',parse_dates=['index_date']);r=pool[pool.code.eq('45378')][['PatientID','date']].drop_duplicates().merge(primary[['PatientID','index_date']],on='PatientID');g=(r.date-r.index_date).dt.days
  assert not g.between(1,730).any()
pd.DataFrame(results).to_csv(R/'tables/table3_broad_sensitivity.csv',index=False)
pd.DataFrame(meta).to_csv(R/'documentation/supplement_source_manifest.csv',index=False)
print(pd.DataFrame(results).to_string(index=False))
