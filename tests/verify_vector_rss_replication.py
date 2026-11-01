"""Re-derive full-cohort RSS without running measurement subprocesses."""
from collections import Counter
import hashlib,json,math
from pathlib import Path
import statistics
import zipfile

ROOT=Path(__file__).resolve().parents[1]
ARMS=('full-json','direct-full','framed-stream','direct-liveness')
def require(ok,message):
    if not ok:raise ValueError(message)
def read_archive(path):
    with zipfile.ZipFile(path) as archive:
        require(not archive.testzip(),'archive CRC')
        names=archive.namelist()
        require(len(names)==len(set(names)),'duplicate members')
        identities=json.loads(archive.read('member-identities.json'))
        require(set(names)==set(identities)|{'member-identities.json'},'manifest membership')
        for name,v in identities.items():
            data=archive.read(name)
            require(len(data)==v['size'] and hashlib.sha256(data).hexdigest()==v['sha256'],'member bytes')
        return {k:json.loads(archive.read(k)) for k in identities}

def verify(protocol,result,summary,prior):
    require(protocol['limits']==dict(wall_seconds=300,total_cpu_seconds=180,
        child_address_bytes=1073741824,child_cpu_seconds=3,workers=1,subprocesses=600),'resource plan')
    require(protocol['cases']==prior['cases'] and protocol['order']==prior['order'],'same full cohort/order')
    require(protocol['prior_activity']['recorded_measurements']==584 and not protocol['prior_activity']['records_merged'],'old activity concealed')
    for rel,digest in protocol['source_bindings'].items():
        require(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,'scientific source changed')
    raw=result['raw'];require(len(raw)==600 and len(protocol['cases'])==50,'incomplete population')
    for i,row in enumerate(raw):
        job=protocol['order'][i];case=protocol['cases'][job['case']]
        require(all(row[k]==job[k] for k in ('case','repetition','position','arm')),'order mismatch')
        require(row['request']==case['id'] and row['outcome']==case['expected'],'outcome mismatch')
        for field in ('peak_rss_kib','baseline_peak_rss_kib','checked_cells'):
            require(type(row[field]) is int and row[field]>0,'invalid memory/work count')
        require(row['peak_rss_kib']>=row['baseline_peak_rss_kib'],'peak below baseline')
        require(math.isfinite(row['child_cpu_seconds']) and row['child_cpu_seconds']>=0,'invalid CPU')
    paired=[]
    for c in protocol['cases']:
        rows=[r for r in raw if r['request']==c['id']]
        require(Counter((r['arm'],r['repetition']) for r in rows)==Counter((a,n) for a in ARMS for n in range(3)),'missing/duplicate cell')
        require(len({r['checked_cells'] for r in rows})==1,'unequal semantic work')
        medians={a:statistics.median(r['peak_rss_kib'] for r in rows if r['arm']==a) for a in ARMS}
        paired.append(dict(request=c['id'],median_peak_rss_kib=medians,
            stream_to_full=medians['framed-stream']/medians['full-json'],
            live_to_direct=medians['direct-liveness']/medians['direct-full'],
            stream_to_matched_direct=medians['framed-stream']/medians['direct-liveness']))
    derived=dict(requests=50,measurements=600,
        median_peak_rss_kib={a:statistics.median(p['median_peak_rss_kib'][a] for p in paired) for a in ARMS},
        **{'median_'+k:statistics.median(p[k] for p in paired) for k in ('stream_to_full','live_to_direct','stream_to_matched_direct')})
    require(result['paired']==paired and result['summary']==derived and summary['statistics']==derived,'arithmetic mismatch')
    require(summary['status']=='COMPLETE_FULL_COHORT_REPLICATION' and summary['prior_activity_status']=='INCOMPLETE_BUDGET_STOP','lineage/status')
    require(0<result['resources']['wall_seconds']<=300 and 0<result['resources']['child_cpu_seconds']<=180,'resource admission')
    require(sum(r['child_cpu_seconds'] for r in raw)<=result['resources']['child_cpu_seconds']+0.01,'CPU undercount')
    return derived

def main():
    directory=ROOT/'results/vector-rss'
    payload=read_archive(directory/'replication.zip')
    require(set(payload)=={'protocol.json','results.json','attempt-started.json'},'unexpected replication members')
    protocol=payload['protocol.json'];result=payload['results.json']
    digest=hashlib.sha256((json.dumps(protocol,indent=2,ensure_ascii=False)+'\n').encode()).hexdigest()
    require(result['protocol_sha256']==digest and payload['attempt-started.json']['protocol_sha256']==digest,'protocol identity')
    prior=read_archive(directory/'observations.zip')['protocol.json']
    summary=json.loads((directory/'replication-summary.json').read_text(encoding='utf-8'))
    derived=verify(protocol,result,summary,prior)
    print(json.dumps(dict(status='VERIFIED_COMPLETE',requests=50,measurements=600,new_measurement_processes=0,statistics=derived)))

if __name__=='__main__':main()
