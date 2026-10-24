# Recorded repeat endoscopy and source ascertainment in linked electronic health record extracts

## Structured abstract

Background: Repeat endoscopy may reflect persistent symptoms, surveillance, procedural completion or other clinical needs. Estimates derived from selected electronic health record extracts depend on cohort definitions and ascertainment of subsequent care.

Objective: To describe recorded first-repeat endoscopy, evaluate cross-source event ascertainment and characterize symptom-associated patterns in available colonoscopy and esophagogastroduodenoscopy (EGD) extracts.

Methods: We conducted a retrospective descriptive analysis of records dated January 1, 2000 through May 31, 2023. Index procedures were the first observed diagnostic or biopsy colonoscopy (45378/45380) or EGD (43235/43239) in their respective source workbooks. Diagnoses were linked by patient and encounter, including both parts of the EGD coded-diagnosis export. Distinct later procedure days were searched across both workbooks. We calculated recorded first-repeat proportions through day 730 among patients with calendar opportunity, Wilson intervals, symptom-code overlap and exploratory adjusted associations. A separate rectal-bleeding-defined colonoscopy component was retained.

Results: Broad cohorts contained 12,776 colonoscopy and 41,772 EGD patients. Among patients with 730 calendar days available, recorded first-repeat proportions were 180/12,462 (1.44%; 95% CI 1.25-1.67%) for colonoscopy and 2,835/38,864 (7.29%; 95% CI 7.04-7.56%) for EGD. Cross-source follow-up recovered 24 and 18 additional repeat patients, respectively. Among symptom-positive index patients, first repeats sharing a target symptom were 48/4,321 (1.11%; 95% CI 0.84-1.47%) and 629/19,200 (3.28%; 95% CI 3.03-3.54%). The bleeding-defined component included 65 patients and zero observed repeats; 60 had zero appointment-based follow-up days. Observation assumptions markedly changed modeled risk sets.

Conclusions: Repeat endoscopy and overlapping symptom codes are demonstrable in these extracts, but their measured frequency depends on source coverage and eligibility. These results describe recorded utilization rather than validated population incidence or low-value care.

Keywords: colonoscopy; esophagogastroduodenoscopy; repeat endoscopy; electronic health records; ascertainment; observational research.

## Introduction

Repeat endoscopic procedures can occur for multiple clinical reasons, including evolving symptoms, surveillance and completion of an inadequate examination. Interpreting repeat utilization requires knowledge of the index findings, examination quality and clinical context. Guideline-based follow-up after colonoscopy depends on these factors [4]; the presence of a repeat procedure alone cannot establish inappropriate care.

Routinely collected data offer a way to examine utilization, but extraction criteria can select the index population and restrict follow-up simultaneously. Multiple billing rows may also describe one procedure. Transparent code definitions, linkage and data preparation are therefore essential [1,2]. We examined recorded first-repeat endoscopy, the contribution of searching an additional procedure source and symptom-code overlap. We retained a narrower bleeding-defined component to show how the clinical index definition changes the available evidence.

## Methods

We analyzed existing institutional EHR-derived relational workbooks covering January 1, 2000 through May 31, 2023. The fixed source extracts define the sample; their original age eligibility was not independently verifiable at the index date. Source AGE lacked a verified reference date and was not used as age at index. Each procedure-specific workbook defined its own index cohort. Patients could contribute to both procedure cohorts, which were not pooled for inferential analyses.

Core colonoscopy codes were 45378 and 45380; core EGD codes were 43235 and 43239. The first observed core patient-day in the corresponding workbook defined the index. A repeat was the earliest later calendar day with a core code in either procedure workbook, through day 730 inclusively. Same-day billing rows were consolidated. Source-specific indices were held fixed when comparing original-source with combined-source follow-up. Calendar opportunity required index plus 730 days to fall on or before the cutoff; it did not require future clinical encounters.

Diagnoses were normalized and aggregated within patient/encounter before linkage. Same-day index encounters were aggregated within patient-day. Both EGD diagnosis worksheets were included, totaling 1,119,247 rows before combined-source deduplication. Clinical code groups were abdominal pain R10*/789.0*, constipation K59.0*/564.0*, rectal bleeding K62.5/569.3, heartburn R12/787.1 and dysphagia R13*/787.2*. Missing encounter diagnoses were flagged separately from negative code groups. Shared-symptom first repeat required at least one target code group at both index and first repeat; it did not establish the principal indication.

A separate component selected the first qualifying 45378 encounter with K62.5 and searched for later 45378 for any reason. The earliest qualifying encounter was distinguished from requiring the first observed procedure to qualify. Appointment-based and admission-based durations were retained as unverified follow-up proxies. No synthetic positive duration was assigned to zero-follow-up patients.

