"""Build the vector diagram used in the main manuscript."""
from pathlib import Path
from visual_grammar import Diagram, BLUE, RED, INK, MUTED, PALE, WARM, GRID

def draw(out):
    d=Diagram(w=408,h=112)
    d.text(200,99,r'$Q(x)=x\,/\,0$',11,INK,bold=True)
    d.line((200,87),(200,78),(99,78),c=MUTED)
    d.arrow((99,78),(99,66),c=BLUE)
    d.line((200,78),(307,78),c=MUTED)
    d.arrow((307,78),(307,66),c=RED)
    d.rect(15,34,168,30,PALE,BLUE,.7)
    d.rect(224,34,167,30,WARM,RED,.7)
    d.text(99,54,'Total circuit value',10,BLUE,bold=True)
    d.text(99,42,r'$V_{x/0}=0$',10)
    d.text(307,54,'Source definedness',10,RED,bold=True)
    d.text(307,42,r'$d_x\wedge d_0\wedge(0\ne 0)=\mathrm{false}$',9.4)
    d.ax.set_ylim(27,112)
    d.fig.set_size_inches(408/72,85/72)
    d.finish(out)

if __name__ == '__main__':
    draw(Path(__file__).with_name('definedness-rule-tree.pdf'))
