"""Create final reports, figures, field dictionaries, and reproducibility documentation."""
from pathlib import Path
import os,sys,json,html,hashlib
import pandas as pd
import numpy as np
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch

R=Path(__file__).resolve().parents[1]; Q=R.parent/'shah_publication_qa';Q.mkdir(exist_ok=True)
deps=R.parent/'cox_analysis/dependencies'
if deps.exists():sys.path.append(str(deps))
os.environ['MPLCONFIGDIR']=str(Q/'mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
T=R/'tables'; D=R/'documentation'
main=json.loads((T/'results.json').read_text()); ext=json.loads((T/'extended_results.json').read_text())
est=pd.read_csv(T/'Repeat estimates.csv'); assoc=pd.read_csv(T/'Exploratory associations.csv')
cox=pd.read_csv(T/'Adjusted Cox results.csv'); fu=pd.read_csv(T/'Follow-up audit.csv'); ph=pd.read_csv(T/'Proportional hazards checks.csv')
coh={ds:pd.read_csv(R/f'data/extended_{ds}_analysis.csv') for ds in ['Colonoscopy','EGD']}
def estimate(ds,definition):
 return est[(est.dataset==ds)&est.definition.eq(definition)].iloc[0]
def fmt(x):return f'{int(x):,}'
def result(ds,definition):
 x=estimate(ds,definition);return f'{fmt(x.events)}/{fmt(x.n)} ({x.proportion*100:.2f}%; 95% CI {x.ci_low*100:.2f}-{x.ci_high*100:.2f}%)'
core='Both source workbooks; core codes; first repeat within 730; calendar opportunity'
sym='Symptom-positive first core index; any core repeat; calendar opportunity'
same='Symptom-positive first core index; first repeat shares coded symptom; calendar opportunity'
def atext(ds,term):
 v=assoc[(assoc.dataset==ds)&assoc.term.eq(term)].iloc[0]
 return f'{v.adjusted_recorded_probability_ratio:.2f} (95% CI {v.ci_low:.2f}-{v.ci_high:.2f})'

# Broad cohort baseline and time distribution, computed from the delivered patient files.
base=[];timing=[]
for ds,d in coh.items():
 f=d[d.calendar730];e=f[f.repeat730]
 base.append([ds,len(d),len(f),int(f.GenderCode.eq('F').sum()),int((~f.diagnosis_available).sum()),int(f.target_symptom.sum()),int(e.shape[0]),float(e.repeat_gap.median())])
 for low,high in [(1,30),(31,90),(91,365),(366,730)]:timing.append([ds,f'{low}-{high}',int(e.repeat_gap.between(low,high).sum()),len(e)])
baseline=pd.DataFrame(base,columns=['cohort','all_index_n','calendar730_n','female_n_calendar730','missing_dx_n_calendar730','target_symptom_n_calendar730','events730','median_repeat_days_events'])
baseline.to_csv(T/'table4_broad_baseline.csv',index=False)
timing=pd.DataFrame(timing,columns=['cohort','first_repeat_days','events','all_events730']);timing.to_csv(T/'table5_repeat_timing.csv',index=False)

# A matched source-ascertainment comparison, not a comparison of clinical risk between procedures.
fig,axs=plt.subplots(1,2,figsize=(10,3.8))
for ax,ds in zip(axs,['Colonoscopy','EGD']):
 local=estimate(ds,'Original source only; core codes; first repeat within 730; calendar opportunity');both=estimate(ds,core)
 ax.bar(['Original source','Both sources'],[local.events,both.events],color=['#a7b3be','#214e70'],width=.55)
 for i,x in enumerate([local.events,both.events]):ax.text(i,x+both.events*.025,fmt(x),ha='center',fontweight='bold')
 ax.set_ylim(0,both.events*1.2);ax.set_title(f'{ds} | same {fmt(both.n)} index patients');ax.set_ylabel('Patients with recorded first repeat')
fig.tight_layout();fig.savefig(R/'figures/figure1_source_ascertainment.png',dpi=300);fig.savefig(R/'figures/figure1_source_ascertainment.svg');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,3.5))
for ax,ds in zip(axs,['Colonoscopy','EGD']):
 x=timing[timing.cohort.eq(ds)];ax.bar(x.first_repeat_days,x.events,color='#214e70')
 for i,row in enumerate(x.itertuples()):ax.text(i,row.events+max(x.events)*.025,fmt(row.events),ha='center')
 ax.set_title(ds);ax.set_xlabel('Days from index to first repeat');ax.set_ylabel('Patients');ax.set_ylim(0,max(x.events)*1.2)
fig.tight_layout();fig.savefig(R/'figures/figure2_repeat_timing.png',dpi=300);fig.savefig(R/'figures/figure2_repeat_timing.svg');plt.close(fig)

refs=[
'1. Benchimol EI, Smeeth L, Guttmann A, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. PLoS Med. 2015;12:e1001885. https://doi.org/10.1371/journal.pmed.1001885',
'2. Kotecha D, Asselbergs FW, Achenbach S, et al. CODE-EHR best practice framework for the use of structured electronic healthcare records in clinical research. BMJ. 2022;378:e069048. https://doi.org/10.1136/bmj-2021-069048',
'3. Zou G. A modified Poisson regression approach to prospective studies with binary data. Am J Epidemiol. 2004;159:702-706. https://doi.org/10.1093/aje/kwh090',
'4. Gupta S, Lieberman D, Anderson JC, et al. Recommendations for follow-up after colonoscopy and polypectomy: a consensus update by the US Multi-Society Task Force on Colorectal Cancer. Gastrointest Endosc. 2020;91:463-485.e5. https://www.asge.org/home/resources/publications/guidelines/recommendations-for-follow-up-after-colonoscopy-and-polypectomy-a-consensus-update-by-the-us-multi-society-task-force-on-colorectal-cancer',
'5. STROBE Initiative. Checklist for cohort studies. https://www.strobe-statement.org/fileadmin/Strobe/uploads/checklists/STROBE_checklist_v4_cohort.pdf'
]

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=10.5,leading=14.5,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=5))
styles.add(ParagraphStyle(name='CellX',fontName='Helvetica',fontSize=9,leading=12))
styles.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=21,leading=25,spaceAfter=14))
styles.add(ParagraphStyle(name='HeadX',fontName='Helvetica-Bold',fontSize=14,leading=18,spaceAfter=10,spaceBefore=7))
def para(text,style='BodyX'):return Paragraph(html.escape(str(text)).replace('\n','<br/>'),styles[style])
def table(headers,rows,widths=None):
 data=[[para(c,'CellX') for c in headers]]+[[para(c,'CellX') for c in row] for row in rows]
 tab=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf1')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#7d8b98')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d9dfe4'))]))
 return tab
class Doc:
 def __init__(self,name,title):self.name=name;self.story=[para(title,'TitleX')];self.md=['# '+title,''];self.title=title
 def p(self,s):self.story.append(para(s));self.md.extend([s,''])
 def h(self,s):self.story.append(para(s,'HeadX'));self.md.extend(['## '+s,''])
 def page(self,s):self.story.append(PageBreak());self.h(s)
 def tab(self,headers,rows,widths=None):
  self.story.append(table(headers,rows,widths));self.story.append(Spacer(1,10));self.md.extend(['| '+' | '.join(map(str,headers))+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('\n',' ') for x in row)+' |' for row in rows]+[''])
 def image(self,file,caption):
  self.story.append(Image(str(R/'figures'/file),width=7*inch,height=2.65*inch));self.story.append(para(caption,'SmallX'));self.md.extend([f'![{caption}](figures/{file})',''])
 def save(self):
  def footer(canvas,doc):
   canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526170'));canvas.drawString(45,27,'Repeat endoscopy research | Final project deliverable | October 24 2026');canvas.drawRightString(567,27,str(doc.page))
  SimpleDocTemplate(str(R/(self.name+'.pdf')),pagesize=(612,792),rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=45,title=self.title,author='Research project team').build(self.story,onFirstPage=footer,onLaterPages=footer)
  (R/(self.name+'.md')).write_text('\n'.join(self.md),encoding='utf-8')

