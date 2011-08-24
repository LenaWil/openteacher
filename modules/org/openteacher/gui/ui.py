#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
import os

class CloseButton(QtGui.QAbstractButton):
	def __init__(self, *args, **kwargs):
		super(CloseButton, self).__init__(*args, **kwargs)
		
		self.setFocusPolicy(QtCore.Qt.NoFocus)
		self.setCursor(QtCore.Qt.ArrowCursor)
		self.setToolTip(_("Close Tab"))
		self.resize(self.sizeHint())

	def sizeHint(self):
		self.ensurePolished()
		width = self.style().pixelMetric(QtGui.QStyle.PM_TabCloseIndicatorWidth, None, self)
		height = self.style().pixelMetric(QtGui.QStyle.PM_TabCloseIndicatorHeight, None, self)
		return QtCore.QSize(width, height)

	def enterEvent(self, *args, **kwargs):
		if self.isEnabled():
			self.update()
		super(CloseButton, self).enterEvent(*args, **kwargs)

	def leaveEvent(self, *args, **kwargs):
		if self.isEnabled():
			self.update()
		super(CloseButton, self).leaveEvent(*args, **kwargs)

	def paintEvent(self, event):
		p = QtGui.QPainter(self)
		opt = QtGui.QStyleOption()
		opt.initFrom(self)
		opt.state = opt.state | QtGui.QStyle.State_AutoRaise
		if self.isEnabled() and self.underMouse() and not self.isChecked() and not self.isDown():
			opt.state = opt.state | QtGui.QStyle.State_Raised
		if self.isChecked():
			opt.state = opt.state | QtGui.QStyle.State_On
		if self.isDown():
			opt.state = opt.state | QtGui.QStyle.State_Sunken

		tb = self.parent()

		if tb.__class__ == QtGui.QTabBar:
			index = tb.currentIndex()
			position = self.style().styleHint(QtGui.QStyle.SH_TabBar_CloseButtonPosition, None, tb)

			if tb.tabButton(index, position) == self:
				opt.state = opt.state | QtGui.QStyle.State_Selected

		self.style().drawPrimitive(QtGui.QStyle.PE_IndicatorTabClose, opt, p, self)

class LessonTabWidget(QtGui.QTabWidget):
	def __init__(self, enterWidget, teachWidget, resultsWidget, *args, **kwargs):
		super(LessonTabWidget, self).__init__(*args, **kwargs)

		if enterWidget:
			self.addTab(enterWidget, _("Enter list"))
		if teachWidget:
			self.addTab(teachWidget, _("Teach me!"))
		if resultsWidget:
			self.addTab(resultsWidget, _("Show results"))

		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

class StartTabButton(QtGui.QPushButton):
	def __init__(self, icon=None, text=u"", *args, **kwargs):
		super(StartTabButton, self).__init__(icon, u"", *args, **kwargs)
		self.setText(text)

		self.setSizePolicy(
			QtGui.QSizePolicy.MinimumExpanding,
			QtGui.QSizePolicy.MinimumExpanding
		)

	def setText(self, text):
		self._text = text
		self._cache = {}

	def sizeHint(self):
		fm = self.fontMetrics()
		width = max(map(fm.width, self._text.split(" "))) +20 #+20 to let it look nice
		height = fm.height() * len(self._splitLines().split("\n")) +10 #+10 to let it look nice

		return QtCore.QSize(width, height)

	def _splitLines(self):
		fm = self.fontMetrics()
		result = u""
		curLine = u""
		words = unicode(self._text).split(u" ")
		w = self.width()
		try:
			return self._cache[w]
		except KeyError:
			pass
		i = 0
		while True:
			try:
				word = words[i]
			except IndexError:
				break
			if not curLine and fm.width(word) >= w:
				result += u"\n" + word
				i += 1
			elif fm.width(curLine + " " + word) >= w:
				result += u"\n" + curLine
				curLine = u""
			else:
				curLine += u" " + word
				i += 1
		result += "\n" + curLine
		result = result.strip()
		self._cache[w] = result
		return result

	def resizeEvent(self, e):
		result = self._splitLines()
		super(StartTabButton, self).setText(result)

