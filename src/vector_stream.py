"""Bounded framed-vector reception with last-use reclamation.

The receiver reconstructs its header and graph from authoritative source. It
checks one submitted node at a time, keeps diagnostic roots, and publishes no
verdict before the terminal integrity seal and exact end of input are checked.
The certificate-free baseline uses the same liveness schedule. Conversion of
an existing full JSON packet is a producer-side operation, not a memory claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import sys

import proof_dag_checker as core

KIND = 'finite-semantic-vector-stream'


def _line(record):
    return core.canonical_bytes(record) + b'\n'


def _read_line(stream, limit):
    raw = stream.readline(limit + 1)
    if type(raw) is not bytes or not raw or len(raw) > limit or not raw.endswith(b'\n'):
        raise core.Invalid('stream framing or line bound')
    return raw


def _record(raw):
    try:
        record = core.load_json_strict(raw.decode('utf-8'))
        if _line(record) != raw:
            raise core.Invalid('stream noncanonical record')
        return record
    except (UnicodeError, ValueError, RecursionError) as error:
        raise core.Invalid('stream invalid JSON record') from error


def _prepare(request):
    domains, names, points = core.validate_request(request)
    circuit, programs, guard, roots = core.build_expected(request)
    header = dict(kind=KIND, request_id=request['id'], word_bits=32,
                  input_order=names, domains=domains, points=points,
                  source_sha256={role:core.digest(request[role]) for role in core.ROLES+('repair_guard',)},
                  node_count=len(circuit.nodes),
                  role_roots={role:dict(output=programs[role].output,
                      defined=programs[role].defined,
                      trace_events=[dict(site=s,reachable=r,guard=g) for s,r,g in programs[role].events])
                      for role in core.ROLES},
                  guard_root=guard, obligation_roots=dict(zip(core.OBLIGATIONS,roots)))
    return header,names,points,circuit,programs,roots


def _evaluate(names,points,circuit,programs,roots,read_node=None,*,reclaim=True):
    future = [0] * len(circuit.nodes) if reclaim else []
    if reclaim:
        for key in circuit.nodes:
            if key[0] not in {'b','u','input'}:
                for child in key[1:]: future[child] += 1
    events = programs['candidate'].events
    retained = set(roots)
    for _site,reachable,guard in events: retained.update((reachable,guard))
    positions = {name:i for i,name in enumerate(names)}
    live = {} if reclaim else []
    peak = 0
    comparisons = 0
    for index,(key,sort) in enumerate(zip(circuit.nodes,circuit.sorts)):
        record = read_node(index,key,sort) if read_node else None
        if read_node is not None:
            descriptor = core._expected_record(index,key,sort)
            if type(record) is not dict or set(record) != set(descriptor)|{'vector'}:
                raise core.Invalid('stream node schema')
            if any(not core.exact_equal(record[k],v) for k,v in descriptor.items()):
                raise core.Invalid('stream node topology')
            if type(record['vector']) is not list or len(record['vector']) != len(points):
                raise core.Invalid('stream vector length')
        op = key[0]
        children = key[1:] if op not in {'b','u','input'} else ()
        child_vectors = tuple(live[c] for c in children)
        arity = len(child_vectors)
        vector = []
        for cell,point in enumerate(points):
            if op in {'b','u'}: value = key[1]
            elif op == 'input': value = point[positions[key[1]]]
            else:
                if arity==1: args=(child_vectors[0][cell],)
                elif arity==2: args=(child_vectors[0][cell],child_vectors[1][cell])
                else: args=(child_vectors[0][cell],child_vectors[1][cell],child_vectors[2][cell])
                value = core.local_value(op,args)
            if read_node is not None:
                supplied = record['vector'][cell]
                comparisons += 1
                if type(supplied) is not type(value) or supplied != value:
                    raise core.Invalid('stream vector type or value')
            vector.append(value)
        if reclaim:live[index] = vector
        else:live.append(vector)
        # Counts include the new vector before its consumed children are freed.
        peak = max(peak,len(live))
        if reclaim:
            for child in children:
                future[child] -= 1
                if future[child] == 0 and child not in retained: del live[child]
            if future[index] == 0 and index not in retained: del live[index]
        del record,vector,child_vectors
    result = core.classify_vectors(points,roots,events,live)
    result.update(checked_nodes=len(circuit.nodes),checked_cells=len(circuit.nodes)*len(points),
                  vector_comparisons=comparisons,peak_live_vectors=peak,
                  peak_live_cells=peak*len(points),retained_diagnostic_vectors=len(retained))
    return result


def check_stream(request, stream):
    header,names,points,circuit,programs,roots = _prepare(request)
    expected = _line(header)
    raw = _read_line(stream,len(expected))
    if raw != expected:
        raise core.Invalid('stream authoritative header binding')
    seal = hashlib.sha256(raw)
    del raw,expected,header
    def read_node(index,key,sort):
        descriptor = core._expected_record(index,key,sort)
        # A canonical uint32 cell takes at most ten digits plus one comma;
        # Boolean cells are shorter. The descriptor is receiver-reconstructed.
        bound = len(core.canonical_bytes(descriptor)) + 16 + 11*len(points)
        raw = _read_line(stream,bound)
        record = _record(raw)
        seal.update(raw)
        return record
    result = _evaluate(names,points,circuit,programs,roots,read_node)
    terminal = _record(_read_line(stream,256))
    if (type(terminal) is not dict or set(terminal) != {'kind','seal'}
            or terminal['kind'] != 'end' or type(terminal['seal']) is not str
            or not re.fullmatch('[0-9a-f]{64}',terminal['seal'])
            or terminal['seal'] != seal.hexdigest()):
        raise core.Invalid('stream terminal integrity')
    if stream.read(1) != b'':
        raise core.Invalid('stream trailing data')
    result['mode'] = 'framed-vector-stream'
    return result


def direct_liveness(request):
    _domains,names,points = core.validate_request(request)
    circuit,programs,_guard,roots = core.build_expected(request)
    result = _evaluate(names,points,circuit,programs,roots)
    result['mode'] = 'direct-liveness'
    return result


def direct_full(request):
    """Same prepared local-rule kernel, but retain all vectors in a list."""
    _domains,names,points = core.validate_request(request)
    circuit,programs,_guard,roots = core.build_expected(request)
    result = _evaluate(names,points,circuit,programs,roots,reclaim=False)
    result['mode'] = 'direct-full'
    return result


def write_packet(packet, stream):
    """Convert a producer's full packet; the conversion does not validate it."""
    fields = {'kind','request_id','word_bits','input_order','domains','points','source_sha256',
              'nodes','role_roots','guard_root','obligation_roots','certificate_sha256'}
    if type(packet) is not dict or set(packet) != fields or packet['kind'] != core.SCHEMA or type(packet['nodes']) is not list:
        raise core.Invalid('stream conversion schema')
    header = {k:v for k,v in packet.items() if k not in {'nodes','certificate_sha256'}}
    header.update(kind=KIND,node_count=len(packet['nodes']))
    seal = hashlib.sha256()
    for record in itertools.chain((header,),packet['nodes']):
        raw = _line(record)
        stream.write(raw)
        seal.update(raw)
    stream.write(_line(dict(kind='end',seal=seal.hexdigest())))


def encode_packet(packet):
    """Convenience conversion for tests; not the file-based memory benchmark."""
    output=io.BytesIO();write_packet(packet,output);return output.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    check=sub.add_parser('check');check.add_argument('request',type=Path);check.add_argument('certificate',type=Path)
    direct=sub.add_parser('direct');direct.add_argument('request',type=Path)
    encode=sub.add_parser('encode');encode.add_argument('certificate',type=Path);encode.add_argument('output',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='encode':
            packet=core.load_json_strict(args.certificate.read_text(encoding='utf-8'))
            with args.output.open('xb') as output:write_packet(packet,output)
            return 0
        request=core.load_json_strict(args.request.read_text(encoding='utf-8'))
        if args.command=='direct': result=direct_liveness(request)
        else:
            with args.certificate.open('rb') as source:result=check_stream(request,source)
        print(json.dumps(result,ensure_ascii=True,sort_keys=True));return 0
    except (core.Invalid,core.Unsupported,ValueError,OSError) as error:
        print(json.dumps(dict(status='INVALID',reason=str(error)),ensure_ascii=True,sort_keys=True));return 2


if __name__=='__main__':sys.exit(main())
