import copy
import itertools
from pathlib import Path
import tempfile
import unittest
from upstream_ceil_case import (
    H, M_AXIS, N_AXIS, request, oracle, observation, run,
    produce, check, point_produce, point_check, Invalid,
)


class UpstreamCeilTests(unittest.TestCase):
    def test_actual_patch_and_nonempty_policy_partitions(self):
        self.assertEqual(oracle("supplied"), {"status":"ACCEPT","witness":None})
        repairs=sum(m+n-1>H for m,n in itertools.product(M_AXIS,N_AXIS))
        self.assertEqual((repairs,len(M_AXIS)*len(N_AXIS)-repairs),(12,30))

    def test_all_three_obligations_are_distinguished(self):
        self.assertEqual(oracle("original")["witness"]["obligation"],"repair")
        self.assertEqual(oracle("regression")["witness"]["obligation"],"preserve")
        self.assertEqual(oracle("definedness")["witness"]["obligation"],"defined")

    def test_canonical_trace_precedes_numeric_input(self):
        self.assertEqual(oracle("trace-overfit")["witness"]["input"],[31,H])
        q=request("trace-overfit")
        w=dict(obligation="repair",input=[2,H],trace=observation("trace-overfit",2,H)[2])
        self.assertEqual(point_check(q,point_produce(q,w))["witness"],w)
        wrong=copy.deepcopy(w)
        wrong["trace"][0][1]=0
        with self.assertRaisesRegex(Invalid,"trace mismatch"):
            point_check(q,point_produce(q,wrong))

    def test_stale_candidate_cannot_reuse_an_acceptance_packet(self):
        q=request("supplied")
        packet=produce(q)
        other=copy.deepcopy(q)
        other["candidate"]=request("regression")["candidate"]
        with self.assertRaisesRegex(Invalid,"source binding"):
            check(other,packet)

    def test_reproducible_complete_model_case(self):
        with tempfile.TemporaryDirectory() as td:
            summary=run(Path(td)/"new")
            self.assertEqual(len(summary["cases"]),5)
            self.assertEqual(summary["candidate_observations"],210)
            self.assertTrue(all(r["full_cells"]==r["direct_cells"] for r in summary["cases"]))


if __name__=="__main__":
    unittest.main()
