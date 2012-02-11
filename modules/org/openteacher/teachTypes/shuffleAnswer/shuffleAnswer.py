#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
#	Copyright 2011, Marten de Vries
#	Copyright 2011, Milan Boers
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

from PyQt4 import QtGui, QtCore
import random
import weakref

class ShuffleAnswerTeachWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShuffleAnswerTeachWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		try:
			typingInput = self._modules.default("active", type="typingInput")
		except IndexError, e:
			raise e #FIXME: what to do?
		else:
			self.inputWidget = typingInput.createWidget()
		
		vbox = QtGui.QVBoxLayout()
		self.hintLabel = QtGui.QLabel()
		vbox.addWidget(self.hintLabel)
		vbox.addWidget(self.inputWidget)
		self.setLayout(vbox)

	def retranslate(self):
		try:
			self.setHint()
		except AttributeError:
			pass

	def setHint(self):
		hint = _("Hint:") + u" "
		answer = self.word["answers"][0][0]#FIXME: use composer
		if len(answer) != 1:
			while True:
				hintList = list(answer)
				random.shuffle(hintList)
				if hintList != list(answer):
					hint += u"".join(hintList)
					break
				else:
					continue
		else:
			hint += u"."
		self.hintLabel.setText(hint)

	def updateLessonType(self, lessonType, *args, **kwargs):
		self.inputWidget.updateLessonType(lessonType, *args, **kwargs)

		lessonType.newItem.handle(self.newWord)

	def newWord(self, word):
		self.word = word
		self.setHint()

class ShuffleAnswerTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShuffleAnswerTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "teachType"
		self.priorities = {
			"student@home": 558,
			"student@school": 558,
			"teacher": 558,
			"wordsonly": 558,
			"selfstudy": 558,
			"testsuite": 558,
			"codedocumentation": 558,
			"all": 558,
		}
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="typingInput"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._activeWidgets = set()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.dataType = "words"
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._activeWidgets
		del self.dataType
		del self.name

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
		self.name = _("Shuffle answer")
		for widget in self._activeWidgets:
			r = widget()
			if r is not None:
				r.retranslate()

	def createWidget(self, tabChanged):
		satw = ShuffleAnswerTeachWidget(self._mm) #FIXME: get rid of the mm here, just pass the widget
		self._activeWidgets.add(weakref.ref(satw))
		return satw

def init(moduleManager):
	return ShuffleAnswerTeachTypeModule(moduleManager)
