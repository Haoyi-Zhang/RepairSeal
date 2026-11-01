"""Fixed five-request offline handoff through producer-free receiver processes."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import zipfile
ROOT=Path(__file__).resolve().parents[1]
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(out):
    if out.exists() or out.resolve().is_relative_to(ROOT.resolve()):raise ValueError('new output outside artifact required')
    cases=['original','supplied','regression','definedness','trace-overfit']
    out.mkdir(parents=True)
    files=['src/admission_journal.py','src/proof_dag_checker.py']
    files += ['results/upstream-ceil/'+n+suffix+'.json' for n in cases for suffix in ('-request','-full')]
    bindings={f:sha(ROOT/f) for f in files}
    registration=dict(cases=cases,source_bindings=bindings,receiver_modules=['admission_journal.py','proof_dag_checker.py'],
        subprocess_limit=30,per_process_seconds=10,campaign_seconds=120,
        outcome='full/direct semantic decision and identity-safe durable approval, not upstream application correctness',
        input_scope='One source-derived request plus four existing controls; no new independent upstream repairs',
        no_performance_or_memory_advantage_claim=True)
    save(out/'registration.json',registration)
    sandbox=out/'receiver';sandbox.mkdir()
    for name in registration['receiver_modules']:shutil.copyfile(ROOT/'src'/name,sandbox/name)
    raw=[];started=time.monotonic()
    def call(database,*args,success=True):
        if len(raw)>=30 or time.monotonic()-started>120:raise RuntimeError('registered campaign cap')
        command=[sys.executable,'-I','-B',str(sandbox/'admission_journal.py'),str(database),*map(str,args)]
        # -I excludes the script directory; explicitly load only the two copied
        # receiver modules in a clean isolated interpreter.
        boot='import runpy,sys;directory,script,*args=sys.argv[1:];sys.path.insert(0,directory);sys.argv=[script,*args];runpy.run_path(script,run_name="__main__")'
        command=[sys.executable,'-I','-B','-c',boot,str(sandbox),str(sandbox/'admission_journal.py'),str(database),*map(str,args)]
        p=subprocess.run(command,capture_output=True,text=True,timeout=10)
        raw.append(dict(arguments=[str(x) if not isinstance(x,Path) else x.name for x in args],
                        database=database.name,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        save(out/'raw-processes.json',[dict(row,
            arguments=[value.replace(str(ROOT),'<ARTIFACT>').replace(str(out),'<OUTPUT>') for value in row['arguments']],
            stdout=row['stdout'].replace(str(out),'<OUTPUT>').replace(str(ROOT),'<ARTIFACT>'),
            stderr=row['stderr'].replace(str(out),'<OUTPUT>').replace(str(ROOT),'<ARTIFACT>')) for row in raw])
        if (p.returncode==0)!=success:raise ValueError('unexpected receiver exit')
        return json.loads(p.stdout) if success else None
    rows=[];dbs=[]
    for name in cases:
        database=out/(name+'.sqlite');dbs.append(database)
        request=ROOT/'results/upstream-ceil'/str(name+'-request.json')
        packet=ROOT/'results/upstream-ceil'/str(name+'-full.json')
        spec=json.loads(request.read_text(encoding='utf-8'))
        registered=call(database,'register',request)
        full=call(database,'decide',spec['id'],'proof','--mode','proof','--packet',packet)
        direct=call(database,'decide',spec['id'],'direct','--mode','direct')
        repeated=call(database,'decide',spec['id'],'proof','--mode','proof','--packet',packet)
        observed=call(database,'approved',spec['id'],registered['request_identity'])
        if any(full[k]!=direct[k] for k in ('semantic_status','approved','witness','checked_cells')):raise ValueError('same-information disagreement')
        if not repeated['replayed_receipt'] or observed['approved']!=full['approved']:raise ValueError('durable receipt differs')
        rows.append(dict(case=name,registration=registered,proof=full,direct=direct,replayed=repeated,
                         identity_scoped_approval=observed))
    # A later current request must not inherit approval for an earlier candidate.
    good=rows[1];request=json.loads((ROOT/'results/upstream-ceil/supplied-request.json').read_text())
    request['candidate']=request['original'];changed=out/'changed-request.json';save(changed,request)
    registered=call(dbs[1],'register',changed,'--expected-identity',good['registration']['request_identity'])
    stale=call(dbs[1],'approved',request['id'],good['registration']['request_identity'])
    if stale['approved']:raise ValueError('stale current approval')
    call(dbs[1],'decide',request['id'],'stale-packet','--mode','proof','--packet',ROOT/'results/upstream-ceil/supplied-full.json',success=False)
    raw=[dict(row,arguments=[value.replace(str(ROOT),'<ARTIFACT>').replace(str(out),'<OUTPUT>') for value in row['arguments']],
              stdout=row['stdout'].replace(str(out),'<OUTPUT>').replace(str(ROOT),'<ARTIFACT>'),
              stderr=row['stderr'].replace(str(out),'<OUTPUT>').replace(str(ROOT),'<ARTIFACT>')) for row in raw]
    save(out/'records.json',dict(rows=rows,stale_approval=stale,revised_request=registered,raw_processes=raw))
    with zipfile.ZipFile(out/'journals.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in dbs:
            info=zipfile.ZipInfo(p.name);info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    summary=dict(status='PASS',requests=len(rows),proof_direct_agreements=len(rows),
        approved=sum(r['proof']['approved'] for r in rows),refuted=sum(not r['proof']['approved'] for r in rows),
        receiver_processes=len(raw),producer_module_in_receiver=False,stale_approval_rejected=True,
        source_bindings=bindings,performance_claim=False,new_independent_programs=0)
    save(out/'summary.json',summary)
    save(out/'environment.json',dict(python=platform.python_version(),platform=platform.platform()))
    print(json.dumps(summary));return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
