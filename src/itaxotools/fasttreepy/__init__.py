
"""Console entry point"""

import sys


def main():
    """Call an (almost) unmodified version of fasttree"""
    from . import fasttree
    fasttree.raw(sys.argv[1:])
