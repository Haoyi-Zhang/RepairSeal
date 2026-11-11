"""Obligation routing and the native-to-model observation check."""
from diagram_ink import Diagram, S, T, A

def obligation_routes():
    d=Diagram(420,105)
    d.mark('guard',23,55,25,S)
    d.txt(23,30,'Guard',9.4,color=S)
    d.wire((36,55),(71,55),(71,81),(101,81),c=S)
    d.wire((71,55),(71,29),(101,29),c=T)
    d.node_label(71,94,'Inside repair region',9.4,color=S)
    d.node_label(71,15,'Outside repair region',9.4,color=T)
    for y,name,c in ((81,r'Target $T$',S),(29,r'Original $P$',T)):
        d.mark('code',115,y,18,c)
        d.txt(132,y,name,9.5,ha='left')
        d.wire((183,y),(209,y),c=c)
    d.txt(220,81,r'$d_Q\wedge d_T,\quad o_Q=o_T$',10.4,ha='left',color=S)
    d.txt(220,29,r'$d_Q\wedge d_P,\quad o_Q=o_P$',10.4,ha='left',color=T)
    d.node_label(288,55,r'Always require $d_Q$',9.5)
    d.mark('check',391,81,15,S)
    d.mark('check',391,29,15,T)
    return d

def native_scalar_boundary():
    d=Diagram(420,104)
    d.mark('code',24,52,27,S)
    d.txt(24,22,'Source',9.4)
    d.dotmark(75,52,1.7,c=S,fill=S)
    d.wire((41,52),(75,52),(75,77),(111,77),c=S)
    d.wire((75,52),(75,27),(111,27),c=T)
    for y,label,kind,output,c in [(77,'Native C execution','trace','Decoded output',S),
                                  (27,'Scalar normalization','vector','Model value',T)]:
        d.txt(123,y,label,9.4,ha='left')
        d.wire((214,y),(237,y),c=c)
        d.mark(kind,249,y,15,c)
        d.txt(263,y,output,9.4,ha='left',color=c)
        d.wire((335,y),(382,y),(382,62 if y>52 else 42),c=c)
    d.diamond(382,52,8,T)
    d.txt(382,13,'Compare',9.4,bold=True)
    return d

def support_projection():
    d=Diagram(420,79)
    d.tag(11,68,'Obligation truth')
    d.tag(11,28,'Least diagnostic')
    d.txt(151,68,r'$B_j$',11,color=S)
    d.txt(239,68,r'$S_j$',11,color=S)
    d.wire((169,68),(220,68),c=S)
    d.txt(194,56,'Extend by minima',8.6,color=S)
    d.mark('array',281,68,16,S)
    d.txt(295,68,'Table-replay key',9.1,ha='left',color=S)
    d.txt(151,28,r'$B_j$',11,color=T)
    d.txt(151,9,r'$T_Q$',10.4,color=A)
    d.wire((168,28),(186,28),(197,21),c=T,arrow=False)
    d.wire((168,9),(186,9),(197,21),c=A,arrow=False)
    d.dotmark(203,21,5.5,c=T)
    d.node_label(203,21,r'$\cup$',9.2,color=T)
    d.wire((211,21),(269,21),c=T)
    d.mark('trace',281,21,16,T)
    d.txt(295,21,'Key preserves truth and trace',9.1,ha='left',color=T)
    return d


FIGURES={'obligation-routes':obligation_routes,'native-scalar-boundary':native_scalar_boundary,
         'support-projection':support_projection}
