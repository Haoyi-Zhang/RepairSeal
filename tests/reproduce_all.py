#!/usr/bin/env python3
"""Run offline reproduction and write its summary."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    core = Path(__file__).with_name("reproduce_all_core.py")
    proc = subprocess.run(
        [sys.executable, str(core), "--output", str(args.output)],
        text=True,
        capture_output=True,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
    )
    if proc.returncode:
        if proc.stdout:
            print(proc.stdout, end="", file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        raise SystemExit(proc.returncode)
    result_path = args.output / "complete-reproduction.json"
    result = json.loads(result_path.read_text())
    root=Path(__file__).resolve().parents[1]
    stream_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_vector_stream.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_vector_stream.py','-v'],
        [sys.executable,'-B',str(root/'tests/vector_stream_study.py'),'--output',
         str(args.output.resolve()/'vector-stream.json'),'--compare',str(root/'results/vector-stream.json')],
    ]
    for index,command in enumerate(stream_commands):
        check=subprocess.run(command,cwd=root,capture_output=True,text=True,
                             env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
        (args.output/('vector-stream-check-'+str(index)+'.txt')).write_text(
            check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:
            raise SystemExit('bounded vector stream reproduction failed: '+str(index))
    stream_result=json.loads((args.output/'vector-stream.json').read_text(encoding='utf-8'))
    result['vector_stream_agreement']={
        'requests':stream_result['requests'],'semantic_cells_per_arm':stream_result['totals']['checked_cells_per_arm'],
        'ordinary_and_optimized_conformance':True,
        'allocation_measurement':'retained separate runtime-specific study; not rerun by deterministic gate',
    }
    macro_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_macro_bridge.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_macro_bridge.py','-v'],
        [sys.executable,'-B',str(root/'tests/macro_transfer_study.py'),'--native','--output',
         str(args.output.resolve()/'macro-transfer')],
    ]
    for index,command in enumerate(macro_commands):
        check=subprocess.run(command,cwd=root,capture_output=True,text=True,
                             env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
        (args.output/('macro-transfer-check-'+str(index)+'.txt')).write_text(
            check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('typed macro transfer reproduction failed: '+str(index))
    macro=json.loads((args.output/'macro-transfer/summary.json').read_text(encoding='utf-8'))
    result['typed_macro_transfer']={k:macro[k] for k in
        ('upstream_changes','inputs','repair_inputs','preserved_inputs','status',
         'cells_per_full_or_direct_arm','native_input_rows','native_scalar_observations',
         'upstream_application_executed')}
    descriptor_commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_descriptor_consumer.py','-v'],
        [sys.executable,'-O','-B','-m','unittest','discover','-s','tests','-p','test_descriptor_consumer.py','-v'],
        [sys.executable,'-B',str(root/'tests/descriptor_consumer_study.py'),'--native','--output',
         str(args.output.resolve()/'descriptor-consumer'),'--compare',str(root/'results/descriptor-consumer')],
    ]
    for index,command in enumerate(descriptor_commands):
        check=subprocess.run(command,cwd=root,capture_output=True,text=True,
                             env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
        (args.output/('descriptor-consumer-check-'+str(index)+'.txt')).write_text(check.stdout+check.stderr,encoding='utf-8')
        if check.returncode:raise SystemExit('descriptor consumer reproduction failed: '+str(index))
    descriptor=json.loads((args.output/'descriptor-consumer/summary.json').read_text(encoding='utf-8'))
    result['descriptor_consumer']={k:descriptor[k] for k in
        ('input_pairs','native_loop_admitted_pairs','excluded_pairs','old_under_reserved_pairs',
         'new_consumer_success_pairs','native_role_rows','upstream_application_or_gpu_executed')}
    candidates = list(args.output.rglob("structured-study.json"))
    if len(candidates) != 1:
        raise SystemExit(f"expected one structured-study.json, found {len(candidates)}")
    study = json.loads(candidates[0].read_text())
    result.update(
        {
            "structured_requests": study["total_requests"],
            "oracle_agreements": study["oracle_agreements"],
            "full_vector_tamper_controls": study["tamper_attempts"],
            "full_vector_tamper_rejections": study["tamper_rejections"],
            "refutation_witnesses": study["refutation_witnesses"],
            "refutation_witness_agreements": study["refutation_witness_agreements"],
            "refutation_tamper_controls": study["refutation_tamper_attempts"],
            "refutation_tamper_rejections": study["refutation_tamper_rejections"],
            "acceptance_misuse_controls": study["acceptance_misuse_attempts"],
            "acceptance_misuse_rejections": study["acceptance_misuse_rejections"],
            "total_certificate_negative_controls": (
                study["tamper_attempts"]
                + study["refutation_tamper_attempts"]
                + study["acceptance_misuse_attempts"]
            ),
            "full_vector_work_equivalence": study["work_equivalence"],
            "compact_refutation_work": study["refutation_work"],
            "scope_note": (
                "Codeflaws evidence is a pinned archival index audit; public sources "
                "are not executed. Generated stress requests are not Codeflaws."
            ),
        }
    )
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
