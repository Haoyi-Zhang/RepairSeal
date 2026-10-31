"""Frozen-cohort agreement and a matched Python-allocation comparison.

All four receivers get the same decoded authoritative request. File decoding,
graph construction and validation are inside the allocation boundary; producer
conversion and request loading are outside it. This measures traced Python
allocations, not RSS, device memory or a separately developed implementation.
"""
from pathlib import Path
import argparse
import gc
import hashlib
import io
import json
import platform
import statistics
import sys
import tempfile
import tracemalloc

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import proof_dag_checker as core
import vector_stream as stream


def load(path):return core.load_json_strict(path.read_text(encoding='utf-8'))
def binding(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def cohort():
    rows=[]
    for population in ('fixture','stress'):
        for item in load(ROOT/'proof-data'/(population+'-cases.json')):
            name=item['id']
            rows.append((population,item,
                         ROOT/'proof-data'/(population+'-inputs')/(name+'.json'),
                         ROOT/'proof-data'/(population+'-certificates')/(name+'.json')))
    return rows


def logical_study():
    rows=[]
    for population,item,request_path,packet_path in cohort():
        request=load(request_path);packet=load(packet_path)
        wire=stream.encode_packet(packet)
        full=core.check(request,packet);direct=core.evaluate_topological(request)
        framed=stream.check_stream(request,io.BytesIO(wire));live=stream.direct_liveness(request)
        prepared=stream.direct_full(request)
        expected={k:item[k] for k in ('status','witness')}
        for result in (full,direct,framed,live,prepared):
            if not core.exact_equal({k:result[k] for k in expected},expected):
                raise core.Invalid('cohort outcome differs: '+item['id'])
            if result['checked_cells']!=full['checked_cells']:
                raise core.Invalid('semantic work differs')
        if framed['peak_live_cells']!=live['peak_live_cells']:
            raise core.Invalid('unequal liveness schedule')
        if prepared['peak_live_vectors']!=full['checked_nodes']:
            raise core.Invalid('full-residency baseline differs')
        rows.append(dict(population=population,request=item['id'],
                         request_binding=binding(request_path),packet_binding=binding(packet_path),
                         status=item['status'],witness=item['witness'],
                         nodes=full['checked_nodes'],points=len(packet['points']),
                         checked_cells_per_arm=full['checked_cells'],
                         full_vector_comparisons=framed['vector_comparisons'],
                         direct_vector_comparisons=live['vector_comparisons'],
                         peak_live_vectors_per_streaming_arm=live['peak_live_vectors'],
                         peak_live_cells_per_streaming_arm=live['peak_live_cells'],
                         retained_diagnostic_vectors=live['retained_diagnostic_vectors'],
                         json_bytes=len(core.canonical_bytes(packet)),framed_bytes=len(wire)))
    if len(rows)!=380 or sum(r['checked_cells_per_arm'] for r in rows)!=1179684:
        raise core.Invalid('frozen cohort changed')
    return dict(scope='retained authored finite cohort; no new source-program admission',
                source_bindings={name:binding(ROOT/name) for name in
                                 ('src/vector_stream.py','src/proof_dag_checker.py','tests/vector_stream_study.py')},
                requests=len(rows),accepted=sum(r['status']=='ACCEPT' for r in rows),
                totals={key:sum(r[key] for r in rows) for key in
                        ('checked_cells_per_arm','full_vector_comparisons','direct_vector_comparisons',
                         'peak_live_cells_per_streaming_arm','json_bytes','framed_bytes')},
                median_live_to_all_vectors=statistics.median(
                    r['peak_live_vectors_per_streaming_arm']/r['nodes'] for r in rows),
                rows=rows)


def allocation_study():
    # Fixed before observing allocations: all 20 correct fixture variants and
    # every tenth stress manifest record (offset zero), without result filtering.
    selected=[r for r in cohort() if r[0]=='fixture' and r[1]['id'].endswith('-correct')]
    selected += [r for i,r in enumerate([r for r in cohort() if r[0]=='stress']) if i%10==0]
    if len(selected)!=50:raise core.Invalid('allocation subset changed')
    arms=('full-json','direct-full','framed-stream','direct-liveness')
    raw=[]
    with tempfile.TemporaryDirectory(prefix='repairseal-vector-stream-') as directory:
        framed_path=Path(directory)/'certificate.rows'
        full_path=Path(directory)/'certificate.json'
        for case,(_population,item,request_path,packet_path) in enumerate(selected):
            request=load(request_path)
            packet=load(packet_path)
            full_path.write_bytes(core.canonical_bytes(packet))
            with framed_path.open('wb') as output:stream.write_packet(packet,output)
            del packet
            def run(arm):
                if arm=='full-json':return core.check(request,load(full_path))
                if arm=='direct-full':return stream.direct_full(request)
                if arm=='direct-liveness':return stream.direct_liveness(request)
                with framed_path.open('rb') as source:return stream.check_stream(request,source)
            # Warm all arms before measuring. No semantic cache crosses calls.
            for arm in arms:run(arm)
            for repetition in range(3):
                offset=(case+repetition)%len(arms)
                order=arms[offset:]+arms[:offset]
                for position,arm in enumerate(order):
                    gc.collect();tracemalloc.start()
                    try:
                        result=run(arm)
                        _current,peak=tracemalloc.get_traced_memory()
                    finally:tracemalloc.stop()
                    if not core.exact_equal({k:result[k] for k in ('status','witness')},
                                            {k:item[k] for k in ('status','witness')}):
                        raise core.Invalid('allocation arm outcome differs')
                    raw.append(dict(request=item['id'],repetition=repetition,position=position,
                                    arm=arm,peak_python_bytes=peak))
                    del result
    paired=[]
    for _,item,_,_ in selected:
        medians={arm:statistics.median(r['peak_python_bytes'] for r in raw
                                     if r['request']==item['id'] and r['arm']==arm) for arm in arms}
        paired.append(dict(request=item['id'],median_peak_python_bytes=medians,
                           stream_to_full=medians['framed-stream']/medians['full-json'],
                           live_to_direct=medians['direct-liveness']/medians['direct-full'],
                           stream_to_matched_direct=medians['framed-stream']/medians['direct-liveness']))
    return dict(scope='50 predetermined retained requests; three repetitions per arm; Python allocations, not RSS',
                boundary='same decoded request; both wire encodings canonical and compact; certificate file decoding, reconstruction and validation included; producer conversion excluded',
                selection='20 correct fixtures plus stress manifest offsets 0,10,...,290',
                runtime=dict(python=sys.version,implementation=platform.python_implementation(),platform=platform.platform()),
                summary=dict(requests=len(selected),measurements=len(raw),
                             median_stream_to_full=statistics.median(r['stream_to_full'] for r in paired),
                             median_live_to_direct=statistics.median(r['live_to_direct'] for r in paired),
                             median_stream_to_matched_direct=statistics.median(r['stream_to_matched_direct'] for r in paired)),
                source_bindings={name:binding(ROOT/name) for name in
                                 ('src/vector_stream.py','src/proof_dag_checker.py','tests/vector_stream_study.py')},
                paired=paired,raw=raw)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--allocations',action='store_true')
    parser.add_argument('--compare',type=Path)
    args=parser.parse_args()
    if args.output.exists():raise core.Invalid('choose a fresh output')
    result=allocation_study() if args.allocations else logical_study()
    if args.compare and not core.exact_equal(result,load(args.compare)):
        raise core.Invalid('deterministic replay differs')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:
        json.dump(result,output,indent=2,ensure_ascii=False);output.write('\n')
    print(json.dumps(result.get('summary',dict(requests=result.get('requests'),totals=result.get('totals'),
                                             median_live_to_all_vectors=result.get('median_live_to_all_vectors')))))


if __name__=='__main__':main()
