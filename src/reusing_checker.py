"""Receiver-owned, process-local semantic reuse across finite repair requests.

No cache import/export or producer-supplied cached facts are accepted. Structural
terms are rebuilt from receiver source, and points are keyed by named values.
Every submitted vector cell is still compared. A failed packet commits no facts.
The same cache and operator semantics are available to the direct baseline.
"""
from __future__ import annotations

import hashlib
import re

import proof_dag_checker as core


class ReceiverCache:
    def __init__(self, capacity=65536):
        if type(capacity) is not int or not 0 <= capacity <= 65536:
            raise core.Invalid('cache capacity')
        self.capacity = capacity
        self._terms = {}
        self._cells = {}

    def clear(self):
        self._terms.clear()
        self._cells.clear()

    def session(self, circuit, names):
        if len(self._terms)+len(circuit.nodes)>32768:
            self.clear()
        ids = []
        for key, sort in zip(circuit.nodes,circuit.sorts):
            op = key[0]
            term = (sort,op,key[1]) if op in {'b','u','input'} else (sort,op,tuple(ids[c] for c in key[1:]))
            if term not in self._terms:
                self._terms[term] = len(self._terms)
            ids.append(self._terms[term])
        return _Session(self, ids, names)


class _Session:
    def __init__(self, cache, ids, names):
        self.cache, self.ids, self.names = cache, ids, tuple(names)
        self.pending = {}
        self.reused, self.recomputed = 0, 0

    def value(self, index, point, calculate):
        key = (self.ids[index],tuple(sorted(zip(self.names,point))))
        if key in self.cache._cells:
            self.reused += 1
            return self.cache._cells[key]
        if key in self.pending:
            self.reused += 1
            return self.pending[key]
        self.recomputed += 1
        value = calculate()
        if len(self.cache._cells)+len(self.pending)<self.cache.capacity:
            self.pending[key] = value
        return value

    def commit(self):
        self.cache._cells.update(self.pending)


def _header(request, certificate):
    domains,names,points = core.validate_request(request)
    fields = {'kind','request_id','word_bits','input_order','domains','points','source_sha256',
              'nodes','role_roots','guard_root','obligation_roots','certificate_sha256'}
    if type(certificate) is not dict or set(certificate)!=fields or certificate['kind']!=core.SCHEMA:
        raise core.Invalid('certificate schema')
    supplied = certificate['certificate_sha256']
    if type(supplied) is not str or not re.fullmatch('[0-9a-f]{64}',supplied):
        raise core.Invalid('certificate digest format')
    body = dict(certificate)
    del body['certificate_sha256']
    if supplied!=hashlib.sha256(core.canonical_bytes(body)).hexdigest():
        raise core.Invalid('certificate digest')
    expected = [request['id'],32,names,domains,points]
    actual = [certificate[k] for k in ['request_id','word_bits','input_order','domains','points']]
    if not core.exact_equal(actual,expected):
        raise core.Invalid('request/domain binding')
    bindings = {role:core.digest(request[role]) for role in core.ROLES+('repair_guard',)}
    if not core.exact_equal(certificate['source_sha256'],bindings):
        raise core.Invalid('source binding')
    circuit,programs,guard,roots = core.build_expected(request)
    roles = {role:{'output':programs[role].output,'defined':programs[role].defined,
                   'trace_events':[{'site':s,'reachable':r,'guard':g} for s,r,g in programs[role].events]}
             for role in core.ROLES}
    if not core.exact_equal(certificate['role_roots'],roles) or not core.exact_equal(certificate['guard_root'],guard) or not core.exact_equal(certificate['obligation_roots'],dict(zip(core.OBLIGATIONS,roots))):
        raise core.Invalid('root binding')
    records = certificate['nodes']
    if type(records) is not list or len(records)!=len(circuit.nodes):
        raise core.Invalid('node count')
    # Check the entire structural envelope before opening the semantic session.
    for index,(record,key,sort) in enumerate(zip(records,circuit.nodes,circuit.sorts)):
        descriptor = core._expected_record(index,key,sort)
        if type(record) is not dict or set(record)!=set(descriptor)|{'vector'}:
            raise core.Invalid('node schema')
        if any(not core.exact_equal(record[k],v) for k,v in descriptor.items()):
            raise core.Invalid('node topology')
        if type(record['vector']) is not list or len(record['vector'])!=len(points):
            raise core.Invalid('node vector length')
    return names,points,circuit,programs,roots


def _evaluate(request,cache,certificate=None):
    if type(cache) is not ReceiverCache:
        raise core.Invalid('receiver cache type')
    if certificate is None:
        _,names,points = core.validate_request(request)
        circuit,programs,_,roots = core.build_expected(request)
    else:
        names,points,circuit,programs,roots = _header(request,certificate)
    session = cache.session(circuit,names)
    positions = {n:i for i,n in enumerate(names)}
    vectors = []
    comparisons = 0
    for index,key in enumerate(circuit.nodes):
        op = key[0]
        vector = []
        for cell,point in enumerate(points):
            def calculate():
                if op in {'b','u'}: return key[1]
                if op=='input': return point[positions[key[1]]]
                return core.local_value(op,tuple(vectors[c][cell] for c in key[1:]))
            value = session.value(index,point,calculate)
            if certificate is not None:
                submitted = certificate['nodes'][index]['vector'][cell]
                comparisons += 1
                if type(submitted) is not type(value) or submitted!=value:
                    raise core.Invalid('node vector type/value mismatch')
            vector.append(value)
        vectors.append(vector)
    result = core.classify_vectors(points,roots,programs['candidate'].events,vectors)
    session.commit()
    result.update({'recomputed_cells':session.recomputed,'reused_cells':session.reused,
                   'vector_comparisons':comparisons,'checked_cells':len(circuit.nodes)*len(points),
                   'cache_entries':len(cache._cells)})
    return result


def check_reusing(request,certificate,cache):
    if type(certificate) is not dict:
        raise core.Invalid('certificate type')
    return _evaluate(request,cache,certificate)


def direct_reusing(request,cache):
    return _evaluate(request,cache)
