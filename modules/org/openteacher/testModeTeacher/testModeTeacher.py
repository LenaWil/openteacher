#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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

from PyQt4 import QtCore
from PyQt4 import QtGui

import copy

class TeachWidget(QtGui.QWidget):
	lessonDone = QtCore.pyqtSignal()
	listChanged = QtCore.pyqtSignal([object])
	def __init__(self, moduleManager, keyboardWidget, applicationActivityChanged, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._composer = self._modules.default("active", type="wordsStringComposer")
		
		layout = QtGui.QVBoxLayout()
		
		self.title = QtGui.QLabel()
		self.title.setStyleSheet("font-size: 18px;")
		layout.addWidget(self.title)
		
		scrollArea = QtGui.QScrollArea()
		#questionsWidget = QtGui.QWidget()
		self.questions = QtGui.QFormLayout()
		#questionsWidget.setLayout(self.questions)
		scrollArea.setLayout(self.questions)
		
		layout.addWidget(scrollArea)
		
		handInButton = QtGui.QPushButton("Hand in answers")
		handInButton.clicked.connect(self.lessonDone.emit)
		layout.addWidget(handInButton)
		
		self.setLayout(layout)
		
	def updateList(self, list):
		self.list = list
	
	def showEvent(self, event):
		# Set title
		self.title.setText(self.list["title"])
		
		self.answerWidgets = []
		
		for item in self.list["items"]:
			answerWidget = QtGui.QLineEdit()
			self.questions.addRow(self._composer.compose(item["questions"]), answerWidget)
			self.answerWidgets.append(answerWidget)
	
	def getAnsweredList(self):
		# Make copy of list
		answeredList = copy.copy(self.list)
		
		# Iterate through the answer widgets
		i = 0;
		for answerWidget in self.answerWidgets:
			self.list["items"][i]["answer"] = unicode(answerWidget.text())
			
			i += 1
		
		return answeredList

class TestModeTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeTeacherModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsTestTeacher"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
		)

	def createWordsTeacher(self):
		tw = TeachWidget(self._mm, self._onscreenKeyboard, self._applicationActivityChanged)
		#self._activeWidgets.add(weakref.ref(tw))
		self._retranslate()

		return tw

	@property
	def _onscreenKeyboard(self):
		try:
			return self._modules.default(
				"active",
				type="onscreenKeyboard"
			).createWidget()
		except IndexError:
			return

	@property
	def _applicationActivityChanged(self):
		uiModule = set(self._mm.mods("active", type="ui")).pop()
		return uiModule.applicationActivityChanged

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		#self._activeWidgets = set()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#Translations
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

		#for widget in self._activeWidgets:
		#	r = widget()
		#	if r is not None:
		#		r.retranslate()

	def disable(self):
		self.active = False

		del self._modules
		#del self._activeWidgets

def init(moduleManager):
	return TestModeTeacherModule(moduleManager)