#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the FastTree GUI"""

import multiprocessing
from itaxotools.fasttreepy.gui import main

if __name__ == '__main__':
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn')
    main()
