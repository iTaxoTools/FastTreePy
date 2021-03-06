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

"""Long module description"""

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtStateMachine
from PySide6 import QtGui

import tempfile
import pathlib
import shutil
import enum
import sys

from itaxotools.common.param.model import Model
from itaxotools.common.param.view import View, ListWidget, FieldWidget

from itaxotools import common
from itaxotools.common import threading
from itaxotools.common import widgets
from itaxotools.common import resources
from itaxotools.common import machine
from itaxotools.common import io

from .. import core


def get_resource(path):
    # return str(_resource_path / path)
    return common.resources.get('itaxotools.fasttreepy.gui', path)
def get_icon(path):
    return common.resources.get_common(pathlib.Path('icons/svg') / path)
def get_about():
    # return str(_package_path / 'about.html')
    return common.resources.get('itaxotools.fasttreepy.gui', 'about.html')


class Action(enum.Enum):
    Update = enum.auto()
    Open = enum.auto()
    Done = enum.auto()
    Fail = enum.auto()
    Run = enum.auto()
    Cancel = enum.auto()


class RadioWidget(FieldWidget):

    dataChanged = QtCore.Signal(object, object)

    def __init__(self, index, field, view, parent=None):
        super().__init__(index, field, view, parent)
        layout = QtWidgets.QVBoxLayout()
        self.radio = dict()
        for k, v in field.list.items():
            self.radio[k] = QtWidgets.QRadioButton(v)
            self.radio[k].toggled.connect(self.onDataChange)
            self.radio[k].setToolTip(field.doc)
            layout.addWidget(self.radio[k])
        self.refreshData()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def onDataChange(self, state):
        for k in self.radio:
            if self.radio[k].isChecked():
                self.dataChanged.emit(self._index, k)
                break

    def refreshData(self):
        value = self._field.value
        for k in self.radio:
            self.radio[k].blockSignals(True)
            self.radio[k].setChecked(k == value)
            self.radio[k].blockSignals(False)

    def setFocus(self, reason=QtCore.Qt.OtherFocusReason):
        self.radio[self._field.value].setFocus(reason)

    # def sizeHint(self):
    #     return self.checkbox.sizeHint() + QSize(5, 0)


class ModelListWidget(ListWidget):
    """Changes contents depending on sequence type"""

    ncodeDict = {4: {'jc':  'JC', 'gtr': 'GTR'},
                 20: {'jtt': 'JTT', 'wag': 'WAG', 'lg':  'LG'}}

    def __init__(self, index, field, view, parent=None):
        self.param = view.model().rootItem
        super().__init__(index, field, view, parent)

    def populateCombo(self):
        self.combo.blockSignals(True)
        self.combo.clear()
        d = self.ncodeDict[self.param.sequence.ncodes.value]
        for k, v in d.items():
            self.combo.addItem(v, k)
        self.combo.blockSignals(False)
        self.refreshData()

    def onModelDataChange(self, index):
        """Change contents if ncodes is altered"""
        param = self._view.model().data(index, Model.DataRole)
        if param is self.param.sequence.ncodes:
            self.populateCombo()
        if index == self._index:
            self.refreshData()

    def refreshData(self):
        value = self._field.value
        try:
            d = self.ncodeDict[self.param.sequence.ncodes.value]
            i = list(d.keys()).index(value)
            self.combo.blockSignals(True)
            self.combo.setCurrentIndex(i)
            self.combo.blockSignals(False)
        except ValueError:
            self.combo.setCurrentIndex(0)
            v = self.combo.currentData()
            self.dataChanged.emit(self._index, v)


class CustomView(View):
    """Param view with custom widgets"""

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.addCustomParamWidget(
            model.rootItem.sequence.ncodes, RadioWidget)
        self.addCustomParamWidget(
            model.rootItem.model.ml_model, ModelListWidget)


