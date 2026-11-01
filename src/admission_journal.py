"""Durable owned repair-approval workflow with receiver-owned request identity.

This is an application consumer, not a source-mapping or deployment proof.
Full checking and certificate-free recalculation have identical information.
An accepted packet may refute a repair; only semantic ACCEPT permits approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import proof_dag_checker as core

LIMIT=32*1024*1024

def canonical(value):return core.canonical_bytes(value)
def identity(value):return hashlib.sha256(canonical(value)).hexdigest()
def read_json(path):
    with Path(path).open('rb') as f:raw=f.read(LIMIT+1)
    if len(raw)>LIMIT:raise ValueError('bounded input exceeded')
    return core.load_json_strict(raw.decode('utf-8'))

class AdmissionJournal:
    def __init__(self,path,work_limit=2_000_000):
        if type(work_limit) is not int or not 0<=work_limit<=2_000_000:raise ValueError('work limit')
        self.work_limit=work_limit
        self.db=sqlite3.connect(str(path),timeout=5,isolation_level=None)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY, revision INTEGER NOT NULL, identity TEXT NOT NULL, body TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS receipts (
            token TEXT PRIMARY KEY, request_id TEXT NOT NULL, revision INTEGER NOT NULL,
            request_identity TEXT NOT NULL, mode TEXT NOT NULL, packet_identity TEXT NOT NULL,
            decision TEXT NOT NULL, result TEXT NOT NULL);
        ''')

    def register(self,request,expected_identity=None):
        core.validate_request(request)
        if len(canonical(request))>LIMIT:raise ValueError('request byte bound')
        digest=identity(request);key=request['id']
        try:
            self.db.execute('BEGIN IMMEDIATE')
            old=self.db.execute('SELECT revision,identity FROM requests WHERE id=?',(key,)).fetchone()
            if old is None:
                if expected_identity is not None:raise ValueError('expected request absent')
                revision=1
            else:
                if expected_identity!=old[1]:raise ValueError('request replacement requires current identity')
                revision=old[0]+1
            self.db.execute('INSERT INTO requests VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,identity=excluded.identity,body=excluded.body',
                (key,revision,digest,canonical(request).decode('utf-8')))
            self.db.commit()
            return dict(request_id=key,revision=revision,request_identity=digest)
        except BaseException:
            if self.db.in_transaction:self.db.rollback()
            raise

    def decide(self,key,token,mode,packet=None):
        if type(token) is not str or not 1<=len(token)<=128:raise ValueError('receipt token')
        if mode not in ('proof','direct'):raise ValueError('decision mode')
        if mode=='direct' and packet is not None:raise ValueError('direct mode accepts no packet')
        packet_id=identity(packet)
        try:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT revision,identity,body FROM requests WHERE id=?',(key,)).fetchone()
            if row is None:raise ValueError('unregistered authoritative request')
            revision,digest,body=row
            previous=self.db.execute('SELECT request_id,revision,request_identity,mode,packet_identity,result FROM receipts WHERE token=?',(token,)).fetchone()
            if previous:
                if previous[:5]!=(key,revision,digest,mode,packet_id):raise ValueError('receipt token belongs to another request or payload')
                self.db.commit();return dict(json.loads(previous[5]),replayed_receipt=True)
            request=core.load_json_strict(body)
            if identity(request)!=digest:raise ValueError('authoritative request identity changed')
            remaining=self.work_limit
            def tick(category,n):
                nonlocal remaining
                remaining-=n
                if remaining<0:raise RuntimeError('consumer work budget exhausted')
            result=core.check(request,packet,count=tick) if mode=='proof' else core.evaluate_topological(request,count=tick)
            if result['status'] not in ('ACCEPT','REFUTED'):raise ValueError('no semantic decision')
            receipt=dict(request_id=key,revision=revision,request_identity=digest,mode=mode,
                packet_identity=packet_id,semantic_status=result['status'],approved=result['status']=='ACCEPT',
                witness=result['witness'],checked_cells=result['checked_cells'])
            self.db.execute('INSERT INTO receipts VALUES(?,?,?,?,?,?,?,?)',
                (token,key,revision,digest,mode,packet_id,result['status'],canonical(receipt).decode('utf-8')))
            self.db.commit();return dict(receipt,replayed_receipt=False)
        except BaseException:
            if self.db.in_transaction:self.db.rollback()
            raise

    def approved(self,key,expected_identity):
        if type(expected_identity) is not str or len(expected_identity)!=64:raise ValueError('explicit request identity required')
        row=self.db.execute('''SELECT COUNT(*) FROM receipts AS r JOIN requests AS q
            ON r.request_id=q.id AND r.revision=q.revision AND r.request_identity=q.identity
            WHERE q.id=? AND q.identity=? AND r.decision='ACCEPT' ''',(key,expected_identity)).fetchone()
        return row[0]>0

    def close(self):self.db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('database',type=Path)
    sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('register');r.add_argument('request',type=Path);r.add_argument('--expected-identity')
    d=sub.add_parser('decide');d.add_argument('request_id');d.add_argument('token');d.add_argument('--mode',choices=['proof','direct'],required=True);d.add_argument('--packet',type=Path)
    q=sub.add_parser('approved');q.add_argument('request_id');q.add_argument('request_identity')
    a=p.parse_args();owner=AdmissionJournal(a.database)
    try:
        if a.action=='register':result=owner.register(read_json(a.request),a.expected_identity)
        elif a.action=='approved':result=dict(approved=owner.approved(a.request_id,a.request_identity))
        else:result=owner.decide(a.request_id,a.token,a.mode,read_json(a.packet) if a.packet else None)
        print(json.dumps(result,sort_keys=True))
    finally:owner.close()
if __name__=='__main__':main()
