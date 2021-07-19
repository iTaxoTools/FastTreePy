
"""Console entry point"""

import sys

from itaxotools.common.io import redirect
from . import core

def main():
    """Process given file, save results to file"""
    try:
        p = sys.argv.index('-o')
        save = sys.argv.pop(p + 1)
        del sys.argv[p]
    except ValueError:
        save = None

    if len(sys.argv) >= 2:
        input = sys.argv[-1]
        args = sys.argv[1:-1]
        a = core.quick(input, save, args)
    else:
        print('Usage: fasttreepy {FASTTREE OPTIONS} [-o SAVE_FILE] INPUT_FILE')
        print('Ex:    fasttreepy -nt examples/simple.fas')
