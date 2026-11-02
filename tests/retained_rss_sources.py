"""Resolve exact recorded RSS producers, without treating them as current runs."""
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    'src/proof_dag_checker.py':'6b111e898f3999929f7e28f39fde127b4e8fc4139bcf9f5a8afd82527e458a01',
    'src/vector_stream.py':'f94dc016107cdb163c61570660b579c51173465fc3bb758d424b85af4cba33e3',
    'tests/vector_rss_study.py':'6bfc99d19a4b59f57d1e58a81789719f44276b05e01bc167f1460bea88a5d3d7',
}
REPLICATION=('tests/vector_rss_replication.py','3ebb00a590dd82d99ff278851a2ab08c834e49086343aabdceeefff4d215449a')

def verify_sources(bindings, replication=False):
    expected=dict(EXPECTED)
    if replication: expected[REPLICATION[0]]=REPLICATION[1]
    if type(bindings) is not dict or bindings!=expected:
        raise ValueError('recorded RSS producer inventory differs')
    changed=[]
    for relative,digest in expected.items():
        current=ROOT/relative
        if hashlib.sha256(current.read_bytes()).hexdigest()==digest: continue
        preimage=ROOT/'results/vector-rss/source-preimage'/relative
        if not preimage.is_file() or hashlib.sha256(preimage.read_bytes()).hexdigest()!=digest:
            raise ValueError('exact recorded RSS source preimage missing or differs')
        changed.append(relative)
    return changed
