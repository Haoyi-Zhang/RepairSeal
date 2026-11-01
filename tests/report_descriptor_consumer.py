"""Generate the paper's consumer counts only from current bound observations."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def report(results):
    read=lambda name:json.loads((results/name).read_text(encoding='utf-8'))
    summary=read('summary.json');rows=read('observations.json');excluded=read('excluded.json');native=read('native-observations.json')
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
