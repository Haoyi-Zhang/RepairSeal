"""Draw the illustrative same-index check for one unsigned addition node."""
import argparse
from pathlib import Path

from visual_grammar import Diagram, INK, TEAL, GRID, GREEN


def render(out):
    U=(1<<32)-1
    a=(2,9,U)
    b=(3,2,1)
    c=tuple((x+y)%(1<<32) for x,y in zip(a,b,strict=True))
    assert c==(5,11,0)
    d=Diagram(w=351,h=106)
    xs=(129,198,270)
    d.rect(246,13,48,80,'#f2f5f6','none')
    d.rect(246,13,48,18,GREEN,TEAL,lw=.7)
    for x,title in zip(xs,('Point 0','Point 1','Point 2')):
        d.text(x,86,title,9.9,INK,bold=True)
    for y,label,values in zip((64,43,22),('Child a','Child b','Sum node'),(a,b,c)):
        d.text(13,y,label,9.6,INK,'left',y==22)
        for x,value in zip(xs,values):
            d.text(x,y,'U' if value==U else str(value),9.6,TEAL if (x==270 and y==22) else INK,bold=y==22)
    d.line((12,33),(325,33),c=GRID,lw=.65)
    d.finish(out)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    render(p.parse_args().output)
