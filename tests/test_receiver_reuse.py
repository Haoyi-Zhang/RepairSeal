"""Owned finite reuse tests; no third-party code or native execution."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import proof_dag_checker as core
from proof_dag_producer import produce
from reusing_checker import ReceiverCache, check_reusing, direct_reusing


def request(candidate='return x + 1u;', axes=None):
    axes = {'x':[0,1,31,4294967295]} if axes is None else axes
    signature = ', '.join('unsigned '+n for n in axes)
    def source(body): return 'unsigned f('+signature+') { '+body+' }'
    return {'id':'reuse','word_bits':32,'inputs':copy.deepcopy(axes),
            'original':source('return x;'),'candidate':source(candidate),
            'reference':source('return x + 1u;'),'repair_guard':'x != 0u'}


def rebind(packet):
    packet.pop('certificate_sha256',None)
    packet['certificate_sha256']=hashlib.sha256(core.canonical_bytes(packet)).hexdigest()


class ReuseTests(unittest.TestCase):
    def test_cold_warm_and_same_information_direct(self):
        req=request(); cert=produce(req)
        a,b=ReceiverCache(),ReceiverCache()
        for _ in range(2):
            full=check_reusing(req,cert,a); direct=direct_reusing(req,b)
            self.assertEqual((full['status'],full['witness']),(core.check(req,cert)['status'],core.check(req,cert)['witness']))
            self.assertEqual(full['recomputed_cells'],direct['recomputed_cells'])
            self.assertEqual(full['vector_comparisons'],full['checked_cells'])
        self.assertEqual(full['recomputed_cells'],0)
        self.assertGreater(full['reused_cells'],0)

    def test_changed_candidate_recomputes_new_terms(self):
        cache=ReceiverCache()
        old=request(); check_reusing(old,produce(old),cache)
        req=request('return x + 2u;')
        result=check_reusing(req,produce(req),cache)
        self.assertEqual((result['status'],result['witness']),(core.evaluate_topological(req)['status'],core.evaluate_topological(req)['witness']))
        self.assertGreater(result['reused_cells'],0)
        self.assertGreater(result['recomputed_cells'],0)

    def test_named_inputs_not_point_offsets(self):
        cache=ReceiverCache()
        a=request(axes={'x':[0,1],'y':[2,3]})
        b=request(axes={'y':[2,3],'x':[0,1]})
        check_reusing(a,produce(a),cache)
        result=check_reusing(b,produce(b),cache)
        cold=core.check(b,produce(b))
        self.assertEqual((result['status'],result['witness']),(cold['status'],cold['witness']))

    def test_new_domain_values_not_reused(self):
        cache=ReceiverCache()
        a=request(axes={'x':[0,1]}); check_reusing(a,produce(a),cache)
        b=request(axes={'x':[0,1,2]}); result=check_reusing(b,produce(b),cache)
        self.assertGreater(result['recomputed_cells'],0)
        self.assertGreater(result['reused_cells'],0)

    def test_failed_packet_commits_no_cells(self):
        req=request(); cert=produce(req); cert['nodes'][-1]['vector'][-1]=not cert['nodes'][-1]['vector'][-1]
        rebind(cert); cache=ReceiverCache()
        with self.assertRaises(core.Invalid): check_reusing(req,cert,cache)
        self.assertEqual(cache._cells,{})
        self.assertEqual(check_reusing(req,produce(req),cache)['reused_cells'],0)

    def test_header_and_warm_value_tampering_rejected(self):
        req=request(); cert=produce(req); cache=ReceiverCache()
        check_reusing(req,cert,cache)
        for absent in (None,False,[],0):
            with self.subTest(absent=absent),self.assertRaises(core.Invalid):
                check_reusing(req,absent,cache)
        for change in ('source','root','point','type','value'):
            packet=copy.deepcopy(cert)
            if change=='source': packet['source_sha256']['candidate']='0'*64
            elif change=='root': packet['guard_root']=True
            elif change=='point': packet['points'][0][0]=True
            elif change=='type': packet['nodes'][0]['vector'][0]=int(packet['nodes'][0]['vector'][0])
            else: packet['nodes'][-1]['vector'][0]=not packet['nodes'][-1]['vector'][0]
            rebind(packet)
            with self.subTest(change=change),self.assertRaises(core.Invalid):
                check_reusing(req,packet,cache)

    def test_zero_and_bounded_capacity(self):
        req=request(); cert=produce(req)
        for capacity in (0,1,10):
            cache=ReceiverCache(capacity)
            for _ in range(2):
                result=check_reusing(req,cert,cache)
                self.assertLessEqual(result['cache_entries'],capacity)
        for capacity in (True,-1,65537):
            with self.assertRaises(core.Invalid): ReceiverCache(capacity)

    def test_undefined_candidate_and_unchanged_inputs(self):
        req=request('return 1u / x;'); cert=produce(req)
        before=copy.deepcopy((req,cert)); cache=ReceiverCache()
        result=check_reusing(req,cert,cache)
        self.assertEqual(result['witness']['obligation'],'defined')
        self.assertEqual(before,(req,cert))


if __name__=='__main__': unittest.main()
