#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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
import urllib2
import urllib
from etree import ElementTree

class VocatrainApi(object):
	"""Public properties:
	    - service. Should be either 'http://vocatrain.com/' or
	      'http://woordjesleren.nl/'. Don't change it while looking up
	      a list, since the id's that are passed to the lookup methods
	      aren't the same anymore after this chagnes.
	"""
	def __init__(self, parseList, *args, **kwargs):
		super(VocatrainApi, self).__init__(*args, **kwargs)

		self.service = "http://vocatrain.com/"
		self._parseList = parseList

	def _open(self, url, **kwargs):
		return urllib2.urlopen(url + "?" + urllib.urlencode(kwargs))

	def getCategories(self):
		fd = self._open(self.service + "api/select_categories.php")
		root = ElementTree.parse(fd).getroot()
		for category in root.findall(".//category"):
			yield (category.text, category.get("id"))

	def getBook(self, categoryId):
		fd = self._open(self.service + "api/select_books.php", category=categoryId)
		root = ElementTree.parse(fd).getroot()
		for book in root.findall(".//book"):
			yield (book.text, book.get("id"))

	def getLists(self, bookId):
		fd = self._open(self.service + "api/select_lists.php", book=bookId)
		root = ElementTree.parse(fd).getroot()
		for list in root.findall(".//list"):
			yield (list.text, list.get("id"))

	def getList(self, listId):
		fd = self._open(self.service + "api/select_list.php", list=listId)
		root = ElementTree.parse(fd).getroot()

		list = root.findtext("list")
		return self._parseList(list)

class Model(QtCore.QAbstractListModel):
	def __init__(self, choices, *args, **kwargs):
		"""Choices should be an iterable object of tuples of size two,
		   with in it first the text to display and second the value to
		   return.

		"""
		super(Model, self).__init__(*args, **kwargs)

		self._choices = list(choices)

	def rowCount(self, parent):
		return len(self._choices)

	def data(self, index, role):
		if not (index.isValid() and role == QtCore.Qt.DisplayRole):
			return

		return self._choices[index.row()][0]

	def getChoice(self, index):
		return self._choices[index.row()][1]

class AbstractSelectDialog(QtGui.QDialog):
	def __init__(self, choices, *args, **kwargs):
		super(AbstractSelectDialog, self).__init__(*args, **kwargs)

		self.label = QtGui.QLabel()

		self._listView = QtGui.QListView()
		self._model = Model(choices)
		self._listView.setModel(self._model)
		self._listView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		self._listView.doubleClicked.connect(self.accept)

		buttonBox = QtGui.QDialogButtonBox(
			QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
			parent=self
		)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		l = QtGui.QVBoxLayout()
		l.addWidget(self.label)
		l.addWidget(self._listView)
		l.addWidget(buttonBox)
		self.setLayout(l)

	@property
	def chosenItems(self):
		return [self._model.getChoice(i) for i in self._listView.selectedIndexes()]

class CategorySelectDialog(AbstractSelectDialog):
	def retranslate(self):
		self.setWindowTitle(_("Select category"))
		self.label.setText(_("Please select a category"))

class BookSelectDialog(AbstractSelectDialog):
	def retranslate(self):
		self.setWindowTitle(_("Select book"))
		self.label.setText(_("Please select a book"))

class ListSelectDialog(AbstractSelectDialog):
	def retranslate(self):
		self.setWindowTitle(_("Select list"))
		self.label.setText(_("Please select a list"))

class VocatrainApiModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(VocatrainApiModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "vocatrainApi"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="buttonRegister"),
			self._mm.mods(type="wordListStringParser"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="loader"),
		)
		self.filesWithTranslations = ("vocatrainApi.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")
		self._buttonRegister = self._modules.default("active", type="buttonRegister")

		self._activeDialogs = set()

		self._enButton = self._buttonRegister.registerButton("load")
		self._enButton.clicked.handle(self.importFromVocatrain)
		#FIXME 3.1: get from self.prioritiies when they're set.
		self._enButton.changePriority.send(210)

		self._nlButton = self._buttonRegister.registerButton("load")
		self._nlButton.clicked.handle(self.importFromWoordjesleren)
		#FIXME 3.1: get from self.prioritiies when they're set.
		self._nlButton.changePriority.send(200)

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		global _
		global ngettext

		#Install translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self._enButton.changeText.send(_("Import from vocatrain.com"))
		self._nlButton.changeText.send(_("Import from woordjesleren.nl"))

		#Translate all active dialogs
		for dialog in self._activeDialogs:
			dialog.retranslate()
			dialog.tab.title = dialog.windowTitle()

	@property
	def _parseList(self):
		return self._modules.default("active", type="wordListStringParser").parseList

	def _showDialog(self, dialog):
		tab = self._uiModule.addCustomTab(dialog)
		tab.closeRequested.handle(tab.close)
		dialog.rejected.connect(tab.close)
		dialog.accepted.connect(tab.close)
		dialog.tab = tab
		self._activeDialogs.add(dialog)

		self._retranslate()
		dialog.exec_()

		self._activeDialogs.remove(dialog)
		return dialog

	def importFromVocatrain(self):
		self._import(VocatrainApi(self._parseList))

	def importFromWoordjesleren(self):
		api = VocatrainApi(self._parseList)
		api.service = "http://woordjesleren.nl/"

		self._import(api)

	def _import(self, api):
		#[5:-1] to strip http:// and the final /
		serviceName = api.service[6:-1]
		try:
			d = self._showDialog(CategorySelectDialog(api.getCategories()))
			if not d:
				return
			for categoryId in d.chosenItems:
				d = self._showDialog(BookSelectDialog(api.getBook(categoryId)))
				if not d:
					continue
				for bookId in d.chosenItems:
					d = self._showDialog(ListSelectDialog(api.getLists(bookId)))
					if not d:
						continue
					for listId in d.chosenItems:
						list = api.getList(listId)
						self._loadList(list)
		except urllib2.URLError, e:
			#for debugging purposes
			print e
			QtGui.QMessageBox.warning(
				self._uiModule.qtParent,
				_("No %s connection") % serviceName,
				_("{serviceName} didn't accept the connection. Are you sure that your internet connection works and {serviceName} is online?").format(serviceName=serviceName)
			)
			return

		#everything went well
		self._uiModule.statusViewer.show(_("The word list was imported from %s successfully.") % serviceName)

	def _loadList(self, list):
		try:
			self._modules.default(
				"active",
				type="loader"
			).loadFromLesson("words", list)
		except NotImplementedError:
			#FIXME 3.1: make this into a separate module? It's shared
			#with plainTextWordsEnterer.
			QtGui.QMessageBox.critical(
				self._uiModule.qtParent,
				_("Can't show the result"),
				_("Can't open the resultive word list, because it can't be shown.")
			)

	def disable(self):
		self.active = False

		self._buttonRegister.unregisterButton(self._enButton)
		self._buttonRegister.unregisterButton(self._nlButton)

		del self._modules
		del self._uiModule
		del self._buttonRegister

		del self._activeDialogs
		del self._enButton
		del self._nlButton

def init(moduleManager):
	return VocatrainApiModule(moduleManager)
