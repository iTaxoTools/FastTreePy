#-----------------------------------------------------------------------------
# Copyright notice goes here
#-----------------------------------------------------------------------------

from PySide6 import QtWidgets

import sys

from .main import Main

def main():
    """Entry point"""
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
