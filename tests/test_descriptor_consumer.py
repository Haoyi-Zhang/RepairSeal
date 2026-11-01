"""The local consumer must preserve its stated assumptions and accounting."""
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from descriptor_consumer_study import U,accounting,ceiling,run,verify_context

STATE=dict(requested=4,allocated=4,consumed=4)

class DescriptorConsumerTests(unittest.TestCase):
    def test_report_aligned_balance_and_actual_macro_values(self):
        old=accounting(2,U,0,STATE);new=accounting(2,U,1,STATE)
        self.assertFalse(old['dispatches_fit'])
        self.assertEqual((old['requested'],old['allocated'],old['consumed']),(4,4,4))
        self.assertEqual(old['first_unreserved_dispatch'],0)
        self.assertTrue(new['dispatches_fit'])
        self.assertEqual((new['requested'],new['allocated'],new['consumed']),(5,6,5))

    def test_zero_batch_and_multidispatch(self):
        self.assertEqual(accounting(0,1,0,STATE)['completed_dispatches'],0)
        result=accounting(7,3,3,STATE)
        self.assertEqual((result['completed_dispatches'],result['final_base']),(3,7))
        self.assertTrue(result['dispatches_fit'])

    def test_existing_slack_can_mask_underreservation(self):
        # The old arithmetic is wrong, but a pool with spare entries need not fail.
        result=accounting(2,U,0,dict(requested=4,allocated=8,consumed=4))
        self.assertTrue(result['dispatches_fit'])
        self.assertFalse(result['requested_increment_covers_loop'])
        self.assertEqual(result['completed_dispatches'],1)

    def test_invalid_types_zero_limit_and_budget_fail_closed(self):
        for batch,limit in [(True,1),(1,True),(-1,1),(U+1,1),(1,0),(1,U+1)]:
            with self.subTest(batch=batch,limit=limit),self.assertRaises(ValueError):ceiling(batch,limit)
        with self.assertRaises(ValueError):accounting(U,1,U,STATE)
        with self.assertRaises(ValueError):accounting(1,1,1,STATE,65)
        with self.assertRaises(ValueError):accounting(1,1,True,STATE)

    def test_bad_prior_balance_and_wrap_are_not_admitted(self):
        for initial in [dict(requested=2,allocated=4,consumed=3),dict(requested=5,allocated=4,consumed=4),
                        dict(requested=U,allocated=U,consumed=U),dict(requested=4,allocated=4,consumed=True)]:
            with self.subTest(initial=initial),self.assertRaises(ValueError):accounting(1,1,1,initial)

    def test_source_identity_must_be_explicit_and_complete(self):
        self.assertFalse(verify_context(None,None)['fresh_whole_source_verified'])
        with self.assertRaises(ValueError):verify_context(Path(__file__),None)
        with self.assertRaises(ValueError):verify_context(Path(__file__),Path(__file__))

    def test_frozen_domain_and_native_exclusions_are_not_successes(self):
        with tempfile.TemporaryDirectory() as temporary:
            result=run(Path(temporary)/'result')
            self.assertEqual(result['input_pairs'],42)
            self.assertEqual(result['native_loop_admitted_pairs'],32)
            self.assertEqual(result['excluded_pairs'],10)
            self.assertEqual(result['old_under_reserved_pairs'],5)
            self.assertEqual(result['new_consumer_success_pairs'],32)
            self.assertEqual(result['full_certificate_status'],'ACCEPT')
            self.assertEqual(result['cells_per_full_or_direct_arm'],1680)
            self.assertFalse(result['native_executed'])
            self.assertEqual(result['native_role_rows'],0)
            self.assertFalse(result['upstream_application_or_gpu_executed'])
            with self.assertRaises(ValueError):run(Path(temporary)/'result')

if __name__=='__main__':unittest.main()
