"""Receiver-owned evidence, verdicts, and witness order."""
from diagram_ink import Diagram,S,T,A,K,G,F,L,P


def checking_boundary():
    d=Diagram(426,132)
    d.zone(101,27,211,81,fill='white')
    d.tag(110,119,'Independent receiver')
    d.mark('graph',32,96,21);d.txt(32,77,'Submitted DAG',8.8)
    d.mark('vector',32,46,21);d.txt(32,28,'Claimed cells',8.8)
    d.wire((46,96),(120,96),c=S)
    d.txt(127,96,'Rebuild roots',9.3,ha='left')
    d.wire((181,96),(204,96),(204,56),c=S)
    d.wire((46,46),(195,46),c=S)
    d.diamond(204,46,7)
    d.txt(191,61,'Valid evidence?',8.9,ha='right')
    d.wire((204,39),(204,15),(233,15),c=A,dash=True)
    d.txt(240,15,'Invalid evidence',8.8,ha='left',color=A)
    d.wire((212,46),(266,46),(266,69),(286,69),c=T)
    d.diamond(295,69,7,T)
    d.txt(283,89,'Obligations',9.0)
    d.wire((302,69),(329,69),(329,99),(374,99),c=T)
    d.wire((329,69),(329,42),(362,42),c=A)
    d.txt(351,109,'All hold',8.7,color=T)
    d.txt(345,28,'Violation',8.7,color=A)
    d.txt(382,99,'Accept',9.3,ha='left',color=T)
    d.txt(368,47,'Least',9.1,ha='left',color=A)
    d.txt(368,35,'refutation',8.6,ha='left',color=A)
    return d


def trust_boundary():
    d=Diagram(426,141)
    d.mark('code',33,79,27);d.txt(33,54,'Bound request',8.8)
    d.wire((48,79),(82,79),c=S)
    d.dotmark(90,79,3,c=S,fill=S)
    d.wire((93,79),(105,79),(105,106),(134,106),c=S)
    d.wire((105,79),(105,47),(134,47),c=T)
    d.tag(144,128,'Replay-table receiver')
    d.tag(144,69,'Direct receiver')
    d.mark('array',146,106,22,S);d.txt(168,107,'Coverage',9.3,ha='left')
    d.wire((219,106),(255,106),c=S)
    d.txt(265,106,'Check rows',9.3,ha='left')
    d.mark('graph',146,47,22,T);d.txt(169,47,'Evaluate obligations',9.3,ha='left')
    d.wire((320,106),(342,106),(342,79),(367,79),c=S)
    d.wire((271,47),(342,47),(342,79),c=T,arrow=False)
    d.mark('trace',380,79,24,T);d.txt(380,55,'Same verdict',9.0)
    d.txt(380,42,'and witness',8.9)
    return d


def diagnostic_order():
    d=Diagram(420,90)
    for x,label in [(53,'Refuting input'),(162,'Site 0'),(249,'Site 1'),(351,'Selected by')]:
        d.txt(x,79,label,9.5,bold=True)
    for y,inp,decision,out,c in ((55,r'$(0,3,0,0)$','true','Input order',S),
                                (23,r'$(0,3,1,0)$','false','Trace, then input',T)):
        d.txt(53,y,inp,9.4)
        d.wire((85,y),(146,y),c=c)
        d.dotmark(161,y,4,c=c,fill='white')
        d.txt(161,y-10,decision,8.5,color=c)
        d.wire((166,y),(236,y),c=c)
        d.dotmark(249,y,4,c=c,fill='white')
        d.txt(249,y-10,'true',8.5,color=c)
        d.wire((254,y),(299,y),c=c)
        d.txt(311,y,out,9.1,ha='left',color=c)
    return d


def reuse_boundary():
    d=Diagram(420,69)
    d.mark('keyed',27,34,23);d.txt(43,34,'Term + input',9.2,ha='left')
    d.wire((108,34),(142,34),c=S)
    d.diamond(150,34,7);d.txt(150,13,'Cache?',8.9)
    d.wire((157,34),(169,34),(169,54),(206,54),c=T)
    d.wire((169,34),(169,14),(206,14),c=A)
    d.mark('store',221,54,20,T);d.txt(237,54,'Reuse value',9,ha='left')
    d.mark('graph',221,14,19,A);d.txt(237,14,'Evaluate',9,ha='left')
    d.wire((298,54),(314,54),(314,34),(339,34),c=T)
    d.wire((284,14),(314,14),(314,34),c=A,arrow=False)
    d.mark('check',352,34,19,T);d.txt(366,34,'Compare',9.2,ha='left')
    return d


def framed_retention():
    d=Diagram(420,71)
    d.mark('vector',29,34,22);d.txt(46,34,'Node vector',9.3,ha='left')
    d.wire((107,34),(143,34),c=S)
    d.mark('check',153,34,17,T);d.txt(165,34,'Compare',9.3,ha='left')
    d.wire((210,34),(247,34),(247,53),(283,53),c=T)
    d.wire((247,34),(247,15),(283,15),c=S)
    d.mark('clock',296,53,19,T);d.txt(312,53,'Free at last use',9.1,ha='left')
    d.mark('pin',296,15,18,S);d.txt(312,15,'Retain diagnostic roots',9.0,ha='left')
    return d


def refutation_scope():
    d=Diagram(420,69)
    d.tag(11,55,'Full vector')
    d.tag(11,19,'Compact')
    for j in range(6):
        xx=123+j*15
        d.dotmark(xx,55,3,c=S,fill=L)
        d.dotmark(xx,19,3,c=A if j==3 else F,fill=A if j==3 else 'white')
    d.txt(232,55,'All points',9.1,ha='left',color=S)
    d.txt(232,19,'Claimed point',9.1,ha='left',color=A)
    d.wire((290,55),(319,55),c=T)
    d.wire((290,19),(319,19),c=A)
    d.mark('trace',333,55,18,T);d.txt(346,55,'Least witness',8.8,ha='left')
    d.mark('reject',333,19,18,A);d.txt(346,19,'One violation',8.8,ha='left')
    return d


FIGURES={f.__name__.replace('_','-'):f for f in (
    checking_boundary,trust_boundary,diagnostic_order,reuse_boundary,framed_retention,refutation_scope)}
