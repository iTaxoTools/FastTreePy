
"""API and console entry-point"""

__all__ = ['PhylogenyApproximation', 'quick']


import sys

from .core import PhylogenyApproximation, quick


def main():
    """Call an (almost) unmodified version of fasttree"""
    from . import fasttree
    fasttree.raw(sys.argv[1:])