report=Doc('Final scientific report','Repeat endoscopy patterns and ascertainment in electronic health record extracts')
report.p('Final scientific deliverables for Dr Eric Shah | October 24 2026')
report.p('This project establishes recorded repeat-endoscopy patterns in the available data, quantifies how source linkage and cohort definitions change those patterns, and evaluates exploratory associations. The analytic work is complete for the supplied extracts. The strongest conclusions concern documented utilization and ascertainment; these data cannot establish the population incidence of repeat endoscopy or identify unnecessary care.')
report.h('Principal findings')
report.tab(['Finding','Final result and meaning'],[
['Recorded repeat colonoscopy',result('Colonoscopy',core)+' after a diagnostic or biopsy index procedure.'],
['Recorded repeat EGD',result('EGD',core)+' after a diagnostic or biopsy index procedure.'],
['Additional source coverage','Linking the second procedure workbook recovered 24 additional colonoscopy and 18 additional EGD repeat patients in the fixed calendar-opportunity cohorts.'],
['Bleeding-defined component','65 qualifying patients; zero observed later 45378 procedures in the original colonoscopy source. Only five patients had positive appointment-based follow-up. Zero observed events does not establish zero clinical risk.'],
['Clinical interpretation','Repeated testing and overlapping symptom codes are measurable. Appropriateness, new-provider effects and same-indication repeat ordering are not identifiable from these extracts.']], [135,387])
report.p('The analysis population is selected by historical source queries. The colonoscopy and EGD cohorts can contain the same individuals and should not be added together as a unique-person total. Two years of calendar opportunity is not proof of continuous follow-up. All findings are observational and exploratory; no causal claim is made.')
report.h('What is delivered')
report.p('The package includes this report, an editable manuscript and printable manuscript, prepared patient-level datasets, exact model inputs, aggregate tables, high-resolution figures, a field dictionary, source checksums, reproducible code and validation records. Source identifiers and exact dates are isolated in the restricted folder. The package remains internal research data and is not a public-use data release.')

report.page('Research questions and design')
report.p('Design: retrospective analysis of linked, routinely collected electronic health record and professional-fee extracts spanning January 1, 2000 through May 31, 2023. The analysis uses a fixed existing sample; no prospective sample-size target or post hoc power calculation is claimed. The final statistical specification was completed with knowledge of these data and is not represented as preregistered.')
report.tab(['Component','Population and endpoint'],[
['Broad colonoscopy','Earliest observed CPT 45378 or 45380 patient-day in the colonoscopy workbook. Outcome: first later patient-day with either core code in either procedure workbook.'],
['Broad EGD','Earliest observed CPT 43235 or 43239 patient-day in the EGD workbook. Outcome: first later patient-day with either core code in either procedure workbook.'],
['Bleeding-defined colonoscopy','Earliest 45378 encounter with same-patient, same-encounter K62.5. Outcome: later-day 45378 for any reason through day 730.'],
['Clinical symptom component','At the first core index, any abdominal pain, constipation or rectal bleeding for colonoscopy; any abdominal pain, heartburn or dysphagia for EGD. A repeat may be for any indication.'],
['Shared symptom component','The first repeat has at least one target diagnosis-code group shared with the index. This is coded overlap, not adjudicated persistence of the same indication.']], [125,397])
report.p('The broad recorded-event estimand is the proportion with a documented first repeat on days 1-730 among index patients with at least 730 calendar days before the cutoff. This restriction standardizes calendar opportunity only. Separate all-index-patient counts retain people with shorter calendar opportunity. Primary descriptive results retain the original source-specific index and broaden only the follow-up search, permitting a matched assessment of source ascertainment.')
report.p('The restricted bleeding analysis answers a different question from the broad cohorts. It is retained in full and is not expanded to manufacture outcome events. First observed qualifying procedure does not mean first lifetime procedure. Same-day records are consolidated; repeated billing lines and multiple diagnosis rows are not repeat procedures.')
report.h('Scope of clinical claims')
report.p('A billed procedure does not establish a completed high-quality examination, a normal examination, an unnecessary examination or a new order. Surveillance recommendations depend on findings, examination quality and clinical context [4]. The data lack sufficiently validated findings, pathology, bowel preparation, order linkage and longitudinal provider assignments for appropriateness or provider-change inference.')

report.page('How the analysis data were prepared')
report.p('Original workbooks were read directly rather than treating previous joined CSV files as the analytic source. Files were retained unchanged. The source manifests record SHA-256 checksums, and every transformation is implemented in the supplied code. The source cutoff remains May 31, 2023; the analysis date does not extend follow-up.')
report.tab(['Step','Implementation'],[
['1 Source selection','Professional-fee procedures, encounter dates and demographics come from the procedure-specific original workbooks. Dedicated coded-diagnosis replacements supply encounter flags; the Clinic workbook supplies appointment timestamps.'],
['2 Complete EGD diagnosis import','Both DiagnosesEverything worksheets were read: 1,000,000 plus 119,247 rows. A single-sheet import would omit 119,247 records. The combined diagnosis data are deduplicated by patient, encounter, code and description.'],
['3 Normalize and link','Dates are parsed and normalized to calendar dates. Codes are trimmed and uppercased where appropriate. Diagnoses join on PatientID AND EncounterID, never on PatientID alone.'],
['4 Aggregate before joining','Presence flags are maximized within encounter. Broad-cohort same-day encounters are then consolidated at patient-day level; the earliest core procedure day defines index.'],
['5 Derive outcomes','Collapse repeat evidence to distinct patient-days, require date strictly after index, select the first repeat and calculate elapsed days. Count events through day 730 inclusively.'],
['6 Preserve ascertainment','Store event, available calendar duration, appointment duration, admission duration and modeled follow-up separately. Missing follow-up is never automatically replaced with 730 days.'],
['7 Export and validate','Export one row per patient per cohort and each exact model input. Use study IDs in analysis files and retain the local source-key crosswalk separately. Reconcile all numerators and denominators to the source derivations.']], [125,397])
report.p('No clinical values were imputed. Unknown diagnosis coverage is explicitly flagged. Source AGE is retained only in the bleeding cohort audit, with an unverified reference date, and is never relabeled age at index. Recorded gender is retained using the source meaning. Smoking and medical history unavailable at the exact index are not treated as clinically absent.')
report.p('The original data dictionary uses 24 months for mood and overlapping pain diagnoses. Those constructs are not inferred from an undocumented alternate lookback. Valid baseline timing and complete observation are unavailable, so those planned predictors are not analyzed. BMI is described at the exact index encounter only. The GI-department flag indicates an available order from a named department, not the identity of the endoscopist or a new referring provider.')

report.page('Final descriptive findings')
rows=[]
for ds in ['Colonoscopy','EGD']:
 dd=ext['details'][ds];rows.append([ds,fmt(dd['index_patients']),result(ds,core),result(ds,sym),result(ds,same)])
report.tab(['Cohort','All index patients','Any core repeat','Symptom index then any repeat','Symptom index and shared code at first repeat'],rows,[65,65,130,130,132])
report.p('The last three columns use patients with 730 calendar days available. Symptom columns use their own symptom-positive index denominators. All intervals are Wilson 95% intervals for recorded-event proportions; they do not quantify uncertainty from extraction bias or outside-system missing events.')
report.image('figure1_source_ascertainment.png','Figure 1. Recorded first-repeat patients increase when both sources are searched, with index membership and calendar opportunity held fixed.')
report.p('The second source increases observed colonoscopy repeat ascertainment by 15.4% relative to the original 156 repeat patients (24 additional), versus 0.64% relative to 2,817 EGD repeat patients (18 additional). This is evidence of source fragmentation, not an intervention effect or the sensitivity of either source against a gold standard.')
report.p('After both EGD diagnosis worksheets are included, unavailable index-diagnosis counts are '+str(ext['details']['Colonoscopy']['missing_index_diagnoses'])+' in colonoscopy and '+str(ext['details']['EGD']['missing_index_diagnoses'])+' in EGD across all index patients. These are current source-coverage findings; blank coding is not evidence that symptoms were clinically absent.')

