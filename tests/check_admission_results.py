"""Recheck retained decisions and closed database journals, not a new study."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from admission_journal import identity
from proof_dag_checker import check,evaluate_topological
def run():
    data=ROOT/'results/admission-journal';registration=json.loads((data/'registration.json').read_text())
    records=json.loads((data/'records.json').read_text());summary=json.loads((data/'summary.json').read_text())
    changed=[]
    for rel,digest in registration['source_bindings'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=digest:
            captured=data/'source-preimage'/rel
            if not captured.is_file() or hashlib.sha256(captured.read_bytes()).hexdigest()!=digest:
                raise ValueError('measured execution preimage missing or differs')
            changed.append(rel)
    approved=0
    for row in records['rows']:
        name=row['case'];request=json.loads((ROOT/'results/upstream-ceil'/str(name+'-request.json')).read_text())
        packet=json.loads((ROOT/'results/upstream-ceil'/str(name+'-full.json')).read_text())
        full=check(request,packet);direct=evaluate_topological(request)
        for result,label in [(full,'proof'),(direct,'direct')]:
            saved=row[label]
            if any(saved[k]!=result[k2] for k,k2 in [('semantic_status','status'),('witness','witness'),('checked_cells','checked_cells')]):raise ValueError('saved semantic result differs')
            if saved['request_identity']!=identity(request) or saved['approved']!=(result['status']=='ACCEPT'):raise ValueError('approval binding')
        approved+=row['proof']['approved']
    if len(records['rows'])!=5 or len(records['raw_processes'])!=28 or approved!=1 or summary['approved']!=approved:raise ValueError('complete event accounting')
    with tempfile.TemporaryDirectory() as directory,zipfile.ZipFile(data/'journals.zip') as z:
        expected={row['case']+'.sqlite' for row in records['rows']}
        if set(z.namelist())!=expected or len(z.namelist())!=len(expected):raise ValueError('journal archive set')
        for row in records['rows']:
            p=Path(directory)/(row['case']+'.sqlite');raw=z.read(p.name)
            if len(raw)>4*1024*1024:raise ValueError('journal byte bound')
            p.write_bytes(raw);db=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True)
            try:
                receipts=[json.loads(r[0]) for r in db.execute('SELECT result FROM receipts ORDER BY token')]
                expected_receipts=[{k:v for k,v in row[label].items() if k!='replayed_receipt'} for label in ('direct','proof')]
                if receipts!=expected_receipts:raise ValueError('durable receipt bytes differ')
                revision,body=db.execute('SELECT revision,body FROM requests').fetchone()
                wanted=2 if row['case']=='supplied' else 1
                if revision!=wanted:raise ValueError('current request revision')
                if wanted==2 and identity(json.loads(body))!=records['revised_request']['request_identity']:raise ValueError('stale approval not invalidated')
            finally:db.close()
    print(json.dumps(dict(status='PASS',requests=5,approvals=1,refutations=4,closed_journals=5,
        measured_sources_differ_from_current=changed,new_execution_claimed=False)))
if __name__=='__main__':run()
