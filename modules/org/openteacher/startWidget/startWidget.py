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
import weakref

class StartWidgetButton(QtGui.QPushButton):
	def __init__(self, *args, **kwargs):
		super(StartWidgetButton, self).__init__(*args, **kwargs)
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
		super(StartWidgetButton, self).setText(result)
		super(StartWidgetButton, self).resizeEvent(*args, **kwargs)

#FIXME: give this class an implementation that doesn't suck. Also, make
#sure that the priority event of the buttons is handled and that button
#register users actually send it... (just the module priority is
#sufficient, there.)
class StartWidget(QtGui.QSplitter):
	def __init__(self, recentlyOpenedViewer, *args, **kwargs):
		super(StartWidget, self).__init__(*args, **kwargs)

		self._buttons = {}

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

		self.retranslate()

	def retranslate(self):
		self.createLessonGroupBox.setTitle(_("Create lesson:"))
		self.loadLessonGroupBox.setTitle(_("Load lesson:"))
		try:
			self.recentlyOpenedGroupBox.setTitle(_("Recently opened:"))
		except AttributeError:
			pass

	def addButton(self, button):
		if button.category == "create":
			qtButton = self._addLessonCreateButton()
		elif button.category == "load":
			qtButton = self._addLessonLoadButton()
		self._buttons[button] = qtButton
		qtButton.clicked.connect(lambda: button.clicked.send())
		button.changeText.handle(qtButton.setText)
		button.changeIcon.handle(lambda i: qtButton.setIcon(QtGui.QIcon(i)))

	def removeButton(self, button):
		if button.category == "create":
			self._removeLessonCreateButton(self._buttons[button])
		elif button.category == "load":
			self._removeLessonLoadButton(self._buttons[button])

	def _addLessonCreateButton(self):
		button = StartWidgetButton()

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

	def _addLessonLoadButton(self):
		button = StartWidgetButton()

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

	def _removeLessonCreateButton(self, button):
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

	def _removeLessonLoadButton(self, button):
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

class StartWidgetModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(StartWidgetModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "startWidget"

		self.requires = (
			self._mm.mods(type="buttonRegister"),
		)
		self.uses = (
			self._mm.mods(type="recentlyOpenedViewer"),
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("startWidget.py",)

	def createStartWidget(self):
		"""By calling this method, you need to be able to guarantee that
		   there's already a QApplication active. E.g. by depending on
		   'ui', or by being the module that manages the QApplication...

		"""
		try:
			recentlyOpenedViewer = self._modules.default(
				"active",
				type="recentlyOpenedViewer"
			).createViewer()
		except IndexError:
			recentlyOpenedViewer = None
		widget = StartWidget(recentlyOpenedViewer)

		self._register.addButton.handle(widget.addButton)
		self._register.removeButton.handle(widget.removeButton)

		self._activeWidgets.add(weakref.ref(widget))
		return widget

	def _retranslate(self):
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		for ref in self._activeWidgets:
			widget = ref()
			if widget is not None:
				widget.retranslate()

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._register = self._modules.default("active", type="buttonRegister")

		self._activeWidgets = set()

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._register
		del self._activeWidgets

def init(moduleManager):
	return StartWidgetModule(moduleManager)