report.page('Timing and clinical interpretation')
report.image('figure2_repeat_timing.png','Figure 2. Distribution of first recorded core repeats among patients with 730 calendar days available. Same-day records are excluded.')
report.tab(['Cohort','Median days to first repeat among events','First repeat on days 31-730','Any repeat on days 31-730'],[[ds,str(ext['details'][ds]['median_gap_among_730_events']),result(ds,'Core codes; first repeat occurs days 31–730; calendar opportunity'),result(ds,'Core codes; any procedure days 31–730; calendar opportunity')] for ds in ['Colonoscopy','EGD']],[80,115,160,167])
report.p('The first-repeat and any-repeat definitions differ because an early repeat can be followed by another later procedure. Excluding early first repeats changes the endpoint; it does not adjudicate the early procedures as inappropriate. A short interval may reflect incomplete preparation, completion of an examination, therapy or evolving symptoms, none of which can be reliably resolved here.')
report.p('EGD has a higher recorded-repeat proportion than colonoscopy in these selected extracts. These are different clinical populations with different selection and coding mechanisms. A cross-procedure risk ratio would invite an unsupported causal or case-mix interpretation and is not reported.')
report.p('Shared symptom coding supplies a narrower description of recurrent symptom-associated utilization. It remains an operational measure: incidental diagnoses can coexist with a different principal indication, and coding may persist even when the reason for repeat testing changes. No count in this package is labeled low-value or unnecessary endoscopy.')
report.h('Scientific contribution')
report.p('The findings jointly show that repeat-procedure research is sensitive to both the clinical index definition and where subsequent care is retrieved. Narrow bleeding eligibility can produce a zero-event subset while broader source populations have observable repeats. Source linkage recovers additional events without changing the index cohort, and complete multi-sheet diagnosis import prevents an avoidable loss of clinical characterization.')

report.page('Statistical methodology and exploratory associations')
report.p('Descriptive analyses report counts, proportions, missingness, medians and interquartile ranges. Wilson confidence intervals accompany broad recorded-event proportions. Models are exploratory, with no multiplicity correction and no causal interpretation. The complete coefficient tables, including nonsignificant results, are supplied.')
report.p('Modified Poisson regression with HC0 robust standard errors models recorded repeat by day 730 among patients with calendar opportunity [3]. Separate models include recorded female versus male gender, index era (2000-2011, 2012-2015, 2016 onward), clinically relevant symptom groups and an unavailable-diagnosis indicator where it varies. The model outputs are adjusted recorded-event probability ratios. They are not hazard ratios or population risk ratios under complete surveillance.')
report.tab(['EGD predictor','Adjusted recorded-event probability ratio'],[[v.replace('_',' ').capitalize(),atext('EGD',v)] for v in ['female','abdominal_pain','heartburn','dysphagia']],[260,262])
report.p('Symptom and recorded-gender associations may reflect case mix, indication, coding practice, source selection and follow-up capture. Age at index is unavailable; residual confounding is substantial. Constancy and zero-event exposure strata are checked, and the rectal-bleeding term is omitted from broad colonoscopy regression rather than presenting an unstable near-zero coefficient.')
report.p('Cox models use Efron tie handling and the same nonredundant predictors under three observation assumptions: calendar cutoff/horizon; latest recorded contact (admission, appointment or procedure); and latest appointment supplemented by repeat-procedure evidence. Outcomes are bounded by day 730 and the cutoff. Zero-duration records are excluded only from that model and enumerated. A recorded repeat supplies contact evidence, creating potential outcome-dependent follow-up; the resulting models are sensitivity analyses rather than validated survival estimators.')
report.p('Rank-transformed Schoenfeld-residual tests assess proportional hazards. Days 1-90 and 91-730 fits examine time-varying patterns; these are exploratory splits. Hazard ratios can change with the observation rule. No single model is selected as definitive because its p values are preferable. Independent statsmodels PHReg fits verify the main lifelines Cox coefficients and standard errors.')
report.p('All final interval fits converged, with a smaller optimization step used for stable estimation. Constant or zero-event binary strata are checked and any omissions are logged. Robustness analyses excluding index IBD codes and restricting to known index diagnoses are supplied separately. Excluding index IBD leaves colonoscopy unchanged and yields 2,775/38,142 EGD repeat patients (7.28%), close to the overall recorded proportion.')
report.p('The specified age-forced and forward/backward Cox analysis is non-estimable in the bleeding-defined cohort because there are no events, and age at index is unverified. Variables 2 and 4 are constant by entry criteria. No stepwise model, penalized substitute or fabricated hazard ratio is used for that component. Broad models address a separate exploratory population and do not masquerade as completion of the restricted model.')

report.page('Observation sensitivity and the bleeding component')
report.tab(['Cohort and observation rule','Analyzed patients','Events','Excluded for zero or unavailable time'],[[str(r.dataset)+' / '+str(r.scenario),fmt(r.n),fmt(r.events),fmt(r.zero_followup)] for r in fu.itertuples()],[270,75,65,112])
report.p('The event count is stable across these observation rules, while the amount of available time and the included risk set change markedly. Event capture and non-event observation therefore have different evidentiary strength. The supplied survival estimates are assumption-dependent sensitivity outputs; they are not endorsed as complete-capture two-year incidence.')
report.p('For EGD, the dysphagia hazard ratio changes from 1.05 (95% CI 0.95-1.15) under calendar follow-up to 1.46 (1.33-1.59) under the latest-contact proxy. The female-gender hazard ratio remains below 1 across all three rules (approximately 0.74-0.77). Five of seven EGD calendar-model terms show proportional-hazards test p values below 0.05. These findings favor reporting model sensitivity and time variation, rather than declaring dysphagia an established independent driver.')
report.p('Exploratory interval models show a stronger dysphagia association early: calendar-rule HR 1.98 (1.65-2.37) on days 1-90 versus 0.87 (0.78-0.97) on days 91-730. Contact-rule estimates are 2.42 (2.02-2.89) and 1.25 (1.12-1.39), respectively. A single overall HR therefore conceals important time variation; the late association also depends on observation assumptions.')
report.p('In the bleeding-defined component, index dates span January 25, 2016 to February 6, 2023. There are 65 patients, 36 with female recorded gender, and zero observed later 45378 events in the original source. Searching both procedure workbooks also finds no 45378 repeat within 730 days. Fifty-five patients have two years of calendar opportunity, but only five have any positive appointment duration.')
report.tab(['Follow-up definition','Zero days','Positive days','Capped proxy days'],[[r.definition,r.zero_days,r.positive_days,r.capped730_proxy_days] for r in pd.read_csv(T/'table2_followup.csv').itertuples()],[310,65,65,82])
report.p('The appointment distribution is 60 at day 0, two at day 1, two at day 3 and one at day 948. Capping at 730 yields 738 proxy patient-days, not verified person-time. The first-observed-procedure eligibility sensitivity retains 64 patients; adding ICD-9 code 569.3 retains 65; neither produces a repeat event. Admission-based duration changes do not resolve the lack of events.')

