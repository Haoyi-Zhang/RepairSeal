"""Render the manuscript example as a vector PDF."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "artifact/figures"))

def repair(root,output):
    import json
    from validation_panels import repair_grid
    source=root/'artifact/results/upstream-ceil/summary.json'
    cases={x['variant']:x for x in json.loads(source.read_text(encoding='utf-8'))['cases']}
    points={tuple(x['input']) for x in cases['original']['observations']}
    return repair_grid(points,output)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path(__file__).with_name('ceil-obligations.pdf'))
    a=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    repair(root,a.output)
