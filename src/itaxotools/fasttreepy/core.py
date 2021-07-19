# -----------------------------------------------------------------------------
# FastTreePy - Maximum-likelihood phylogenetic tree approximation with FastTree
# Copyright (C) 2021  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------


from multiprocessing import Process

import tempfile
import shutil
import pathlib
import os
import sys

from itaxotools.common.io import redirect

from . import fasttree
from . import params

class PhylogenyApproximation():

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state

    def __init__(self, file=None):
        """
        """
        self.file = file
        self.target = None
        self.results = None
        self.log = None
        self.param = params.params

    def run(self):
        """
        Run the FastTree core with given params,
        save results to a temporary directory.
        """
        kwargs = self.param.dumps()
        fasttree.main(self.file, **kwargs)
        self.results = self.target

    def launch(self):
        """
        Should always use a seperate process to launch the FastTree core,
        as some internal functions call exit(), while repeated calls may
        cause segfaults. Results are saved in a temporary directory,
        use fetch() to retrieve them.
        """
        self._temp = tempfile.TemporaryDirectory(prefix='fasttree_')
        self.target = pathlib.Path(self._temp.name).as_posix()
        p = Process(target=self.run)
        p.start()
        p.join()
        if p.exitcode != 0:
            raise RuntimeError('FastTree internal error, please check logs.')
        self.results = self.target

def quick(input=None, save=None):
    """Quick analysis"""
    a = PhylogenyApproximation(input)
    a.launch()
    if save is not None:
        savefile = open(save, 'w')
    else:
        savefile = sys.stdout
    with open(pathlib.Path(a.results) / 'pre') as result:
        print(result.read(), file=savefile)
    if save is not None:
        savefile.close()
