
import sys

from . import core

def main():
    """Process given file"""
    if len(sys.argv) == 2:
        a=core.PhylogenyApproximation(sys.argv[1]).launch()
    else:
        print('Usage: fasttreepy FILE')
        print('Ex:    fasttreepy examples/simple.fas')
