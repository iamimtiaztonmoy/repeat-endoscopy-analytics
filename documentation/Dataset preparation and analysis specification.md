# Dataset preparation and statistical analysis specification

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