report.page('Limitations and final conclusions')
report.p('Selection: source queries contain extensive diagnosis exclusions, including code 569.3 in exclusion blocks. The supplied files cannot determine how the extraction engine executed the mapping or how many eligible source patients were removed. The dedicated colonoscopy diagnosis replacement contains two 569.3 rows, neither linked to an eligible index. Adding this code locally cannot reconstruct excluded encounters.')
report.p('Outcome ascertainment: follow-up may be filtered by the extraction design; out-of-system care, death, enrollment and complete observation are unavailable. Appointments can be scheduled rather than completed visits. No-reported-repeat is not synonymous with no repeat procedure. Broad confidence intervals account for binomial variation, not these systematic errors.')
report.p('Clinical classification: billing and diagnosis codes do not establish completed procedure quality, principal indication, ordering intent or appropriateness. K59 includes conditions beyond constipation, R10.1 denotes upper abdominal pain rather than diagnosed functional dyspepsia, and R10.8/R10.9 are other or unspecified abdominal pain codes. These labels are handled as code groups, not asserted clinical diagnoses.')
report.p('Confounding and transportability: verified age, complete baseline disease history and provider trajectories are unavailable. Recorded gender and symptom associations should be interpreted within the filtered source population. Calendar-era effects may reflect clinical practice, code-system changes or source selection. The clinical cohorts overlap and are analyzed separately.')
report.p('Final conclusion: the available extracts establish documented repeat endoscopy and shared-symptom coding patterns, with materially greater event ascertainment after cross-source linkage. They also demonstrate that narrow eligibility and incomplete follow-up can yield a misleadingly reassuring zero-event result. These are completed findings from this project; population incidence, appropriateness and provider-change effects remain outside what the data can identify.')
report.h('Publication positioning')
report.p('The accompanying manuscript is positioned as a retrospective descriptive study of recorded utilization and ascertainment, with exploratory associations. It does not require additional clinical investigation to support the stated conclusions. Author identities and contributions, institutional setting details, ethics/IRB determination, funding, conflicts and permission to disclose data must be supplied by the authors before journal submission; none is invented here. These are publication declarations, not uncompleted analytic work.')
report.page('References')
for ref in refs:report.p(ref)
report.save()

man=Doc('Scientific manuscript','Recorded repeat endoscopy and source ascertainment in linked electronic health record extracts')
man.h('Structured abstract')
man.p('Background: Repeat endoscopy may reflect persistent symptoms, surveillance, procedural completion or other clinical needs. Estimates derived from selected electronic health record extracts depend on cohort definitions and ascertainment of subsequent care.')
man.p('Objective: To describe recorded first-repeat endoscopy, evaluate cross-source event ascertainment and characterize symptom-associated patterns in available colonoscopy and esophagogastroduodenoscopy (EGD) extracts.')
man.p('Methods: We conducted a retrospective descriptive analysis of records dated January 1, 2000 through May 31, 2023. Index procedures were the first observed diagnostic or biopsy colonoscopy (45378/45380) or EGD (43235/43239) in their respective source workbooks. Diagnoses were linked by patient and encounter, including both parts of the EGD coded-diagnosis export. Distinct later procedure days were searched across both workbooks. We calculated recorded first-repeat proportions through day 730 among patients with calendar opportunity, Wilson intervals, symptom-code overlap and exploratory adjusted associations. A separate rectal-bleeding-defined colonoscopy component was retained.')
man.p('Results: Broad cohorts contained 12,776 colonoscopy and 41,772 EGD patients. Among patients with 730 calendar days available, recorded first-repeat proportions were '+result('Colonoscopy',core)+' for colonoscopy and '+result('EGD',core)+' for EGD. Cross-source follow-up recovered 24 and 18 additional repeat patients, respectively. Among symptom-positive index patients, first repeats sharing a target symptom were '+result('Colonoscopy',same)+' and '+result('EGD',same)+'. The bleeding-defined component included 65 patients and zero observed repeats; 60 had zero appointment-based follow-up days. Observation assumptions markedly changed modeled risk sets.')
man.p('Conclusions: Repeat endoscopy and overlapping symptom codes are demonstrable in these extracts, but their measured frequency depends on source coverage and eligibility. These results describe recorded utilization rather than validated population incidence or low-value care.')
man.p('Keywords: colonoscopy; esophagogastroduodenoscopy; repeat endoscopy; electronic health records; ascertainment; observational research.')

man.page('Introduction')
man.p('Repeat endoscopic procedures can occur for multiple clinical reasons, including evolving symptoms, surveillance and completion of an inadequate examination. Interpreting repeat utilization requires knowledge of the index findings, examination quality and clinical context. Guideline-based follow-up after colonoscopy depends on these factors [4]; the presence of a repeat procedure alone cannot establish inappropriate care.')
man.p('Routinely collected data offer a way to examine utilization, but extraction criteria can select the index population and restrict follow-up simultaneously. Multiple billing rows may also describe one procedure. Transparent code definitions, linkage and data preparation are therefore essential [1,2]. We examined recorded first-repeat endoscopy, the contribution of searching an additional procedure source and symptom-code overlap. We retained a narrower bleeding-defined component to show how the clinical index definition changes the available evidence.')
man.h('Methods')
man.p('We analyzed existing institutional EHR-derived relational workbooks covering January 1, 2000 through May 31, 2023. The fixed source extracts define the sample; their original age eligibility was not independently verifiable at the index date. Source AGE lacked a verified reference date and was not used as age at index. Each procedure-specific workbook defined its own index cohort. Patients could contribute to both procedure cohorts, which were not pooled for inferential analyses.')
man.p('Core colonoscopy codes were 45378 and 45380; core EGD codes were 43235 and 43239. The first observed core patient-day in the corresponding workbook defined the index. A repeat was the earliest later calendar day with a core code in either procedure workbook, through day 730 inclusively. Same-day billing rows were consolidated. Source-specific indices were held fixed when comparing original-source with combined-source follow-up. Calendar opportunity required index plus 730 days to fall on or before the cutoff; it did not require future clinical encounters.')
man.p('Diagnoses were normalized and aggregated within patient/encounter before linkage. Same-day index encounters were aggregated within patient-day. Both EGD diagnosis worksheets were included, totaling 1,119,247 rows before combined-source deduplication. Clinical code groups were abdominal pain R10*/789.0*, constipation K59.0*/564.0*, rectal bleeding K62.5/569.3, heartburn R12/787.1 and dysphagia R13*/787.2*. Missing encounter diagnoses were flagged separately from negative code groups. Shared-symptom first repeat required at least one target code group at both index and first repeat; it did not establish the principal indication.')
man.p('A separate component selected the first qualifying 45378 encounter with K62.5 and searched for later 45378 for any reason. The earliest qualifying encounter was distinguished from requiring the first observed procedure to qualify. Appointment-based and admission-based durations were retained as unverified follow-up proxies. No synthetic positive duration was assigned to zero-follow-up patients.')

man.page('Statistical analysis')
man.p('We report observed counts and proportions, Wilson 95% confidence intervals, and repeat-interval distributions. Confidence intervals describe sampling variability in recorded events and do not incorporate missed procedures or source-selection bias. Analysis of the broad calendar-opportunity cohorts used modified Poisson regression with HC0 robust standard errors [3]. Covariates were recorded female gender, index era, procedure-relevant symptom groups and unavailable diagnoses when varying. Constant or zero-event exposure strata were omitted rather than estimated with unstable coefficients. All model estimates are exploratory; no multiple-testing correction was applied.')
man.p('Cox models with Efron ties were fitted as sensitivity analyses under calendar-based, latest-recorded-contact and latest-appointment-plus-repeat observation rules. Follow-up was bounded by the study cutoff and day 730. Positive-duration analytic populations, exclusions and events are reported for each rule. Rank-based Schoenfeld checks and early/late interval fits assessed proportional-hazards stability. Independent software fits verified main coefficients and standard errors. The zero-event bleeding component did not support univariable, multivariable or stepwise Cox estimation. Age was not forced into any model using an unverified substitute.')
man.p('No structural missingness was imputed. The final analysis was developed after review of the available data and is exploratory rather than preregistered. Prepared datasets, code lists, source manifests and full model tables accompany the report, consistent with transparent reporting of routinely collected data [1,2,5].')
man.h('Results')
man.p('The source-specific broad cohorts included 12,776 colonoscopy and 41,772 EGD patients. Of these, 12,462 and 38,864, respectively, had 730 calendar days available. Combined-source searches identified 180 and 2,835 first-repeat patients within this window. Original-source searches identified 156 and 2,817; thus cross-source retrieval added 24 colonoscopy and 18 EGD repeat patients without changing index membership (Table 1; Figure 1).')
man.p('The median first-repeat interval among events with calendar opportunity was '+str(ext['details']['Colonoscopy']['median_gap_among_730_events'])+' days for colonoscopy and '+str(ext['details']['EGD']['median_gap_among_730_events'])+' days for EGD. First repeats on days 31-730 occurred in '+result('Colonoscopy','Core codes; first repeat occurs days 31–730; calendar opportunity')+' and '+result('EGD','Core codes; first repeat occurs days 31–730; calendar opportunity')+', respectively. Counting any repeat in that interval gives different numerators because some patients had an earlier first repeat (Figure 2).')
man.p('Among symptom-positive index patients, any first core repeat occurred in '+result('Colonoscopy',sym)+' for colonoscopy and '+result('EGD',sym)+' for EGD. Shared-symptom first repeats occurred in '+result('Colonoscopy',same)+' and '+result('EGD',same)+', respectively. These counts identify overlapping coded symptoms, not confirmed repeat testing for an unchanged indication.')

