"""Read-only artifact admission regressions; never run the study or compilers.

Paper parity remains in paper/test_descriptor_report_contract.py.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_descriptor_consumer as consumer
from descriptor_consumer_study import ceiling
from upstream_ceil_case import M_AXIS, N_AXIS

RESULTS = consumer.ROOT / 'results/descriptor-consumer'
READ_TEXT = Path.read_text
READ_BYTES = Path.read_bytes


class DescriptorReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {name: json.loads(READ_TEXT(RESULTS / name, encoding='utf-8')) for name in
                       ('summary.json', 'observations.json', 'excluded.json', 'native-observations.json')}

    def report(self, changes=None, stale=False):
        changes = changes or {}

        def read(path, *args, **kwargs):
            if path.parent == RESULTS and path.name in changes:
                return json.dumps(changes[path.name])
            return READ_TEXT(path, *args, **kwargs)

        def read_bytes(path, *args, **kwargs):
            if stale and path == consumer.ROOT / 'src/macro_bridge.py':
                return b'owned hypothetical changed source\n'
            return READ_BYTES(path, *args, **kwargs)

        with patch.object(Path, 'read_text', read), patch.object(Path, 'read_bytes', read_bytes):
            return consumer.report(RESULTS)

    def test_complete_current_records_and_derived_partition(self):
        text = self.report()
        _, budget = consumer.consumer_contract()
        domain = {(m, n) for m in M_AXIS for n in N_AXIS}
        excluded = {key for key in domain if ceiling(*key) > budget}
        rows = self.records['observations.json']
        self.assertEqual(len(domain), 42)
        self.assertEqual(len(excluded), 10)
        self.assertIn('\\DescriptorAdmitted}{' + str(len(domain - excluded)) + '}', text)
        self.assertIn('\\DescriptorExcluded}{' + str(len(excluded)) + '}', text)
        self.assertIn('\\DescriptorOldFailures}{' + str(sum(not r['old']['dispatches_fit'] for r in rows)) + '}', text)
        self.assertIn('\\DescriptorNativeRows}{' + str(len(self.records['native-observations.json'])) + '}', text)

    def test_binding_inventory_is_exact_and_checked_before_source_reads(self):
        good = self.records['summary.json']['source_bindings']
        cases = [{}, [], None, dict(good, extra='0' * 64)]
        cases.extend({k: v for k, v in good.items() if k != missing} for missing in good)
        for bindings in cases:
            summary = copy.deepcopy(self.records['summary.json'])
            summary['source_bindings'] = bindings
            with self.subTest(bindings=bindings), \
                    patch.object(Path, 'read_bytes', side_effect=AssertionError('read before inventory validation')), \
                    self.assertRaisesRegex(ValueError, 'binding inventory'):
                consumer.validate_source_bindings(summary)

    def test_valid_row_permutations_are_verified_not_compared_to_a_fixed_report(self):
        changes = {name: list(reversed(self.records[name])) for name in
                   ('observations.json', 'excluded.json', 'native-observations.json')}
        summary = copy.deepcopy(self.records['summary.json'])
        summary['source_bindings'] = dict(reversed(list(summary['source_bindings'].items())))
        changes['summary.json'] = summary
        self.assertEqual(self.report(changes), self.report())

    def test_binding_digest_format_before_hashes(self):
        for digest in (None, True, 0, '', '0' * 63, '0' * 65, 'G' * 64, 'A' * 64, '0' * 64 + '\n'):
            summary = copy.deepcopy(self.records['summary.json'])
            summary['source_bindings']['src/macro_bridge.py'] = digest
            with self.subTest(digest=digest), \
                    patch.object(Path, 'read_bytes', side_effect=AssertionError('read before digest validation')), \
                    self.assertRaisesRegex(ValueError, 'digest format'):
                consumer.validate_source_bindings(summary)

    def test_stale_source_and_omitted_bindings_cannot_issue_report(self):
        with self.assertRaisesRegex(ValueError, 'stale consumer source'):
            self.report(stale=True)
        for key in (None, *consumer.REQUIRED_SOURCE_BINDINGS):
            summary = copy.deepcopy(self.records['summary.json'])
            if key is None:
                summary['source_bindings'] = {}
            else:
                del summary['source_bindings'][key]
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'binding inventory'):
                self.report({'summary.json': summary}, stale=True)

    def test_duplicate_json_fields_cannot_hide_a_binding_map(self):
        with patch.object(Path, 'read_text', return_value='{"source_bindings":{},"source_bindings":{}}'), \
                self.assertRaisesRegex(ValueError, 'duplicate consumer JSON key'):
            consumer.report(RESULTS)

    def test_empty_or_short_exclusions_with_self_adjusted_summary_rejected(self):
        for excluded in ([], self.records['excluded.json'][:-1]):
            summary = copy.deepcopy(self.records['summary.json'])
            summary.update(input_pairs=len(self.records['observations.json']) + len(excluded), excluded_pairs=len(excluded))
            with self.subTest(count=len(excluded)), self.assertRaisesRegex(ValueError, 'partition coverage'):
                self.report({'summary.json': summary, 'excluded.json': excluded})

    def test_duplicate_excluded_identity_not_just_list_length(self):
        excluded = self.records['excluded.json']
        for bad in ([excluded[0]] * len(excluded), excluded[:-1] + [excluded[0]]):
            with self.assertRaisesRegex(ValueError, 'excluded input coverage'):
                self.report({'excluded.json': bad})

    def test_excluded_schema_types_domain_budget_and_reason(self):
        replacements = [dict(batch=0), dict(batch=True), dict(batch=4294967293),
                        dict(limit=0), dict(limit=True), dict(required_dispatches=True),
                        dict(required_dispatches=65), dict(reason=''), dict(reason='other reason'),
                        dict(extra='not allowed')]
        for replacement in replacements:
            bad = copy.deepcopy(self.records['excluded.json'])
            bad[0].update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                self.report({'excluded.json': bad})
        for bad in (None, {}, [None], [{k: v for k, v in self.records['excluded.json'][0].items() if k != 'reason'}]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.report({'excluded.json': bad})

    def test_admitted_and_excluded_are_disjoint_not_relabelable(self):
        bad = copy.deepcopy(self.records['excluded.json'])
        admitted = self.records['observations.json'][0]
        bad[0].update({key: admitted[key] for key in ('batch', 'limit', 'required_dispatches')})
        with self.assertRaises(ValueError):
            self.report({'excluded.json': bad})
        rows = copy.deepcopy(self.records['observations.json'])
        rows.pop()
        summary = copy.deepcopy(self.records['summary.json'])
        summary['native_loop_admitted_pairs'] = len(rows)
        with self.assertRaises(ValueError):
            self.report({'summary.json': summary, 'observations.json': rows})

    def test_evidence_flags_require_literal_boolean_true(self):
        for field in ('native_executed', 'fresh_whole_source_verified'):
            for value in ('false', 'true', 1, 0, False, None, [], {}):
                summary = copy.deepcopy(self.records['summary.json'])
                target = summary if field == 'native_executed' else summary['source_context']
                target[field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'recorded native run'):
                    self.report({'summary.json': summary})
            summary = copy.deepcopy(self.records['summary.json'])
            del (summary if field == 'native_executed' else summary['source_context'])[field]
            with self.assertRaises(ValueError):
                self.report({'summary.json': summary})

    def test_summary_counts_and_accounting_contract_are_not_authoritative(self):
        original = self.records['summary.json']
        for field in ('input_pairs', 'native_loop_admitted_pairs', 'excluded_pairs', 'old_under_reserved_pairs',
                      'old_consumer_failed_pairs', 'new_consumer_success_pairs', 'native_role_rows',
                      'maximum_dispatches_per_pair'):
            for value in (str(original[field]), True, original[field] + 1):
                summary = copy.deepcopy(original)
                summary[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.report({'summary.json': summary})
        summary = copy.deepcopy(original)
        summary['initial_state']['allocated'] += 1
        with self.assertRaises(ValueError):
            self.report({'summary.json': summary})

    def test_evidence_domain_flags_have_exact_types(self):
        for field, values in (('upstream_application_or_gpu_executed', ('false', 0, True, None)),
                              ('new_independent_programs', ('0', False, 1, None))):
            for value in values:
                summary = copy.deepcopy(self.records['summary.json'])
                summary[field] = value
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'domain changed'):
                    self.report({'summary.json': summary})

    def test_native_inventory_values_and_strict_scalar_types_remain_checked(self):
        for kind in ('value', 'bool', 'role', 'compiler', 'input', 'duplicate', 'missing'):
            native = copy.deepcopy(self.records['native-observations.json'])
            if kind == 'value': native[0]['values'][1] += 1
            elif kind == 'bool': native[0]['values'][0] = False
            elif kind == 'role': native[0]['role'] = 'new'
            elif kind == 'compiler': native[0]['compiler'] = 'other'
            elif kind == 'input': native[0]['batch'] = 999
            elif kind == 'duplicate': native[-1] = native[0]
            elif kind == 'missing': native.pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.report({'native-observations.json': native})


if __name__ == '__main__':
    unittest.main()
