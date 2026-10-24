# Cox proportional hazards analysis of recorded repeat endoscopy

Final analysis for Dr Eric Shah | October 24 2026

Cox models were fitted separately for broad colonoscopy and EGD cohorts under three follow-up assumptions. The first later-day core procedure is the event, through day 730. Hazard ratios are exploratory associations within selected extracts. Unverified observation, missing age at index and nonproportional hazards limit clinical interpretation. The bleeding-defined cohort has zero events and no estimable Cox model.

## Analysis populations

| Cohort and follow-up rule | N analyzed | Events | Zero-time exclusions |
| --- | --- | --- | --- |
| Colonoscopy / Administrative | 12,776 | 181 | 0 |
| Colonoscopy / Last recorded contact | 3,437 | 181 | 9,339 |
| Colonoscopy / Last appointment plus repeat evidence | 1,402 | 181 | 11,374 |
| EGD / Administrative | 41,767 | 2,952 | 5 |
| EGD / Last recorded contact | 16,944 | 2,952 | 24,828 |
| EGD / Last appointment plus repeat evidence | 9,261 | 2,952 | 32,511 |

Calendar follow-up ends at the earlier of day 730 and May 31, 2023. The contact proxy additionally uses the latest available admission, appointment or procedure. The appointment proxy uses the latest appointment supplemented by repeat evidence. All rules retain observed repeats; proxy rules remove many zero-duration non-event records. These are different observation assumptions and analytic populations, not interchangeable estimates of one validated clinical risk.

## Key interpretation

Female recorded gender is associated with lower recorded-repeat EGD hazard across all three assumptions (HR approximately 0.74-0.77). EGD dysphagia is inconclusive under calendar follow-up (HR 1.05; 95% CI 0.95-1.15) but positive under contact follow-up (1.46; 1.33-1.59). Thus dysphagia cannot be called a robust independent driver. Neither finding establishes a causal effect, and age is not controlled.

Models use Efron ties and a fixed nonredundant exploratory predictor set. The main lifelines results were independently reproduced with statsmodels PHReg for both cohorts under calendar and contact rules, with maximum absolute log-HR differences below 0.0001. No forward/backward model is estimable for the zero-event bleeding component. Broad models are not a substitute for that restricted analysis.

## Colonoscopy hazard ratios

| Predictor | Calendar rule | Contact proxy | Appointment proxy |
| --- | --- | --- | --- |
| female | 0.87 (0.64-1.18) p = 0.361 | 0.73 (0.54-0.99) p = 0.046 | 0.73 (0.54-0.99) p = 0.040 |
| era 2012 2015 | 1.19 (0.73-1.95) p = 0.483 | 1.38 (0.83-2.27) p = 0.213 | 0.88 (0.53-1.45) p = 0.604 |
| era 2016 plus | 0.49 (0.26-0.91) p = 0.023 | 1.64 (0.87-3.11) p = 0.126 | 1.09 (0.58-2.04) p = 0.792 |
| abdominal pain | 1.18 (0.84-1.64) p = 0.340 | 1.08 (0.78-1.51) p = 0.639 | 1.09 (0.78-1.52) p = 0.628 |
| constipation | 0.89 (0.56-1.41) p = 0.617 | 0.88 (0.55-1.39) p = 0.582 | 0.92 (0.58-1.45) p = 0.714 |
| unknown dx | 1.45 (0.36-5.87) p = 0.603 | 3.47 (0.85-14.14) p = 0.082 | 2.61 (0.64-10.61) p = 0.180 |

Cells show hazard ratio (95% confidence interval) and two-sided exploratory p value. Reference categories: male recorded gender; index years 2000-2011; no recorded symptom code among patients with available diagnoses. unknown dx indicates unavailable index diagnoses. The model retains no-code symptom flags plus this indicator for unknown records; no-code is not verified clinical absence.

Calendar-era indicators are 2012-2015 and 2016 onward. Colonoscopy includes abdominal pain and constipation; rectal bleeding is omitted because its exposed group has zero events. EGD includes abdominal pain, heartburn and dysphagia. Verified index age, complete baseline comorbidity and provider-change measures are unavailable. Hazard ratios are not risk ratios, and residual confounding and coding-era effects remain.

## EGD hazard ratios

| Predictor | Calendar rule | Contact proxy | Appointment proxy |
| --- | --- | --- | --- |
| female | 0.77 (0.71-0.82) p <0.001 | 0.74 (0.69-0.79) p <0.001 | 0.74 (0.68-0.79) p <0.001 |
| era 2012 2015 | 0.95 (0.86-1.05) p = 0.297 | 1.32 (1.20-1.46) p <0.001 | 1.25 (1.13-1.38) p <0.001 |
| era 2016 plus | 0.92 (0.84-1.01) p = 0.084 | 2.10 (1.92-2.30) p <0.001 | 1.96 (1.79-2.14) p <0.001 |
| abdominal pain | 0.52 (0.47-0.57) p <0.001 | 0.83 (0.75-0.91) p <0.001 | 0.84 (0.76-0.92) p <0.001 |
| heartburn | 0.40 (0.33-0.48) p <0.001 | 0.72 (0.59-0.86) p <0.001 | 0.71 (0.59-0.86) p <0.001 |
| dysphagia | 1.05 (0.95-1.15) p = 0.331 | 1.46 (1.33-1.59) p <0.001 | 1.43 (1.30-1.56) p <0.001 |
| unknown dx | 2.20 (0.98-4.90) p = 0.054 | 5.35 (2.40-11.93) p <0.001 | 4.93 (2.21-11.00) p <0.001 |

