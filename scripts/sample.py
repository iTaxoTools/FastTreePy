#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the sample GUI"""

import multiprocessing
from itaxotools.sample.gui import main

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