man.page('Results continued')
man.p('Exploratory EGD adjusted recorded-event probability ratios were '+atext('EGD','female')+' for female recorded gender, '+atext('EGD','abdominal_pain')+' for abdominal pain, '+atext('EGD','heartburn')+' for heartburn and '+atext('EGD','dysphagia')+' for dysphagia. These associations are conditional on the included variables and extraction design. Complete coefficients, including calendar era and nonsignificant terms, are available in the accompanying tables.')
man.p('Censoring choices substantially changed the number of patients with analyzable positive follow-up while retaining observed events. Consequently, sensitivity hazard ratios and cumulative-repeat estimates should not be interpreted as uniquely identified population parameters. The data lack verified continuous observation and death information, and contact-based observation may depend on care-seeking and the outcome itself.')
man.p('For example, the EGD dysphagia hazard ratio was 1.05 (95% CI 0.95-1.15) with calendar follow-up and 1.46 (1.33-1.59) with the latest-contact proxy. Five of seven EGD calendar-model terms had proportional-hazards test p values below 0.05. Excluding index-encounter IBD codes yielded 2,775/38,142 EGD patients with recorded repeats (7.28%); colonoscopy was unchanged. Restriction to known index diagnoses produced similar descriptive proportions (supplementary tables).')
man.p('The EGD dysphagia association was stronger on days 1-90 than days 91-730: calendar-rule HRs were 1.98 (95% CI 1.65-2.37) and 0.87 (0.78-0.97); contact-rule HRs were 2.42 (2.02-2.89) and 1.25 (1.12-1.39). These exploratory interval results support time-varying associations, with the late estimate additionally dependent on the observation rule.')
man.p('The bleeding-defined component contained 65 patients with no observed later 45378 in the original source; no repeat within 730 days was recovered from the second procedure source. Sixty patients had zero appointment follow-up days, two had one day, two had three days and one had 948 days. The capped appointment proxy totaled 738 days. Requiring the first observed 45378 to qualify reduced the component to 64 patients; adding ICD-9 bleeding retained 65. These findings do not establish an absence of repeat colonoscopy in a clinically complete bleeding cohort.')
man.page('Discussion')
man.p('Three findings are supported. First, repeat endoscopy is observable in the broader source populations even when a narrow bleeding-defined subset has no events. Second, searching another source changes event ascertainment while holding the index population fixed. The proportional gain is greater for colonoscopy than EGD in these data, consistent with differing source fragmentation. Third, a subset of first repeats shares symptom codes with the index, providing a reproducible description of recurrent symptom-associated utilization without assigning appropriateness.')
man.p('The apparent difference between colonoscopy and EGD is not a causal comparison: their clinical populations, indications and extraction mechanisms differ. Symptom and gender associations may reflect these mechanisms and incomplete adjustment. Importing all diagnosis worksheets is necessary for clinical characterization; row limits or single-sheet assumptions can otherwise create artificial missingness. Association estimates should therefore be understood as features of these selected recorded data.')
man.p('Limitations include preexisting diagnosis exclusions, uncertain completeness of subsequent procedures, missing outside-system care, unavailable death/enrollment data, unverified age at index and absence of clinically adjudicated indications or examination quality. Code 569.3 appears in saved source-query exclusion blocks, creating uncertainty about the representativeness of bleeding eligibility. The local data cannot reconstruct patients removed upstream. Confidence intervals and robust standard errors do not correct these biases.')
man.p('In conclusion, this completed project characterizes recorded repeat endoscopy and demonstrates the influence of source coverage and cohort definition. Its defensible interpretation is a descriptive utilization and ascertainment study, with exploratory associations. It does not estimate unnecessary endoscopy, effects of provider change or complete-capture population incidence.')

man.page('Tables and figure legends')
man.tab(['Table 1 Cohort','Original source repeats','Both-source repeats','Both-source proportion with 95% CI'],[[ds,fmt(estimate(ds,'Original source only; core codes; first repeat within 730; calendar opportunity').events),fmt(estimate(ds,core).events),result(ds,core)] for ds in ['Colonoscopy','EGD']],[100,100,100,222])
man.p('Denominators: 12,462 colonoscopy and 38,864 EGD index patients with at least 730 calendar days before May 31, 2023. Index membership and core-code definitions are held fixed across follow-up sources. Intervals are Wilson intervals for recorded-event proportions.')
man.tab(['Table 2 Symptom component','Any core repeat','First repeat sharing a target symptom'],[[ds,result(ds,sym),result(ds,same)] for ds in ['Colonoscopy','EGD']],[110,206,206])
man.p('Target symptoms: colonoscopy, abdominal pain/constipation/rectal bleeding; EGD, abdominal pain/heartburn/dysphagia. Groups can overlap. Shared coding is not adjudicated principal indication or low-value care.')
man.p('Figure 1. Recorded first-repeat patients under original-source and combined-source follow-up, with index membership fixed. Figure 2. Distribution of first-repeat intervals among patients with 730 calendar days available. Figures are supplied as 300 dpi PNG and editable SVG files.')
man.h('Publication declarations')
man.p('Authorship and affiliations, institutional setting description, ethics/IRB determination and consent waiver if applicable, funding, conflicts of interest and data-access permission require author-supplied factual declarations before submission. No ethics approval, exemption, funding source or authorship contribution is asserted by this analytic package. Patient-level datasets are restricted research materials; the public manuscript should contain aggregate results only.')
man.page('References')
for ref in refs:man.p(ref)
man.save()

