"""Source-derived reservation/consumption, separate from actual Vulkan execution."""
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
from checker import Session
from macro_bridge import translate
from proof_dag_producer import produce
from proof_dag_checker import check,evaluate_topological
from upstream_ceil_case import M_AXIS,N_AXIS,REFERENCE,source

U=2**32-1

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def ceiling(batch,limit):
    if type(batch) is not int or type(limit) is not int or not 0<=batch<=U or not 1<=limit<=U:
        raise ValueError('unsigned32 batch and positive unsigned32 limit required')
    return 0 if batch==0 else 1+(batch-1)//limit

def accounting(batch,limit,reservation,initial,iteration_limit=64):
    required=ceiling(batch,limit)
    if type(iteration_limit) is not int or not 1<=iteration_limit<=64 or required>iteration_limit:
        raise ValueError('predeclared loop budget exceeded')
    if type(reservation) is not int or not 0<=reservation<=U:
        raise ValueError('reservation type/range')
    if set(initial)!={'requested','allocated','consumed'} or any(type(v) is not int or not 0<=v<=U for v in initial.values()):
        raise ValueError('initial accounting schema')
    requested,allocated,index=(initial[k] for k in ('requested','allocated','consumed'))
    if not index<=requested<=allocated or requested+reservation>U:
        raise ValueError('unproved prior balance or cumulative overflow')
    requested+=reservation
    if allocated<requested:
        allocated=max(3*allocated//2,requested)
        if allocated>U:raise ValueError('unproved allocation-size narrowing')
    base=0;completed=0;failed=False
    while base<batch:
        if completed>=iteration_limit:raise ValueError('loop exceeded registered budget')
        groups=min(batch-base,limit)
        if index>=allocated:
            failed=True;break
        index+=1;completed+=1;base+=groups
    return dict(requested=requested,allocated=allocated,consumed=index,
                completed_dispatches=completed,required_dispatches=required,
                first_unreserved_dispatch=completed if failed else None,
                requested_increment_covers_loop=reservation>=required,
                dispatches_fit=not failed,final_base=base)

def verify_context(before,after):
    if (before is None)!=(after is None):raise ValueError('both immutable source files are required')
    if before is None:return dict(fresh_whole_source_verified=False,mode='offline retained contract only')
    provenance=json.loads((ROOT/'public-data/ceil-div-source.json').read_text(encoding='utf-8'))
    context=json.loads((ROOT/'public-data/descriptor-context.json').read_text(encoding='utf-8'))
    rows=[]
    for role,path in [('before',before),('after',after)]:
        if not path.is_file() or path.stat().st_size>2_000_000 or sha(path)!=provenance[role]['sha256']:
            raise ValueError('whole source identity mismatch '+role)
        lines=path.read_text(encoding='utf-8').splitlines();stripped=[line.strip() for line in lines]
        if provenance[role]['line'] not in stripped:raise ValueError('macro identity mismatch')
        caller=stripped.index('static void ggml_vk_matmul(')
        end=next(i for i in range(caller+1,len(stripped)) if stripped[i].startswith('static vk_pipeline ggml_vk_guess_matmul_id_pipeline'))
        selected=stripped[caller:end]
        anchors=[]
        for anchor in context['caller_anchors']:
            if anchor not in selected:raise ValueError('caller anchor mismatch '+role)
            anchors.append(dict(line=caller+selected.index(anchor)+1,text=anchor))
        for anchor in context['accounting_anchors']:
            if anchor not in stripped:raise ValueError('accounting anchor mismatch '+role)
            anchors.append(dict(line=stripped.index(anchor)+1,text=anchor))
        rows.append(dict(role=role,bytes=path.stat().st_size,sha256=sha(path),anchors=anchors))
    return dict(fresh_whole_source_verified=True,mode='exact selected anchors in both complete immutable sources',sources=rows,
                general_callsite_inference=False,upstream_application_executed=False)

def native_observations(rows,definitions,out):
    inputs=',\n'.join('{'+str(row['batch'])+'u,'+str(row['limit'])+'u}' for row in rows)
    code='\n'.join(('#include <stdint.h>','#include <stdio.h>','#include <limits.h>',
      '_Static_assert(UINT_MAX == 4294967295u, "requires unsigned32");',
      definitions['before'].replace('#define CEIL_DIV(','#define OLD(',1),
      definitions['after'].replace('#define CEIL_DIV(','#define NEW(',1),
      'static const uint32_t inputs[][2] = {'+inputs+'};',
      'static void run(uint32_t batch,uint32_t limit,uint32_t n,unsigned role,unsigned pos) {',
      'uint32_t requested=4u+n,allocated=4u,index=4u,base=0u,completed=0u; unsigned failed=0u;',
      'if(allocated<requested) allocated=6u>requested?6u:requested;',
      'while(base<batch) { uint32_t left=batch-base,groups=left<limit?left:limit;',
      'if(completed>=64u) return;',
      'if(index>=allocated) { failed=1u; break; } ++index; ++completed; base+=groups; }',
      'printf("%u,%u,%u,%u,%u,%u,%u,%u,%u\\n",pos,role,n,requested,allocated,index,completed,failed,base); }',
      'int main(void) { for(unsigned i=0;i<sizeof(inputs)/sizeof(inputs[0]);++i) {',
      'uint32_t b=inputs[i][0],n=inputs[i][1]; run(b,n,OLD(b,n),0u,i); run(b,n,NEW(b,n),1u,i); } return 0; }'))+'\n'
    (out/'accounting-harness.c').write_text(code,encoding='utf-8')
    observed=[];tools=[]
    with tempfile.TemporaryDirectory(prefix='repairseal-accounting-') as temporary:
        scratch=Path(temporary);p=scratch/'consumer.c';p.write_text(code,encoding='utf-8')
        for compiler in ('gcc','clang'):
            exe=shutil.which(compiler)
            if not exe:raise ValueError('native consumer requires GCC and Clang')
            binary=scratch/compiler
            compiled=subprocess.run([exe,'-std=c11','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(binary)],capture_output=True,text=True,timeout=15)
            if compiled.returncode:raise ValueError(compiled.stderr)
            executed=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5)
            if executed.returncode or executed.stderr:raise ValueError('native consumer failed')
            lines=executed.stdout.splitlines()
            if len(lines)!=2*len(rows):raise ValueError('native row count')
            for ordinal,line in enumerate(lines):
                values=[int(v) for v in line.split(',')]
                if len(values)!=9:raise ValueError('native row schema')
                pos,role=divmod(ordinal,2)
                if values[:2]!=[pos,role]:raise ValueError('native row ordering')
                label=('old','new')[role];expected=rows[pos][label]
                wanted=[rows[pos][label+'_reservation'],expected['requested'],expected['allocated'],expected['consumed'],
                        expected['completed_dispatches'],int(not expected['dispatches_fit']),expected['final_base']]
                if values[2:]!=wanted:raise ValueError('native/accounting disagreement')
                observed.append(dict(compiler=compiler,batch=rows[pos]['batch'],limit=rows[pos]['limit'],role=label,values=values[2:]))
            version=subprocess.run([exe,'--version'],capture_output=True,text=True,timeout=5,check=True)
            tools.append(dict(compiler=compiler,executable=str(Path(exe).resolve()),version_first_line=version.stdout.splitlines()[0],
                              flags=['-std=c11','-O2','-Wall','-Wextra','-Werror'],compile_returncode=compiled.returncode,run_returncode=executed.returncode))
    return observed,tools

def run(out,before=None,after=None,native=False,compare=None):
    if out.exists():raise ValueError('output must be new')
    context=verify_context(before,after)
    provenance=json.loads((ROOT/'public-data/ceil-div-source.json').read_text(encoding='utf-8'))
    contract=json.loads((ROOT/'public-data/descriptor-context.json').read_text(encoding='utf-8'))
    translated={role:translate(provenance[role]['line'],['m','n'])['source'] for role in ('before','after')}
    request=dict(id='descriptor-allocation-policy',word_bits=32,inputs={'m':M_AXIS,'n':N_AXIS},
                 original=translated['before'],candidate=translated['after'],reference=source(REFERENCE),
                 repair_guard='m > (4294967295u - (n - 1u))')
    packet=produce(request);full=check(request,packet);direct=evaluate_topological(request)
    if full['status']!='ACCEPT' or full['witness']!=direct['witness'] or full['checked_cells']!=direct['checked_cells']:
        raise ValueError('certificate/direct decision mismatch')
    session=Session(request);rows=[];excluded=[]
    for batch,limit in itertools.product(M_AXIS,N_AXIS):
        required=ceiling(batch,limit)
        if required>contract['iteration_limit']:
            excluded.append(dict(batch=batch,limit=limit,required_dispatches=required,reason='predeclared loop budget'));continue
        reservations=[]
        for role in ('original','candidate'):
            defined,value,_=session.run(role,{'m':batch,'n':limit})
            if not defined:raise ValueError('undefined reservation')
            reservations.append(value)
        if reservations[1]!=required:raise ValueError('repair certificate/reference mismatch')
        old,new=[accounting(batch,limit,value,contract['initial_state'],contract['iteration_limit']) for value in reservations]
        if not new['dispatches_fit'] or not new['requested_increment_covers_loop'] or new['completed_dispatches']!=required:raise ValueError('new consumer contract failed')
        rows.append(dict(batch=batch,limit=limit,required_dispatches=required,
                         old_reservation=reservations[0],new_reservation=reservations[1],old=old,new=new))
    out.mkdir(parents=True)
    observations=[];compilers=[]
    if native:
        observations,compilers=native_observations(rows,{role:provenance[role]['line'] for role in ('before','after')},out)
    summary=dict(input_pairs=42,native_loop_admitted_pairs=len(rows),excluded_pairs=len(excluded),
                 initial_state=contract['initial_state'],maximum_dispatches_per_pair=contract['iteration_limit'],
                 old_under_reserved_pairs=sum(not row['old']['requested_increment_covers_loop'] for row in rows),
                 old_consumer_failed_pairs=sum(not row['old']['dispatches_fit'] for row in rows),
                 new_consumer_success_pairs=sum(row['new']['dispatches_fit'] for row in rows),
                 full_certificate_status=full['status'],cells_per_full_or_direct_arm=full['checked_cells'],
                 native_executed=native,native_role_rows=len(observations),compilers=compilers,source_context=context,
                 new_independent_programs=0,upstream_application_or_gpu_executed=False,
                 source_bindings={name:sha(ROOT/name) for name in ('tests/descriptor_consumer_study.py','src/macro_bridge.py',
                     'public-data/ceil-div-source.json','public-data/descriptor-context.json')},
                 scope='Owned source-derived local accounting abstraction. Exact unchanged caller anchors and conditional loop correspondence, not a general source translator or local reproduction of the upstream device report.')
    save(out/'observations.json',rows);save(out/'excluded.json',excluded)
    if native:save(out/'native-observations.json',observations)
    save(out/'request.json',request);save(out/'certificate.json',packet);save(out/'summary.json',summary)
    if compare is not None:
        retained=json.loads((compare/'summary.json').read_text(encoding='utf-8'))
        for key in ('input_pairs','native_loop_admitted_pairs','excluded_pairs','initial_state',
                    'maximum_dispatches_per_pair','old_under_reserved_pairs','old_consumer_failed_pairs','new_consumer_success_pairs',
                    'full_certificate_status','cells_per_full_or_direct_arm','source_bindings'):
            if summary[key]!=retained[key]:raise ValueError('retained consumer field mismatch '+key)
        for name in ('observations.json','excluded.json','request.json','certificate.json'):
            if json.loads((out/name).read_text(encoding='utf-8'))!=json.loads((compare/name).read_text(encoding='utf-8')):
                raise ValueError('retained consumer data mismatch '+name)
        if native:
            if observations!=json.loads((compare/'native-observations.json').read_text(encoding='utf-8')):
                raise ValueError('retained native observations differ')
        save(out/'retained-comparison.json',dict(semantic_fields_equal=True,request_packet_and_rows_equal=True,
             native_rows_equal=True if native else None,
             original_acquisition_repeated=before is not None,upstream_application_or_gpu_executed=False))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('source_context','compilers','source_bindings')}))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-before',type=Path);parser.add_argument('--source-after',type=Path)
    parser.add_argument('--compare',type=Path)
    parser.add_argument('--native',action='store_true')
    args=parser.parse_args();run(args.output,args.source_before,args.source_after,args.native,args.compare)
