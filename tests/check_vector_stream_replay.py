"""Current finite-cohort replay against exact retained producer identities.

This unmeasured consumer does not rerun allocations or rewrite the frozen study.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import vector_stream_study as study

ROOT=Path(__file__).resolve().parents[1]
RECORDED={
    'src/vector_stream.py':'f94dc016107cdb163c61570660b579c51173465fc3bb758d424b85af4cba33e3',
    'src/proof_dag_checker.py':'6b111e898f3999929f7e28f39fde127b4e8fc4139bcf9f5a8afd82527e458a01',
    'tests/vector_stream_study.py':'ffc9654ebd51bbbf476480506668f1d47cd3dcb5029cfc8b5b6fc765d2525399',
}

def compare(current,recorded):
    if type(current) is not dict or type(recorded) is not dict:
        raise ValueError('logical study must be an object')
    if not study.core.exact_equal(recorded.get('source_bindings'),RECORDED):
        raise ValueError('complete registered historical source map required')
    actual={name:study.binding(ROOT/name) for name in RECORDED}
    if not study.core.exact_equal(current.get('source_bindings'),actual):
        raise ValueError('current logical replay source map differs')
    changed=[]
    for name,digest in RECORDED.items():
        if actual[name]==digest:continue
        captured=ROOT/'results/vector-rss/source-preimage'/name
        if not captured.is_file() or study.binding(captured)!=digest:
            raise ValueError('exact retained logical source preimage missing or differs')
        changed.append(name)
    old={k:v for k,v in recorded.items() if k!='source_bindings'}
    now={k:v for k,v in current.items() if k!='source_bindings'}
    if not study.core.exact_equal(now,old):
        raise ValueError('deterministic logical replay differs')
    return dict(scientific_rows_and_counts_equal=True,retained_producer_identities_verified=True,
        measured_sources_differ_from_current=changed,current_source_campaign_claimed=False,
        current_logical_sources=actual,new_allocation_measurements=0)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--compare',type=Path,default=ROOT/'results/vector-stream.json')
    args=parser.parse_args()
    if args.output.exists():raise ValueError('choose a fresh output')
    current=study.logical_study();verification=compare(current,study.load(args.compare))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as handle:
        json.dump(dict(current_logical_replay=current,retained_comparison=verification),handle,indent=2,allow_nan=False)
        handle.write('\n')
    print(json.dumps(dict(requests=current['requests'],totals=current['totals'],**verification)))

if __name__=='__main__':main()
