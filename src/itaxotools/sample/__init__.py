#-----------------------------------------------------------------------------
# Copyright notice goes here
#-----------------------------------------------------------------------------

from itaxotools.common.functions import add_one
from .core import config, zeros
from .my_extension import foo

def main():
    """Entry point for the application script"""
    print(config())
    print(zeros(5))
    print('41 + 1 =', add_one(41))
    print('foo:', foo())
