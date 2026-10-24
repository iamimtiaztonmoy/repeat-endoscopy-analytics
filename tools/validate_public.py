"""Validate the public release without accessing clinical data or third-party packages."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest_path = ROOT / 'documentation/public_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    expected = set(manifest) | {'documentation/public_manifest.json'}
    if (ROOT / '.git').exists():
        raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
        actual = set(raw.decode().strip('\0').split('\0'))
    else:
        actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    assert actual == expected, f'Inventory mismatch: added={actual-expected}, missing={expected-actual}'
    forbidden = {'PatientID', 'EncounterID', 'study_id', 'index_date', 'repeat_date', 'patient_id', 'encounter_id'}
    for rel, digest in manifest.items():
        p = ROOT / rel
        assert not any(part in {'data', 'restricted', 'Dataset', 'Research Project'} for part in p.relative_to(ROOT).parts), rel
        assert p.suffix.lower() not in {'.xlsx', '.xls', '.pkl', '.zip', '.rar', '.mp4', '.m4a', '.accdb'}, rel
        assert hashlib.sha256(p.read_bytes()).hexdigest() == digest, f'Checksum mismatch: {rel}'
        if p.suffix == '.py':
            ast.parse(p.read_text(encoding='utf-8-sig'), filename=rel)
        if rel.startswith('tables/') and p.suffix == '.csv':
            with p.open(encoding='utf-8-sig', newline='') as f:
                headers = next(csv.reader(f))
            assert not forbidden.intersection(headers), f'Patient-level header: {rel}'
    with (ROOT / 'tables/Repeat estimates.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    definition = 'Both source workbooks; core codes; first repeat within 730; calendar opportunity'
    for cohort, n, events in [('Colonoscopy', 12462, 180), ('EGD', 38864, 2835)]:
        matches = [r for r in rows if r['dataset'] == cohort and r['definition'] == definition]
        assert len(matches) == 1, cohort
        r = matches[0]
        assert int(r['n']) == n and int(r['events']) == events
        proportion = events / n
        assert math.isclose(float(r['proportion']), proportion, rel_tol=1e-12)
        z = 1.959963984540054
        denominator = 1 + z*z/n
        center = (proportion + z*z/(2*n)) / denominator
        half = z * math.sqrt(proportion*(1-proportion)/n + z*z/(4*n*n)) / denominator
        assert math.isclose(float(r['ci_low']), center-half, abs_tol=1e-10)
        assert math.isclose(float(r['ci_high']), center+half, abs_tol=1e-10)
    print(f'PASS: {len(expected)} public files; checksums, Python syntax, CSV headers, and principal Wilson estimates verified.')
    print('Patient-level reconstruction and clinical validation were not performed by this check.')

if __name__ == '__main__':
    main()
