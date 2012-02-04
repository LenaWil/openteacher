#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

#INFO: ICON_PATH is set by gui.py . Set it yourself when re-using this
#code in another context.

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
	def __init__(self, *args, **kwargs):
		super(StartTabButton, self).__init__(*args, **kwargs)
		#our setText is reimplemented and the QPushButton constructor
		#doesn't call setText by default.
		self.setText(self.text())

		self.setSizePolicy(
			QtGui.QSizePolicy.MinimumExpanding,
			QtGui.QSizePolicy.MinimumExpanding
		)

	def setText(self, text):
		self._text = text
		self._cache = {}

	def sizeHint(self):
		fm = self.fontMetrics()
		width = max(map(fm.width, self._text.split(" "))) + 20 #+20 to keep margin
		height = fm.height() * len(self._splitLines().split("\n")) +10 #+10 to keep margin

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
			if not curLine and fm.width(" " + word) >= w:
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

	def resizeEvent(self, *args, **kwargs):
		result = self._splitLines()
		super(StartTabButton, self).setText(result)
		super(StartTabButton, self).resizeEvent(*args, **kwargs)

class StartWidget(QtGui.QSplitter):
	def __init__(self, recentlyOpenedViewer, *args, **kwargs):
		super(StartWidget, self).__init__(*args, **kwargs)

		self._createLessonCurrentRow = 0
		self._createLessonCurrentColumn = 0

		self._loadLessonCurrentRow = 0
		self._loadLessonCurrentColumn = 0

		self.createLessonLayout = QtGui.QGridLayout()

		self.createLessonGroupBox = QtGui.QGroupBox()
		self.createLessonGroupBox.setLayout(self.createLessonLayout)

		self.loadLessonLayout = QtGui.QGridLayout()

		self.loadLessonGroupBox = QtGui.QGroupBox()
		self.loadLessonGroupBox.setLayout(self.loadLessonLayout)

		openLayout = QtGui.QVBoxLayout()
		openLayout.addWidget(self.createLessonGroupBox)
		openLayout.addWidget(self.loadLessonGroupBox)

		left = self.style().pixelMetric(QtGui.QStyle.PM_LayoutLeftMargin)
		openLayout.setContentsMargins(left, 0, 0, 0)

		openWidget = QtGui.QWidget(self)
		openWidget.setLayout(openLayout)

		self.addWidget(openWidget)

		self.setStretchFactor(0, 7)

		if recentlyOpenedViewer:
			recentlyOpenedLayout = QtGui.QVBoxLayout()

			right = self.style().pixelMetric(QtGui.QStyle.PM_LayoutRightMargin)
			recentlyOpenedLayout.setContentsMargins(0, 0, 0, 0)
			recentlyOpenedLayout.addWidget(recentlyOpenedViewer)

			self.recentlyOpenedGroupBox = QtGui.QGroupBox()
			self.recentlyOpenedGroupBox.setLayout(recentlyOpenedLayout)

			self.addWidget(self.recentlyOpenedGroupBox)
			self.setStretchFactor(1, 2)

	def retranslate(self):
		self.createLessonGroupBox.setTitle(_("Create lesson:"))
		self.loadLessonGroupBox.setTitle(_("Load lesson:"))
		self.recentlyOpenedGroupBox.setTitle(_("Recently opened:"))

	def addLessonCreateButton(self):
		button = StartTabButton()

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

	def addLessonLoadButton(self):
		button = StartTabButton()

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

	def removeLessonCreateButton(self, button):
		i = self.createLessonLayout.indexOf(button)
		row, column = self.createLessonLayout.getItemPosition(i)[:2]

		self.createLessonLayout.removeWidget(button)
		prevColumn = column
		column += 1
		if column == 2:
			column = 0
			row += 1
		while row != self.createLessonLayout.rowCount():
			item = self.createLessonLayout.itemAtPosition(row, column)
			self.createLessonLayout.addItem(item, row, column)
			prevColumn = column
			column += 1
			if column == 2:
				column = 0
				row += 1

		self._createLessonCurrentColumn -= 1
		if self._createLessonCurrentColumn == 0:
			self._createLessonCurrentRow -= 1
			self._createLessonCurrentColumn = 1

	def removeLessonLoadButton(self, button):
		i = self.loadLessonLayout.indexOf(button)
		row, column = self.createLessonLayout.getItemPosition(i)[:2]

		self.loadLessonLayout.removeWidget(button)
		button.setParent(None)
		prevColumn = column
		column += 1
		if column == 2:
			column = 0
			row += 1
		while True:
			item = self.loadLessonLayout.itemAtPosition(row, column)
			if not item:
				break
			self.loadLessonLayout.addItem(item, row, column)
			prevColumn = column
			column += 1
			if column == 2:
				column = 0
				row += 1

		self._loadLessonCurrentColumn -= 1
		if self._loadLessonCurrentColumn == 0:
			self._loadLessonCurrentRow -= 1
			self._loadLessonCurrentColumn = 1