## Statistical analysis

We report observed counts and proportions, Wilson 95% confidence intervals, and repeat-interval distributions. Confidence intervals describe sampling variability in recorded events and do not incorporate missed procedures or source-selection bias. Analysis of the broad calendar-opportunity cohorts used modified Poisson regression with HC0 robust standard errors [3]. Covariates were recorded female gender, index era, procedure-relevant symptom groups and unavailable diagnoses when varying. Constant or zero-event exposure strata were omitted rather than estimated with unstable coefficients. All model estimates are exploratory; no multiple-testing correction was applied.

Cox models with Efron ties were fitted as sensitivity analyses under calendar-based, latest-recorded-contact and latest-appointment-plus-repeat observation rules. Follow-up was bounded by the study cutoff and day 730. Positive-duration analytic populations, exclusions and events are reported for each rule. Rank-based Schoenfeld checks and early/late interval fits assessed proportional-hazards stability. Independent software fits verified main coefficients and standard errors. The zero-event bleeding component did not support univariable, multivariable or stepwise Cox estimation. Age was not forced into any model using an unverified substitute.

No structural missingness was imputed. The final analysis was developed after review of the available data and is exploratory rather than preregistered. Prepared datasets, code lists, source manifests and full model tables accompany the report, consistent with transparent reporting of routinely collected data [1,2,5].

## Results

The source-specific broad cohorts included 12,776 colonoscopy and 41,772 EGD patients. Of these, 12,462 and 38,864, respectively, had 730 calendar days available. Combined-source searches identified 180 and 2,835 first-repeat patients within this window. Original-source searches identified 156 and 2,817; thus cross-source retrieval added 24 colonoscopy and 18 EGD repeat patients without changing index membership (Table 1; Figure 1).

The median first-repeat interval among events with calendar opportunity was 179.5 days for colonoscopy and 273.0 days for EGD. First repeats on days 31-730 occurred in 129/12,462 (1.04%; 95% CI 0.87-1.23%) and 2,632/38,864 (6.77%; 95% CI 6.53-7.03%), respectively. Counting any repeat in that interval gives different numerators because some patients had an earlier first repeat (Figure 2).

Among symptom-positive index patients, any first core repeat occurred in 64/4,321 (1.48%; 95% CI 1.16-1.89%) for colonoscopy and 1,071/19,200 (5.58%; 95% CI 5.26-5.91%) for EGD. Shared-symptom first repeats occurred in 48/4,321 (1.11%; 95% CI 0.84-1.47%) and 629/19,200 (3.28%; 95% CI 3.03-3.54%), respectively. These counts identify overlapping coded symptoms, not confirmed repeat testing for an unchanged indication.

## Results continued

Exploratory EGD adjusted recorded-event probability ratios were 0.78 (95% CI 0.72-0.83) for female recorded gender, 0.54 (95% CI 0.49-0.59) for abdominal pain, 0.40 (95% CI 0.34-0.49) for heartburn and 1.05 (95% CI 0.96-1.15) for dysphagia. These associations are conditional on the included variables and extraction design. Complete coefficients, including calendar era and nonsignificant terms, are available in the accompanying tables.

Censoring choices substantially changed the number of patients with analyzable positive follow-up while retaining observed events. Consequently, sensitivity hazard ratios and cumulative-repeat estimates should not be interpreted as uniquely identified population parameters. The data lack verified continuous observation and death information, and contact-based observation may depend on care-seeking and the outcome itself.

For example, the EGD dysphagia hazard ratio was 1.05 (95% CI 0.95-1.15) with calendar follow-up and 1.46 (1.33-1.59) with the latest-contact proxy. Five of seven EGD calendar-model terms had proportional-hazards test p values below 0.05. Excluding index-encounter IBD codes yielded 2,775/38,142 EGD patients with recorded repeats (7.28%); colonoscopy was unchanged. Restriction to known index diagnoses produced similar descriptive proportions (supplementary tables).

The EGD dysphagia association was stronger on days 1-90 than days 91-730: calendar-rule HRs were 1.98 (95% CI 1.65-2.37) and 0.87 (0.78-0.97); contact-rule HRs were 2.42 (2.02-2.89) and 1.25 (1.12-1.39). These exploratory interval results support time-varying associations, with the late estimate additionally dependent on the observation rule.

The bleeding-defined component contained 65 patients with no observed later 45378 in the original source; no repeat within 730 days was recovered from the second procedure source. Sixty patients had zero appointment follow-up days, two had one day, two had three days and one had 948 days. The capped appointment proxy totaled 738 days. Requiring the first observed 45378 to qualify reduced the component to 64 patients; adding ICD-9 bleeding retained 65. These findings do not establish an absence of repeat colonoscopy in a clinically complete bleeding cohort.

