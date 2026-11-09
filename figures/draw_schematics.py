"""Compatibility command for the canonical journal schematics."""
import argparse
from pathlib import Path

from figure_style import paper_style
from publication_figures import boundary, receiver


def draw(out):
    paper_style('tosem')
    for fn in (boundary, receiver):
        fn(out,None)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    draw(parser.parse_args().output)
