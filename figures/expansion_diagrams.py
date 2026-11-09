"""Obligation routing and the native-to-model observation check."""
from diagram_ink import Diagram, S, T, A

def obligation_routes():
    d=Diagram(420,105)
    d.mark('guard',23,55,25,S)
    d.txt(23,30,'Guard',9.5,color=S)
    d.wire((36,55),(73,55),(73,81),(100,81),c=S)
    d.wire((73,55),(73,29),(100,29),c=T)
    d.txt(70,94,r'$r$ true',9.6,color=S)
    d.txt(71,15,r'$r$ false',9.6,color=T)
    d.txt(112,81,r'Target $T$',10,ha='left',bold=True)
    d.txt(112,29,r'Original $P$',10,ha='left',bold=True)
    d.wire((177,81),(208,81),c=S)
    d.wire((177,29),(208,29),c=T)
    d.txt(220,81,r'$d_Q\wedge d_T,\quad o_Q=o_T$',10.4,ha='left',color=S)
    d.txt(220,29,r'$d_Q\wedge d_P,\quad o_Q=o_P$',10.4,ha='left',color=T)
    d.txt(299,55,r'$q_0=d_Q$ at every point',10.1,bold=True)
    d.mark('check',394,81,16,S)
    d.mark('check',394,29,16,T)
    return d

def native_scalar_boundary():
    d=Diagram(420,104)
    d.mark('code',24,52,27,S)
    d.txt(24,22,'Source',9.4,bold=True)
    d.wire((41,52),(75,52),(75,77),(111,77),c=S)
    d.wire((75,52),(75,27),(111,27),c=T)
    d.txt(122,77,'Native C execution',9.8,ha='left')
    d.txt(122,27,'Scalar normalization',9.8,ha='left')
    d.wire((236,77),(263,77),c=S)
    d.wire((236,27),(263,27),c=T)
    d.txt(272,77,'Decoded output',9.7,ha='left',color=S)
    d.txt(272,27,'Model value',9.7,ha='left',color=T)
    d.wire((353,77),(382,77),(382,62),c=S)
    d.wire((342,27),(382,27),(382,43),c=T)
    d.diamond(382,52,8,T)
    d.txt(382,13,'Compare',9.4,bold=True)
    return d

FIGURES={'obligation-routes':obligation_routes,'native-scalar-boundary':native_scalar_boundary}