class StartWidget(QtGui.QSplitter):
	def __init__(self, *args, **kwargs):
		super(StartWidget, self).__init__(*args, **kwargs)

		self._createLessonCurrentRow = 0
		self._createLessonCurrentColumn = 0

		self._loadLessonCurrentRow = 0
		self._loadLessonCurrentColumn = 0

		self.createLessonLayout = QtGui.QGridLayout()

		createLessonGroupBox = QtGui.QGroupBox(_("Create lesson:"))
		createLessonGroupBox.setLayout(self.createLessonLayout)

		self.loadLessonLayout = QtGui.QGridLayout()

		loadLessonGroupBox = QtGui.QGroupBox(_("Load lesson:"))
		loadLessonGroupBox.setLayout(self.loadLessonLayout)

		openLayout = QtGui.QVBoxLayout()
		openLayout.addWidget(createLessonGroupBox)
		openLayout.addWidget(loadLessonGroupBox)

		openWidget= QtGui.QWidget(self)
		openWidget.setLayout(openLayout)

		recentlyOpenedListView = QtGui.QListView()
		recentlyOpenedListView.setModel(QtGui.QStringListModel([
			"French (words)",
			"Europe (topo)",
			"Exam German (text)"
		], self))

		recentlyOpenedLayout = QtGui.QVBoxLayout()
		recentlyOpenedLayout.addWidget(recentlyOpenedListView)

		recentlyOpenedGridBox = QtGui.QGroupBox(_("Recently opened:"))
		recentlyOpenedGridBox.setLayout(recentlyOpenedLayout)

		self.addWidget(openWidget)
		self.addWidget(recentlyOpenedGridBox)

	def addLessonCreateButton(self, text, icon=QtGui.QIcon()):
		button = StartTabButton(icon, text, self)

		self.createLessonLayout.addWidget(
			button,
			self._createLessonCurrentRow,
			self._createLessonCurrentColumn
		)

		self._createLessonCurrentColumn += 1
		if self._createLessonCurrentColumn == 2:
			self._createLessonCurrentRow += 1
			self._createLessonCurrentColumn = 0

		return button

	def addLessonLoadButton(self, text, icon=QtGui.QIcon()):
		button = StartTabButton(icon, text, self)

		self.loadLessonLayout.addWidget(
			button,
			self._loadLessonCurrentRow,
			self._loadLessonCurrentColumn
		)

		self._loadLessonCurrentColumn += 1
		if self._loadLessonCurrentColumn == 2:
			self._loadLessonCurrentRow += 1
			self._loadLessonCurrentColumn = 0

		return button

class FilesTabWidget(QtGui.QTabWidget):
	def __init__(self, *args, **kwargs):
		super(FilesTabWidget, self).__init__(*args, **kwargs)

		self.indexes = []

		self.startWidget = StartWidget(self)
		super(FilesTabWidget, self).addTab(
			self.startWidget,
			QtGui.QIcon.fromTheme("add",
				QtGui.QIcon(ICON_PATH + "add.png"),
			),
			""
		) # super because our method does add a close button

		self.setDocumentMode(True)

	def addTab(self, *args, **kwargs):
		return self.insertTab(self.count() -1, *args, **kwargs) #-1 because of +-tab

	def insertTab(self, *args, **kwargs):
		#create tab
		i = super(FilesTabWidget, self).insertTab(*args, **kwargs)
		
		#add close button
		closeButton = CloseButton()
		self.tabBar().setTabButton(i, QtGui.QTabBar.RightSide, closeButton)

		#set new tab to current
		self.setCurrentIndex(i)

		return i

