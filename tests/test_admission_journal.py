import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from admission_journal import AdmissionJournal, identity
from proof_dag_producer import produce
from proof_dag_checker import Invalid

class AdmissionJournalTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.path=Path(self.directory.name)/'journal.sqlite'
        self.owner=AdmissionJournal(self.path)
        self.request=json.loads((ROOT/'results/upstream-ceil/supplied-request.json').read_text())
        self.packet=json.loads((ROOT/'results/upstream-ceil/supplied-full.json').read_text())
    def tearDown(self):self.owner.close();self.directory.cleanup()
    def test_producer_absent_reopen_and_idempotent_receipt(self):
        self.owner.register(self.request)
        a=self.owner.decide(self.request['id'],'accepted','proof',self.packet)
        self.assertTrue(a['approved']);self.owner.close();self.owner=AdmissionJournal(self.path)
        b=self.owner.decide(self.request['id'],'accepted','proof',self.packet)
        self.assertTrue(b['replayed_receipt']);self.assertTrue(self.owner.approved(self.request['id'],identity(self.request)))
        c=self.owner.decide(self.request['id'],'direct','direct')
        self.assertEqual((a['semantic_status'],a['witness'],a['checked_cells']),
                         (c['semantic_status'],c['witness'],c['checked_cells']))
    def test_stale_source_cannot_reuse_old_approval(self):
        registered=self.owner.register(self.request)
        self.owner.decide(self.request['id'],'old','proof',self.packet)
        changed=copy.deepcopy(self.request);changed['candidate']=changed['original']
        self.owner.register(changed,registered['request_identity'])
        self.assertFalse(self.owner.approved(self.request['id'],identity(self.request)))
        with self.assertRaises(ValueError):self.owner.decide(changed['id'],'old','proof',self.packet)
        with self.assertRaises(Invalid):self.owner.decide(changed['id'],'stale','proof',self.packet)
        no=self.owner.decide(changed['id'],'refuted','proof',produce(changed))
        self.assertFalse(no['approved']);self.assertFalse(self.owner.approved(changed['id'],identity(changed)))
    def test_invalid_packet_creates_no_receipt(self):
        self.owner.register(self.request)
        bad=copy.deepcopy(self.packet);bad['certificate_sha256']='0'*64
        with self.assertRaises(Invalid):self.owner.decide(self.request['id'],'bad','proof',bad)
        self.assertEqual(self.owner.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)
        self.assertFalse(self.owner.db.in_transaction)
    def test_source_replacement_needs_compare_and_swap_and_direct_has_no_packet(self):
        registered=self.owner.register(self.request)
        for expected in (None,'stale'):
            with self.assertRaises(ValueError):self.owner.register(self.request,expected)
        with self.assertRaises(ValueError):self.owner.decide(self.request['id'],'x','direct',self.packet)
        self.assertEqual(self.owner.db.execute('SELECT revision FROM requests').fetchone()[0],1)
    def test_unknown_request_and_token_collision_reject(self):
        with self.assertRaises(ValueError):self.owner.decide('unknown','x','direct')
        self.owner.register(self.request)
        self.owner.decide(self.request['id'],'x','direct')
        with self.assertRaises(ValueError):self.owner.decide(self.request['id'],'x','proof',self.packet)
    def test_exhaustion_never_records_approval(self):
        self.owner.register(self.request);self.owner.work_limit=0
        for mode,packet in [('proof',self.packet),('direct',None)]:
            with self.assertRaises(RuntimeError):self.owner.decide(self.request['id'],mode,mode,packet)
        self.assertEqual(self.owner.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0],0)
if __name__=='__main__':unittest.main()