class FilesTabWidget(QtGui.QTabWidget):
	def __init__(self, recentlyOpenedViewer, *args, **kwargs):
		super(FilesTabWidget, self).__init__(*args, **kwargs)

		self.startWidget = StartWidget(recentlyOpenedViewer, self)
		
		super(FilesTabWidget, self).addTab(
			self.startWidget,
			QtGui.QIcon.fromTheme("add",
				QtGui.QIcon(ICON_PATH + "add.png"),
			),
			""
		) # super because our method does add a close button

		self.setDocumentMode(True)

	def addTab(self, w, *args, **kwargs):
		w.setAutoFillBackground(True)
		return self.insertTab(self.count() -1, w, *args, **kwargs) #-1 because of +-tab

	def insertTab(self, *args, **kwargs):
		#create tab
		i = super(FilesTabWidget, self).insertTab(*args, **kwargs)
		
		#add close button
		closeButton = CloseButton()
		self.tabBar().setTabButton(i, QtGui.QTabBar.RightSide, closeButton)

		#set new tab to current
		self.setCurrentIndex(i)

		return i

	def retranslate(self):
		self.startWidget.retranslate()

class OpenTeacherWidget(QtGui.QMainWindow):
	activityChanged = QtCore.pyqtSignal([object])

	def __init__(self, recentlyOpenedViewer=None, aeroSetting=False, *args, **kwargs):
		super(OpenTeacherWidget, self).__init__(*args, **kwargs)

		self.resize(640, 480)

		#tabWidget
		self.tabWidget = FilesTabWidget(recentlyOpenedViewer, self)
		
		self.setCentralWidget(self.tabWidget)

		#File menu
		self.fileMenu = self.menuBar().addMenu("")
		
		self.newAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("filenew",
				QtGui.QIcon(ICON_PATH + "new.png"),
			),
			""
		)
		self.newAction.setShortcut(QtGui.QKeySequence.New)

		self.openAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("fileopen",
				QtGui.QIcon(ICON_PATH + "open.png")
			),
			""
		)
		self.openAction.setShortcut(QtGui.QKeySequence.Open)

		self.fileMenu.addSeparator()

		self.saveAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("filesave",
				QtGui.QIcon(ICON_PATH + "save.png")
			),
			""
		)
		self.saveAction.setShortcut(QtGui.QKeySequence.Save)

		self.saveAsAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("filesaveas",
				QtGui.QIcon(ICON_PATH + "save_as.png"),
			),
			""
		)
		self.saveAsAction.setShortcut(QtGui.QKeySequence.SaveAs)

		self.fileMenu.addSeparator()

		self.printAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("fileprint",
				QtGui.QIcon(ICON_PATH + "print.png")
			),
			""
		)
		self.printAction.setShortcut(QtGui.QKeySequence.Print)

		self.fileMenu.addSeparator()

		self.quitAction = self.fileMenu.addAction(
			QtGui.QIcon.fromTheme("exit",
				QtGui.QIcon(ICON_PATH + "quit.png")
			),
			""
		)
		self.quitAction.setShortcut(QtGui.QKeySequence.Quit)
		
		#Edit
		self.editMenu = self.menuBar().addMenu("")
		self.settingsAction = self.editMenu.addAction(
			QtGui.QIcon(ICON_PATH + "settings.png"),
			""
		)

		#Help
		self.helpMenu = self.menuBar().addMenu("")

		self.docsAction = self.helpMenu.addAction(
			QtGui.QIcon.fromTheme("help",
				QtGui.QIcon(ICON_PATH + "help.png")
			),
			""
		)
		self.aboutAction = self.helpMenu.addAction(
			QtGui.QIcon(ICON_PATH + "about.png"),
			""
		)

		#Toolbar
		self.toolBar = self.addToolBar("")
		self.toolBar.addAction(self.newAction)
		self.toolBar.addAction(self.openAction)
		self.toolBar.addSeparator()
		self.toolBar.addAction(self.saveAction)
		self.toolBar.addAction(self.saveAsAction)
		self.toolBar.addSeparator()
		self.toolBar.addAction(self.printAction)
		self.toolBar.addSeparator()
		self.toolBar.addAction(self.quitAction)

		self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

		#activate statusBar
		self.statusBar()
		
		# Aero glass
		if aeroSetting:
			self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
			pal = self.palette()
			bg = pal.window().color()
			bg.setAlpha(230)
			pal.setColor(QtGui.QPalette.Window, bg)
			self.setPalette(pal)
			from ctypes import windll, c_int, byref
			windll.dwmapi.DwmExtendFrameIntoClientArea(c_int(self.winId()), byref(c_int(-1)))
			# Refill status bar
			self.statusBar().setAutoFillBackground(True)
			# Remove borders from toolbar
			self.toolBar.setStyleSheet("border: 0;")
			# Make menu bar transparent
			self.menuBar().setStyleSheet("QMenuBar { background-color:transparent; } QMenuBar::item { background-color: transparent; }")

	def retranslate(self):
		self.fileMenu.setTitle(_("&File"))
		self.newAction.setText(_("&New"))
		self.openAction.setText(_("&Open"))
		self.saveAction.setText(_("&Save"))
		self.saveAsAction.setText(_("Save &As"))
		self.printAction.setText(_("&Print"))
		self.quitAction.setText(_("&Quit"))

		self.editMenu.setTitle(_("&Edit"))
		self.settingsAction.setText(_("&Settings"))

		self.helpMenu.setTitle(_("&Help"))
		self.docsAction.setText(_("&Documentation"))
		self.aboutAction.setText(_("&About"))

		self.toolBar.setWindowTitle(_("Toolbar"))

		self.tabWidget.retranslate()

	def changeEvent(self, event):
		if event.type() == QtCore.QEvent.ActivationChange:
			self.activityChanged.emit(self.isActiveWindow())
