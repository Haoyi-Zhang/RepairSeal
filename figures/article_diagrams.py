"""Receiver-owned evidence, verdicts, and witness order."""
from diagram_ink import Diagram,S,T,A,K,G,F,L,P,O
from matplotlib.patches import FancyBboxPatch


def checking_boundary():
    from pathlib import Path
    import json
    cases={c['variant']:c for c in json.loads((Path(__file__).resolve().parents[1]/
        'results/upstream-ceil/summary.json').read_text(encoding='utf-8'))['cases']}
    supplied, original=cases['supplied'], cases['original']
    observations=lambda c: {tuple(r['input']):r for r in c['observations']}
    new,old=observations(supplied),observations(original)
    pairs=set(new)
    u=2**32-1
    repair={(m,n) for m,n in pairs if m>u-(n-1)}
    assert (len(pairs),len(repair))==(42,12) and set(old)==pairs
    assert supplied['status']=='ACCEPT' and original['status']=='REFUTED'
    assert original['witness']['input']==[2,u] and original['witness']['obligation']=='repair'
    overflow, unaffected=(2,u),(0,2)
    assert overflow in repair and unaffected in pairs-repair
    for point, old_value, new_value in ((overflow,0,1),(unaffected,0,0)):
        assert old[point]['defined'] and new[point]['defined']
        assert (old[point]['value'],new[point]['value'])==(old_value,new_value)
    assert all(r['defined'] for r in new.values())
    assert all(new[m,n]['value']==(m+n-1)//n for m,n in repair)
    assert all(new[p]['value']==old[p]['value'] for p in pairs-repair)

    d=Diagram(426,142)
    d.tag(11,130,'Two of the 42 admitted inputs')
    d.tag(251,130,'Receiver checks the full vector')
    for x,label in ((34,r'$(m,n)$'),(96,'Target value'),(165,'Candidate'),(215,'Original')):
        d.txt(x,108,label,8.8,bold=True)
    for y,p,label,c in ((87,overflow,'1 (reference)',A),(63,unaffected,'0 (original)',S)):
        ptext=r'$(2,U)$' if p==overflow else r'$(0,2)$'
        d.block(12,y-7,44,14,c,'white')
        d.node_label(34,y,ptext,9,color=c)
        d.wire((58,y),(65,y),c=c)
        d.txt(96,y,label,8.9,color=c)
        d.block(157,y-6,16,12,T,P)
        d.node_label(165,y,str(new[p]['value']),9.4,color=T)
        d.txt(215,y,str(old[p]['value']),9.7,color=A if p==overflow else G)
    d.txt(12,37,'12 repair points; 30 preservation points',8.8,ha='left')
    d.txt(12,20,'Definedness checked at every point',8.8,ha='left')

    d.mark('graph',259,108,13,S)
    d.mark('vector',259,89,13,T)
    # The two displayed replacement values illustrate cells within the full submission.
    d.wire((174,87),(185,87),(185,49),(239,49),(239,89),(251,89),c=T)
    d.wire((174,63),(185,63),c=T,arrow=False)
    d.dotmark(185,63,1.4,c=T,fill=T)
    d.wire((268,108),(283,108),(296,97),c=S,arrow=False)
    d.wire((268,89),(283,89),(296,97),c=T,arrow=False)
    d.diamond(303,97,6,S)
    d.txt(296,116,'Match rules',8.6)
    d.wire((311,97),(344,97),c=A,dash=True)
    d.txt(343,107,'Mismatch',7.6,color=A)
    d.mark('reject',352,97,10,A)
    d.txt(362,97,'Invalid evidence',8.6,ha='left',color=A)
    d.wire((303,89),(303,72),c=T)
    d.txt(295,81,'Match',7.6,ha='right',color=T)
    d.diamond(303,65,6,T)
    d.txt(292,65,'Obligations',8.7,ha='right')
    d.wire((311,65),(341,65),c=T)
    d.txt(328,75,'All hold',7.6,color=T)
    d.mark('check',351,65,10,T)
    d.txt(362,65,'Accept',8.8,ha='left',color=T)
    d.wire((303,57),(303,40),(341,40),c=A,dash=True)
    d.txt(325,50,'Violated',7.6,color=A)
    d.mark('cert',351,40,12,A)
    d.txt(362,44,'Least refutation',8.6,ha='left',color=A)
    d.txt(362,31,r'$\min(\tau_Q(u),u)$',8.8,ha='left',color=A)
    d.mark('graph',262,15,11,S)
    d.txt(272,15,'Rebuilt circuit',8.1,ha='left')
    d.mark('vector',345,15,11,T)
    d.txt(355,15,'Submitted cells',8.1,ha='left')
    return d


def trust_boundary():
    d=Diagram(426,141)
    d.mark('keyed',29,74,20,S)
    d.txt(29,48,'Request',9.1)
    d.wire((43,74),(75,74),c=S,arrow=False)
    d.dotmark(75,74,1.9,c=S,fill=S)
    d.wire((78,75),(102,99),(121,99),c=S)
    d.wire((78,73),(102,35),(224,35),c=T)
    d.txt(153,48,'Direct evaluation',9.2,color=T)
    for x,label in ((132,'Key coverage'),(228,'Row equality')):
        d.diamond(x,99,6,S)
        d.txt(x,82,label,9.2)
    d.mark('array',84,124,14,S)
    d.wire((94,123),(117,112),(126,106),c=S,dash=True)
    d.txt(73,124,'Table',8.7,ha='right')
    d.wire((140,99),(217,99),c=S)
    d.wire((236,99),(281,99),(310,68),c=S)
    d.wire((227,35),(279,35),(310,62),c=T)
    d.mark('graph',240,35,15,T)
    d.dotmark(317,65,5,c=T,fill=P)
    d.wire((323,65),(335,65),c=T)
    d.ax.add_patch(FancyBboxPatch((338,48),80,34,boxstyle='round,pad=0,rounding_size=3',
                  linewidth=.75,edgecolor=T,facecolor='white',zorder=3))
    d.mark('keyed',349,65,12,T)
    d.txt(359,71,'Accept or least',8.3,ha='left',color=T)
    d.txt(359,59,'refutation',8.3,ha='left',color=T)
    for x,l in ((132,'Uncovered'),(228,'Invalid')):
        d.wire((x,106),(x,131),(x+11,131),c=A,dash=True)
        d.mark('reject',x+18,131,9,A)
        d.txt(x+26,131,l,9,ha='left',color=A)
    return d


def diagnostic_order():
    d=Diagram(420,90)
    for x,label in [(53,'Refuting input'),(157,'Site 0'),(244,'Site 1'),(348,'Selected by')]:
        d.txt(x,79,label,9.5,bold=True)
    for y,inp,decision,out,c in [(54,r'$(0,3,0,0)$','T','Input order',S),
                                (23,r'$(0,3,1,0)$','F','Trace, then input',T)]:
        d.txt(53,y,inp,9.6)
        d.wire((89,y),(148,y),c=c)
        d.dotmark(157,y,6.2,c=c)
        d.node_label(157,y,decision,9.1,color=c)
        d.wire((166,y),(235,y),c=c,arrow=False)
        d.dotmark(244,y,6.2,c=G)
        d.node_label(244,y,'T',9.1,color=G)
        d.wire((253,y),(299,y),c=c)
        d.mark('pin',309,y,12,c)
        d.txt(320,y,out,9.4,ha='left',color=c)
    d.wire((170,64),(170,67),(144,67),(144,64),c=G,arrow=False)
    d.txt(158,10,'First differing site',8.6,color=G)
    return d


def reuse_boundary():
    d=Diagram(420,69)
    d.mark('keyed',13,32,14,S)
    d.txt(25,32,'Term + input',8.9,ha='left')
    d.wire((79,32),(91,32),c=S)
    d.diamond(98,32,5.2,S)
    for y,k,gate,act,c in ((46,'store','Hit','Reuse value',T),(16,'graph','Miss','Evaluate term',S)):
        d.wire((105,32),(121,y),(139,y),c=c,dash=y==16)
        d.txt(128,y+8,gate,8.2,color=c)
        d.mark(k,148,y,13,c)
        d.txt(159,y,act,8.8,ha='left',color=c)
        d.wire((218,y),(232,y),(248,31),c=c,arrow=False)
    d.dotmark(248,31,1.6,c=G,fill=G)
    d.wire((251,31),(263,31),c=G)
    d.diamond(270,31,5.2,T)
    d.mark('vector',270,58,12,S)
    d.wire((270,50),(270,38),c=S)
    d.txt(258,58,'Submitted',8.6,ha='right')
    d.wire((277,31),(290,42),(307,42),c=T)
    d.txt(301,49,'Equal',8.0,color=T)
    d.mark('check',315,42,11,T)
    d.txt(327,42,'Continue',8.8,ha='left',color=T)
    d.wire((277,31),(290,15),(307,15),c=A,dash=True)
    d.txt(301,24,r'$\ne$',9.0,color=A)
    d.mark('reject',315,15,11,A)
    d.txt(327,15,'Invalid evidence',8.6,ha='left',color=A)
    return d


def framed_retention():
    d=Diagram(420,84)
    d.txt(14,65,'Child cells',9.1,ha='left')
    d.txt(14,35,'Diagnostic roots',9.1,ha='left')
    d.mark('vector',100,65,13,S)
    d.mark('keyed',100,35,13,T)
    d.wire((109,65),(156,65),c=S)
    d.dotmark(162,65,3,c=S,fill=S)
    d.txt(203,71,'Last parent checked',9,color=S)
    d.wire((162,60),(162,51),c=S)
    d.txt(162,44,'Release',8.8,color=S)
    d.wire((109,35),(238,35),c=T)
    d.diamond(245,35,5,T)
    d.txt(264,54,'Seal and EOF',9.1)
    d.wire((252,35),(299,35),c=T)
    d.mark('check',310,35,12,T)
    d.txt(324,35,'Select verdict',8.9,ha='left',color=T)
    d.wire((245,28),(245,12),(295,12),c=A,dash=True)
    d.txt(305,12,'Invalid; no verdict',8.9,ha='left',color=A)
    return d


def refutation_scope():
    d=Diagram(420,103)
    d.tag(10,91,'Example: same obligation and trace')
    d.tag(275,91,'Checked result')
    for y,lab,c in ((66,'Full vector',S),(30,'Compact',A)):
        d.txt(10,y,lab,9.2,ha='left',bold=True)
        for j,x in enumerate((103,126,149,172,195,218)):
            if y==66 and j not in (1,4):
                d.mark('check',x,y,8,T)
            elif y==66 or j==4:
                d.mark('reject',x,y,8,A)
            else:
                d.dotmark(x,y,3,c=F,fill='white')
        d.wire((227,y),(263,y),c=c)
    d.txt(126,50,r'$u_2$',8.2,color=A)
    d.txt(195,50,r'$u_5$',8.2,color=A)
    d.txt(275,67,r'Least refutation at $u_2$',9.1,ha='left',color=T)
    d.txt(275,51,r'$NM$ checks; accepts if all pass',8.5,ha='left')
    d.txt(275,31,r'Named refutation at $u_5$',9.1,ha='left',color=A)
    d.txt(275,15,r'$N$ checks; no claim about $u_2$',8.5,ha='left')
    d.dotmark(99,11,3,c=F,fill='white')
    d.txt(108,11,'Not checked',8.2,ha='left',color=G)
    return d


FIGURES={f.__name__.replace('_','-'):f for f in (
    checking_boundary,trust_boundary,diagnostic_order,reuse_boundary,framed_retention,refutation_scope)}
