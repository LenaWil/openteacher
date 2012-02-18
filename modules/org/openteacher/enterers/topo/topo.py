#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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
from PyQt4 import QtCore

import os

"""
List widget of all the places
"""
class EnterPlacesWidget(QtGui.QListWidget):
	def __init__(self, enterWidget, *args, **kwargs):
		super(EnterPlacesWidget, self).__init__(*args, **kwargs)
		
		self.enterWidget = enterWidget
	
	def update(self):
		self.clear()
		
		# Add all the places to the list
		for place in self.enterWidget.list["items"]:
			self.addItem(place["name"] + " (" + unicode(place["x"]) + "," + unicode(place["y"]) + ")")

"""
The dropdown menu for choosing the map
"""
class EnterMapChooser(QtGui.QComboBox):
	def __init__(self, parent, mapWidget, *args, **kwargs):
		super(EnterMapChooser, self).__init__(*args, **kwargs)
		
		self.mapWidget = mapWidget
		self.enterWidget = parent
		
		# Ask if user wants to remove added places when changing map
		self.ask = True
		
		# Fill the MapChooser with the maps
		self._fillBox()
		# Change the map
		self._otherMap()
		
		self.currentIndexChanged.connect(self._otherMap)

	def _fillBox(self):
		for module in base._modules.sort("active", type="map"):
			self.addItem(module.mapName, unicode({'mapName': module.mapName, 'mapPath': module.mapPath, 'knownPlaces': module.knownPlaces}))
		
		self.addItem("From hard disk...", unicode({}))
		
	def _otherMap(self):
		if self.ask:
			if len(self.enterWidget.list["items"]) > 0:
				warningD = QtGui.QMessageBox()
				warningD.setIcon(QtGui.QMessageBox.Warning)
				warningD.setWindowTitle(_("Warning"))
				warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
				warningD.setText(_("Are you sure you want to use another map? This will remove all your places!"))
				feedback = warningD.exec_()
				if feedback != QtGui.QMessageBox.Ok:
					self.ask = False
					self.setCurrentIndex(self.prevIndex)
					return
			if self.currentMap == {}:
				_uiModule = set(base._mm.mods("active", type="ui")).pop()
				path = _uiModule.getLoadPath(
					QtCore.QDir.homePath(),
					["gif", "jpg", "jpeg", "png", "bmp", "svg"]
				)
				if path:
					name = os.path.splitext(os.path.basename(path))[0]
					
					self.setCurrentIndex(0)
					self.insertItem(0, name, unicode({'mapPath': path, 'knownPlaces': ''}))
					self.setCurrentIndex(0)
			elif len(self.enterWidget.list["items"]) > 0 and self.ask:
				# Clear the entered items
				self.enterWidget.list = {
					"items": list(),
					"tests": list()
				}
				# Update the list
				self.enterWidget.currentPlaces.update()
				self.mapWidget.setMap(self.currentMap["mapPath"])
				self.enterWidget.addPlaceEdit.updateKnownPlaces(self.currentMap["knownPlaces"])
				self.prevIndex = self.currentIndex()
			else:
				self.mapWidget.setMap(self.currentMap["mapPath"])
				self.enterWidget.addPlaceEdit.updateKnownPlaces(self.currentMap["knownPlaces"])
				self.prevIndex = self.currentIndex()
		else:
			self.ask = True
	
	@property
	def currentMap(self):
		return eval(unicode(self.itemData(self.currentIndex()).toString()))

"""
The add-place-by-name edit
"""
class EnterPlaceByName(QtGui.QLineEdit):
	def __init__(self, *args, **kwargs):
		super(EnterPlaceByName, self).__init__(*args, **kwargs)
	
	"""
	Gets list of names from the knownPlaces dict list
	"""
	def _getNames(self, list):
		feedback = []
		for item in list:
			for name in item["names"]:
				feedback.append(name)
		return feedback
	
	"""
	Updates the list of names
	"""
	def updateKnownPlaces(self, knownPlaces):
		self.completer = QtGui.QCompleter(self._getNames(knownPlaces))
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.setCompleter(self.completer)

class DummyLesson(object):
	pass

