"""Current evidence pointers use the documented artifact-relative base."""
import csv
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ClaimLedgerPaths(unittest.TestCase):
    def test_ceil_evidence_uses_existing_artifact_inputs(self):
        with (ROOT/'claim_evidence_ledger.csv').open(encoding='utf-8',newline='') as stream:
            rows={r['claim_id']:r for r in csv.DictReader(stream)}
        row=rows['C38'];paths=[p.strip() for p in row['evidence'].split(';')]
        self.assertEqual(paths,['tests/upstream_ceil_case.py','results/upstream-ceil/summary.json','../paper/generate_ceil.py'])
        self.assertTrue(all((ROOT/p).is_file() for p in paths[:-1]))

    def test_paper_companion_is_explicitly_optional(self):
        with (ROOT/'claim_evidence_ledger.csv').open(encoding='utf-8',newline='') as stream:
            row=next(r for r in csv.DictReader(stream) if r['claim_id']=='C38')
        self.assertIn('paper companion is optional for the standalone artifact',row['boundary'])
        if (ROOT.parent/'paper').is_dir():
            self.assertTrue((ROOT/'../paper/generate_ceil.py').is_file())

if __name__=='__main__':unittest.main()
