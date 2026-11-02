"""Tiny owned malformed inputs and read-only retained-data acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import proof_dag_checker as full
import refutation_witness_checker as compact
from proof_dag_producer import produce
from refutation_witness_producer import produce as compact_produce
from reusing_checker import ReceiverCache,check_reusing as cached_check
from report_descriptor_consumer import report,validate_native_rows
from retained_rss_sources import EXPECTED,verify_sources

def request(refuted=False):
    source='unsigned f(unsigned x) { return x; }'
    return dict(id='owned-caf\u00e9',word_bits=32,inputs={'x':[1]},original=source,
        candidate='unsigned f(unsigned x) { return x + 1u; }' if refuted else source,
        reference=source,repair_guard='x == 1u')

class ReceivingContracts(unittest.TestCase):
    def invoke(self,script,req,cert,optimized=False):
        with tempfile.TemporaryDirectory() as tmp:
            rp,cp=Path(tmp)/'request.json',Path(tmp)/'certificate.json'
            for path,value in ((rp,req),(cp,cert)):
                path.write_bytes(value if type(value) is bytes else json.dumps(value).encode('utf-8'))
            command=[sys.executable,'-X','utf8']+(['-O'] if optimized else [])+['-B',str(ROOT/'src'/script),str(rp),str(cp)]
            result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertNotIn('Traceback',result.stderr)
            return result.returncode,json.loads(result.stdout)

    def test_cli_invalid_is_json_and_nonzero_under_both_modes(self):
        for optimized in (False,True):
            for script in ('proof_dag_checker.py','refutation_witness_checker.py'):
                for req,cert in ((request(),{}),(request(),b'{'),(request(),b'\xff'),(b'\xff',{})):
                    with self.subTest(optimized=optimized,script=script,cert=cert):
                        code,result=self.invoke(script,req,cert,optimized)
                        self.assertNotEqual(code,0);self.assertEqual(result['status'],'INVALID')

    def test_valid_accept_and_refutation_remain_successful_validation(self):
        for optimized in (False,True):
            req=request();code,result=self.invoke('proof_dag_checker.py',req,produce(req),optimized)
            self.assertEqual((code,result['status']),(0,'ACCEPT'))
            req=request(True)
            for script,packet in (('proof_dag_checker.py',produce(req)),
                ('refutation_witness_checker.py',compact_produce(req,dict(obligation='repair',input=[1],trace=[])))):
                code,result=self.invoke(script,req,packet,optimized)
                self.assertEqual((code,result['status']),(0,'REFUTED'))

    def test_lone_surrogates_reject_without_cached_cells(self):
        good=request(True);packet=produce(good)
        compact_packet=compact_produce(good,dict(obligation='repair',input=[1],trace=[]))
        for field in ('original','candidate','reference','repair_guard'):
            bad=dict(good,**{field:'\ud800'})
            for checker,cert in ((full.check,packet),(compact.check,compact_packet)):
                with self.subTest(field=field),self.assertRaises((full.Invalid,full.Unsupported)):
                    checker(bad,cert)
            cache=ReceiverCache()
            with self.assertRaises((full.Invalid,full.Unsupported)):cached_check(bad,packet,cache)
            self.assertFalse(cache._cells)
            for script,cert in (('proof_dag_checker.py',packet),('refutation_witness_checker.py',compact_packet)):
                code,result=self.invoke(script,bad,cert)
                self.assertNotEqual(code,0);self.assertEqual(result['status'],'INVALID')

    def test_archive_population_contract_survives_optimization(self):
        lines=(ROOT/'public-data/codeflaws-first-300.tsv').read_text(encoding='utf-8').splitlines()
        duplicate=list(lines);duplicate[-1]=duplicate[0]
        wrong=list(lines);wrong[0]=wrong[0].replace('\tDCCR\t','\tOTHER\t')
        cases=[[],lines[:1],lines[:-1],lines+lines[:1],duplicate,wrong,['bad']+lines[1:]]
        with tempfile.TemporaryDirectory() as tmp:
            for optimized in (False,True):
                for i,rows in enumerate(cases+[lines]):
                    inp=Path(tmp)/f'in-{optimized}-{i}.tsv';out=inp.with_suffix('.json')
                    inp.write_text('\n'.join(rows)+'\n' if rows else '',encoding='utf-8')
                    command=[sys.executable,'-X','utf8']+(['-O'] if optimized else [])+['-B',str(ROOT/'tests/public_archive_audit.py'),'--input',str(inp),'--output',str(out)]
                    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30)
                    if i==len(cases):
                        self.assertEqual(result.returncode,0,result.stderr)
                        data=json.loads(out.read_text());self.assertEqual(data['summary']['record_count'],len(data['records']))
                        self.assertEqual(data['summary']['unique_task_ids'],300)
                    else:
                        self.assertNotEqual(result.returncode,0);self.assertFalse(out.exists())

    def test_retained_native_values_and_exact_coverage(self):
        results=ROOT/'results/descriptor-consumer'
        rows=json.loads((results/'observations.json').read_text())
        native=json.loads((results/'native-observations.json').read_text())
        validate_native_rows(rows,native)
        mutations=[]
        for change in ('value','bool','role','compiler','input','duplicate','missing'):
            bad=copy.deepcopy(native)
            if change=='value':bad[0]['values'][1]+=1
            elif change=='bool':bad[0]['values'][0]=False
            elif change=='role':bad[0]['role']='new'
            elif change=='compiler':bad[0]['compiler']='other'
            elif change=='input':bad[0]['batch']=999
            elif change=='duplicate':bad[-1]=bad[0]
            elif change=='missing':bad.pop()
            with self.subTest(change=change),self.assertRaises(ValueError):validate_native_rows(rows,bad)
            original=Path.read_text
            with patch.object(Path,'read_text',lambda p,*a,**kw:json.dumps(bad) if p==results/'native-observations.json' else original(p,*a,**kw)),self.assertRaises(ValueError):
                report(results)
        self.assertIn('\\DescriptorNativeRows}{128}',report(results))

    def test_recorded_rss_source_inventory_and_exact_preimage(self):
        changed=verify_sources(dict(EXPECTED));self.assertIn('src/proof_dag_checker.py',changed)
        for wrong in ({},{k:v for k,v in EXPECTED.items() if k!='src/proof_dag_checker.py'},dict(EXPECTED,extra='0'*64)):
            with self.assertRaises(ValueError):verify_sources(wrong)
        original=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:b'wrong' if 'source-preimage' in p.parts else original(p)),self.assertRaises(ValueError):
            verify_sources(dict(EXPECTED))

if __name__=='__main__':unittest.main()
