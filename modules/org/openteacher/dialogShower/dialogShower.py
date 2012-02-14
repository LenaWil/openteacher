#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
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
from PyQt4 import QtCore

class Dialog(QtGui.QWidget):
	buttonClicked = QtCore.pyqtSignal()
	def __init__(self, imagePath, text, redText=False, *args, **kwargs):
		super(Dialog, self).__init__(*args, **kwargs)
		
		frame = QtGui.QFrame()
		frame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
		frame.setMidLineWidth(2)
		frame.setLineWidth(3)
		
		frameLayout = QtGui.QHBoxLayout()
		frameLayout.setAlignment(QtCore.Qt.AlignHCenter)
		
		imageLabel = QtGui.QLabel("<img src=\"" + imagePath + "\" />")
		imageLabel.setAlignment(QtCore.Qt.AlignHCenter)
		frameLayout.addWidget(imageLabel)
		
		textLabel = QtGui.QLabel(text)
		textLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		textLabel.setWordWrap(True)
		textLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		if redText:
			textLabel.setStyleSheet("color: #b60000; font-weight: bold;")
		else:
			textLabel.setStyleSheet("font-weight: bold;")
		frameLayout.addWidget(textLabel)
		
		backButton = QtGui.QPushButton("Close")
		backButton.clicked.connect(lambda: self.buttonClicked.emit())
		frameLayout.addWidget(backButton)
		
		frame.setLayout(frameLayout)
		
		layout = QtGui.QHBoxLayout()
		layout.addWidget(frame)
		self.setLayout(layout)

class BigDialog(QtGui.QWidget):
	def __init__(self, imagePath, text, *args, **kwargs):
		super(BigDialog, self).__init__(*args, **kwargs)
		
		layout = QtGui.QVBoxLayout()
		
		image = QtGui.QPixmap(imagePath)
		imageLabel = QtGui.QLabel()
		imageLabel.setPixmap(image)
		imageLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		layout.addWidget(imageLabel)
		
		textLabel = QtGui.QLabel(text)
		textLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
		textLabel.setWordWrap(True)
		textLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
		layout.addWidget(textLabel)
		
		self.setLayout(layout)

class DialogShower(object):
	def __init__(self, logoImagePath, brokenImagePath, bigLogoImagePath, bigBrokenImagePath, uiModule, *args, **kwargs):
		super(DialogShower, self).__init__(*args, **kwargs)
		
		self.logoImagePath = logoImagePath
		self.brokenImagePath = brokenImagePath
		self.bigLogoImagePath = bigLogoImagePath
		self.bigBrokenImagePath = bigBrokenImagePath
		
		self.uiModule = uiModule
		
	def showError(self, tab, text):
		dialog = Dialog(self.brokenImagePath, text, True)
		self.showDialog(tab, dialog)
	
	def showMessage(self, tab, text):
		dialog = Dialog(self.logoImagePath, text)
		self.showDialog(tab, dialog)
	
	def showBigMessage(self, text):
		dialog = BigDialog(self.bigLogoImagePath, text)
		self.showBigDialog(dialog)
	
	def showBigError(self, text):
		dialog = BigDialog(self.bigBrokenImagePath, text)
		self.showBigDialog(dialog)
	
	def showBigDialog(self, dialog):
		tab = self.uiModule.addCustomTab(dialog)
		tab.closeRequested.handle(tab.close)
	
	def showDialog(self, tab, dialog):
		tabLayout = tab._widget.layout()
				
		# First, remove all other errors if any are there
		for i in xrange(tabLayout.count() - 1):
			it = tabLayout.itemAt(i)
			w = tabLayout.itemAt(i).widget()
			if type(w) == Dialog:
				# Old error is still there, remove it.
				tabLayout.removeItem(it)
				w.setParent(None)
		
		# What happens when you click the button on the dialog
		def removeWidget():
			tabLayout.removeWidget(dialog)
			dialog.setParent(None)
		
		dialog.buttonClicked.connect(lambda: removeWidget())
		
		tabLayout.insertWidget(0, dialog)

class DialogShowerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DialogShowerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "dialogShower"
		
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="event"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		_event = self._modules.default(type="event")
		
		#setup translation
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
		
		logoImagePath = self._mm.resourcePath("images/ot240.png")
		brokenImagePath = self._mm.resourcePath("images/otbroken240.png")
		bigLogoImagePath = self._mm.resourcePath("images/ot2300.png")
		bigBrokenImagePath = self._mm.resourcePath("images/otbroken2300.png")
		
		uiModule = self._modules.default("active", type="ui")
		
		self.dialogShower = DialogShower(logoImagePath, brokenImagePath, bigLogoImagePath, bigBrokenImagePath, uiModule)
		
		self.showError = _event.createEvent()
		self.showMessage = _event.createEvent()
		self.showBigMessage = _event.createEvent()
		self.showBigError = _event.createEvent()
		self.showBigDialog = _event.createEvent()
		self.showDialog = _event.createEvent()
		
		self.showError.handle(self.dialogShower.showError)
		self.showMessage.handle(self.dialogShower.showMessage)
		self.showBigMessage.handle(self.dialogShower.showBigMessage)
		self.showBigError.handle(self.dialogShower.showBigError)
		self.showBigDialog.handle(self.dialogShower.showBigDialog)
		self.showDialog.handle(self.dialogShower.showDialog)
		
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return DialogShowerModule(moduleManager)
