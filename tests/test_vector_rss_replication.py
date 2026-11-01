"""Retained-evidence negative controls; no measurement subprocesses."""
import copy,json
from pathlib import Path
import sys,tempfile,unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parent))
import verify_vector_rss_replication as verifier

class ReplicationAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=verifier.ROOT/'results/vector-rss'
        cls.payload=verifier.read_archive(directory/'replication.zip')
        cls.prior=verifier.read_archive(directory/'observations.zip')['protocol.json']
        cls.summary=json.loads((directory/'replication-summary.json').read_text(encoding='utf-8'))

    def test_all_600_rows_and_50_pairs_are_rederived(self):
        result=verifier.verify(self.payload['protocol.json'],self.payload['results.json'],self.summary,self.prior)
        self.assertEqual(result['measurements'],600)

    def test_missing_duplicate_outcome_cost_and_resource_changes_are_refused(self):
        for mutation in ['missing','duplicate','outcome','work','rss','cpu','paired','status','cohort']:
            with self.subTest(mutation=mutation):
                protocol=copy.deepcopy(self.payload['protocol.json']);result=copy.deepcopy(self.payload['results.json']);summary=copy.deepcopy(self.summary)
                if mutation=='missing':result['raw'].pop()
                elif mutation=='duplicate':result['raw'][1]=copy.deepcopy(result['raw'][0])
                elif mutation=='outcome':result['raw'][0]['outcome']['status']='incorrect'
                elif mutation=='work':result['raw'][0]['checked_cells']+=1
                elif mutation=='rss':result['raw'][0]['peak_rss_kib']=0
                elif mutation=='cpu':result['resources']['child_cpu_seconds']=181
                elif mutation=='paired':result['paired'][0]['stream_to_full']+=0.1
                elif mutation=='status':summary['prior_activity_status']='COMPLETE'
                elif mutation=='cohort':protocol['cases'][0]['id']='replacement'
                with self.assertRaises(ValueError):verifier.verify(protocol,result,summary,self.prior)

    @unittest.skipUnless(sys.platform=='linux','measurement driver requires Linux')
    def test_reentry_sentinel_refuses_a_second_attempt(self):
        import vector_rss_replication as driver
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            (out/'protocol.json').write_text(json.dumps(self.payload['protocol.json']),encoding='utf-8')
            (out/'attempt-started.json').write_text('{}',encoding='utf-8')
            with mock.patch.object(driver.original,'run') as measured:
                with self.assertRaises(FileExistsError):driver.run(out)
                measured.assert_not_called()

if __name__=='__main__':unittest.main()
