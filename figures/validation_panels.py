"""Editable manuscript panels."""
import numpy as np
from visual_grammar import *


def repair_boundary(out):
    d=Diagram(h=147)
    d.rect(5,14,413,58,GREEN,TEAL,.7)
    d.text(12,21,'Receiver boundary',8.6,TEAL,'left',True)
    d.rect(119,87,235,53,WARM,RED,.7,dash=True)
    d.text(126,131,'Untrusted',8.8,RED,'left',True)
    d.doc(54,50,BLUE)
    d.text(54,33,'Request',9.2,BLUE,bold=True)
    d.arrow((64,50),(215,50),c=BLUE)
    d.arrow((54,61),(54,111),(140,111),c=BLUE)
    d.token(151,111,'P',RED)
    d.text(173,111,'Producer',8.8,RED,'left')
    d.arrow((218,111),(251,111),c=RED)
    d.doc(265,111,RED,WARM)
    d.text(279,111,'Proof DAG',8.8,RED,'left')
    d.arrow((265,100),(265,75),(231,75),(231,62),c=RED,dash=True)
    d.token(231,50,'C',TEAL,GREEN)
    d.text(244,36,'Independent checker',9,TEAL,'left',True)
    d.arrow((241,50),(351,50),c=TEAL)
    d.check(363,55);d.cross(363,39)
    d.text(373,55,'Accept',9,TEAL,'left')
    d.text(373,39,'Refute',9,RED,'left')
    d.finish(out)


def repair_control(out):
    d=Diagram(h=146)
    d.text(13,127,'Same request',9.2,BLUE,'left',True)
    d.doc(52,94)
    d.arrow((62,94),(88,94),(88,110),(112,110),c=BLUE)
    d.arrow((62,94),(88,94),(88,53),(112,53),c=BLUE)
    d.title(119,130,'A','Certificate replay')
    d.title(119,75,'B','Direct control')
    d.range(117,106,97,6,(1,2,3,4),RED)
    d.range(117,49,97,6,(1,2,3,4),TEAL)
    d.text(166,94,'Asserted rows',8.7,RED)
    d.text(166,36,'Same obligations',8.7,TEAL)
    d.arrow((217,110),(247,110),c=RED)
    d.arrow((217,53),(247,53),c=TEAL)
    d.token(259,110,'1',RED);d.token(259,53,'2',TEAL)
    d.text(275,110,'Check coverage / truth',8.7,RED,'left')
    d.text(275,53,'Evaluate directly',8.7,TEAL,'left')
    d.arrow((365,110),(376,110),(376,84),(383,84),c=RED)
    d.arrow((351,53),(376,53),(376,84),(383,84),c=TEAL)
    d.check(395,84)
    d.text(402,67,'Same',8.6,TEAL,bold=True)
    d.text(402,55,'diagnostic',8.5,TEAL)
    d.line((110,22),(413,22),c=GRID)
    d.text(119,10,'An inadmissible certificate is not a counterexample.',8.6,MUTED,'left')
    d.finish(out)


def repair_grid(pts,out):
    d=Diagram(w=390,h=157)
    U=(1<<32)-1
    ms=sorted({m for m,_ in pts});ns=sorted({n for _,n in pts})
    assert len(pts)==42 and len(ms)==7 and len(ns)==6
    assert sum(m>U-(n-1) for m,n in pts)==12
    x0,y0,step=64,34,16
    for j,n in enumerate(ns):
        y=y0+j*step
        d.text(46,y,'U' if n==U else str(n),9.6,INK,'right')
        for i,m in enumerate(ms):
            x=x0+i*step
            repair=m>U-(n-1)
            d.rect(x-7.5,y-7.5,15,15,WARM if repair else PALE,GRID,.55)
            if repair:d.cross(x,y,RED,3.05)
            else:d.dot(x,y,2.15,BLUE,'white')
    for i,m in enumerate(ms):
        d.text(x0+i*step,18,'U−1' if m==U-1 else 'U' if m==U else str(m),9.6)
    d.text(113,6,'Numerator m',9.4)
    d.text(17,76,'n',9,INK,italic=True)
    d.title(47,145,'A','Receiver-selected input grid')
    d.title(202,145,'B','Finite obligations')
    d.dot(216,114,2.6,BLUE,'white')
    d.text(232,114,'Preserve original  ·  30',10,BLUE,'left',True)
    d.cross(216,89,RED,3.0)
    d.text(232,89,'Compare with reference  ·  12',10,RED,'left',True)
    d.text(208,48,'Definedness: all 42 inputs',9.6,INK,'left')
    d.finish(out)


def repair_mappings(model,seen,out):
    d=Diagram(h=137)
    lookup={(r['case'],r['candidate_origin']):r for r in model}
    pairs=sorted({r['case'] for r in model})
    assert len(lookup)==4 and len(pairs)==2
    d.text(19,106,'Source case',9.7,INK,'left',True)
    d.text(109,106,'Original',9.7,INK,'left',True)
    d.text(197,106,'Supplied repair',9.7,INK,'left',True)
    d.text(352,106,'Native agreements',9.7,INK,bold=True)
    d.line((19,94),(407,94),c=GRID,lw=.62)
    d.line((281,36),(281,95),c=GRID,lw=.62)
    for y,case in zip((76,48),pairs):
        d.text(19,y,case,9.7,INK,'left',True)
        for role in ('buggy','supplied'):
            row=lookup[case,role]
            assert row['points']==64 and seen[case,role]==64
            assert row['status']==('REFUTED' if role=='buggy' else 'ACCEPT')
            if role=='buggy':assert row['witness']['input']==[2]
        d.cross(99,y,RED,2.6)
        d.text(109,y,'Input 2',9.5,RED,'left')
        d.check(187,y,BLUE)
        d.text(197,y,'64 / 64',9.5,BLUE,'left')
        n=sum(seen[case,role] for role in ('buggy','supplied'))
        expected=sum(lookup[case,role]['points'] for role in ('buggy','supplied'))
        assert n==expected==128
        d.rect(299,y-6,53,12,PALE,BLUE,.65)
        d.rect(352,y-6,53,12,GREEN,BLUE,.65)
        d.text(325.5,y,'64',9.1,INK)
        d.text(378.5,y,'64',9.1,INK)
    assert sum(seen.values())==256
    d.text(352,23,'256 / 256 total',9.5,BLUE,bold=True)
    d.finish(out)
