"""Obligation routing and the native-to-model observation check."""
from diagram_ink import Diagram, S, T, A, G, F

def obligation_routes():
    d=Diagram(420,105)
    for x,label in ((48,'Guard'),(131,r'$q_0$'),(236,r'$q_1$'),(352,r'$q_2$')):
        d.txt(x,90,label,10,bold=True)
    for y,guard,active,vacuous,c in ((61,'1',236,352,S),(25,'0',352,236,T)):
        d.dotmark(48,y,8,c=c)
        d.node_label(48,y,guard,9.7,color=c)
        d.wire((62,y),(87,y),c=c)
        d.block(94,y-10,74,20,G,'white')
        d.node_label(131,y,r'$d_Q$',10)
        d.block(active-48,y-10,96,20,c,'white')
        expr=(r'$d_Q\wedge d_T\wedge(o_Q=o_T)$' if guard=='1'
              else r'$d_Q\wedge d_P\wedge(o_Q=o_P)$')
        d.node_label(active,y,expr,9.4,color=c)
        d.node_label(vacuous,y,r'$\mathrm{true}$ (vacuous)',9,color=G)
    return d

def native_scalar_boundary():
    d=Diagram(420,104)
    d.mark('code',37,51,21,S)
    d.txt(38,28,'Shared input',9.1)
    d.wire((51,51),(84,51),c=S,arrow=False)
    d.dotmark(84,51,1.8,c=S,fill=S)
    for y,label,k,r,c in ((77,'Execute C','trace','Decoded output',S),
                          (25,'Normalize','vector','Model value',T)):
        d.wire((88,51),(113,y),(136,y),c=c)
        d.mark(k,148,y,16,c)
        d.txt(166,y,label,9.3,ha='left',color=c)
        d.txt(246,y,r,9.2,ha='left')
        d.wire((317,y),(344,y),(365,51),c=c,arrow=False)
    d.dotmark(374,51,6,c=T)
    d.node_label(374,51,'=',10,color=T)
    d.txt(371,15,'Compare values',8.8,color=T)
    return d

def support_projection():
    d=Diagram(420,79)
    d.txt(59,58,r'$u|_{B_j}$',11,color=S)
    d.wire((82,58),(114,58),c=S,arrow=False)
    d.dotmark(114,58,1.8,c=S,fill=S)
    d.wire((117,58),(149,58),(205,58),c=S)
    d.txt(164,69,'Fill new coordinates by minima',8.7,color=S)
    d.mark('array',222,58,14,S)
    d.txt(239,58,r'Table key on $S_j$',9.3,ha='left',color=S)
    d.wire((116,56),(148,21),(193,21),c=T)
    d.txt(69,12,r'$u|_{T_Q}$',10.1,color=A)
    d.wire((90,12),(147,12),(194,17),c=A,arrow=False)
    d.dotmark(203,21,7,c=T)
    d.node_label(203,21,r'$\cup$',9.2,color=T)
    d.wire((213,21),(250,21),c=T)
    d.mark('trace',265,21,15,T)
    d.txt(282,21,r'Diagnostic key on $B_j\cup T_Q$',9.0,ha='left',color=T)
    return d


FIGURES={'obligation-routes':obligation_routes,'native-scalar-boundary':native_scalar_boundary,
         'support-projection':support_projection}
