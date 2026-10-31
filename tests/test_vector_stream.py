"""Framing, fail-closed reception, canonical diagnosis, and liveness parity."""
from pathlib import Path
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import proof_dag_checker as core
from proof_dag_producer import produce
import vector_stream as stream
from test_receiver_reuse import request


def reseal(lines):
    body=b''.join(lines[:-1])
    return body+stream._line(dict(kind='end',seal=hashlib.sha256(body).hexdigest()))


class BoundedInput(io.BytesIO):
    def __init__(self,data):
        super().__init__(data);self.bounds=[];self.eof_checked=False
    def readline(self,size=-1):
        if size<=0:raise AssertionError('unbounded stream read')
        self.bounds.append(size)
        return super().readline(size)
    def read(self,size=-1):
        if size!=1:raise AssertionError('unexpected stream read')
        self.eof_checked=True
        return super().read(size)


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.req=request();self.packet=produce(self.req)
        self.wire=stream.encode_packet(self.packet)

    def check(self,wire):return stream.check_stream(self.req,io.BytesIO(wire))

    def test_status_witness_and_same_information_work(self):
        for candidate in ('return x;', 'return x + 1u;',
                          'return 1u / x;',
                          'unsigned y = x + 1u; if (x > 31u) { y = x + 2u; } else { y = x + 1u; } return y;'):
            req=request(candidate);packet=produce(req)
            before=copy.deepcopy((req,packet))
            full=core.check(req,packet)
            bounded=BoundedInput(stream.encode_packet(packet))
            result=stream.check_stream(req,bounded)
            direct=stream.direct_liveness(req)
            prepared=stream.direct_full(req)
            for key in ('status','witness','checked_nodes','checked_cells'):
                self.assertEqual(result[key],full[key])
                self.assertEqual(result[key],direct[key])
                self.assertEqual(result[key],prepared[key])
            self.assertEqual(prepared['peak_live_vectors'],full['checked_nodes'])
            self.assertEqual(result['peak_live_cells'],direct['peak_live_cells'])
            self.assertEqual(result['vector_comparisons'],full['checked_cells'])
            self.assertEqual(direct['vector_comparisons'],0)
            self.assertTrue(bounded.eof_checked)
            self.assertEqual(before,(req,packet))

    def test_repeated_children_and_dead_nodes(self):
        circuit=SimpleNamespace(nodes=[('input','x'),('+',0,0),('u',1),
                                       ('==',1,2),('b',True)],
                                sorts=['u32','u32','u32','bool','bool'])
        result=stream._evaluate(['x'],[[0],[1]],circuit,
                                {'candidate':SimpleNamespace(events=())},(4,4,4))
        self.assertEqual(result['status'],'ACCEPT')
        self.assertEqual(result['peak_live_vectors'],3)
        self.assertEqual(result['retained_diagnostic_vectors'],1)

    def test_actual_nested_canonical_trace(self):
        from upstream_ceil_case import request as ceil_request
        req=ceil_request('trace-overfit');packet=produce(req)
        actual=stream.check_stream(req,io.BytesIO(stream.encode_packet(packet)))
        full=core.check(req,packet)
        self.assertEqual(actual['witness'],full['witness'])
        self.assertIsNotNone(actual['witness'])

    def test_null_node_is_not_direct_mode(self):
        lines=self.wire.splitlines(keepends=True);lines[1]=b'null\n'
        with self.assertRaises(core.Invalid):self.check(reseal(lines))

    def test_resealed_structural_and_semantic_mutations(self):
        original=self.wire.splitlines(keepends=True)
        for change in ('header','null','array','missing','extra','index','type','value','swap','length'):
            lines=original.copy()
            if change=='header':
                record=json.loads(lines[0]);record['request_id']='other';lines[0]=stream._line(record)
            elif change=='null':lines[1]=b'null\n'
            elif change=='array':lines[1]=b'[]\n'
            elif change=='swap':lines[1],lines[2]=lines[2],lines[1]
            else:
                record=json.loads(lines[1])
                if change=='missing':record.pop('vector')
                elif change=='extra':record['untrusted']=1
                elif change=='index':record['id']=999
                elif change=='length':record['vector'].pop()
                elif change=='type':
                    value=record['vector'][0]
                    record['vector'][0]=int(value) if type(value) is bool else bool(value)
                else:
                    value=record['vector'][0]
                    record['vector'][0]=not value if type(value) is bool else (value+1)&core.MASK
                lines[1]=stream._line(record)
            with self.subTest(change=change),self.assertRaises(core.Invalid):self.check(reseal(lines))

    def test_bad_json_and_noncanonical_records(self):
        original=self.wire.splitlines(keepends=True)
        for raw in (b'{"id":0,"id":0}\n', b'{"x":NaN}\n', b'\xff\n',
                    b' '+original[1],original[1].rstrip(b'\n')+b' \n'):
            lines=original.copy();lines[1]=raw
            with self.subTest(raw=raw[:30]),self.assertRaises(core.Invalid):self.check(reseal(lines))

    def test_terminal_and_exact_eof_required(self):
        lines=self.wire.splitlines(keepends=True)
        for raw in (self.wire[:-1], b''.join(lines[:-1]),self.wire+b' ',
                    self.wire+b'\n',self.wire+lines[-1],
                    b''.join(lines[:-1])+stream._line(dict(kind='end',seal='0'*64))):
            with self.subTest(size=len(raw)),self.assertRaises(core.Invalid):self.check(raw)
        for at in (0,1,len(lines[0])-1,len(self.wire)//2):
            with self.subTest(truncated=at),self.assertRaises(core.Invalid):self.check(self.wire[:at])

    def test_receiver_owned_limits_bound_untrusted_lines(self):
        header_size=len(self.wire.splitlines(keepends=True)[0])
        reader=BoundedInput(b'x'*1000000+b'\n')
        with self.assertRaises(core.Invalid):stream.check_stream(self.req,reader)
        self.assertEqual(reader.tell(),header_size+1)
        reader=BoundedInput(self.wire.splitlines(keepends=True)[0]+b'x'*1000000+b'\n')
        with self.assertRaises(core.Invalid):stream.check_stream(self.req,reader)
        self.assertLess(reader.tell(),header_size+10000)
        self.assertFalse(reader.eof_checked)

    def test_terminal_failure_exposes_no_partial_cli_verdict(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);req=root/'request.json';wire=root/'packet.rows'
            req.write_bytes(core.canonical_bytes(self.req))
            for optimized in (False,True):
                for valid in (False,True):
                    wire.write_bytes(self.wire if valid else self.wire[:-20])
                    cmd=[sys.executable,'-B']+(['-O'] if optimized else [])
                    cmd += [str(ROOT/'src/vector_stream.py'),'check',str(req),str(wire)]
                    process=subprocess.run(cmd,capture_output=True,text=True,check=False)
                    self.assertEqual(process.returncode,0 if valid else 2,process.stderr)
                    self.assertEqual(len(process.stdout.splitlines()),1)
                    result=json.loads(process.stdout)
                    self.assertEqual(result['status'],core.check(self.req,self.packet)['status'] if valid else 'INVALID')


if __name__=='__main__':unittest.main()