cx=Doc('Cox proportional hazards analysis','Cox proportional hazards analysis of recorded repeat endoscopy')
cx.p('Final analysis for Dr Eric Shah | October 24 2026')
cx.p('Cox models were fitted separately for broad colonoscopy and EGD cohorts under three follow-up assumptions. The first later-day core procedure is the event, through day 730. Hazard ratios are exploratory associations within selected extracts. Unverified observation, missing age at index and nonproportional hazards limit clinical interpretation. The bleeding-defined cohort has zero events and no estimable Cox model.')
cx.h('Analysis populations')
cx.tab(['Cohort and follow-up rule','N analyzed','Events','Zero-time exclusions'],[[r.dataset+' / '+r.scenario,fmt(r.n),fmt(r.events),fmt(r.zero_followup)] for r in fu.itertuples()],[285,80,60,97])
cx.p('Calendar follow-up ends at the earlier of day 730 and May 31, 2023. The contact proxy additionally uses the latest available admission, appointment or procedure. The appointment proxy uses the latest appointment supplemented by repeat evidence. All rules retain observed repeats; proxy rules remove many zero-duration non-event records. These are different observation assumptions and analytic populations, not interchangeable estimates of one validated clinical risk.')
cx.h('Key interpretation')
cx.p('Female recorded gender is associated with lower recorded-repeat EGD hazard across all three assumptions (HR approximately 0.74-0.77). EGD dysphagia is inconclusive under calendar follow-up (HR 1.05; 95% CI 0.95-1.15) but positive under contact follow-up (1.46; 1.33-1.59). Thus dysphagia cannot be called a robust independent driver. Neither finding establishes a causal effect, and age is not controlled.')
cx.p('Models use Efron ties and a fixed nonredundant exploratory predictor set. The main lifelines results were independently reproduced with statsmodels PHReg for both cohorts under calendar and contact rules, with maximum absolute log-HR differences below 0.0001. No forward/backward model is estimable for the zero-event bleeding component. Broad models are not a substitute for that restricted analysis.')
for ds in ['Colonoscopy','EGD']:
 cx.page(ds+' hazard ratios')
 scenarios=['Administrative','Last recorded contact','Last appointment plus repeat evidence']
 terms=cox.loc[(cox.dataset==ds)&(cox.scenario=='Administrative'),'term'].tolist()
 rows=[]
 for term in terms:
  cells=[term.replace('_',' ')]
  for sc in scenarios:
   v=cox[(cox.dataset==ds)&(cox.scenario==sc)&(cox.term==term)].iloc[0]
   pv='<0.001' if v.p_value<.001 else f'= {v.p_value:.3f}'
   cells.append(f'{v.hazard_ratio:.2f} ({v.ci_low:.2f}-{v.ci_high:.2f})\np {pv}')
  rows.append(cells)
 cx.tab(['Predictor','Calendar rule','Contact proxy','Appointment proxy'],rows,[135,129,129,129])
 cx.p('Cells show hazard ratio (95% confidence interval) and two-sided exploratory p value. Reference categories: male recorded gender; index years 2000-2011; no recorded symptom code among patients with available diagnoses. unknown dx indicates unavailable index diagnoses. The model retains no-code symptom flags plus this indicator for unknown records; no-code is not verified clinical absence.')
 cx.p('Calendar-era indicators are 2012-2015 and 2016 onward. Colonoscopy includes abdominal pain and constipation; rectal bleeding is omitted because its exposed group has zero events. EGD includes abdominal pain, heartburn and dysphagia. Verified index age, complete baseline comorbidity and provider-change measures are unavailable. Hazard ratios are not risk ratios, and residual confounding and coding-era effects remain.')
 if ds=='EGD':cx.p('The 2016 onward era estimate changes from approximately 0.92 under calendar follow-up to 2.10 under the contact proxy. This reversal reinforces the dependence of associations on observation selection; it is not evidence of a proven increase or decrease in underlying clinical utilization over time.')
cx.page('Proportional hazards diagnostics and model limits')
rows=[]
for ds in ['Colonoscopy','EGD']:
 for term in cox.loc[(cox.dataset==ds)&(cox.scenario=='Administrative'),'term']:
  cells=[ds+' / '+term.replace('_',' ')]
  for sc in ['Administrative','Last recorded contact','Last appointment plus repeat evidence']:
   v=ph[(ph.dataset==ds)&(ph.scenario==sc)&(ph.term==term)].p_value.iloc[0];cells.append('<0.001' if v<.001 else f'{v:.3f}')
  rows.append(cells)
cx.tab(['Predictor','Calendar p','Contact p','Appointment p'],rows,[285,79,79,79])
cx.p('Rank-transformed Schoenfeld-residual tests. Small p values suggest time-varying associations; multiple tests are exploratory. Five of seven EGD calendar-model terms have p<0.05. Absence of significance does not prove proportional hazards. A single constant HR should not be treated as an adequate description where the assumption is doubtful.')
audit=json.loads((D/'cox_model_audit.json').read_text());failed=[v for v in audit['fits'] if v.get('status')]
cx.p('Early/late analyses split at day 90. Constant or zero-event binary strata are checked before interval fits and any omissions are logged. All eight final interval fits converged without penalization. Full interval results and optimization details are supplied in Early and late hazard ratios.csv and cox_model_audit.json.')
cx.p('The prepared data/model_*.csv files contain the exact positive-duration input matrices. Follow-up audit.csv, Proportional hazards checks.csv, Adjusted Cox results.csv, Survival estimates and risk sets.csv and cox_verification.json provide the full audit trail. Survival estimates are scenario-dependent sensitivity calculations and must not be quoted as validated two-year incidence. Missing death information precludes a competing-risk analysis.')
cx.page('Early and late EGD associations')
iv=pd.read_csv(T/'Early and late hazard ratios.csv'); iv=iv[iv.dataset.eq('EGD')]
rows=[]
for term in cox.loc[(cox.dataset=='EGD')&(cox.scenario=='Administrative'),'term']:
 cells=[term.replace('_',' ')]
 for sc,period in [('Administrative','Days 1-90'),('Administrative','Days 91-730'),('Last recorded contact','Days 1-90'),('Last recorded contact','Days 91-730')]:
  v=iv[iv.scenario.eq(sc)&iv.period.eq(period)&iv.term.eq(term)].iloc[0]
  cells.append(f'{v.hazard_ratio:.2f}\n({v.ci_low:.2f}-{v.ci_high:.2f})')
 rows.append(cells)
cx.tab(['Predictor','Calendar days 1-90','Calendar days 91-730','Contact days 1-90','Contact days 91-730'],rows,[126,99,99,99,99])
cx.p('Hazard ratios with 95% confidence intervals. Later-period models use delayed entry at day 90 and include only patients still under the scenario-specific observation rule beyond that day. The early models have 596 events; later models have 2,356. These counts include all index dates with positive follow-up, so they differ from descriptive counts restricted to full calendar opportunity.')
cx.p('Dysphagia has a stronger relative recorded-repeat hazard early under both assumptions: 1.98 versus 0.87 with the calendar rule, and 2.42 versus 1.25 with the contact proxy. This pattern helps explain why the overall calendar-model HR is close to 1 despite a proportional-hazards violation. The result supports time variation within these data, not a clinical mechanism or a causal effect.')
cx.p('The early fits required a smaller optimization step of 0.1 for stable unpenalized estimation. No covariates or records were removed to obtain these EGD fits. All eight early/late models across both procedure cohorts were independently checked with a second implementation. Full colonoscopy interval estimates and all interval p values remain in the accompanying CSV table.')
cx.save()

