import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render(path):
    data=json.loads((ROOT/'results/admission-journal/summary.json').read_text())
    if data['status']!='PASS' or data['requests']!=data['proof_direct_agreements']:raise ValueError('incomplete admission results')
    fields={'AdmissionRequests':'requests','AdmissionProcesses':'receiver_processes','AdmissionApprovals':'approved','AdmissionRefutations':'refuted'}
    path.write_text(''.join('\\newcommand{\\'+key+'}{'+str(data[value])+'}\n' for key,value in fields.items()),encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);render(p.parse_args().output)
