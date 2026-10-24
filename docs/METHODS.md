# Methods and interpretation

## Estimands and index definitions

The principal descriptive estimand is the proportion with a recorded first core-code repeat on days 1–730, among source-specific index patients with 730 calendar days available before May 31, 2023. Index is the first observed core patient-day within the original procedure-specific workbook. It is not necessarily the first lifetime procedure. Follow-up searches both procedure workbooks without redefining the index population.

Diagnosis flags are aggregated by patient and encounter before linkage; same-day index encounters are then consolidated to patient-days. This avoids assigning every diagnosis in a patient's history to every procedure. Both EGD diagnosis parts must be read. The second part has 119,247 rows.

## Statistical analyses

- Wilson intervals accompany recorded proportions.
- Modified Poisson regression uses HC0 robust standard errors for exploratory adjusted recorded-event probability ratios.
- Cox models use Efron ties and three observation rules: calendar cutoff, latest recorded contact, and latest appointment plus repeat evidence.
- Rank-based Schoenfeld checks and early/late fits examine proportional-hazards stability.
- Independent PHReg comparisons are documented in the archived verification evidence.

The code omits constant or zero-event exposure strata rather than reporting unstable estimates. The separate 65-patient bleeding component has zero observed repeats and cannot support Cox estimation.

## Limits on inference

Calendar eligibility does not prove continuous capture. Contact-based censoring may depend on care-seeking and the outcome. Cohort-specific estimates cannot be interpreted as causal comparisons between procedures. Coded symptom overlap does not establish a principal indication. Index age, complete outside care, and death data are not verified. There is no multiple-testing correction, preregistration claim, or clinical appropriateness adjudication.

The complete operational specification is in [Dataset preparation and analysis specification](../documentation/Dataset%20preparation%20and%20analysis%20specification.md). Scientific references are retained in the [manuscript](../Scientific%20manuscript.md).
