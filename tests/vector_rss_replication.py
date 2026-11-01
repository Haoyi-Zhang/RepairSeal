"""Complete independent RSS replication; never extend or splice the stopped run.

One attempt only. Freeze all inputs and limits before any measurement. The
original child implements the same four arms; it is not changed by this file.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rss_original', ROOT/'tests/vector_rss_study.py')
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
LIMITS = dict(wall_seconds=300, total_cpu_seconds=180, child_address_bytes=1073741824,
              child_cpu_seconds=3, workers=1, subprocesses=600)

def prepare(directory):
    if sys.platform != 'linux' or directory.exists():
        raise ValueError('requires Linux and a fresh output directory')
    directory.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rss-prepare-', dir=directory.parent) as temporary:
        generated = Path(temporary)/'wires'
        original.prepare(generated)
        protocol = original.read(generated/'protocol.json')
        protocol.update(scope='Independent full-cohort RSS replication after explicit user continuation request; prior interrupted activity stays incomplete',
            prior_activity=dict(status='INCOMPLETE_BUDGET_STOP', recorded_measurements=584,
                                original_wall_limit_seconds=110, records_merged=False),
            limits=LIMITS,
            stopping_rule='One complete600-measurement attempt, no retry, no extension or outcome filtering',
            interpretation='Descriptive paired process RSS, not a benefit target, independent-program sample or throughput experiment')
        protocol['source_bindings']['tests/vector_rss_replication.py'] = original.seal(Path(__file__).resolve())
        directory.mkdir()
        for source in generated.iterdir():
            if source.name != 'protocol.json':
                shutil.copyfile(source, directory/source.name)
        original.write(directory/'protocol.json', protocol)
    print(json.dumps(dict(protocol_sha256=original.seal(directory/'protocol.json'),
                          measurements=len(protocol['order']), limits=LIMITS)))

def run(directory):
    protocol = original.read(directory/'protocol.json')
    if protocol['limits'] != LIMITS or protocol['prior_activity']['records_merged']:
        raise ValueError('frozen independent resource/lineage plan differs')
    # Exclusive sentinel persists even on a budget stop or process failure.
    original.write(directory/'attempt-started.json', dict(protocol_sha256=original.seal(directory/'protocol.json'),
                   one_attempt_only=True, pid=os.getpid()))
    original.run(directory)
    result = original.read(directory/'results.json')
    if result['summary']['measurements'] != 600 or result['resources']['wall_seconds'] > 300 or result['resources']['child_cpu_seconds'] > 180:
        raise ValueError('completion/resource admission failed; retain all raw data')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--run', action='store_true')
    args=parser.parse_args()
    (prepare if args.prepare else run)(args.directory.resolve())

if __name__ == '__main__':
    main()
