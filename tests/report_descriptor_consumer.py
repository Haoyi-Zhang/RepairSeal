"""Generate the paper's consumer counts only from current bound observations."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def validate_native_rows(rows, native):
    """Check the complete retained compiler/input/role product without execution."""
    from descriptor_consumer_study import U, accounting, ceiling
    from upstream_ceil_case import M_AXIS,N_AXIS
    expected_inputs={(batch,limit) for batch in M_AXIS for limit in N_AXIS if ceiling(batch,limit)<=64}
    if type(rows) is not list or len(rows)!=32 or type(native) is not list:
        raise ValueError('descriptor observation inventory')
    inputs={}
    for row in rows:
        fields={'batch','limit','old','new','old_reservation','new_reservation','required_dispatches'}
        if type(row) is not dict or set(row)!=fields or any(type(row.get(k)) is not int for k in ('batch','limit')):
            raise ValueError('descriptor input types')
        key=(row['batch'],row['limit'])
        if key not in expected_inputs or key in inputs: raise ValueError('descriptor model input coverage')
        batch,limit=key
        reservations={'old':((batch+limit-1)&U)//limit,'new':ceiling(batch,limit)}
        if type(row['required_dispatches']) is not int or row['required_dispatches']!=ceiling(batch,limit):
            raise ValueError('descriptor dispatch count')
        for role,reservation in reservations.items():
            if type(row[role+'_reservation']) is not int or row[role+'_reservation']!=reservation:
                raise ValueError('descriptor reservation disagreement')
            wanted=accounting(batch,limit,reservation,dict(requested=4,allocated=4,consumed=4))
            model=row[role]
            if type(model) is not dict or set(model)!=set(wanted) or any(
                    type(model[k]) is not type(value) or model[k]!=value for k,value in wanted.items()):
                raise ValueError('descriptor model accounting disagreement')
        inputs[key]=row
    if set(inputs)!=expected_inputs: raise ValueError('descriptor model input coverage')
    expected={(compiler,batch,limit,role) for compiler in ('gcc','clang')
              for batch,limit in inputs for role in ('old','new')}
    seen=set()
    for item in native:
        if type(item) is not dict or set(item)!={'compiler','batch','limit','role','values'}:
            raise ValueError('descriptor native row schema')
        if any(type(item[k]) is not int for k in ('batch','limit')):
            raise ValueError('descriptor native input types')
        if type(item['compiler']) is not str or type(item['role']) is not str:
            raise ValueError('descriptor native labels')
        key=(item['compiler'],item['batch'],item['limit'],item['role'])
        if key not in expected or key in seen: raise ValueError('descriptor native key coverage')
        seen.add(key)
        values=item['values']
        if type(values) is not list or len(values)!=7 or any(type(value) is not int for value in values):
            raise ValueError('descriptor native scalar types')
        row=inputs[(item['batch'],item['limit'])];role=item['role'];model=row[role]
        integer_fields=('requested','allocated','consumed','completed_dispatches','final_base')
        if any(type(model[k]) is not int for k in integer_fields) or type(model['dispatches_fit']) is not bool:
            raise ValueError('descriptor model scalar types')
        if type(row[role+'_reservation']) is not int: raise ValueError('descriptor reservation type')
        wanted=[row[role+'_reservation'],model['requested'],model['allocated'],model['consumed'],
                model['completed_dispatches'],int(not model['dispatches_fit']),model['final_base']]
        if values!=wanted: raise ValueError('native/accounting disagreement')
    if seen!=expected: raise ValueError('descriptor native key coverage')

def report(results):
    read=lambda name:json.loads((results/name).read_text(encoding='utf-8'))
    summary=read('summary.json');rows=read('observations.json');excluded=read('excluded.json');native=read('native-observations.json')
    validate_native_rows(rows,native)
    for rel,digest in summary['source_bindings'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=digest:raise ValueError('stale consumer source '+rel)
    expected=dict(input_pairs=len(rows)+len(excluded),native_loop_admitted_pairs=len(rows),excluded_pairs=len(excluded),
        old_under_reserved_pairs=sum(not row['old']['requested_increment_covers_loop'] for row in rows),
        old_consumer_failed_pairs=sum(not row['old']['dispatches_fit'] for row in rows),
        new_consumer_success_pairs=sum(row['new']['dispatches_fit'] for row in rows),native_role_rows=len(native))
    if any(summary[k]!=value for k,value in expected.items()):raise ValueError('consumer summary mismatch')
    if not summary['native_executed'] or not summary['source_context']['fresh_whole_source_verified']:
        raise ValueError('paper evidence needs recorded native run and whole-source verification')
    if summary['upstream_application_or_gpu_executed'] or summary['new_independent_programs']:
        raise ValueError('evidence domain changed')
    reported=[row for row in rows if row['limit']==2**32-1]
    return ('% Generated from the current source-derived descriptor consumer.\n'+
        '\\newcommand{\\DescriptorAdmitted}{'+str(expected['native_loop_admitted_pairs'])+'}\n'+
        '\\newcommand{\\DescriptorExcluded}{'+str(expected['excluded_pairs'])+'}\n'+
        '\\newcommand{\\DescriptorOldFailures}{'+str(expected['old_consumer_failed_pairs'])+'}\n'+
        '\\newcommand{\\DescriptorReportedLimitPairs}{'+str(len(reported))+'}\n'+
        '\\newcommand{\\DescriptorNativeRows}{'+str(expected['native_role_rows'])+'}\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,default=ROOT/'results/descriptor-consumer')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.write_text(report(args.results),encoding='utf-8')
