"""Generate the paper's consumer counts only from current bound observations."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
REQUIRED_SOURCE_BINDINGS=frozenset((
    'tests/descriptor_consumer_study.py','src/macro_bridge.py',
    'public-data/ceil-div-source.json','public-data/descriptor-context.json'))

def load_json(path):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('duplicate consumer JSON key '+key)
            result[key]=value
        return result
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)

def validate_source_bindings(summary):
    """The inventory comes from the producer, never from the supplied map."""
    bindings=summary.get('source_bindings') if type(summary) is dict else None
    if type(bindings) is not dict or set(bindings)!=REQUIRED_SOURCE_BINDINGS:
        raise ValueError('consumer source binding inventory')
    if any(type(digest) is not str or re.fullmatch(r'[0-9a-f]{64}',digest) is None
           for digest in bindings.values()):
        raise ValueError('consumer source binding digest format')
    for rel in sorted(REQUIRED_SOURCE_BINDINGS):
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=bindings[rel]:
            raise ValueError('stale consumer source '+rel)

def consumer_contract():
    contract=load_json(ROOT/'public-data/descriptor-context.json')
    initial=contract['initial_state'];budget=contract['iteration_limit']
    if (type(initial) is not dict or set(initial)!={'requested','allocated','consumed'}
            or any(type(value) is not int for value in initial.values())
            or type(budget) is not int or not 1<=budget<=64):
        raise ValueError('consumer fixture accounting contract')
    return initial,budget

def validate_native_rows(rows, native, contract=None):
    """Check the complete retained compiler/input/role product without execution."""
    from descriptor_consumer_study import U, accounting, ceiling
    from upstream_ceil_case import M_AXIS,N_AXIS
    initial,budget=consumer_contract() if contract is None else contract
    expected_inputs={(batch,limit) for batch in M_AXIS for limit in N_AXIS if ceiling(batch,limit)<=budget}
    if type(rows) is not list or len(rows)!=len(expected_inputs) or type(native) is not list:
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
            wanted=accounting(batch,limit,reservation,initial,budget)
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

def validate_partition(rows,excluded,budget):
    """Recompute every fixture-axis identity and its budget classification."""
    from descriptor_consumer_study import ceiling
    from upstream_ceil_case import M_AXIS,N_AXIS
    domain={(batch,limit) for batch in M_AXIS for limit in N_AXIS}
    expected={key for key in domain if ceiling(*key)>budget}
    if type(excluded) is not list: raise ValueError('descriptor excluded inventory')
    seen=set()
    for row in excluded:
        if type(row) is not dict or set(row)!={'batch','limit','required_dispatches','reason'}:
            raise ValueError('descriptor excluded schema')
        if any(type(row[key]) is not int for key in ('batch','limit','required_dispatches')):
            raise ValueError('descriptor excluded scalar types')
        key=(row['batch'],row['limit'])
        if key not in expected or key in seen:
            raise ValueError('descriptor excluded input coverage')
        if row['required_dispatches']!=ceiling(*key) or row['reason']!='predeclared loop budget':
            raise ValueError('descriptor excluded budget/reason disagreement')
        seen.add(key)
    admitted={(row['batch'],row['limit']) for row in rows}
    if seen!=expected or admitted & seen or admitted | seen!=domain:
        raise ValueError('descriptor input partition coverage')
    return domain

def report(results):
    summary=load_json(results/'summary.json')
    validate_source_bindings(summary)
    initial,budget=consumer_contract()
    rows=load_json(results/'observations.json');excluded=load_json(results/'excluded.json');native=load_json(results/'native-observations.json')
    validate_native_rows(rows,native,(initial,budget))
    domain=validate_partition(rows,excluded,budget)
    expected=dict(input_pairs=len(domain),native_loop_admitted_pairs=len(rows),excluded_pairs=len(excluded),
        old_under_reserved_pairs=sum(not row['old']['requested_increment_covers_loop'] for row in rows),
        old_consumer_failed_pairs=sum(not row['old']['dispatches_fit'] for row in rows),
        new_consumer_success_pairs=sum(row['new']['dispatches_fit'] for row in rows),native_role_rows=len(native))
    if any(type(summary.get(k)) is not int or summary[k]!=value for k,value in expected.items()):
        raise ValueError('consumer summary mismatch')
    if (type(summary.get('initial_state')) is not dict or set(summary['initial_state'])!=set(initial)
            or any(type(summary['initial_state'][k]) is not int or summary['initial_state'][k]!=v for k,v in initial.items())
            or type(summary.get('maximum_dispatches_per_pair')) is not int or summary['maximum_dispatches_per_pair']!=budget):
        raise ValueError('consumer summary accounting contract mismatch')
    context=summary.get('source_context')
    if (summary.get('native_executed') is not True or type(context) is not dict
            or context.get('fresh_whole_source_verified') is not True):
        raise ValueError('paper evidence needs recorded native run and whole-source verification')
    if (summary.get('upstream_application_or_gpu_executed') is not False
            or type(summary.get('new_independent_programs')) is not int or summary['new_independent_programs']!=0):
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
