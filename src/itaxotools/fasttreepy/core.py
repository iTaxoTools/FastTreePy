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
import pathlib
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
        self.args = []

    def run(self):
        """
        Run the FastTree core with given params,
        save results to a temporary directory.
        """
        kwargs = self.param.dumps()
        path = str(self.fetch())
        with redirect(fasttree, 'stdout', path, 'w'), \
             redirect(fasttree, 'stderr', self.log, 'a'):
            fasttree.main(self.file, args=self.args, **kwargs)
        self.results = self.target

    def launch(self):
        """
        Should always use a seperate process to launch the FastTree core,
        as some internal functions call exit(), while repeated calls may
        cause segfaults. Results are saved in a temporary directory,
        use fetch() to retrieve them.
        """
        self.results = None
        self._temp = tempfile.TemporaryDirectory(prefix='fasttree_')
        self.target = pathlib.Path(self._temp.name).as_posix()
        p = Process(target=self.run)
        p.start()
        p.join()
        if p.exitcode != 0:
            raise RuntimeError('FastTree internal error, please check logs.')
        self.results = self.target

    def fetch(self):
        """
        Return the path to the resulting tree file.
        """
        if self.target is None:
            return None
        return pathlib.Path(self.target) / 'tree'


def quick(input=None, save=None, args=[]):
    """Quick analysis"""
    a = PhylogenyApproximation(input)
    a.args = args
    a.launch()
    with open(a.fetch()) as result:
        if save is not None:
            with open(save, 'w') as savefile:
                print(result.read(), file=savefile)
        else:
            print(result.read())