"""
The enter tab
"""
class EnterWidget(QtGui.QSplitter):
	def __init__(self, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		#self.places = List()
		self.list = {
			"items": list(),
			"tests": list()
		}
		self.lesson = DummyLesson()
		
		#create the GUI
		self.addPlaceEdit = EnterPlaceByName()
		
		#left side
		leftSide = QtGui.QVBoxLayout()
		
		#left side - top
		mapLabel = QtGui.QLabel(_("Map:"))
		
		#left side - middle
		self.enterMap = base._modules.default("active", type="topoMaps").getEnterMap(self)
		
		#left side - top
		self.mapChooser = EnterMapChooser(self, self.enterMap)
		
		chooseMap = QtGui.QHBoxLayout()
		chooseMap.addWidget(mapLabel)
		chooseMap.addWidget(self.mapChooser)
		
		#left side - bottom
		explanationLabel = QtGui.QLabel(_("Add a place by doubleclicking it on the map"))
		
		#left side
		leftSide.addLayout(chooseMap)
		leftSide.addWidget(self.enterMap)
		leftSide.addWidget(explanationLabel)
		
		#right side
		rightSide = QtGui.QVBoxLayout()
		
		#right side - top
		placesLabel = QtGui.QLabel(_("Places in your test"))
		
		removePlace = QtGui.QPushButton(_("Remove selected place"))
		removePlace.clicked.connect(self.removePlace)
		
		rightTop = QtGui.QHBoxLayout()
		rightTop.addWidget(placesLabel)
		rightTop.addWidget(removePlace)
		
		#right side - middle
		self.currentPlaces = EnterPlacesWidget(self)
		
		#right side - bottom
		addPlace = QtGui.QHBoxLayout()
		
		addPlaceName = QtGui.QLabel(_("Add a place by name:"))
		
		addPlaceButton = QtGui.QPushButton(_("Add"))
		
		addPlaceButton.clicked.connect(lambda: self.addPlaceByName(self.addPlaceEdit.text()))
		self.addPlaceEdit.returnPressed.connect(lambda: self.addPlaceByName(self.addPlaceEdit.text()))
		
		addPlace.addWidget(self.addPlaceEdit)
		addPlace.addWidget(addPlaceButton)
		
		#right side
		rightSide.addLayout(rightTop)
		rightSide.addWidget(self.currentPlaces)
		rightSide.addWidget(addPlaceName)
		rightSide.addLayout(addPlace)
		
		#total layout
		leftSideWidget = QtGui.QWidget()
		leftSideWidget.setLayout(leftSide)
		rightSideWidget = QtGui.QWidget()
		rightSideWidget.setLayout(rightSide)
		
		self.addWidget(leftSideWidget)
		self.addWidget(rightSideWidget)
	
	"""
	Updates the widgets on the EnterWidget after the list of places has changed
	"""
	def updateWidgets(self):
		self.enterMap.update()
		self.currentPlaces.update()
	
	"""
	Add a place to the list
	"""
	def addPlace(self,place):
		self.list["items"].append(place)
		self.lesson.changed = True
		self.updateWidgets()
	
	"""
	Add a place by looking at the list of known places
	"""
	def addPlaceByName(self, name):
		for placeDict in self.mapChooser.currentMap["knownPlaces"]:
			if name in placeDict["names"]:
				try:
					id = self.list["items"][-1]["id"] + 1
				except IndexError:
					id = 0
				self.list["items"].append({
					"name": unicode(name),
					"x": placeDict["x"],
					"y": placeDict["y"],
					"id": id
				})
				self.updateWidgets()
				return
		else:
			QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Place not found", "Sorry, this place is not in the list of known places. Please add it manually by doubleclicking on the right location in the map.").exec_()
		
		self.addPlaceEdit.setText("")
		self.addPlaceEdit.setFocus()

		self.lesson.changed = True
		
	"""
	Remove a place from the list
	"""
	def removePlace(self):
		for placeItem in self.currentPlaces.selectedItems():
			for place in self.list["items"]:
				if placeItem.text() == unicode(place["name"] + " (" + unicode(place["x"]) + "," + unicode(place["y"]) + ")"):
					self.list["items"].remove(place)
			self.lesson.changed = True
		self.updateWidgets()

class TopoEntererModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TopoEntererModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		
		self._mm = moduleManager
		
		self.type = "topoEnterer"
		self.priorities = {
			"student@home": 640,
			"student@school": 640,
			"teacher": 640,
			"wordsonly": -1,
			"selfstudy": 640,
			"testsuite": 640,
			"codedocumentation": 640,
			"all": 640,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="topoMaps"),
			self._mm.mods(type="ui"),
		)
	
	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.active = True
		
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
	
	def disable(self):
		self.active = False
	
	def createTopoEnterer(self):
		return EnterWidget()

def init(moduleManager):
	return TopoEntererModule(moduleManager)
