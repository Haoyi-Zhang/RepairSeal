"""Fresh-process Linux RSS comparison on the existing, fixed allocation cohort.

This is not an allocator-only measurement: each child includes its interpreter,
imports and authoritative decoded request. Certificate production is outside
the child. Identical semantic work and outcomes are required for all four arms.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('full-json', 'direct-full', 'framed-stream', 'direct-liveness')
SOURCES = ('src/proof_dag_checker.py', 'src/vector_stream.py',
           'tests/vector_rss_study.py')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def seal(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as output:
        json.dump(value, output, indent=2, ensure_ascii=False)
        output.write('\n')


def prepare(directory):
    if directory.exists():
        raise ValueError('prepare requires a fresh directory')
    directory.mkdir(parents=True)
    sys.path.insert(0, str(ROOT/'src'))
    import proof_dag_checker as core
    import vector_stream as stream
    selected = [('fixture', r) for r in read(ROOT/'proof-data/fixture-cases.json')
                if r['id'].endswith('-correct')]
    selected += [('stress', r) for i, r in enumerate(read(ROOT/'proof-data/stress-cases.json'))
                 if i % 10 == 0]
    if len(selected) != 50:
        raise ValueError('fixed cohort differs')
    cases = []
    for population, item in selected:
        name = item['id']
        request = ROOT/'proof-data'/(population+'-inputs')/(name+'.json')
        packet = ROOT/'proof-data'/(population+'-certificates')/(name+'.json')
        wire_json = directory/(name+'.json')
        wire_rows = directory/(name+'.rows')
        decoded = core.load_json_strict(packet.read_text(encoding='utf-8'))
        wire_json.write_bytes(core.canonical_bytes(decoded))
        with wire_rows.open('wb') as output:
            stream.write_packet(decoded, output)
        cases.append(dict(id=name, population=population,
                          request=str(request.relative_to(ROOT)),
                          request_sha256=seal(request), packet=str(packet.relative_to(ROOT)),
                          packet_sha256=seal(packet), json_sha256=seal(wire_json),
                          rows_sha256=seal(wire_rows), expected={k:item[k] for k in ('status','witness')}))
    order = []
    for index, case in enumerate(cases):
        for repetition in range(3):
            offset = (index+repetition) % len(ARMS)
            for position, arm in enumerate(ARMS[offset:]+ARMS[:offset]):
                order.append(dict(case=index, repetition=repetition, position=position, arm=arm))
    protocol = dict(scope='fresh-process RSS on the retained allocation subset, not new source programs',
                    boundary='whole fresh interpreter including imports and decoded authoritative request; file decoding, reconstruction and checking included; producer conversion excluded',
                    selection='20 correct fixtures plus stress offsets 0,10,...,290; no outcome filtering',
                    source_bindings={p:seal(ROOT/p) for p in SOURCES},
                    limits=dict(wall_seconds=110, total_cpu_seconds=115, child_address_bytes=1073741824,
                                child_cpu_seconds=3, workers=1, subprocesses=600),
                    child_environment=dict(PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1'),
                    cases=cases, order=order)
    write(directory/'protocol.json', protocol)
    print(json.dumps(dict(prepared=len(cases), children=len(order))))


def child(directory, index, arm):
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    protocol = read(directory/'protocol.json')
    case = protocol['cases'][index]
    sys.path.insert(0, str(ROOT/'src'))
    import proof_dag_checker as core
    import vector_stream as stream
    request = core.load_json_strict((ROOT/case['request']).read_text(encoding='utf-8'))
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    start = time.perf_counter()
    if arm == 'full-json':
        packet = core.load_json_strict((directory/(case['id']+'.json')).read_text(encoding='utf-8'))
        result = core.check(request, packet)
    elif arm == 'direct-full':
        result = stream.direct_full(request)
    elif arm == 'direct-liveness':
        result = stream.direct_liveness(request)
    else:
        with (directory/(case['id']+'.rows')).open('rb') as source:
            result = stream.check_stream(request, source)
    elapsed = time.perf_counter()-start
    if not core.exact_equal({k:result[k] for k in ('status','witness')}, case['expected']):
        raise ValueError('outcome differs')
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps(dict(outcome={k:result[k] for k in ('status','witness')},
                          checked_cells=result['checked_cells'],
                          baseline_peak_rss_kib=before, peak_rss_kib=usage.ru_maxrss,
                          operation_seconds=elapsed, child_cpu_seconds=usage.ru_utime+usage.ru_stime)))


def run(directory):
    if sys.platform != 'linux':
        raise ValueError('RSS units and process limits require Linux')
    protocol = read(directory/'protocol.json')
    if any(seal(ROOT/p) != identity for p, identity in protocol['source_bindings'].items()):
        raise ValueError('source changed after protocol freeze')
    for c in protocol['cases']:
        for path, key in ((ROOT/c['request'],'request_sha256'),(ROOT/c['packet'],'packet_sha256'),
                          (directory/(c['id']+'.json'),'json_sha256'),(directory/(c['id']+'.rows'),'rows_sha256')):
            if seal(path) != c[key]:
                raise ValueError('input changed after protocol freeze')
    start = time.monotonic()
    initial = resource.getrusage(resource.RUSAGE_CHILDREN)
    raw = []
    env = dict(os.environ, **protocol['child_environment'])
    limits = protocol['limits']
    try:
        for job in protocol['order']:
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu = usage.ru_utime+usage.ru_stime-initial.ru_utime-initial.ru_stime
            remaining = limits['wall_seconds']-(time.monotonic()-start)
            if remaining <= 0 or cpu >= limits['total_cpu_seconds']:
                raise ValueError('declared activity budget exhausted; no retry')
            completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                       '--directory', str(directory), '--child', str(job['case']),
                                       '--arm', job['arm']], capture_output=True, text=True,
                                      env=env, timeout=min(remaining, 5), check=True)
            result = json.loads(completed.stdout)
            raw.append(dict(**job, request=protocol['cases'][job['case']]['id'], **result))
    except BaseException as error:
        write(directory/'incomplete.json', dict(error=repr(error), completed=len(raw), raw=raw))
        raise
    if len(raw) != 600:
        raise ValueError('population incomplete')
    paired = []
    for case in protocol['cases']:
        rows = [r for r in raw if r['request']==case['id']]
        if len({r['checked_cells'] for r in rows}) != 1:
            raise ValueError('semantic work differs')
        medians = {arm:statistics.median(r['peak_rss_kib'] for r in rows if r['arm']==arm) for arm in ARMS}
        paired.append(dict(request=case['id'], median_peak_rss_kib=medians,
                           stream_to_full=medians['framed-stream']/medians['full-json'],
                           live_to_direct=medians['direct-liveness']/medians['direct-full'],
                           stream_to_matched_direct=medians['framed-stream']/medians['direct-liveness']))
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    summary = dict(requests=50, measurements=len(raw),
                   median_peak_rss_kib={arm:statistics.median(p['median_peak_rss_kib'][arm] for p in paired) for arm in ARMS},
                   **{'median_'+key:statistics.median(p[key] for p in paired) for key in
                      ('stream_to_full','live_to_direct','stream_to_matched_direct')})
    result = dict(scope=protocol['scope'], boundary=protocol['boundary'],
                  protocol_sha256=seal(directory/'protocol.json'), source_bindings=protocol['source_bindings'],
                  runtime=dict(python=sys.version, platform=platform.platform(), pythonhashseed='0',
                               memory_unit='KiB, Linux getrusage(RUSAGE_SELF).ru_maxrss'),
                  resources=dict(wall_seconds=time.monotonic()-start,
                                 child_cpu_seconds=usage.ru_utime+usage.ru_stime-initial.ru_utime-initial.ru_stime,
                                 workers=1), summary=summary, paired=paired, raw=raw)
    write(directory/'results.json', result)
    print(json.dumps(summary))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--child', type=int)
    parser.add_argument('--arm', choices=ARMS)
    args=parser.parse_args()
    if args.prepare:
        prepare(args.directory.resolve())
    elif args.run:
        run(args.directory.resolve())
    elif args.child is not None and args.arm:
        child(args.directory.resolve(), args.child, args.arm)
    else:
        parser.error('select --prepare or --run')


if __name__=='__main__':
    main()