Cells show hazard ratio (95% confidence interval) and two-sided exploratory p value. Reference categories: male recorded gender; index years 2000-2011; no recorded symptom code among patients with available diagnoses. unknown dx indicates unavailable index diagnoses. The model retains no-code symptom flags plus this indicator for unknown records; no-code is not verified clinical absence.

Calendar-era indicators are 2012-2015 and 2016 onward. Colonoscopy includes abdominal pain and constipation; rectal bleeding is omitted because its exposed group has zero events. EGD includes abdominal pain, heartburn and dysphagia. Verified index age, complete baseline comorbidity and provider-change measures are unavailable. Hazard ratios are not risk ratios, and residual confounding and coding-era effects remain.

The 2016 onward era estimate changes from approximately 0.92 under calendar follow-up to 2.10 under the contact proxy. This reversal reinforces the dependence of associations on observation selection; it is not evidence of a proven increase or decrease in underlying clinical utilization over time.

## Proportional hazards diagnostics and model limits

| Predictor | Calendar p | Contact p | Appointment p |
| --- | --- | --- | --- |
| Colonoscopy / female | 0.316 | 0.185 | 0.228 |
| Colonoscopy / era 2012 2015 | 0.126 | 0.741 | 0.812 |
| Colonoscopy / era 2016 plus | 0.002 | 0.238 | 0.156 |
| Colonoscopy / abdominal pain | 0.276 | 0.422 | 0.293 |
| Colonoscopy / constipation | 0.457 | 0.478 | 0.510 |
| Colonoscopy / unknown dx | 0.303 | 0.249 | 0.309 |
| EGD / female | <0.001 | 0.007 | 0.013 |
| EGD / era 2012 2015 | 0.038 | 0.168 | 0.295 |
| EGD / era 2016 plus | 0.937 | 0.207 | 0.247 |
| EGD / abdominal pain | <0.001 | <0.001 | <0.001 |
| EGD / heartburn | 0.684 | 0.512 | 0.624 |
| EGD / dysphagia | <0.001 | <0.001 | <0.001 |
| EGD / unknown dx | <0.001 | <0.001 | <0.001 |

Rank-transformed Schoenfeld-residual tests. Small p values suggest time-varying associations; multiple tests are exploratory. Five of seven EGD calendar-model terms have p<0.05. Absence of significance does not prove proportional hazards. A single constant HR should not be treated as an adequate description where the assumption is doubtful.

Early/late analyses split at day 90. Constant or zero-event binary strata are checked before interval fits and any omissions are logged. All eight final interval fits converged without penalization. Full interval results and optimization details are supplied in Early and late hazard ratios.csv and cox_model_audit.json.

The prepared data/model_*.csv files contain the exact positive-duration input matrices. Follow-up audit.csv, Proportional hazards checks.csv, Adjusted Cox results.csv, Survival estimates and risk sets.csv and cox_verification.json provide the full audit trail. Survival estimates are scenario-dependent sensitivity calculations and must not be quoted as validated two-year incidence. Missing death information precludes a competing-risk analysis.

## Early and late EGD associations

| Predictor | Calendar days 1-90 | Calendar days 91-730 | Contact days 1-90 | Contact days 91-730 |
| --- | --- | --- | --- | --- |
| female | 0.63 (0.53-0.74) | 0.81 (0.74-0.87) | 0.64 (0.55-0.75) | 0.77 (0.71-0.83) |
| era 2012 2015 | 1.14 (0.93-1.41) | 0.91 (0.81-1.01) | 1.17 (0.94-1.44) | 1.37 (1.23-1.54) |
| era 2016 plus | 0.97 (0.80-1.18) | 0.91 (0.83-1.01) | 2.05 (1.69-2.50) | 2.11 (1.91-2.34) |
| abdominal pain | 0.95 (0.78-1.15) | 0.44 (0.39-0.49) | 1.40 (1.15-1.69) | 0.71 (0.63-0.79) |
| heartburn | 0.37 (0.23-0.59) | 0.41 (0.33-0.50) | 0.62 (0.39-0.98) | 0.74 (0.60-0.91) |
| dysphagia | 1.98 (1.65-2.37) | 0.87 (0.78-0.97) | 2.42 (2.02-2.89) | 1.25 (1.12-1.39) |
| unknown dx | 12.83 (5.29-31.14) | 0.42 (0.06-3.01) | 22.35 (9.20-54.28) | 1.13 (0.16-8.03) |

Hazard ratios with 95% confidence intervals. Later-period models use delayed entry at day 90 and include only patients still under the scenario-specific observation rule beyond that day. The early models have 596 events; later models have 2,356. These counts include all index dates with positive follow-up, so they differ from descriptive counts restricted to full calendar opportunity.

Dysphagia has a stronger relative recorded-repeat hazard early under both assumptions: 1.98 versus 0.87 with the calendar rule, and 2.42 versus 1.25 with the contact proxy. This pattern helps explain why the overall calendar-model HR is close to 1 despite a proportional-hazards violation. The result supports time variation within these data, not a clinical mechanism or a causal effect.

The early fits required a smaller optimization step of 0.1 for stable unpenalized estimation. No covariates or records were removed to obtain these EGD fits. All eight early/late models across both procedure cohorts were independently checked with a second implementation. Full colonoscopy interval estimates and all interval p values remain in the accompanying CSV table.
