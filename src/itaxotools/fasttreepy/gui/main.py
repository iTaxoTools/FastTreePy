#-----------------------------------------------------------------------------
# Copyright notice goes here
#-----------------------------------------------------------------------------

"""Long module description"""

from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui

import importlib.resources

from itaxotools.common import resources

from itaxotools.common.param.model import Model
from itaxotools.common.param.view import View
from itaxotools.common.param import Field
from ..params import params

_resource_path = importlib.resources.files(resources)
def get_resource(path):
    return str(_resource_path / path)

class Main(QtWidgets.QDialog):
    """Main window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = 'Sample Tool'
        self.pyr8s = None

        self.setWindowTitle(self.title)

        path = get_resource('logos/png/itaxotools-micrologo.png')
        pixmap = QtGui.QPixmap(path)
        label = QtWidgets.QLabel()
        label.setPixmap(pixmap.scaled(100, 50, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding))

        self.params = params

        model = Model(self.params)
        view = QtWidgets.QTreeView()
        view.setModel(model)
        # view2 = QtWidgets.QTreeView()
        # view2.setModel(model)
        # view2.setRootIndex(model.createIndex(0,0,self.params.general))
        # view2.setRootIndex(model.paramIndex(self.params.general))
        # i = model.paramIndex(self.params.general.delta)
        # model.setData(i, 42)

        view3 = View(model)

        # view4 = View(model)
        # view4.setRootIndex(model.paramIndex(params.general))
        #
        # view5 = View(model)
        # view5.setRootIndex(model.paramIndex(params.general.delta))

        self.model = model
        self.bar = 'bar'
        button_foo = QtWidgets.QPushButton('Foo')
        button_foo.clicked.connect(self.foo)

        button_config = QtWidgets.QPushButton('Show config')
        button_config.clicked.connect(self.show_config)

        button_pyr8s = QtWidgets.QPushButton('Launch pyr8s')
        button_pyr8s.clicked.connect(self.show_pyr8s)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label, 0)
        layout.addWidget(view, 0)
        # layout.addWidget(view2, 0)
        layout.addWidget(view3, 0)
        # layout.addWidget(view4, 0)
        # layout.addWidget(view5, 0)
        layout.addWidget(button_foo, 0)
        layout.addWidget(button_config, 0)
        layout.addWidget(button_pyr8s, 0)
        layout.setSpacing(4)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def foo(self):
        self.params.general.gamme = 51
        self.params.add(Field('baz'))
        self.params.general.add(Field('bazar'))
        self.bar += 'bar'
        self.model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, self.bar)
        p = self.model.index(0,0, QtCore.QModelIndex())
        self.model.dataChanged.emit(p, p)

    def show_config(self):
        config = "core.config()"
        msgBox = QtWidgets.QMessageBox.information(self, 'Config', str(config))

    def show_pyr8s(self):
        try:
            from itaxotools.pyr8s.gui.main import Main as Pyr8sMain
            if self.pyr8s is None:
                self.pyr8s = Pyr8sMain()
            self.pyr8s.show()
        except Exception as e:
            print(e)
