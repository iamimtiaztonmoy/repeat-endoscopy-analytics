from pathlib import Path
import sys,json
PACKAGE=Path(__file__).resolve().parents[1]
SOURCE=PACKAGE.parents[1]
R=PACKAGE/'restricted/cox';R.mkdir(parents=True,exist_ok=True)

import pandas as pd
def read(ds,table):
 p=SOURCE/'Dataset/colonoscopy clinic.xlsx' if ds=='Clinic' else SOURCE/'Research Project/Drivers for Repeat Endoscopy'/f'{ds} dataset.xlsx'
 return pd.read_excel(p,sheet_name=table)
END=pd.Timestamp('2023-05-31')
contacts=[]; appointments=[]; sources=[]
for ds in ['Colonoscopy','EGD','Clinic']:
 d=read(ds,'EncounterAll')
 for col in ['AdmitDate','AppointmentTime']:
  if col not in d:continue
  v=pd.DataFrame({'PatientID':d.PatientID,'date':pd.to_datetime(d[col],errors='coerce').dt.normalize()})
  v=v[v.date.between('2000-01-01',END)]
  contacts.append(v);sources.append({'source':ds,'field':col,'valid_rows':len(v)})
  if col=='AppointmentTime':appointments.append(v)
for ds in ['Colonoscopy','EGD']:
 d=read(ds,'ProceduresProFee')
 v=pd.DataFrame({'PatientID':d.PatientID,'date':pd.to_datetime(d.Date,errors='coerce').dt.normalize()})
 contacts.append(v[v.date.between('2000-01-01',END)])
last=pd.concat(contacts).groupby('PatientID').date.max()
appt=pd.concat(appointments).groupby('PatientID').date.max()
last.rename('last_contact').to_csv(R/'last_contacts.csv')
appt.rename('last_appointment').to_csv(R/'last_appointments.csv')
(R/'contact_sources.json').write_text(json.dumps(sources))

