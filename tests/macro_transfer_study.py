"""A selected upstream macro transferred by typed lowering, not manual bodies.

The optional native harness contains only two reviewed pure unsigned arithmetic
macros and their generated scalar lowerings. It does not compile the upstream
application, execute a vulnerability, or infer callsite/type applicability.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import proof_dag_checker as core
from proof_dag_producer import produce
from checker import Session
from macro_bridge import translate
from upstream_ceil_case import M_AXIS,N_AXIS,REFERENCE,source,retrieve


def store(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(out,verify_upstream=False,native=False):
    if out.exists():raise ValueError('output must be new')
    metadata=json.loads((ROOT/'public-data/ceil-div-source.json').read_text(encoding='utf-8'))
    # This separate retrieval checks entire immutable source files and the
    # selected lines. Offline replay does not pretend to have retrieved them.
    retrieval=retrieve() if verify_upstream else None
    before=translate(metadata['before']['line'],['m','n'])
    after=translate(metadata['after']['line'],['m','n'])
    request=dict(id='typed-upstream-ceil',word_bits=32,inputs={'m':M_AXIS,'n':N_AXIS},
                 original=before['source'],candidate=after['source'],reference=source(REFERENCE),
                 repair_guard='m > (4294967295u - (n - 1u))')
    packet=produce(request);checked=core.check(request,packet);direct=core.evaluate_topological(request)
    if checked['status']!='ACCEPT' or not core.exact_equal(checked['witness'],direct['witness']):
        raise ValueError('lowered repair policy differs')
    if checked['checked_cells']!=direct['checked_cells']:raise ValueError('unequal direct baseline')
    session=Session(request);points=list(itertools.product(M_AXIS,N_AXIS));rows=[];U=2**32-1
    for m,n in points:
        if not 0<=m<=U or not 1<=n<=U:raise ValueError('unsafe native domain')
        expected=[((m+n-1)%(2**32))//n,(m+n-1)//n]
        observations=[]
        for role,value in zip(('original','candidate'),expected):
            defined,actual,_trace=session.run(role,{'m':m,'n':n})
            if not defined or actual!=value:raise ValueError('source/reference disagreement')
            observations.append(actual)
        rows.append(dict(input=[m,n],old=observations[0],new=observations[1],
                         repair_region=m+n-1>U))
    out.mkdir(parents=True)
    store(out/'request.json',request);store(out/'certificate.json',packet)
    store(out/'lowering.json',dict(before=before,after=after))
    native_rows=[];compilers=[]
    if native:
        definitions=[metadata[role]['line'].replace('#define CEIL_DIV(',
                     '#define '+name+'(',1) for role,name in [('before','OLD_CEIL'),('after','NEW_CEIL')]]
        old_source=before['source'].replace('unsigned f(','unsigned old_lowered(',1)
        new_source=after['source'].replace('unsigned f(','unsigned new_lowered(',1)
        inputs=',\n'.join('{'+str(m)+'u,'+str(n)+'u}' for m,n in points)
        harness='\n'.join(('#include <stdio.h>','#include <limits.h>',
                   '_Static_assert(UINT_MAX == 4294967295u, "requires unsigned32");',
                   *definitions,old_source,new_source,'static const unsigned inputs[][2] = {'+inputs+'};',
                   'int main(void) { for (unsigned i=0;i<42u;++i) {',
                   'unsigned m=inputs[i][0],n=inputs[i][1];',
                   'printf("%u,%u,%u,%u\\n",OLD_CEIL(m,n),NEW_CEIL(m,n),old_lowered(m,n),new_lowered(m,n));',
                   '} return 0; }'))+'\n'
        (out/'native-harness.c').write_text(harness,encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='repairseal-reviewed-macro-') as temporary:
            scratch=Path(temporary);code=scratch/'harness.c';code.write_text(harness,encoding='utf-8')
            for name in ('gcc','clang'):
                executable=shutil.which(name)
                if not executable:raise ValueError('native study needs GCC and Clang')
                binary=scratch/('macro-'+name)
                command=[executable,'-std=c11','-O2',str(code),'-o',str(binary)]
                built=subprocess.run(command,capture_output=True,text=True,timeout=15,check=False)
                if built.returncode:raise ValueError('native compilation failed: '+built.stderr)
                observed=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5,check=False)
                if observed.returncode:raise ValueError('native harness failed')
                lines=observed.stdout.splitlines()
                if len(lines)!=42:raise ValueError('native row count')
                for row,line in zip(rows,lines):
                    values=[int(x) for x in line.split(',')]
                    expected=[row['old'],row['new'],row['old'],row['new']]
                    if values!=expected:raise ValueError('native macro/lowering disagreement')
                    native_rows.append(dict(compiler=name,input=row['input'],
                                            old_macro=values[0],new_macro=values[1],
                                            old_lowered=values[2],new_lowered=values[3]))
                version=subprocess.run([executable,'--version'],capture_output=True,text=True,timeout=5,check=True)
                compilers.append(dict(id=name,executable=str(Path(executable).resolve()),
                                      version_first_line=version.stdout.splitlines()[0],
                                      flags=['-std=c11','-O2'],compile_returncode=built.returncode,run_returncode=observed.returncode))
    store(out/'observations.json',rows)
    if native:store(out/'native-observations.json',native_rows)
    summary=dict(upstream_changes=1,selected_macro_definitions=2,inputs=42,
                 repair_inputs=sum(row['repair_region'] for row in rows),
                 preserved_inputs=sum(not row['repair_region'] for row in rows),
                 status=checked['status'],canonical_witness=checked['witness'],
                 cells_per_full_or_direct_arm=checked['checked_cells'],
                 lowered_models_match_mathematical_reference=True,
                 upstream_source_retrieval=retrieval,native_harness_executed=native,
                 native_input_rows=len(native_rows),native_scalar_observations=4*len(native_rows),
                 compilers=compilers,upstream_application_executed=False,
                 bridge_scope='Selected pure unsigned expression lowering only; no preprocessing/callsite/type inference or general C admission',
                 diagnostic_scope='Traces belong to the generated scalar normalization, not native macro events',
                 source_bindings={name:sha(ROOT/name) for name in ('src/macro_bridge.py','tests/macro_transfer_study.py','public-data/ceil-div-source.json')})
    store(out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('compilers','source_bindings','upstream_source_retrieval')}))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--verify-upstream',action='store_true')
    parser.add_argument('--native',action='store_true')
    args=parser.parse_args();run(args.output,args.verify_upstream,args.native)