# Field-level dictionary for every delivered analysis dataset, including exact model inputs.
defs={
'study_id':'Package-specific patient identifier within the stated cohort. Cross-cohort prefixes are not a unique-person linkage.',
'variable1':'Any literal K59. diagnosis at the index; broader than clinical constipation.',
'variable2':'K62.5 rectal bleeding code at the index.',
'variable3':'In analysis_cohort: any other K62 code even if bleeding coexists. In extended datasets: another K62 code AND no K62.5 at the index.',
'variable3_exclusive':'Other K62 code AND no K62.5 at index; retained to expose the encounter-level ambiguity.',
'variable3_any_other_code':'Other K62 code even when K62.5 coexists at the index.',
'variable4':'Any of variables 1, 2 or 3.',
'variable5':'R10.1 prefix: upper abdominal pain, not confirmed functional dyspepsia.',
'variable6':'R10.2 prefix: pelvic pain.',
'variable7':'R10.3 prefix: lower abdominal pain.',
'variable8':'R10.8 or R10.9 prefix: other or unspecified abdominal pain.',
'variable9':'Any of variables 5 through 8.',
'repeat_gap_days':'Days to earliest later-day 45378 in original colonoscopy source; missing means no later observed target procedure.',
'repeat_gap':'Days to earliest later-day core repeat across both procedure workbooks; missing means none recorded.',
'gap':'Days to earliest later-day core repeat across both workbooks; missing means none recorded.',
'appointment_days':'Latest Clinic appointment date minus billing index date; unverified observation proxy.',
'admission_days':'Latest original colonoscopy admission date minus billing index date.',
'both_admission_days':'Latest admission date minus admission date of the qualifying index encounter.',
'calendar_days':'May 31 2023 minus index date in days; not observed follow-up.',
'event730':'1 if a first target repeat is recorded on days 1-730; otherwise 0.',
'censor':'1 minus event730; does not imply follow-up is clinically verified.',
'legacy_event_time':'Observed repeat gap if <=730, else legacy sentinel 731; missing if no observed repeat.',
'legacy_followup_days':'Legacy event time if present; otherwise appointment_days. Not valid person-time by default.',
'appointment_proxy_days730':'Appointment proxy capped by calendar cutoff and 730, with unknown observation retained.',
'admission_proxy_days730':'Admission proxy capped by calendar cutoff and 730.',
'both_admission_proxy_days730':'Both-admission duration capped at 730.',
'no_positive_appointment_followup':'1 if appointment duration is zero or negative; otherwise 0.',
'calendar730_available':'1 if index plus 730 days <= May 31 2023. Not complete observation.',
'calendar730':'True if 730 calendar days available before source cutoff. Not complete observation.',
'prior_observed45378':'1 if an earlier 45378 exists before the first bleeding-qualifying index.',
'index_year':'Calendar year of the index procedure.',
'source_age_unanchored':'Source AGE with unknown reference date; not usable as verified index age.',
'GenderCode':'Source recorded gender code; F female, M male; not independently verified biological sex.',
'GenderName':'Source recorded gender label.',
'age_at_index':'Verified age at index; unavailable for all bleeding-cohort patients.',
'female_recorded_gender':'F=1 and M=0 from source recorded gender; other/unknown missing.',
'index_height_cm':'Numeric height at exact index encounter, centimeters; blank if unavailable.',
'index_weight_kg':'Numeric weight at exact index encounter, kilograms; blank if unavailable.',
'index_bmi':'Numeric BMI at exact index encounter, kg/m2; blank if unavailable.',
'bmi_review_flag':'1 if observed BMI outside 10-80; screening flag only, not clinical adjudication.',
'index_order_rows':'Number of order records at exact index encounter; zero means no available rows.',
'gi_department_proxy':'Any index order department matching GI liver/gastroenterology/txp/gi proc/med proc unit/hepatology; missing if no order rows.',
'index_history_rows':'Number of medical-history rows at the exact index encounter; zero is lack of rows, not lack of disease.',
'index_smoking_status':'Known Current/Former/Never at exact index; missing if unknown or unavailable.',
'ibd_code_any_export':'Any supplied K50/K51/555/556 code for this patient at any available time; audit only, not timed baseline eligibility.',
'verified_observation_days':'Clinically verified continuous follow-up; unavailable and not imputed.',
'analysis_disposition':'Interpretive restriction for the bleeding-defined cohort.',
'abdominal_pain':'R10 or 789.0 diagnosis prefix at index.',
'constipation':'K59.0 or 564.0 diagnosis prefix at index.',
'rectal_bleeding':'K62.5 or 569.3 diagnosis at index.',
'heartburn':'R12 or 787.1 diagnosis prefix at index.',
'dysphagia':'R13 or 787.2 diagnosis prefix at index.',
'reflux':'K21 or 530.81 diagnosis prefix; distinct from heartburn.',
'ibd':'K50/K51/555/556 diagnosis prefix at index.',
'diagnosis_available':'At least one linked coded diagnosis available for index core procedure day.',
'repeat730':'First core repeat occurs on days 1-730.',
'repeat_any':'Any later recorded core procedure, regardless of elapsed duration.',
'repeat31to730':'Any core repeat on days 31-730, including when first repeat occurred earlier.',
'repeat31to730_first':'First core repeat occurs on days 31-730.',
'n_later_days':'Number of distinct later core procedure days across both sources.',
'target_symptom':'Any target symptom for that procedure cohort at index.',
'same_symptom_first_repeat':'First repeat within 730 days shares at least one target symptom group with index.',
'duration':'Elapsed event or censoring time under the scenario in the filename, capped at 730 and cutoff; positive-duration patients only.',
'event':'Recorded first repeat within the modeled duration; 1 event and 0 censored.',
'female':'F=1, M=0; other/unknown excluded from model inputs and enumerated.',
'era_2012_2015':'Index year 2012-2015 indicator; reference 2000-2011.',
'era_2016_plus':'Index year >=2016 indicator; reference 2000-2011.',
'unknown_dx':'No linked coded diagnosis at index. Model symptom zeros in these rows mean unavailable coding, not clinical absence.'}
defs.update({'era':'Index era categorical predictor: 2000_2011 reference, 2012_2015, 2016_plus.','y':'Binary first recorded core repeat on days 1-730, used as the modified Poisson outcome.'})
dictionary=[]
for f in sorted((R/'data').glob('*.csv')):
 d=pd.read_csv(f)
 for c in d:
  definition=defs.get(c)
  if definition is None and c.startswith('repeat_'):
   corevar=c[len('repeat_'):];definition='At first core repeat: '+defs.get(corevar,corevar)+ ' Missing when no repeat or no linked repeat diagnosis.'
  if definition is None:raise ValueError('Undocumented field '+c)
  if c in ['abdominal_pain','constipation','rectal_bleeding','heartburn','dysphagia','reflux','ibd']:
   definition+=' Interpret with diagnosis_available: a false flag with unavailable diagnoses is unknown clinical status, not confirmed absence.'
  dictionary.append({'file':f.name,'variable':c,'definition':definition,'dtype':str(d[c].dtype),'rows':len(d),'missing_n':int(d[c].isna().sum()),'missing_meaning':'Unavailable/not applicable; never assume clinically negative. For event gaps: no observed qualifying later procedure.','source_and_timing':'See dataset preparation and code; index flags are baseline, repeat_ fields are post-index outcomes and never baseline predictors.'})
pd.DataFrame(dictionary).to_csv(D/'data_dictionary.csv',index=False)

readme='''# Final repeat endoscopy project package

Prepared for Dr Eric Shah. Final analytic deliverables, October 24 2026.

Start with **Final scientific report.pdf**. **Scientific manuscript.pdf** and its matching Markdown file contain the completed scientific narrative. **Cox proportional hazards analysis.pdf** provides the full hazard ratio tables, diagnostic tests and early/late interpretation. All conclusions are limited to the supplied selected extracts; no further clinical investigation is assigned as a project deliverable.

## Files

- `data/analysis_cohort.csv`: the 65-patient bleeding-defined analysis, with unknown verified follow-up explicit.
- `data/extended_Colonoscopy_analysis.csv` and `data/extended_EGD_analysis.csv`: final broad patient cohorts with symptom variables, event timing and ascertainment flags. Both EGD diagnosis parts are included.
- `data/model_*.csv`: exact pseudonymous Cox input matrices for every observation scenario. The broader patient files also contain all inputs for the modified Poisson models; the analysis code applies the calendar-opportunity and recorded-gender restrictions.
- `data/supplement_*.csv`: independent procedure-only reconstruction used to verify broad event counts.
- `tables/`: all aggregate results, missingness, all coefficients, proportional-hazards checks and interval analyses. No omitted nonsignificant model rows.
- `figures/`: 300 dpi PNG and editable SVG figures.
- `documentation/data_dictionary.csv`: field definitions and missingness for every analysis file.
- `documentation/`: source hashes, verification, query-exclusion evidence and reproducibility notes.
- `restricted/`: local source identifiers, exact dates, detailed encounter derivations and model audit files. Internal authorized research access only.
- `code/`: reproducible derivation and report generation.

## Interpretation and scope

The main scientific analysis is broad recorded utilization and source ascertainment. The bleeding-defined component preserves the narrower definition and has no estimable Cox model. Broad models are exploratory and are not age-adjusted, because verified index age is absent. Do not report observed proportions as complete-capture incidence or repeats as unnecessary care. Do not merge cohort-specific study IDs across datasets; linkage to source patients is in restricted crosswalks. Patient cohorts can overlap.

## Reproduce

Use Python 3.12 and install the versions recorded in `documentation/software_versions.json`. Keep this package under `SOURCE_ROOT/outputs/shah_publication_package`, or adjust SOURCE in the extended/contact scripts to the source root. Original workbook relative paths and hashes are recorded in the source manifests. Original data are not duplicated into the distribution.

Run, in order:

```
python code/rebuild_analysis.py --source-root SOURCE_ROOT
python code/rebuild_supplement.py --source-root SOURCE_ROOT
python code/rebuild_extended.py
python code/prepare_contacts.py
python code/run_cox.py
python code/verify_cox.py
python code/final_robustness.py
python code/build_deliverables.py
python code/validate_package.py
```

The scripts read the original workbooks and do not require old joined datasets or prior analysis results. Local dependency fallback paths are optional; a normal environment with the recorded packages works without them. Do not rerun on changed source files without recording a new source manifest and version. Code and CSV are UTF-8. Dates are ISO formatted in restricted files. Blank values are missing, not zero.

## Data handling

Study IDs remove direct source keys from the analysis files, but this is pseudonymization, not a certified de-identification determination. Patient-level data and linkage files are not journal supplements or public downloads. The distribution is for the authorized project team. Public-facing scientific content is in the aggregate reports, tables and figures, subject to institutional disclosure rules.

## Publication declarations

No further data collection is required for the bounded conclusions delivered here. A journal submission still requires factual author/affiliation, ethics/IRB, consent-waiver if applicable, funding/conflict and data-sharing declarations. Those administrative facts cannot be inferred or fabricated from the analysis. No email was sent and no external files were uploaded.
'''
(R/'README.md').write_text(readme,encoding='utf-8')

