"""Receiver-owned evidence, verdicts, and witness order."""
from diagram_ink import Diagram,S,T,A,K,G,F,L,P


def checking_boundary():
    d=Diagram(426,132)
    d.mark('code',38,99,26,S)
    d.mark('graph',109,99,25,S)
    d.mark('array',109,51,25,S)
    d.mark('lens',183,76,29,S)
    d.mark('vector',256,76,29,T)
    d.txt(38,119,'Sources',9.6)
    d.txt(109,119,'Rebuilt DAG',9.6)
    d.txt(109,32,'Certificate',9.6)
    d.txt(183,103,'Validate',10.0,bold=True)
    d.txt(256,103,'Obligations',10.0,bold=True)
    d.wire((51,99),(95,99),c=S)
    d.wire((124,99),(149,99),(169,84),c=S)
    d.wire((124,51),(149,51),(169,69),c=S)
    d.wire((198,76),(241,76),c=T)
    d.wire((271,76),(288,76),c=T,arrow=False)
    d.dotmark(288,76,1.8,c=T,fill=T)
    d.wire((290,77),(315,104),(330,104),c=T)
    d.wire((290,75),(315,58),(330,58),c=A)
    d.wire((183,61),(183,19),(330,19),c=G,dash=True)
    for y,kind,label,color in ((104,'check','Accept',T),
                              (58,'trace','Least refutation',A),
                              (19,'reject','Invalid',G)):
        d.mark(kind,342,y,20,color)
        d.txt(354,y,label,9.7,ha='left',color=color)
    return d


def trust_boundary():
    d=Diagram(426,141)
    d.mark('code',30,68,23,S)
    d.txt(30,47,'Request',9.5)
    d.wire((45,68),(92,68),c=S)
    d.mark('keyed',105,68,21,S)
    d.txt(105,45,'Rebuilt keys',9.4)
    d.wire((120,68),(142,68),c=S,arrow=False)
    d.dotmark(142,68,2,c=S,fill=S)
    for y,kind,label,c in [(100,'check','Check coverage + cells',S),
                           (35,'vector','Evaluate obligations',T)]:
        d.wire((142,68),(165,y),(183,y),c=c)
        d.mark(kind,196,y,18,c)
        d.txt(211,y,label,9.3,ha='left',color=c)
        d.wire((312,y),(333,y),c=c)
        d.mark('trace',347,y,18,c)
    d.mark('array',195,127,16,S)
    d.txt(210,127,'Submitted table',9.2,ha='left',color=S)
    d.wire((195,116),(195,110),c=S,dash=True)
    d.wire((347,88),(347,47),c=G,dash=True,arrow=False)
    d.txt(374,122,'Verdict + witness',9.2)
    d.txt(382,68,'Agree on\ncomplete,\nfaithful tables',8.9,color=G)
    return d


def diagnostic_order():
    d=Diagram(420,90)
    for x,label in [(53,'Refuting input'),(157,'Site 0'),(244,'Site 1'),(348,'Selected by')]:
        d.txt(x,79,label,9.5,bold=True)
    for y,inp,decision,out,c in [(54,r'$(0,3,0,0)$','T','Input order',S),
                                (23,r'$(0,3,1,0)$','F','Trace, then input',T)]:
        d.txt(53,y,inp,9.6)
        for a,b in [(86,148),(166,235),(253,295)]:d.wire((a,y),(b,y),c=c)
        for x,t in [(157,decision),(244,'T')]:
            d.dotmark(x,y,6.2,c=c)
            d.node_label(x,y,t,9.1,color=c)
        d.mark('pin',309,y,12,c)
        d.txt(320,y,out,9.4,ha='left',color=c)
    return d


def reuse_boundary():
    d=Diagram(420,69)
    d.mark('keyed',18,34,19,S)
    d.txt(33,34,'Term + input',9.3,ha='left')
    d.wire((92,34),(112,34),c=S)
    d.diamond(119,34,5,S)
    d.wire((126,36),(145,54),(183,54),c=T)
    d.wire((126,32),(145,14),(183,14),c=A,dash=True)
    d.txt(146,62,'Hit',8.7,color=T)
    d.txt(161,23,'Miss',8.7,color=A)
    d.mark('store',194,54,15,T)
    d.mark('graph',194,14,15,A)
    d.txt(208,54,'Reuse value',9.2,ha='left',color=T)
    d.txt(208,14,'Evaluate term',9.2,ha='left',color=A)
    d.wire((269,54),(279,54),(289,35),c=T,arrow=False)
    d.wire((269,14),(279,14),(289,35),c=A,arrow=False)
    d.dotmark(289,35,2,c=G,fill=G)
    d.wire((293,35),(314,35),c=G)
    d.diamond(321,35,5,T)
    d.mark('vector',321,59,12,S)
    d.wire((321,51),(321,43),c=S)
    d.txt(337,58,'Claimed cell',8.9,ha='left')
    d.txt(335,35,'Compare',9.2,ha='left')
    return d


def framed_retention():
    d=Diagram(420,71)
    d.mark('vector',24,45,21)
    d.txt(24,23,'Node vector',9.2)
    d.wire((40,45),(89,45),c=S)
    d.mark('check',101,45,17,T)
    d.txt(101,23,'Check vector',9.2)
    d.wire((115,45),(149,45),c=T,arrow=False)
    d.dotmark(149,45,2,c=T,fill=T)
    d.wire((153,45),(201,45),c=T)
    d.mark('store',215,45,20,T)
    d.txt(215,23,'Retain roots',9.3)
    d.wire((149,42),(149,10),(187,10),c=G,dash=True)
    d.txt(197,10,'Free children at last use',9.0,ha='left',color=G)
    d.wire((229,45),(292,45),c=T)
    d.mark('guard',306,45,21,T)
    d.txt(306,23,'Seal + EOF',9.2)
    d.wire((321,45),(366,45),c=T)
    d.mark('cert',379,45,19,T)
    d.txt(379,23,'Publish result',9.2)
    return d


def refutation_scope():
    d=Diagram(420,69)
    d.tag(11,55,'Full vector')
    d.tag(11,19,'Compact')
    for j in range(6):
        xx=123+j*15
        d.dotmark(xx,55,3,c=S,fill=L)
        if j==3:
            d.dotmark(xx,19,3,c=A,fill=A)
        else:
            d.rule(xx-2.9,19,xx+2.9,19,c=G,lw=.85)
    d.wire((211,55),(260,55),c=T)
    d.wire((211,19),(260,19),c=A)
    d.mark('trace',272,55,17,T)
    d.mark('pin',272,19,17,A)
    d.txt(289,55,'Least witness',9.3,ha='left',color=T)
    d.txt(289,19,'Claimed violation',9.3,ha='left',color=A)
    return d


FIGURES={f.__name__.replace('_','-'):f for f in (
    checking_boundary,trust_boundary,diagnostic_order,reuse_boundary,framed_retention,refutation_scope)}
