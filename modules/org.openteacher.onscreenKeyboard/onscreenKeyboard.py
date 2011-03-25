#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
#	Copyright 2008-2011, Milan Boers
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

DIACRITIC_CHARS = (
	(u"à", u"á", u"â", u"ä", u"ã", u"å"),
	(u"À", u"Á", u"Â", u"Ä", u"Ã", u"Å"),
	(u"è", u"é", u"ê", u"ë", u"Ç", u"ç"),
	(u"È", u"É", u"Ê", u"Ë", u"Ñ", u"ñ"),
	(u"ì", u"ì", u"î", u"ï", u"Û", u"û"),
	(u"Ì", u"Í", u"Î", u"Ï", u"Ú", u"ú"),
	(u"ò", u"ó", u"ô", u"ö", u"Ü", u"ü"),
	(u"Ò", u"Ó", u"Ô", u"Ö", u"Ù", u"ß")
)

GREEK_CHARS = (
	(u"α", u"β", u"γ", u"Γ", u"δ", u"Δ"),
	(u"ε", u"Ε", u"ζ", u"η", u"Η", u"θ"),
	(u"Θ", u"ι", u"Ι", u"κ", u"λ", u"Λ"),
	(u"μ", u"ν", u"ξ", u"Ξ", u"ο", u"Ο"),
	(u"π", u"Π", u"ρ", u"σ", u"Σ", u"τ"),
	(u"υ", u"φ", u"Φ", u"χ", u"Χ", u"ψ"),
	(u"Ψ", u"ω", u"Ω", u"", u"", u"")
)

class CharactersTableModel(QtCore.QAbstractTableModel):
	"""This class is a tableModel, which means it can be used in a
	   QTableView. (What happens in OpenTeacher.)

	   Properties:
	   - characters - a list of lists of characters
	   - readOnly - if true, the model doesn't accept edits."""
	def __init__(self, characters, readOnly=True, *args, **kwargs):
		super(CharactersTableModel, self).__init__(*args, **kwargs)

		#Set the characters inside the model.
		self.characters = map(list, characters)
		self.readOnly = readOnly

	def headerData(self, column, orientation, role):
		"""Returns the headers to the tableView"""
		if role == QtCore.Qt.DisplayRole:
			return unicode(column +1)
		else:
			return

	def rowCount(self, parent=None):
		"""Returns the amount of character rows"""
		return len(self.characters)

	def columnCount(self, parent=None):
		"""Returns the length of the first character row. (and should be equal to the length of all rows!)"""
		try:
			return len(self.characters[0])
		except IndexError:
			return 0

	def data(self, index, role=QtCore.Qt.DisplayRole):
		"""Returns the character for a specified position (index)."""
		if index.isValid() and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole):
			return self.characters[index.row()][index.column()]
	
	def setData(self, index, value, role):
		"""Does the same as data(), but now it saves instead of returns."""
		letter = unicode(value.toString())
		#Only save when not readOnly, valid index, and when a character (len=1)
		if index.isValid() and role == QtCore.Qt.EditRole and len(letter) == 1 and not self.readOnly:
			self.characters[index.row()][index.column()] = letter
			return True
		return False

	def flags(self, index):
		"""Return flags for the specified index. Returns baseflags, and in addition the
		ItemIsEditable-flag when the model's read-only property isn't true."""
		baseflags = super(CharactersTableModel, self).flags(index)
		if self.readOnly:
			return baseflags
		else:
			return baseflags | QtCore.Qt.ItemIsEditable

class OnscreenKeyboardWidget(QtGui.QTableView):
	def __init__(self, manager, characters, *args,  **kwargs):
		super(OnscreenKeyboardWidget, self).__init__(*args, **kwargs)

		self.manager = manager
		self._model = CharactersTableModel(characters)
		self.setModel(self._model)

	def setModel(self, *args, **kwargs):
		super(OnscreenKeyboardWidget, self).setModel(*args, **kwargs)

		self.resizeColumnsToContents()
		self.resizeRowsToContents()

		hheader = self.horizontalHeader()
		vheader = self.verticalHeader()
		charWidth = vheader.sizeHint().width() + hheader.length()
		charHeight = hheader.sizeHint().height() + vheader.length()
		self.setMinimumSize(charWidth, charHeight)

		self.clicked.connect(self.indexClicked)
		
		self.letterChosen = self.manager.createEvent()

	def indexClicked(self, index):
		letter = self._model.data(index)
		self.letterChosen.emit(letter)

class OnscreenKeyboardModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(OnscreenKeyboardModule, self).__init__(*args, **kwargs)

		self.manager = manager
		self.supports = (
			"onscreen_keyboard",
			"greek_onscreen_keyboard",
			"diacritic_onscreen_keyboard"
		)
		self.requires = (1, 0)

	def enable(self): pass #FIXME
	def disable(self): pass #FIXME

	def getWidget(self, characters):
		return OnscreenKeyboardWidget(self.manager, characters)

	def getGreekWidget(self):
		return OnscreenKeyboardWidget(self.manager, GREEK_CHARS)

	def getDiacriticWidget(self):
		return OnscreenKeyboardWidget(self.manager, DIACRITIC_CHARS)

def init(manager):
	return OnscreenKeyboardModule(manager)
