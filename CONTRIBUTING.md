# Contributing

Open an issue describing the scientific or reproducibility problem before proposing a substantive change. Include the affected file, estimand, denominator, and expected behavior. Never include clinical rows, identifiers, exact encounter dates, source workbooks, or screenshots containing patient data.

For a pull request, explain changes to cohort membership, diagnosis linkage, index selection, event definitions, censoring, or model covariates explicitly. Preserve original aggregate findings unless a documented reanalysis supports the correction. Separate a formatting correction from a scientific change.

Run `python tools/validate_public.py`. If authorized aggregate outputs change, review their disclosure suitability, document the reason in CHANGELOG.md, and deliberately update `documentation/public_manifest.json` with the new file hashes. Do not update hashes merely to silence an unexplained mismatch.

Full model checks require restricted data and must run in an authorized local environment. Public CI must never download or request those data. Keep feedback constructive and focused on evidence. Rights and institutional approvals must be resolved before contributing third-party materials.
