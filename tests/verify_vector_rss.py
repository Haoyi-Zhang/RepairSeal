"""Read-only verification of the interrupted RSS evidence, without new runs."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import zipfile

ROOT=Path(__file__).resolve().parents[1]
from retained_rss_sources import verify_sources
def main():
    directory=ROOT/'results/vector-rss'
    summary=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(directory/'observations.zip') as archive:
        identities=json.loads(archive.read('member-identities.json'))
        if set(archive.namelist()) != {'protocol.json','incomplete.json','member-identities.json'} or archive.testzip():
            raise ValueError('archive structure/CRC differs')
        for name,identity in identities.items():
            raw=archive.read(name)
            if len(raw)!=identity['size'] or hashlib.sha256(raw).hexdigest()!=identity['sha256']:
                raise ValueError('raw identity differs')
        protocol=json.loads(archive.read('protocol.json'))
        incomplete=json.loads(archive.read('incomplete.json'))
    changed=verify_sources(protocol['source_bindings'])
    raw=incomplete['raw'];arms=('full-json','direct-full','framed-stream','direct-liveness')
    if summary['status']!='INCOMPLETE_BUDGET_STOP' or len(raw)!=584 or len(protocol['order'])!=600:
        raise ValueError('interrupted population concealed')
    complete=[]
    for index,row in enumerate(raw):
        job=protocol['order'][index];case=protocol['cases'][job['case']]
        if any(row[k]!=job[k] for k in ('case','repetition','position','arm')) or row['outcome']!=case['expected']:
            raise ValueError('order/outcome differs')
    for case in protocol['cases']:
        rows=[r for r in raw if r['request']==case['id']]
        if len(rows)!=12:
            continue
        if Counter((r['arm'],r['repetition']) for r in rows)!=Counter((a,n) for a in arms for n in range(3)) or len({r['checked_cells'] for r in rows})!=1:
            raise ValueError('incomplete/unequal pair')
        medians={a:statistics.median(r['peak_rss_kib'] for r in rows if r['arm']==a) for a in arms}
        complete.append(dict(request=case['id'],median_peak_rss_kib=medians,
            stream_to_full=medians['framed-stream']/medians['full-json'],
            live_to_direct=medians['direct-liveness']/medians['direct-full'],
            stream_to_matched_direct=medians['framed-stream']/medians['direct-liveness']))
    if complete!=summary['paired'] or len(complete)!=48:
        raise ValueError('post-stop paired analysis differs')
    for key in ('stream_to_full','live_to_direct','stream_to_matched_direct'):
        if statistics.median(p[key] for p in complete)!=summary['median_'+key]:
            raise ValueError('paired median differs')
    print(json.dumps(dict(recorded_measurements=len(raw),complete_paired_requests=len(complete),
        status='VERIFIED_INCOMPLETE',new_process_measurements=0,
        measured_sources_differ_from_current=changed)))

if __name__=='__main__':main()