## Discussion

Three findings are supported. First, repeat endoscopy is observable in the broader source populations even when a narrow bleeding-defined subset has no events. Second, searching another source changes event ascertainment while holding the index population fixed. The proportional gain is greater for colonoscopy than EGD in these data, consistent with differing source fragmentation. Third, a subset of first repeats shares symptom codes with the index, providing a reproducible description of recurrent symptom-associated utilization without assigning appropriateness.

The apparent difference between colonoscopy and EGD is not a causal comparison: their clinical populations, indications and extraction mechanisms differ. Symptom and gender associations may reflect these mechanisms and incomplete adjustment. Importing all diagnosis worksheets is necessary for clinical characterization; row limits or single-sheet assumptions can otherwise create artificial missingness. Association estimates should therefore be understood as features of these selected recorded data.

Limitations include preexisting diagnosis exclusions, uncertain completeness of subsequent procedures, missing outside-system care, unavailable death/enrollment data, unverified age at index and absence of clinically adjudicated indications or examination quality. Code 569.3 appears in saved source-query exclusion blocks, creating uncertainty about the representativeness of bleeding eligibility. The local data cannot reconstruct patients removed upstream. Confidence intervals and robust standard errors do not correct these biases.

In conclusion, this completed project characterizes recorded repeat endoscopy and demonstrates the influence of source coverage and cohort definition. Its defensible interpretation is a descriptive utilization and ascertainment study, with exploratory associations. It does not estimate unnecessary endoscopy, effects of provider change or complete-capture population incidence.

## Tables and figure legends

| Table 1 Cohort | Original source repeats | Both-source repeats | Both-source proportion with 95% CI |
| --- | --- | --- | --- |
| Colonoscopy | 156 | 180 | 180/12,462 (1.44%; 95% CI 1.25-1.67%) |
| EGD | 2,817 | 2,835 | 2,835/38,864 (7.29%; 95% CI 7.04-7.56%) |

Denominators: 12,462 colonoscopy and 38,864 EGD index patients with at least 730 calendar days before May 31, 2023. Index membership and core-code definitions are held fixed across follow-up sources. Intervals are Wilson intervals for recorded-event proportions.

| Table 2 Symptom component | Any core repeat | First repeat sharing a target symptom |
| --- | --- | --- |
| Colonoscopy | 64/4,321 (1.48%; 95% CI 1.16-1.89%) | 48/4,321 (1.11%; 95% CI 0.84-1.47%) |
| EGD | 1,071/19,200 (5.58%; 95% CI 5.26-5.91%) | 629/19,200 (3.28%; 95% CI 3.03-3.54%) |

Target symptoms: colonoscopy, abdominal pain/constipation/rectal bleeding; EGD, abdominal pain/heartburn/dysphagia. Groups can overlap. Shared coding is not adjudicated principal indication or low-value care.

Figure 1. Recorded first-repeat patients under original-source and combined-source follow-up, with index membership fixed. Figure 2. Distribution of first-repeat intervals among patients with 730 calendar days available. Figures are supplied as 300 dpi PNG and editable SVG files.

## Publication declarations

Authorship and affiliations, institutional setting description, ethics/IRB determination and consent waiver if applicable, funding, conflicts of interest and data-access permission require author-supplied factual declarations before submission. No ethics approval, exemption, funding source or authorship contribution is asserted by this analytic package. Patient-level datasets are restricted research materials; the public manuscript should contain aggregate results only.

## References

1. Benchimol EI, Smeeth L, Guttmann A, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. PLoS Med. 2015;12:e1001885. https://doi.org/10.1371/journal.pmed.1001885

2. Kotecha D, Asselbergs FW, Achenbach S, et al. CODE-EHR best practice framework for the use of structured electronic healthcare records in clinical research. BMJ. 2022;378:e069048. https://doi.org/10.1136/bmj-2021-069048

3. Zou G. A modified Poisson regression approach to prospective studies with binary data. Am J Epidemiol. 2004;159:702-706. https://doi.org/10.1093/aje/kwh090

4. Gupta S, Lieberman D, Anderson JC, et al. Recommendations for follow-up after colonoscopy and polypectomy: a consensus update by the US Multi-Society Task Force on Colorectal Cancer. Gastrointest Endosc. 2020;91:463-485.e5. https://www.asge.org/home/resources/publications/guidelines/recommendations-for-follow-up-after-colonoscopy-and-polypectomy-a-consensus-update-by-the-us-multi-society-task-force-on-colorectal-cancer

5. STROBE Initiative. Checklist for cohort studies. https://www.strobe-statement.org/fileadmin/Strobe/uploads/checklists/STROBE_checklist_v4_cohort.pdf