methods='''# Dataset preparation and statistical analysis specification

Status: final implemented exploratory analysis of the supplied data. This specification is not represented as prospectively registered.

## Source precedence

Use original procedure-specific workbooks for procedure dates and codes. Use dedicated diagnosis replacement workbooks for coded encounter diagnoses; include both EGD parts. Use Dataset/colonoscopy clinic.xlsx for Clinic appointment timestamps. Prefer original relational data to legacy patient-only joins. Retain the original source-specific index for matched comparisons of follow-up sources. Additional supplied duplicate workbooks are not additional patients.

## Cohort and variables

Primary broad reporting uses first observed 45378/45380 colonoscopy or 43235/43239 EGD in the original respective source. First later-day core repeat for any reason is identified across both procedure workbooks. Same-day records collapse to one patient-day. Day 1 through 730 is inclusive. First observed does not imply first lifetime. Core codes do not encompass every therapeutic procedure; expanded procedure-family and pooled-index sensitivities appear in Repeat estimates.csv and their exact code lists are in rebuild_extended.py.

Clinical code groups are specified in the manuscript. Prefix matching uses literal string prefixes, not an unescaped decimal regular expression. The nine requested ICD-10 groups are supplied separately from the mixed-era clinical symptom groups. Broad variable3 is encounter/patient-day exclusive of K62.5; variable3_any_other_code retains coexisting other K62 codes. In the 65-patient component, variable3 retains coexisting other K62 codes and variable3_exclusive supplies the alternative. All bleeding-component patients have variable3_exclusive=0. This ambiguity cannot yield an estimable restricted model because the outcome has zero events under either interpretation.

Do not include composite variables alongside all their components. Do not model variable2 or variable4 in the bleeding component because they are constant. Repeat symptom flags and provider information at the repeat are post-index and cannot be used as baseline predictors. The original 24-month baseline disease constructs are not approximated with a new undocumented window.

## Statistical estimands

1. Recorded first-repeat proportion among patients with 730 calendar days available. Wilson intervals apply to the recorded binary endpoint and do not account for systematic missing events.
2. Matched source contribution, holding index membership and code scope constant. Report added repeat patients and relative gain over original-source counts.
3. Shared-symptom code overlap at first repeat among symptom-positive index patients. This is not a clinically adjudicated same-indication endpoint.
4. Exploratory adjusted recorded-event probability ratios from modified Poisson regression with HC0 robust covariance. Model formula: repeat730 ~ female + era + procedure-specific symptoms + unknown_dx (if varying). The eras are 2000-2011/reference, 2012-2015, 2016 onward. Rectal bleeding is omitted from broad colonoscopy if its exposure stratum contains no events. Model missing diagnosis as an explicit category indicator; false symptom flags in such rows mean no available code, not known clinical absence.
5. Sensitivity Cox hazard ratios under calendar, contact and appointment-plus-repeat observation rules. Use Efron ties; exclude zero/unavailable durations and unknown gender from the model only, enumerate all exclusions, retain the original cohort in descriptive tables. The contact proxy uses latest available admission/appointment/procedure dates, not a certified observation period. Repeat evidence itself can extend this proxy. No competing-risk analysis is possible without death data.

## Model interpretation

No age adjustment is claimed. Baseline BMI, smoking, overlapping pain, mood conditions and provider continuity do not have adequate validated timing/coverage for the broad models. No imputation is used to invent entirely absent information. Forward/backward selection is not performed in the zero-event bleeding cohort and is not silently substituted into a different population. Broad models use the reported fixed exploratory covariate set. All p values are two-sided, exploratory and unadjusted for multiple comparisons; 95% intervals describe conditional model uncertainty.

Proportional hazards are assessed with rank-transformed Schoenfeld residuals; early and late fits split at day 90. A significant test or a changing interval estimate cautions against a single constant hazard ratio. Zero events are reported as non-estimable, not solved by artificial censoring times or a penalized estimate. We do not report a rule-of-three upper bound for the underlying clinical risk because ascertainment is inadequate.

## Reconciliation

The original-source 45378-only cohort has 89 events across all 8,133 index patients but 88 events among the 7,939 with 730 calendar days. Using 89/7,939 mixes two populations. Both-source follow-up yields 90/7,939. The final independent reconstruction preserves these distinct denominators. Core broad results reconcile to 180/12,462 colonoscopy and 2,835/38,864 EGD.

All EGD coded diagnoses now include the 119,247-row second sheet. Earlier single-sheet symptom estimates and models are superseded by the supplied final complete-sheet results. Primary procedure counts need not change when diagnosis coverage changes. Source-exclusion evidence remains a limitation even after full local import.
'''
(D/'Dataset preparation and analysis specification.md').write_text(methods,encoding='utf-8')
checklist=[['Title and abstract','Manuscript title and structured abstract','Retrospective routinely collected data; recorded-event outcome identified'],['Setting and selection','Methods; source manifests; cohort tables','Source study window and eligibility stated; exact institutional description remains an author declaration'],['Variables and linkage','Methods; data dictionary; code','Patient+encounter linkage and patient-day consolidation documented'],['Bias','Discussion; final report','Selection, incomplete follow-up, missing age, coding and ascertainment addressed'],['Study size and missingness','Baseline and missingness CSV files','Fixed available sample; no post hoc power claim'],['Statistical methods','Analysis specification; full model tables','Exploratory status, sensitivity assumptions and missingness handling documented'],['Results and uncertainty','Tables and figures','Denominators, events and Wilson/model intervals supplied'],['Validation','validation.json; cox_verification.json','Computational validation completed; no clinical gold-standard validation claimed'],['Interpretation','Discussion','No low-value care, provider-change or complete population-risk claim'],['Ethics and other information','Publication declarations','Author-supplied IRB, funding, conflicts and affiliations required before journal submission']]
pd.DataFrame(checklist,columns=['STROBE_RECORD_domain','package_location','status']).to_csv(D/'reporting_checklist.csv',index=False)
import importlib.metadata as im
extra=R.parent/'repeat_endoscopy_analysis/dependencies'
if extra.exists():sys.path.append(str(extra))
versions={p:im.version(p) for p in ['pandas','numpy','openpyxl','statsmodels','lifelines','matplotlib','reportlab','pypdf','scipy','Pillow']}
(D/'software_versions.json').write_text(json.dumps(versions,indent=2))
(R/'code/requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n')
print('Reports, figures, dictionaries and methods created.',flush=True)
