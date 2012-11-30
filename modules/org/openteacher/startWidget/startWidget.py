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

import weakref

def getStartWidgetButton():
	class StartWidgetButton(QtGui.QPushButton):
		def __init__(self, *args, **kwargs):
			super(StartWidgetButton, self).__init__(*args, **kwargs)
			#our setText is reimplemented, the QPushButton constructor
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
	return StartWidgetButton

def getButtonsGroupBox():
	class ButtonsGroupBox(QtGui.QGroupBox):
		def __init__(self, *args, **kwargs):
			super(ButtonsGroupBox, self).__init__(*args, **kwargs)

			self._buttons = {}
			self._layout = QtGui.QGridLayout()
			self.setLayout(self._layout)

		def _updateLayout(self):
			#empty layout
			while True:
				item = self._layout.takeAt(0)
				if not item:
					break
				item.widget().setParent(None)
			i = 0
			j = 0
			for button, desc in sorted(self._buttons.iteritems(), key=lambda data: data[1]["priority"]):
				qtButton = StartWidgetButton(desc["text"])
				qtButton.setIcon(QtGui.QIcon(desc["icon"]))
				#lambda to remove some qt argument. The second lambda so it
				#works as expected in a for-loop.
				qtButton.clicked.connect(
					(lambda button: lambda: button.clicked.send())(button)
				)
				self._layout.addWidget(qtButton, i, j)
				j += 1
				if j > 1:
					j = 0
					i += 1

		def addButton(self, button):
			self._buttons[button] = {
				"text": "",
				"icon": "",
				"priority": 0,
			}
			button.changeText.handle(lambda t: self._updateText(button, t))
			button.changeIcon.handle(lambda i: self._updateIcon(button, i))
			button.changePriority.handle(lambda p: self._updatePriority(button, p))
			self._updateLayout()

		def removeButton(self, button):
			del self._buttons[button]
			self._updateLayout()

		def _updateText(self, button, text):
			self._buttons[button]["text"] = text
			self._updateLayout()

		def _updateIcon(self, button, icon):
			self._buttons[button]["icon"] = icon
			self._updateLayout()

		def _updatePriority(self, button, priority):
			self._buttons[button]["priority"] = priority
			self._updateLayout()

	return ButtonsGroupBox

def getStartWidget():
	class StartWidget(QtGui.QSplitter):
		def __init__(self, recentlyOpenedViewer, *args, **kwargs):
			super(StartWidget, self).__init__(*args, **kwargs)

			self.createLessonGroupBox = ButtonsGroupBox()
			self.loadLessonGroupBox = ButtonsGroupBox()

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
				self.createLessonGroupBox.addButton(button)
			elif button.category == "load":
				self.loadLessonGroupBox.addButton(button)

		def removeButton(self, button):
			if button.category == "create":
				self.createLessonGroupBox.removeButton(button)
			elif button.category == "load":
				self.loadLessonGroupBox.removeButton(button)
	return StartWidget

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
		global QtCore, QtGui
		try:
			from PyQt4 import QtCore, QtGui
		except ImportError:
			return
		global ButtonsGroupBox, StartWidget, StartWidgetButton
		ButtonsGroupBox = getButtonsGroupBox()
		StartWidget = getStartWidget()
		StartWidgetButton = getStartWidgetButton()

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