class OpenTeacherWidget(QtGui.QMainWindow):
	activityChanged = QtCore.pyqtSignal([object])
	def __init__(self, *args, **kwargs):
		super(OpenTeacherWidget, self).__init__(*args, **kwargs)

		self.resize(640, 480)

		#tabWidget
		self.tabWidget = FilesTabWidget(self)
		self.setCentralWidget(self.tabWidget)

		#File menu
		fileMenu = self.menuBar().addMenu(_("&File"))

		self.newAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("filenew",
				QtGui.QIcon(ICON_PATH + "new.png"),
			),
			_("&New")
		)
		self.newAction.setShortcut(QtGui.QKeySequence(_("Ctrl+N")))

		self.openAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("fileopen",
				QtGui.QIcon(ICON_PATH + "open.png")
			),
			_("&Open")
		)
		self.openAction.setShortcut(QtGui.QKeySequence(_("Ctrl+O")))

		fileMenu.addSeparator()

		self.saveAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("filesave",
				QtGui.QIcon(ICON_PATH + "save.png")
			),
			_("&Save")
		)
		self.saveAction.setShortcut(QtGui.QKeySequence(_("Ctrl+S")))

		self.saveAsAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("filesaveas",
				QtGui.QIcon(ICON_PATH + "save_as.png"),
			),
			_("Save &As")
		)
		self.saveAsAction.setShortcut(QtGui.QKeySequence(_("Ctrl+Shift+S")))

		fileMenu.addSeparator()

		self.printAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("fileprint",
				QtGui.QIcon(ICON_PATH + "print.png")
			),
			_("&Print")
		)
		self.printAction.setShortcut(QtGui.QKeySequence(_("Ctrl+P")))

		fileMenu.addSeparator()

		self.quitAction = fileMenu.addAction(
			QtGui.QIcon.fromTheme("exit",
				QtGui.QIcon(ICON_PATH + "quit.png")
			),
			_("&Quit")
		)
		self.quitAction.setShortcut(QtGui.QKeySequence(_("Ctrl+Q")))

		#Edit
		editMenu = self.menuBar().addMenu(_("&Edit"))
		self.settingsAction = editMenu.addAction(
			QtGui.QIcon(ICON_PATH + "settings.png"),
			_("&Settings")
		)

		#Help
		helpMenu = self.menuBar().addMenu(_("&Help"))

		self.docsAction = helpMenu.addAction(
			QtGui.QIcon.fromTheme("help",
				QtGui.QIcon(ICON_PATH + "help.png")
			),
			_("&Documentation")
		)
		self.aboutAction = helpMenu.addAction(
			QtGui.QIcon(ICON_PATH + "about.png"),
			_("&About")
		)

		#Toolbar
		toolBar = self.addToolBar(_("Toolbar"))
		toolBar.addAction(self.newAction)
		toolBar.addAction(self.openAction)
		toolBar.addSeparator()
		toolBar.addAction(self.saveAction)
		toolBar.addAction(self.saveAsAction)
		toolBar.addSeparator()
		toolBar.addAction(self.printAction)
		toolBar.addSeparator()
		toolBar.addAction(self.quitAction)

		toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

		#activate statusBar
		self.statusBar()

	def changeEvent(self, event):
		if event.type() == QtCore.QEvent.ActivationChange:
			self.activityChanged.emit(self.isActiveWindow())

class ItemChooser(QtGui.QDialog):#FIXME
	def __init__(self, items, *args, **kwargs):
		super(ItemChooser, self).__init__(*args, **kwargs)
		
		vbox = QtGui.QVBoxLayout()
		
		self.dict = {}
		for item in items:
			self.dict[str(item)] = item

		for item in self.dict:
			button = QtGui.QPushButton(item)
			button.clicked.connect(self.buttonClicked)
			vbox.addWidget(button)
		self.setLayout(vbox)

	def buttonClicked(self):
		key = str(self.sender().text())
		self.item = self.dict[key]
		self.accept()