class TextEditLogger(common.widgets.TextEditLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTextEdit {
                background-color: palette(Base);
                border: 1px solid palette(Mid);
                }
            """)


class Header(QtWidgets.QFrame):
    """
    The Taxotools toolbar, with space for a title, description,
    citations and two logos.
    """
    def __init__(self):
        """ """
        super().__init__()

        self._title = None
        self._description = None
        self._citation = None
        self._logoTool = None

        self.logoSize = 64

        self.draw()

    def draw(self):
        """ """
        self.setStyleSheet("""
            Header {
                background: palette(Light);
                border-top: 2px solid palette(Mid);
                border-bottom: 1px solid palette(Dark);
                }
            """)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum)

        self.labelTitle = QtWidgets.QLabel('TITLE')
        self.labelTitle.setAlignment(QtCore.Qt.AlignBottom)
        self.labelTitle.setStyleSheet("""
            color: palette(Text);
            font-size: 14px;
            letter-spacing: 1px;
            font-weight: bold;
            text-decoration: underline;
            """)

        self.labelCitation = QtWidgets.QLabel('CITATION')
        self.labelCitation.setAlignment(QtCore.Qt.AlignBottom)
        self.labelCitation.setStyleSheet("""
            color: palette(Shadow);
            font-size: 12px;
            font-style: italic;
            """)

        self.labelDescription = QtWidgets.QLabel('DESCRIPTION')
        self.labelDescription.setAlignment(QtCore.Qt.AlignTop)
        self.labelDescription.setStyleSheet("""
            color: palette(Text);
            font-size: 12px;
            letter-spacing: 1px;
            """)

        labels = QtWidgets.QGridLayout()
        labels.setRowStretch(0, 2)
        labels.addWidget(self.labelTitle, 1, 0)
        labels.addWidget(self.labelCitation, 1, 1)
        labels.addWidget(self.labelDescription, 2, 0, 1, 3)
        labels.setRowStretch(3, 2)
        labels.setColumnStretch(2, 1)
        labels.setHorizontalSpacing(4)
        labels.setVerticalSpacing(6)
        labels.setContentsMargins(0, 0, 0, 4)

        self.labelLogoTool = QtWidgets.QLabel()
        self.labelLogoTool.setAlignment(QtCore.Qt.AlignCenter)

        self.labelLogoProject = common.widgets.ScalingImage()
        layoutLogoProject = QtWidgets.QHBoxLayout()
        layoutLogoProject.addWidget(self.labelLogoProject)
        layoutLogoProject.setContentsMargins(2, 4, 2, 4)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(32, 32))
        self.toolbar.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.toolbar.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.toolbar.setStyleSheet("""
            QToolBar {
                spacing: 2px;
                }
            QToolButton {
                color: palette(ButtonText);
                background: transparent;
                border: 2px solid transparent;
                border-radius: 3px;
                font-size: 14px;
                min-width: 50px;
                min-height: 60px;
                padding: 6px 0px 0px 0px;
                margin: 4px 0px 4px 0px;
                }
            QToolButton:hover {
                background: palette(Window);
                border: 2px solid transparent;
                }
            QToolButton:pressed {
                background: palette(Midlight);
                border: 2px solid palette(Mid);
                border-radius: 3px;
                }
            QToolButton[popupMode="2"]:pressed {
                padding-bottom: 5px;
                border: 1px solid palette(Dark);
                margin: 5px 1px 0px 1px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                }
            QToolButton::menu-indicator {
                image: none;
                width: 30px;
                border-bottom: 2px solid palette(Mid);
                subcontrol-origin: padding;
                subcontrol-position: bottom;
                }
            QToolButton::menu-indicator:disabled {
                border-bottom: 2px solid palette(Midlight);
                }
            QToolButton::menu-indicator:pressed {
                border-bottom: 0px;
                }
            """)

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(8)
        layout.addWidget(self.labelLogoTool)
        layout.addSpacing(6)
        layout.addWidget(common.widgets.VLineSeparator())
        layout.addSpacing(12)
        layout.addLayout(labels, 0)
        layout.addSpacing(12)
        layout.addWidget(common.widgets.VLineSeparator())
        layout.addSpacing(8)
        layout.addWidget(self.toolbar, 0)
        layout.addStretch(1)
        layout.addWidget(common.widgets.VLineSeparator())
        layout.addLayout(layoutLogoProject, 0)
        # layout.addWidget(self.labelLogoProject)
        layout.addSpacing(2)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self.labelTitle.setText(title)
        self._title = title

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self.labelDescription.setText(description)
        self._description = description

    @property
    def citation(self):
        return self._citation

    @citation.setter
    def citation(self, citation):
        self.labelCitation.setText(citation)
        self._citation = citation

    @property
    def logoTool(self):
        return self._logoTool

    @logoTool.setter
    def logoTool(self, logo):
        self.labelLogoTool.setPixmap(logo)
        self._logoTool = logo

    @property
    def logoProject(self):
        return self.labelLogoProject.logo

    @logoProject.setter
    def logoProject(self, logo):
        self.labelLogoProject.logo = logo


class Main(common.widgets.ToolDialog):
    """Main window, handles everything"""

    actionSignal = QtCore.Signal(Action, list, dict)

    def __init__(self, parent=None, init=None):
        super(Main, self).__init__(parent)

        self.title = 'FastTreePy'
        self.analysis = core.PhylogenyApproximation()
        self.file = None
        self._temp = None
        self.temp = None

        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(get_resource('logos/fasttree.ico')))
        self.resize(860, 570)

        self.process = None
        self.machine = None
        self.skin()
        self.draw()
        self.act()
        self.cog()

        if init is not None:
            self.machine.started.connect(init)

        self.setAcceptDrops(True)

    def __getstate__(self):
        return (self.analysis,)

    def __setstate__(self, state):
        (self.analysis,) = state

    def postAction(self, action, *args, **kwargs):
        self.actionSignal.emit(action, args, kwargs)

    def taggedTransition(self, action):
        return common.machine.TaggedTransition(self.actionSignal, action)

    def dragEnterEvent(self, event):
        """Accept single file drops as long as state is idle"""
        if not self.state['idle'] in list(self.machine.configuration()):
            event.ignore()
            return
        data = event.mimeData()
        if data.hasUrls():
            urls = data.urls()
            if len(urls) == 1:
                url = data.urls()[0]
                file = QtCore.QFileInfo(url.toLocalFile())
                if file.isFile():
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        if data.hasUrls():
            url = data.urls()[0]
            self.handleOpen(fileName=url.toLocalFile())

    def onReject(self):
        """If running, verify cancel"""
        if self.state['running'] in list(self.machine.configuration()):
            self.handleStop()
            return True
        else:
            return None

    def cog(self):
        """Initialize state machine"""

        self.machine = QtStateMachine.QStateMachine(self)

        self.state = {}
        self.state['idle'] = QtStateMachine.QState(
            QtStateMachine.QState.ChildMode.ParallelStates, self.machine)

        self.state['idle/input'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle/input.none'] = QtStateMachine.QState(self.state['idle/input'])
        self.state['idle/input.file'] = QtStateMachine.QState(self.state['idle/input'])
        self.state['idle/input.last'] = QtStateMachine.QHistoryState(self.state['idle/input'])
        self.state['idle/input.last'].setDefaultState(self.state['idle/input.none'])
        self.state['idle/input'].setInitialState(self.state['idle/input.none'])

        self.state['idle/output'] = QtStateMachine.QState(self.state['idle'])
        self.state['idle/output.none'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.complete'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.failed'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.outdated'] = QtStateMachine.QState(self.state['idle/output'])
        self.state['idle/output.last'] = QtStateMachine.QHistoryState(self.state['idle/output'])
        self.state['idle/output.last'].setDefaultState(self.state['idle/output.none'])
        self.state['idle/output'].setInitialState(self.state['idle/output.none'])

        self.state['running'] = QtStateMachine.QState(self.machine)

        self.machine.setInitialState(self.state['idle'])

        state = self.state['idle']
        state.assignProperty(self.action['run'], 'visible', True)
        state.assignProperty(self.action['stop'], 'visible', False)
        state.assignProperty(self.action['open'], 'enabled', True)
        state.assignProperty(self.pane['params'], 'enabled', True)

        state = self.state['idle/input.none']
        state.assignProperty(self.action['run'], 'enabled', False)
        state.assignProperty(self.pane['output'], 'visible', False)
        state.assignProperty(self.pane['about'], 'visible', True)

        state = self.state['idle/input.file']
        state.assignProperty(self.action['run'], 'enabled', True)
        state.assignProperty(self.pane['output'], 'visible', True)
        state.assignProperty(self.pane['about'], 'visible', False)

        state = self.state['idle/output.none']
        state.assignProperty(self.action['save'], 'enabled', False)
        tip = 'Hover parameters for tips.'
        state.assignProperty(self.footer, 'text', tip)

        state = self.state['idle/output.failed']
        state.assignProperty(self.action['save'], 'enabled', False)
        tip = 'An error occured, please check the logs for details.'
        state.assignProperty(self.footer, 'text', tip)

        state = self.state['idle/output.complete']
        state.assignProperty(self.action['save'], 'enabled', True)
        tip = 'Tree generation was successful. Click "Save" to save results.'
        state.assignProperty(self.footer, 'text', tip)

        state = self.state['idle/output.outdated']
        state.assignProperty(self.action['save'], 'enabled', True)
        tip = 'Parameters have changed, run again to update results.'
        state.assignProperty(self.footer, 'text', tip)

        state = self.state['running']
        state.assignProperty(self.action['run'], 'visible', False)
        state.assignProperty(self.action['stop'], 'visible', True)
        state.assignProperty(self.action['open'], 'enabled', False)
        state.assignProperty(self.action['save'], 'enabled', False)
        state.assignProperty(self.pane['params'], 'enabled', False)
        tip = 'Generating tree, please wait...'
        state.assignProperty(self.footer, 'text', tip)

        internal = QtStateMachine.QAbstractTransition.TransitionType.InternalTransition

        transition = self.taggedTransition(Action.Update)
        transition.setTransitionType(internal)
        transition.setTargetState(self.state['idle/output.outdated'])
        self.state['idle/output.complete'].addTransition(transition)

        transition = self.taggedTransition(Action.Open)
        transition.setTransitionType(internal)
        def onTransition(event):
            event = common.machine.TaggedEvent(event)
            self.subheader.file.setText(event.kwargs['file'])
            fileInfo = QtCore.QFileInfo(event.kwargs['file'])
            fileName = fileInfo.fileName()
            if len(fileName) > 40:
                fileName = fileName[:37] + '...'
            self.setWindowTitle(self.title + ' - ' + fileName)
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.file'],
            self.state['idle/output.none'],
            ])
        self.state['idle'].addTransition(transition)

        transition = self.taggedTransition(Action.Run)
        transition.setTargetState(self.state['running'])
        self.state['idle'].addTransition(transition)

        transition = self.taggedTransition(Action.Done)
        def onTransition(event):
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setWindowTitle(self.windowTitle())
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Tree generation complete.')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
            self.msgShow(msgBox)
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.complete'],
            ])
        self.state['running'].addTransition(transition)

        transition = self.taggedTransition(Action.Fail)
        def onTransition(event):
            self.fail(event.args[0])
        transition.onTransition = onTransition
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.failed'],
            ])
        self.state['running'].addTransition(transition)

        transition = self.taggedTransition(Action.Cancel)
        transition.setTargetStates([
            self.state['idle/input.last'],
            self.state['idle/output.last'],
            ])
        self.state['running'].addTransition(transition)

        self.machine.start()

    def skin(self):
        """Configure widget appearance"""
        color = {
            'white':  '#ffffff',
            'light':  '#eff1ee',
            'beige':  '#e1e0de',
            'gray':   '#abaaa8',
            'iron':   '#8b8d8a',
            'black':  '#454241',
            'red':    '#ee4e5f',
            'pink':   '#eb9597',
            'orange': '#eb6a4a',
            'brown':  '#655c5d',
            'green':  '#00ff00',
            }
        # using green for debugging
        palette = QtGui.QGuiApplication.palette()
        scheme = {
            QtGui.QPalette.Active: {
                QtGui.QPalette.Window: 'light',
                QtGui.QPalette.WindowText: 'black',
                QtGui.QPalette.Base: 'white',
                QtGui.QPalette.AlternateBase: 'light',
                QtGui.QPalette.PlaceholderText: 'brown',
                QtGui.QPalette.Text: 'black',
                QtGui.QPalette.Button: 'light',
                QtGui.QPalette.ButtonText: 'black',
                QtGui.QPalette.Light: 'white',
                QtGui.QPalette.Midlight: 'beige',
                QtGui.QPalette.Mid: 'gray',
                QtGui.QPalette.Dark: 'iron',
                QtGui.QPalette.Shadow: 'brown',
                QtGui.QPalette.Highlight: 'red',
                QtGui.QPalette.HighlightedText: 'white',
                # These work on linux only?
                QtGui.QPalette.ToolTipBase: 'beige',
                QtGui.QPalette.ToolTipText: 'brown',
                # These seem bugged anyway
                QtGui.QPalette.BrightText: 'green',
                QtGui.QPalette.Link: 'red',
                QtGui.QPalette.LinkVisited: 'pink',
                },
            QtGui.QPalette.Disabled: {
                QtGui.QPalette.Window: 'light',
                QtGui.QPalette.WindowText: 'iron',
                QtGui.QPalette.Base: 'white',
                QtGui.QPalette.AlternateBase: 'light',
                QtGui.QPalette.PlaceholderText: 'green',
                QtGui.QPalette.Text: 'iron',
                QtGui.QPalette.Button: 'light',
                QtGui.QPalette.ButtonText: 'gray',
                QtGui.QPalette.Light: 'white',
                QtGui.QPalette.Midlight: 'beige',
                QtGui.QPalette.Mid: 'gray',
                QtGui.QPalette.Dark: 'iron',
                QtGui.QPalette.Shadow: 'brown',
                QtGui.QPalette.Highlight: 'pink',
                QtGui.QPalette.HighlightedText: 'white',
                # These seem bugged anyway
                QtGui.QPalette.BrightText: 'green',
                QtGui.QPalette.ToolTipBase: 'green',
                QtGui.QPalette.ToolTipText: 'green',
                QtGui.QPalette.Link: 'green',
                QtGui.QPalette.LinkVisited: 'green',
                },
            }
        scheme[QtGui.QPalette.Inactive] = scheme[QtGui.QPalette.Active]
        for group in scheme:
            for role in scheme[group]:
                palette.setColor(group, role,
                    QtGui.QColor(color[scheme[group][role]]))
        QtGui.QGuiApplication.setPalette(palette)

        self.colormap = {
            common.widgets.VectorIcon.Normal: {
                '#000': color['black'],
                '#f00': color['red'],
                },
            common.widgets.VectorIcon.Disabled: {
                '#000': color['gray'],
                '#f00': color['orange'],
                },
            }
        self.colormap_icon = {
            '#000': color['black'],
            '#f00': color['red'],
            '#f88': color['pink'],
            }
        self.colormap_icon_light = {
            '#000': color['iron'],
            '#ff0000': color['red'],
            '#ffa500': color['pink'],
            }

    def draw(self):
        """Draw all widgets"""

        self.header = Header()
        self.header.logoTool = common.widgets.VectorPixmap(
            get_resource('logos/fasttree.svg'),
            colormap=self.colormap_icon)
        self.header.logoProject = QtGui.QPixmap(
            get_resource('logos/itaxotools-micrologo.png'))
        self.header.title = 'FastTree'
        self.header.citation = (
            'by M.N. Price, P.S. Dehal and A.P. Arkin'
            )
        self.header.description = (
            'Infer approximately-maximum-likelihood trees\n'
            'for large multiple sequence alignments'
        )

        self.subheader = common.widgets.Subheader()
        self.subheader.setStyleSheet(self.subheader.styleSheet() +
            """QRadioButton {padding-right: 12px; padding-top: 2px;}""")

        self.subheader.icon = QtWidgets.QLabel()
        self.subheader.icon.setPixmap(common.widgets.VectorPixmap(
            get_icon('arrow-right.svg'),
            colormap=self.colormap_icon_light))
        self.subheader.icon.setStyleSheet('border-style: none;')

        self.subheader.file = QtWidgets.QLineEdit()
        self.subheader.file.setPlaceholderText(
            'Open or drop a file in fasta or interleaved phylip format to begin')
        self.subheader.file.setReadOnly(True)
        self.subheader.file.setStyleSheet("""
            QLineEdit {
                background-color: palette(Base);
                padding: 2px 4px 2px 4px;
                border-radius: 4px;
                border: 1px solid palette(Mid);
                }
            """)

        layout = QtWidgets.QHBoxLayout()
        layout.addSpacing(4)
        layout.addWidget(self.subheader.icon)
        layout.addSpacing(2)
        layout.addWidget(self.subheader.file)
        layout.addSpacing(14)
        layout.setContentsMargins(4, 4, 4, 4)
        self.subheader.setLayout(layout)

        self.pane = {}

        self.paramModel = Model(self.analysis.param)
        self.paramModel.dataChanged.connect(self.handleDataChanged)
        self.paramView = CustomView(self.paramModel)

        self.pane['params'] = common.widgets.Panel(self)
        self.pane['params'].title = 'Parameters'
        self.pane['params'].footer = ''
        self.pane['params'].body.addWidget(self.paramView)
        self.pane['params'].body.setContentsMargins(0, 0, 0, 0)

        self.textLogger = TextEditLogger()
        self.textLogger.document().setDocumentMargin(10)
        self.textLogIO = common.io.TextEditLoggerIO(self.textLogger)

        self.pane['output'] = common.widgets.Panel(self)
        self.pane['output'].title = 'Progress Log'
        self.pane['output'].footer = ''
        self.pane['output'].body.addWidget(self.textLogger)
        self.pane['output'].body.setContentsMargins(0, 0, 0, 0)

        self.textAbout = QtWidgets.QTextBrowser()
        self.textAbout.setOpenExternalLinks(True)
        with open(get_about()) as about:
            self.textAbout.setHtml(about.read())
        self.textAbout.document().setDocumentMargin(10)

        self.pane['about'] = common.widgets.Panel(self)
        self.pane['about'].title = 'About'
        self.pane['about'].footer = ''
        self.pane['about'].body.addWidget(self.textAbout)
        self.pane['about'].body.setContentsMargins(0, 0, 0, 0)

        self.body = QtWidgets.QHBoxLayout()
        self.body.addSpacing(4)
        self.body.addWidget(self.pane['params'], 0)
        self.body.addSpacing(8)
        self.body.addWidget(self.pane['output'], 1)
        self.body.addWidget(self.pane['about'], 1)
        self.body.addSpacing(4)
        # self.body.setContentsMargins(8, 4, 8, 4)

        self.footer = QtWidgets.QLabel()
        self.footer.setStyleSheet("""
            QLabel {
                color: palette(Shadow);
                font-size: 12px;
                background: palette(Window);
                border-top: 1px solid palette(Mid);
                padding: 6px 8px 8px 8px;
                }
            QLabel:disabled {
                color: palette(Mid);
                background: palette(Window);
                border: 1px solid palette(Mid);
                }
            """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.header, 0)
        layout.addWidget(self.subheader, 0)
        layout.addSpacing(8)
        layout.addLayout(self.body, 1)
        layout.addSpacing(8)
        layout.addWidget(self.footer, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def act(self):
        """Populate dialog actions"""
        self.action = {}

        self.action['open'] = QtGui.QAction('&Open', self)
        self.action['open'].setIcon(common.widgets.VectorIcon(get_icon('open.svg'), self.colormap))
        self.action['open'].setShortcut(QtGui.QKeySequence.Open)
        self.action['open'].setStatusTip('Open an existing file')
        self.action['open'].triggered.connect(self.handleOpen)

        self.action['save'] = QtGui.QAction('&Save', self)
        self.action['save'].setIcon(common.widgets.VectorIcon(get_icon('save.svg'), self.colormap))
        self.action['save'].setShortcut(QtGui.QKeySequence.Save)
        self.action['save'].setStatusTip('Save results')
        self.action['save'].triggered.connect(self.handleSave)

        self.action['run'] = QtGui.QAction('&Run', self)
        self.action['run'].setIcon(common.widgets.VectorIcon(get_icon('run.svg'), self.colormap))
        self.action['run'].setShortcut('Ctrl+R')
        self.action['run'].setStatusTip('Align sequences')
        self.action['run'].triggered.connect(self.handleRun)

        self.action['stop'] = QtGui.QAction('&Stop', self)
        self.action['stop'].setIcon(common.widgets.VectorIcon(get_icon('stop.svg'), self.colormap))
        self.action['stop'].setStatusTip('Cancel alignment')
        self.action['stop'].triggered.connect(self.handleStop)

        self.header.toolbar.addAction(self.action['open'])
        self.header.toolbar.addAction(self.action['save'])
        self.header.toolbar.addAction(self.action['run'])
        self.header.toolbar.addAction(self.action['stop'])

    def handleDataChanged(self):
        """Update output state on param update"""
        if self.machine is not None:
            self.postAction(Action.Update)

    def handleRunWork(self):
        """Runs on the Process, defined here for pickability"""
        self.analysis.log = sys.stdout
        self.analysis.run()
        return self.analysis.results

    def handleRun(self):
        """Called by Run button"""
        try:
            self._temp = tempfile.TemporaryDirectory(prefix='fasttreepy_')
            target = pathlib.Path(self._temp.name)
            self.analysis.target = target.as_posix()
            self.analysis.file = self.file
        except Exception as exception:
            self.fail(exception)
            return

        def done(result):
            self.temp = self._temp
            self.analysis.results = result
            with open(self.analysis.fetch()) as output:
                self.textLogger.append(
                    f'\n> Resulting tree: \n\n{output.read()}\n')
            self.postAction(Action.Done, True)

        def fail(exception):
            self.postAction(Action.Fail, exception)

        def error(exitcode):
            self.textLogger.append(
                f'> Internal error: exited with code: {exitcode}\n\n')
            exception = RuntimeError(
                f'Subprocess exited with error code {exitcode}')
            self.postAction(Action.Fail, exception)

        self.process = common.threading.Process(self.handleRunWork)
        self.process.done.connect(done)
        self.process.fail.connect(fail)
        self.process.error.connect(error)
        self.process.setStream(self.textLogIO)
        self.process.start()

        self.postAction(Action.Run)

    def handleStop(self):
        """Called by cancel button"""
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowTitle(self.windowTitle())
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText('Cancel ongoing analysis?')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        confirm = self.msgShow(msgBox)
        if confirm == QtWidgets.QMessageBox.Yes:
            if self.process is not None:
                self.process.quit()
            self.textLogger.append('\n> Interrupted by user\n\n')
            self.postAction(Action.Cancel)

    def handleOpen(self, checked=False, fileName=None):
        """Called by toolbar action"""
        # `checked` kwarg provided by default trigger event
        if fileName is None:
            (fileName, _) = QtWidgets.QFileDialog.getOpenFileName(self,
                self.title + ' - Open File',
                QtCore.QDir.currentPath(),
                'All Files (*)')
        if len(fileName) == 0:
            return
        self.textLogger.clear()
        self.textLogger.append(f'> Now working on file: {fileName}\n\n')
        self.textLogger.append('# You may hover parameters for tips.\n\n')
        self.postAction(Action.Open, file=fileName)
        self.file = fileName

    def handleSave(self):
        """Save latest results"""
        if self.file is not None:
            outName = pathlib.Path(self.file).stem
        else:
            outName = "tree"
        outName += '.tre'
        (fileName, _) = QtWidgets.QFileDialog.getSaveFileName(self,
            self.title + ' - Save Tree',
            QtCore.QDir.currentPath() + '/' + outName,
            'Newick Tree (*.tre)')
        if len(fileName) == 0:
            return
        try:
            source = pathlib.Path(self.analysis.fetch())
            shutil.copyfile(source, fileName)
        except Exception as exception:
            self.fail(exception)
        else:
            self.footer.setText(f'Saved Newick tree to file: {fileName}')
