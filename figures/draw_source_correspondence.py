"""Visualize the two retained natural-source mappings without rerunning them."""
import csv
import json
from collections import Counter
from pathlib import Path
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

HERE=Path(__file__).resolve().parent
DATA=HERE.parent/'results/source-correspondence'

def render(out=HERE/'source-correspondence.pdf'):
    from validation_panels import repair_mappings
    model=json.loads((DATA/'model-outcomes.json').read_text(encoding='utf-8'))
    assert len(model)==4 and sum(r['direct_cells'] for r in model)==4352
    with (DATA/'native-observations.csv').open(encoding='utf-8',newline='') as f:
        observations=list(csv.DictReader(f))
    seen=Counter((r['case'],r['role']) for r in observations if r['agrees']=='True')
    assert len(observations)==sum(seen.values())==256
    return repair_mappings(model,seen,out)

if __name__=='__main__':
    render()
