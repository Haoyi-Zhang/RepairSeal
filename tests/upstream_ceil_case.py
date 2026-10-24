"""Source-linked ceiling-division policy case; only reviewed owned models run.

The optional retrieval reads fingerprinted official source as text. It never
builds or executes llama.cpp, upstream scripts, Vulkan, or an exploit.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from checker import Session
from proof_dag_checker import check, evaluate_topological, canonical_bytes, Invalid
from proof_dag_producer import produce
from refutation_witness_checker import check as point_check
from refutation_witness_producer import produce as point_produce

H = 2**32-1
M_AXIS = [0, 1, 2, 31, 32, H-1, H]
N_AXIS = [1, 2, 3, 7, 32, H]
VARIANTS = ("original", "supplied", "regression", "definedness", "trace-overfit")
OLD = "return (m + n - 1u) / n;"
SAFE = ("unsigned r = m / n; if (m % n != 0u) { r = r + 1u; } "
        "else { r = r; } ")
REFERENCE = ("unsigned r = 0u; if (m == 0u) { r = 0u; } "
             "else { r = 1u + (m - 1u) / n; } return r;")


def source(body):
    return "unsigned f(unsigned m, unsigned n) { " + body + " }"


def request(variant):
    bodies = {
        "original": OLD,
        "supplied": SAFE + "return r;",
        "regression": SAFE + "if (m == 0u) { r = 1u; } else { r = r; } return r;",
        "definedness": "unsigned discarded = 1u / (n - 1u); " + SAFE + "return r;",
        "trace-overfit": (
            "unsigned r = (m + n - 1u) / n; unsigned scratch = 0u; "
            "if (m == 2u) { scratch = 1u; } else { scratch = 0u; } "
            "if (n == 2u) { if (m % n != 0u) { r = m / n + 1u; } "
            "else { r = m / n; } } else { r = r; } return r;"),
    }
    return dict(id="upstream-ceil-"+variant, word_bits=32,
                inputs={"m": M_AXIS, "n": N_AXIS}, original=source(OLD),
                candidate=source(bodies[variant]), reference=source(REFERENCE),
                repair_guard="m > (4294967295u - (n - 1u))")


def observation(variant, m, n):
    old = ((m+n-1) % (2**32)) // n
    ceiling = (m+n-1) // n
    if variant == "original":
        return True, old, []
    if variant == "definedness" and n == 1:
        return False, None, []
    if variant == "trace-overfit":
        trace = [[0, int(m == 2)], [1, int(n == 2)]]
        if n == 2:
            trace.append([2, int(m % n != 0)])
        return True, ceiling if n == 2 else old, trace
    trace = [[0, int(m % n != 0)]]
    if variant == "regression":
        trace.append([1, int(m == 0)])
    return True, 1 if variant == "regression" and m == 0 else ceiling, trace


def oracle(variant):
    violations = [[], [], []]
    repair_points = 0
    for m, n in itertools.product(M_AXIS, N_AXIS):
        defined, value, trace = observation(variant, m, n)
        selected = m+n-1 > H
        repair_points += int(selected)
        old, target = ((m+n-1) % (2**32)) // n, (m+n-1)//n
        truth = (defined, not selected or (defined and value == target),
                 selected or (defined and value == old))
        for j, holds in enumerate(truth):
            if not holds:
                violations[j].append((trace, [m, n]))
    for name, rows in zip(("defined", "repair", "preserve"), violations):
        if rows:
            trace, point = min(rows)
            return dict(status="REFUTED", witness=dict(obligation=name, trace=trace, input=point))
    return dict(status="ACCEPT", witness=None)


def retrieve():
    provenance = json.loads((ROOT/"public-data/ceil-div-source.json").read_text(encoding="utf-8"))
    checked = []
    for role in ("before", "after"):
        item = provenance[role]
        url = ("https://raw.githubusercontent.com/ggml-org/llama.cpp/" +
               item["commit"] + "/" + provenance["path"])
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000 or hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("upstream byte identity differs: " + role)
        if item["line"] not in data.decode("utf-8").splitlines():
            raise ValueError("upstream macro line differs: " + role)
        checked.append(dict(role=role, url=url, bytes=len(data), sha256=item["sha256"],
                            macro_line_verified=True, executed=False))
    return checked


def run(out, verify_upstream=False):
    if out.exists():
        raise ValueError("output must be new")
    retrieval = retrieve() if verify_upstream else None
    out.mkdir(parents=True)
    rows = []
    for variant in VARIANTS:
        q = request(variant)
        expected = oracle(variant)
        packet = produce(q)
        full, direct = check(q, packet), evaluate_topological(q)
        for result in (full, direct):
            if {k: result[k] for k in ("status", "witness")} != expected:
                raise ValueError("status/witness disagreement: " + variant)
        if full["checked_cells"] != direct["checked_cells"]:
            raise ValueError("unequal obligations")
        session = Session(q)
        observations = []
        for m, n in itertools.product(M_AXIS, N_AXIS):
            actual = session.run("candidate", {"m": m, "n": n})
            got = (actual[0], actual[1], [list(e) for e in actual[2]])
            if got != observation(variant, m, n):
                raise ValueError("source/literal disagreement")
            observations.append(dict(input=[m,n], defined=got[0], value=got[1], trace=got[2]))
        negative = copy.deepcopy(packet)
        v = negative["nodes"][-1]["vector"][0]
        negative["nodes"][-1]["vector"][0] = not v if type(v) is bool else (v+1) & H
        negative["certificate_sha256"] = hashlib.sha256(canonical_bytes(
            {k:v for k,v in negative.items() if k != "certificate_sha256"})).hexdigest()
        try:
            check(q, negative)
        except Invalid:
            pass
        else:
            raise ValueError("rehashed intermediate corruption accepted")
        if expected["witness"]:
            compact = point_produce(q, expected["witness"])
            if point_check(q, compact)["witness"] != expected["witness"]:
                raise ValueError("compact disagreement")
            (out/(variant+"-compact.json")).write_text(json.dumps(compact,indent=2)+"\n",encoding="utf-8")
        (out/(variant+"-request.json")).write_text(json.dumps(q,indent=2)+"\n",encoding="utf-8")
        (out/(variant+"-full.json")).write_text(json.dumps(packet,indent=2)+"\n",encoding="utf-8")
        rows.append(dict(variant=variant, **expected, full_cells=full["checked_cells"],
                         direct_cells=direct["checked_cells"], full_bytes=len(canonical_bytes(packet)),
                         rehashed_intermediate_corruption_rejected=True, observations=observations))
    # A nonleast witness is a legitimate compact refutation, not a least diagnostic.
    q = request("trace-overfit")
    nonleast = dict(obligation="repair", input=[2,H], trace=observation("trace-overfit",2,H)[2])
    point_check(q, point_produce(q, nonleast))
    if oracle("trace-overfit")["witness"]["input"] == nonleast["input"]:
        raise ValueError("trace-priority example failed")
    summary = dict(cases=rows, points_per_request=42, candidate_observations=210,
                   repair_points=sum(m+n-1>H for m,n in itertools.product(M_AXIS,N_AXIS)),
                   preserve_points=sum(m+n-1<=H for m,n in itertools.product(M_AXIS,N_AXIS)),
                   nonleast_compact_verified=nonleast, upstream_retrieval=retrieval,
                   upstream_execution=False, controls="Four variants except supplied are owned diagnostic controls, not upstream fixes.")
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="cases"}))
    print(json.dumps([{k:v for k,v in r.items() if k!="observations"} for r in rows]))
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--verify-upstream",action="store_true")
    a=p.parse_args()
    run(a.output,a.verify_upstream)


if __name__=="__main__":
    main()
