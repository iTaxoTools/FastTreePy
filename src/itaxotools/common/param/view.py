# -----------------------------------------------------------------------------
# Param - Parameter view
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


"""
Parameter view for PySide6
"""

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QSize, Signal
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QCheckBox, QScrollArea,
    QMessageBox, QSizePolicy, QComboBox, QGroupBox, QVBoxLayout,
    QHBoxLayout, QLayout)
from PySide6.QtGui import QIntValidator, QDoubleValidator

from . import Field, Group
from .model import Model


class FieldWidget(QFrame):

    # Emit (_index, value) when user changes the field value
    dataChanged = Signal(object, object)

    def __init__(self, index, field, view, parent=None):
        super().__init__(parent)
        view.dataChanged.connect(self.refreshData)
        self._index = index
        self._field = field
        self._view = view

    def refreshData(self):
        """Called by view when field value is changed"""
        raise NotImplementedError()


class BoolWidget(FieldWidget):

    dataChanged = Signal(object, object)

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.checkbox = QCheckBox()
        self.checkbox.setText(self._field.label)
        self.checkbox.stateChanged.connect(self.onDataChange)
        self.checkbox.setToolTip(self._field.doc)
        self.refreshData()
        layout = FieldLayout()
        layout.addWidget(self.checkbox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def onDataChange(self):
        v = self.checkbox.isChecked()
        self.dataChanged.emit(self._index, v)

    def refreshData(self):
        data = self._field.value
        self.checkbox.setChecked(data)


class EntryWidget(FieldWidget):

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.label = QLabel(self._field.label + ': ')
        self.entry = QLineEdit()
        self.entry.editingFinished.connect(self.onDataChange)
        if issubclass(self._field.type, int):
            self.entry.setValidator(QIntValidator(self.entry))
        elif issubclass(self._field.type, float):
            self.entry.setValidator(QDoubleValidator(self.entry))
        self.label.setToolTip(self._field.doc)
        self.entry.setToolTip(self._field.doc)
        self.refreshData()
        layout = FieldLayout()
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.entry)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def onDataChange(self):
        v = self.entry.text()
        self.dataChanged.emit(self._index, v)

    def refreshData(self):
        self.entry.setText(str(self._field.value))


class ListWidget(FieldWidget):

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        self.label = QLabel(self._field.label + ': ')
        self.combo = QComboBox()
        self.combo.setFocusPolicy(Qt.StrongFocus)
        self.combo.currentIndexChanged.connect(self.onDataChange)
        self.populateCombo()
        self.label.setToolTip(self._field.doc)
        self.combo.setToolTip(self._field.doc)
        layout = FieldLayout()
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def populateCombo(self):
        self.combo.clear()
        if isinstance(self._field.list, list):
            for k in self._field.list:
                self.combo.addItem(str(k), k)
        elif isinstance(self._field.list, dict):
            for k, v in self._field.list.items():
                self.combo.addItem(k, v)
        self.refreshData()

    def onDataChange(self):
        v = self.combo.currentData()
        self.dataChanged.emit(self._index, v)

    def refreshData(self):
        data = self._field.value
        i = list(self._field.list).index(data)
        self.combo.setCurrentIndex(i)


class FieldLayout(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    #     self.setSizeConstraint(QLayout.SetMinAndMaxSize)
    #
    # def minimumSize(self):
    #     return QSize(10,0)
    # #
    # def maximumSize(self):
    #     return QSize(300,200)

class FieldView(QFrame):

    def __init__(self, param, parent=None):
        super().__init__(parent)
        layout = FieldLayout()
        label = QLabel(param.label)
        lineEdit = QLineEdit(str(param.value))
        # lineEdit.setMinimumHeight(30)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(lineEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        # self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        # self.setMinimumHeight(1)
        label.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum)
        lineEdit.setMinimumWidth(100)
        lineEdit.setMaximumWidth(100)
        lineEdit.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Minimum)


class View(QScrollArea):

    # Emit to update field widgets on model data change
    dataChanged = Signal()

    def __init__(self, model=None, parent=None):
        super().__init__(parent)
        self._model = None
        self._rootIndex = QModelIndex()
        self._widgets = dict()
        self.setWidgetResizable(False)
        if model is not None:
            self.setModel(model)

    def rootIndex(self):
        return self._rootIndex

    def setRootIndex(self, index):
        self._rootIndex = index
        self.draw()

    def model(self):
        return self._model

    def setModel(self, model):
        self._widgets = dict()
        self._model = model
        model.dataChanged.connect(self._onModelDataChange)
        self.setRootIndex(QModelIndex())
        self.draw()

    def draw(self):
        widget = self._populate(self._rootIndex, 0)
        self.setWidget(widget)
        widget.setStyleSheet("""
            FieldView[depth="1"] {
                margin-left: 1px;
                margin-right: 10px;
                }
            FieldWidget[depth="1"] {
                margin-left: 1px;
                margin-right: 10px;
                }
            QGroupBox:!flat {
                background-color: rgba(0,0,0,0.02);
                border: 1px solid Palette(Mid);
                margin-top: 28px;
                padding: 0px;
                }
            QGroupBox::title:!flat {
                color: Palette(Text);
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px -1px;
                }
            QGroupBox:flat {
                border-top: 1px solid Palette(Mid);
                border-left: 0px;
                border-bottom: 0px;
                margin-top: 24px;
                margin-right: -20px;
                padding-left: 12px;
                padding-bottom: 0px;
                }
            QGroupBox::title:flat {
                color: Palette(Text);
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px -1px;
                }
        """)
        widget.show()

    def onInvalidValue(self, error):
        """Called when a field value was invalid"""
        QMessageBox.warning(self, 'Warning', error)

    def _onModelDataChange(self, topLeft, bottomRight, roles):
        """Simply refresh all widgets"""
        self.dataChanged.emit()

    def _onWidgetDataChange(self, index, data):
        """Update model"""
        if not self._model.setData(index, data):
            self.onInvalidValue(self._model.setDataError)
            self.sender().refreshData()

    def _fieldWidget(self, index, field, depth=0):
        """Generate and return an appropriate widget for the field"""
        if field.list:
            widget = ListWidget(index, field, self)
            widget.setProperty('depth', depth)
            return widget
        type_to_widget = {
            bool: BoolWidget,
            float: EntryWidget,
            str: EntryWidget,
            int: EntryWidget,
            }
        if field.type in type_to_widget.keys():
            widget = type_to_widget[field.type](index, field, self)
        else:
            widget = EntryWidget(index, field, self)
        widget.dataChanged.connect(self._onWidgetDataChange)
        widget.setProperty('depth', depth)
        return widget

    def _populate(self, index, depth=0):
        """Recursively populate and return a widget with params"""
        data = self._model.data(index, self._model.DataRole)

        if isinstance(data, Field):
            return self._fieldWidget(index, data, depth)

        if depth == 0:
            widget = QFrame()
            layout = QVBoxLayout()
        elif depth == 1:
            widget = QGroupBox(data.label)
            layout = QVBoxLayout()
        else:
            widget = QGroupBox(data.label)
            widget.setFlat(True)
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 6, 0, 3)

        rows = self._model.rowCount(index)
        for row in range(0, rows):
            childIndex = self._model.index(row, 0, index)
            child = self._populate(childIndex, depth+1)
            layout.addWidget(child)
        widget.setLayout(layout)
        return widget
