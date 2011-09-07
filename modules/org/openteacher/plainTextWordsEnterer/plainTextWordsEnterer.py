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

from PyQt4 import QtGui

class EnterPlainTextDialog(QtGui.QDialog):
	def __init__(self, parse, *args, **kwargs):
		super(EnterPlainTextDialog, self).__init__(*args, **kwargs)

		self._parse = parse

		buttonBox = QtGui.QDialogButtonBox(
			QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
			parent=self
		)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		label = QtGui.QLabel(_("Please enter the plain text in the text edit. Separate words with a new line and questions from answers with an equals sign ('=') or a tab."))
		label.setWordWrap(True)
		self._textEdit = QtGui.QTextEdit()

		layout = QtGui.QVBoxLayout()
		layout.addWidget(label)
		layout.addWidget(self._textEdit)
		layout.addWidget(buttonBox)
		self.setLayout(layout)

		self.setWindowTitle(_("Plain text words enterer"))

	def exec_(self, *args, **kwargs):
		self._textEdit.setFocus()

		super(EnterPlainTextDialog, self).exec_(*args, **kwargs)

	@property
	def list(self):
		list = {"items": [], "tests": []}
		text = unicode(self._textEdit.toPlainText())
		counter = 0
		for line in text.split("\n"):
			try:
				questionText, answerText = line.split("=")
			except ValueError:
				try:
					questionText, answerText = line.split("\t")
				except ValueError:
					continue
			word = {
				"id": counter,
				"questions": self._parse(questionText),
				"answers": self._parse(answerText),
			}	
			list["items"].append(word)

			counter += 1
		return list

class PlainTextWordsEntererModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PlainTextWordsEntererModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "plainTextWordsEnterer"
		self.requires = (
			(
				("active",),
				{"type": "ui"},
			),
			(
				("active",),
				{"type": "wordsStringParser"},
			),
			(
				("active",),
				{"type": "loader"},
			),
		)
		self.uses = (
			(
				("active",),
				{"type": "translator"},
			),
		)

	def enable(self):
		self._references = set()

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")

		#load translator
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

		self.name = _("Plain text words enterer")

		event = self._uiModule.addLessonCreateButton(_("Create words lesson by entering plain text"))
		event.handle(self.createLesson)
		self._references.add(event)

		self.active = True

	def createLesson(self):
		parse = self._modules.default(
			"active",
			type="wordsStringParser"
		).parse

		eptd = EnterPlainTextDialog(parse)
		tab = self._uiModule.addCustomTab(eptd.windowTitle(), eptd)
		tab.closeRequested.handle(tab.close)
		eptd.rejected.connect(tab.close)
		eptd.accepted.connect(tab.close)

		eptd.exec_()
		if not eptd.result():
			return

		self._modules.default(
			"active",
			type="loader"
		).loadFromList("words", eptd.list)

	def disable(self):
		self.active = False

		del self._references
		del self._modules
		del self._uiModule
		del self.name
		#remove create lesson button

def init(moduleManager):
	return PlainTextWordsEntererModule(moduleManager)
