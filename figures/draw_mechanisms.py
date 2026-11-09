"""Rebuild the paper's mechanism schematics at their intended physical size."""
from pathlib import Path
from diagram_core import Figure, BLUE, GRAY, INK, RED

def below(f,x,y,icon,label):
    """Keep multiline labels clear of the glyph at actual print scale."""
    f.icon(icon,x,y)
    f.t(x,y+f.units(19.5)[1],label)

def proof_polarity(f):
    below(f,55,45,'source','Bound source\nand obligation')
    f.route((71,45),(118,45))
    f.line((118,23),(118,73),color=BLUE,check=True)
    f.route((118,23),(151,23))
    f.route((118,73),(151,73),color=RED)
    f.node(167,23,'checkgrid','Complete domain',side='right')
    f.node(167,73,'point','One violated input',side='right',color=RED)
    f.route((269,23),(298,23))
    f.route((269,73),(298,73),color=RED)
    f.node(313,23,'check','Accept if all hold',side='right')
    f.node(313,73,'reject','Reject on replay',side='right',color=RED)

def cache_commit(f):
    for x,icon,label in [(39,'store','Prior facts'),(130,'cert','Bound request'),
                         (236,'compare','Validate all checks'),(356,'store','Commit facts')]:
        f.node(x,28,icon,label)
    for a,b in [(54,115),(145,221),(251,341)]:
        f.route((a,28),(b,28))
    f.route((286,29),(286,76),(314,76),dash=True,color=RED)
    f.node(328,76,'reject','Keep prior cache',side='right',color=RED)
    f.t(275,73,'invalid packet',align='right',color=RED)

FIGURES = [('proof_polarity', 420, 76), ('cache_commit', 420, 79)]

if __name__ == '__main__':
    for name,w,h in FIGURES:
        f=Figure(dict(media=(w,h),trim=(0,0,0,0),width=w))
        globals()[name](f)
        f.finish(Path(__file__).parent/(name.replace('_','-')+'.pdf'))
