#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the FastTree GUI"""

import multiprocessing
from itaxotools.fasttree.gui import main

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
