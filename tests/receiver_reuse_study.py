"""Retained 380-request replay with equally informed receiver-owned caches.

No new third-party execution, time/speed claims or rewrite of frozen runs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import proof_dag_checker as core
from reusing_checker import ReceiverCache,check_reusing,direct_reusing


def study():
    cache_full,cache_direct=ReceiverCache(),ReceiverCache()
    rows=[]
    for population in ('fixture','stress'):
        manifest=core.load_json_strict((ROOT/'proof-data'/(population+'-cases.json')).read_text(encoding='utf-8'))
        for record in manifest:
            name=record['id']
            request=core.load_json_strict((ROOT/'proof-data'/(population+'-inputs')/(name+'.json')).read_text(encoding='utf-8'))
            certificate=core.load_json_strict((ROOT/'proof-data'/(population+'-certificates')/(name+'.json')).read_text(encoding='utf-8'))
            cold_full=core.check(request,certificate)
            cold_direct=core.evaluate_topological(request)
            reused_full=check_reusing(request,certificate,cache_full)
            reused_direct=direct_reusing(request,cache_direct)
            expected={'status':record['status'],'witness':record['witness']}
            for result in (cold_full,cold_direct,reused_full,reused_direct):
                if not core.exact_equal({k:result[k] for k in expected},expected):
                    raise core.Invalid('result disagreement: '+name)
            if any(reused_full[k]!=reused_direct[k] for k in ('recomputed_cells','reused_cells','checked_cells')):
                raise core.Invalid('unequal cached semantic work: '+name)
            if reused_full['checked_cells']!=cold_full['checked_cells'] or cold_full['checked_cells']!=cold_direct['checked_cells']:
                raise core.Invalid('cell inventory differs: '+name)
            rows.append({'population':population,'request':name,'request_binding':hashlib.sha256(core.canonical_bytes(request)).hexdigest(),
                         'status':record['status'],'witness':record['witness'],
                         'cold_cells_per_arm':cold_full['checked_cells'],
                         'cached_cells_recomputed_per_arm':reused_full['recomputed_cells'],
                         'cached_cells_reused_per_arm':reused_full['reused_cells'],
                         'full_vector_comparisons':reused_full['vector_comparisons'],
                         'direct_vector_comparisons':reused_direct['vector_comparisons']})
    totals={k:sum(r[k] for r in rows) for k in ('cold_cells_per_arm','cached_cells_recomputed_per_arm',
            'cached_cells_reused_per_arm','full_vector_comparisons','direct_vector_comparisons')}
    if len(rows)!=380 or totals['cold_cells_per_arm']!=1179684:
        raise core.Invalid('retained cohort differs')
    controls=[]
    for record in core.load_json_strict((ROOT/'proof-data/fixture-cases.json').read_text(encoding='utf-8')):
        name=record['id']
        if not name.endswith('-correct'): continue
        request=core.load_json_strict((ROOT/'proof-data/fixture-inputs'/(name+'.json')).read_text(encoding='utf-8'))
        certificate=core.load_json_strict((ROOT/'proof-data/fixture-certificates'/(name+'.json')).read_text(encoding='utf-8'))
        cache=ReceiverCache()
        check_reusing(request,certificate,cache)
        for path in sorted((ROOT/'proof-data/controls').glob(name+'-*.json')):
            damaged=core.load_json_strict(path.read_text(encoding='utf-8'))
            before=dict(cache._cells)
            try:
                check_reusing(request,damaged,cache)
            except (core.Invalid,core.Unsupported):
                if before!=cache._cells: raise core.Invalid('invalid packet altered established facts')
                controls.append({'packet':path.name,'status':'rejected'})
            else:
                raise core.Invalid('warm receiver accepted retained mutation: '+path.name)
    if len(controls)!=600: raise core.Invalid('retained first-seed controls differ')
    return {'requests':len(rows),'capacity':65536,'order':'fixture manifest followed by stress manifest; fixed retained order',
            'scope':'owned finite retained core; no new public source admission or timing experiment',
            'totals':totals,'rows':rows,'retained_first_seed_mutations_rejected':len(controls),'controls':controls}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--compare',type=Path)
    args=parser.parse_args()
    if args.output.exists(): raise core.Invalid('choose a fresh output')
    result=study()
    if args.compare and not core.exact_equal(result,core.load_json_strict(args.compare.read_text(encoding='utf-8'))):
        raise core.Invalid('reuse replay differs')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'requests':result['requests'],'totals':result['totals']}))


if __name__=='__main__':main()
