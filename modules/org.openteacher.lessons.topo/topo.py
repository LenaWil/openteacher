#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2008-2011, Milan Boers
#
#    This file is part of OpenTeacher.
#
#    OpenTeacher is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenTeacher is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.


from PyQt4 import QtGui
from PyQt4 import QtCore

import os
import time

class Order:
	Normal, Inversed = xrange(2)

class Result(str):
	def __init__(self, *args, **kwargs):
		super(Result, self).__init__(*args, **kwargs)
		
		self.itemId = int()
		
		#optional
		self.active = list()

class List(object):
	def __init__(self, *args, **kwargs):
		super(List, self).__init__(*args, **kwargs)
		
		self.items = []
		self.tests = []

"""
Place in the test
"""
class Place(object):
	def __init__(self, name = "None", x = 0, y = 0, *args, **kwargs):
		super(Place, self).__init__(*args, **kwargs)
		
		self.name = name
		
		# Position on the map
		if x > 0 and y > 0:
			self.x = int(x)
			self.y = int(y)

"""
List widget of all the places
"""
class EnterPlacesWidget(QtGui.QListWidget):
	def __init__(self, *args, **kwargs):
		super(EnterPlacesWidget, self).__init__(*args, **kwargs)
	
	def update(self):
		self.clear()
		
		# Add all the places to the list
		for place in base.enterWidget.places.items:
			self.addItem(place.name + " (" + str(place.x) + "," + str(place.y) + ")")

"""
The graphics scene of the map where you enter
"""
class EnterMapScene(QtGui.QGraphicsScene):
	def __init__(self, parent, *args, **kwargs):
		super(EnterMapScene, self).__init__(*args, **kwargs)
		self.widget = parent
	
	def mouseDoubleClickEvent(self,gsme):
		# Get coordinates
		x = gsme.lastScenePos().x()
		y = gsme.lastScenePos().y()
		# If its in the map
		if x > 0 and y > 0:
			# Ask for the name
			name = QtGui.QInputDialog.getText(self.widget, "Name for this place", "What's this place's name?")
			if name[1] and str(name[0]).strip() != "":
				# Make the place
				place = Place(name[0], x, y)
				# And add the place
				base.enterWidget.addPlace(place)

"""
Abstract class for the map widgets
"""
class Map(QtGui.QGraphicsView):
	def __init__(self,*args, **kwargs):
		super(Map, self).__init__(*args, **kwargs)
	
	def setMap(self, map):
		mapsPath = base.api.resourcePath("resources/maps")
		picturePath = os.path.join(mapsPath, unicode(map + ".gif"))
		self._setPicture(picturePath)
	
	def _setPicture(self,picture):
		# Create a new scene
		self.scene = QtGui.QGraphicsScene()
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	def wheelEvent(self,wheelevent):
		# Scrolling makes it zoom
		if wheelevent.delta() > 0:
			self.scale(1.1,1.1)
		else:
			self.scale(0.9,0.9)

"""
The map on the enter tab
"""
class EnterMap(Map):
	def __init__(self, *args, **kwargs):
		super(EnterMap, self).__init__(*args, **kwargs)
		# Make it scrollable and draggable
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		
		self.placesGroup = QtGui.QGraphicsItemGroup()
	
	"""
	Override base class _setPicture with one that uses an EnterMapScene instead of QGraphicsScene
	"""
	def _setPicture(self, picture):
		# Create a new scene
		self.scene = EnterMapScene(self)
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	def update(self):		
		placesList = []
		
		# Add all the places
		for place in base.enterWidget.places.items:
			# Make the little rectangle
			rect = QtGui.QGraphicsRectItem(place.x,place.y,6,6)
			rect.setBrush(QtGui.QBrush(QtGui.QColor("red")))
			# Place the rectangle in the list of items
			placesList.append(rect)
			
			# Make the shadow of the text
			shadow = QtGui.QGraphicsTextItem(place.name)
			shadow.setFont(QtGui.QFont("sans-serif",15,75))
			shadow.setPos(place.x+2,place.y+2)
			shadow.setDefaultTextColor(QtGui.QColor("black"))
			shadow.setOpacity(0.5)
			# Place the shadow in the list of items
			placesList.append(shadow)
			
			item = QtGui.QGraphicsTextItem(place.name)
			item.setFont(QtGui.QFont("sans-serif",15,75))
			item.setPos(place.x,place.y)
			item.setDefaultTextColor(QtGui.QColor("red"))
			# Place the text in the list of items
			placesList.append(item)
		
		# Place the list of items on the map
		self.placesGroup = self.scene.createItemGroup(placesList)

"""
The dropdown menu for choosing the map
"""
class EnterMapChooser(QtGui.QComboBox):
	def __init__(self, parent, mapWidget, *args, **kwargs):
		super(EnterMapChooser, self).__init__(*args, **kwargs)
		
		self.mapWidget = mapWidget
		self.enterWidget = parent
		
		# Fill the MapChooser with the maps
		self._fillBox()
		# Change the map
		self._otherMap()
		
		self.currentIndexChanged.connect(self._otherMap)

	def _fillBox(self):
		mapPaths = base.api.resourcePath("resources/maps")
		for name in os.listdir(mapPaths):
			self.addItem(os.path.splitext(name)[0], name)
	
	def _otherMap(self):
		if len(self.enterWidget.places.items) > 0:
			warningD = QtGui.QMessageBox()
			warningD.setIcon(QtGui.QMessageBox.Warning)
			warningD.setWindowTitle("Warning")
			warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
			warningD.setText("Are you sure you want to use another map? This will remove all your places!")
			feedback = warningD.exec_()
			if feedback == QtGui.QMessageBox.Ok:
				# Clear the entered items
				self.enterWidget.places = List()
				# Update the list
				self.enterWidget.currentPlaces.update()
			else:
				self.ask = False
				self.setCurrentIndex(self.prevIndex)
				return
		self.mapWidget.setMap(self.currentText())
		self.prevIndex = self.currentIndex()

"""
The enter tab
"""
class EnterWidget(QtGui.QSplitter):
	def __init__(self, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self.places = List()
		
		#create the GUI
		
		#left side
		leftSide = QtGui.QVBoxLayout()
		
		#left side - top
		mapLabel = QtGui.QLabel("Map:")
		
		#left side - middle
		self.pictureBox = EnterMap()
		
		#left side - top
		self.mapChooser = EnterMapChooser(self, self.pictureBox)
		
		chooseMap = QtGui.QHBoxLayout()
		chooseMap.addWidget(mapLabel)
		chooseMap.addWidget(self.mapChooser)
		
		#left side - bottom
		explanationLabel = QtGui.QLabel("Add a place by doubleclicking it on the map")
		
		#left side
		leftSide.addLayout(chooseMap)
		leftSide.addWidget(self.pictureBox)
		leftSide.addWidget(explanationLabel)
		
		#right side
		rightSide = QtGui.QVBoxLayout()
		
		#right side - top
		placesLabel = QtGui.QLabel("Places in your test")
		
		removePlace = QtGui.QPushButton("Remove selected place")
		removePlace.clicked.connect(self.removePlace)
		
		rightTop = QtGui.QHBoxLayout()
		rightTop.addWidget(placesLabel)
		rightTop.addWidget(removePlace)
		
		#right side - middle
		self.currentPlaces = EnterPlacesWidget()
		
		#right side - bottom
		addPlace = QtGui.QHBoxLayout()
		
		addPlaceName = QtGui.QLabel("Add a place by name:")
		
		addPlaceEdit = QtGui.QLineEdit()
		addPlaceButton = QtGui.QPushButton("Add")
		
		addPlace.addWidget(addPlaceEdit)
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
	Add a place to the list
	"""
	def addPlace(self,place):
		self.places.items.append(place)
		self.pictureBox.update()
		self.currentPlaces.update()
	
	"""
	Remove a place from the list
	"""
	def removePlace(self):
		for placeItem in self.currentPlaces.selectedItems():
			for place in self.places.items:
				if placeItem.text() == str(place.name + " (" + str(place.x) + "," + str(place.y) + ")"):
					self.places.items.remove(place)
		self.pictureBox.update()
		self.currentPlaces.update()
	
	"""
	What happens when you click the Enter tab
	"""
	def showEvent(self, event):
		if base.inLesson:
			warningD = QtGui.QMessageBox()
			warningD.setIcon(QtGui.QMessageBox.Warning)
			warningD.setWindowTitle("Warning")
			warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
			warningD.setText("Are you sure you want to go back to the teach tab? This will end your lesson!")
			feedback = warningD.exec_()
			if feedback == QtGui.QMessageBox.Ok:
				base.teachWidget.stopLesson()
			else:
				base.fileTab.currentTab = base.teachWidget

"""
The dropdown menu to choose lesson type
"""
class LessonTypeChooser(QtGui.QComboBox):
	def __init__(self, *args, **kwargs):
		super(LessonTypeChooser, self).__init__(*args, **kwargs)
		
		self.currentIndexChanged.connect(self.changeLessonType)
		
		self._lessonTypeModules = list(
			base.api.mods("active", type="lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	"""
	What happens when you change the lesson type
	"""
	def changeLessonType(self, index):
		if base.inLesson:
			base.teachWidget.initiateLesson()
	
	"""
	Get the current lesson type
	"""
	@property
	def currentLessonType(self):
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype

"""
The dropdown menu to choose lesson order
"""
class LessonOrderChooser(QtGui.QComboBox):
	def __init__(self, *args, **kwargs):
		super(LessonOrderChooser, self).__init__(*args, **kwargs)
		
		self.currentIndexChanged.connect(self.changeLessonOrder)
		
		self.addItem("Place - Name", 0)
		self.addItem("Name - Place", 1)
	
	"""
	What happens when you change the lesson order
	"""
	def changeLessonOrder(self, index):
		if base.inLesson:
			base.teachWidget.initiateLesson()

"""
A place on the map for the inverted order
"""
class PlaceOnMap(QtGui.QGraphicsRectItem):
	def __init__(self, place, *args, **kwargs):
		super(PlaceOnMap, self).__init__(*args, **kwargs)
		
		width = 10
		height = 10
		
		self.setRect(place.x - width / 2, place.y - height / 2, width, height)
		self.setBrush(QtGui.QBrush(QtGui.QColor("red")))
		
		self.place = place

"""
Scene for the TeachPictureMap
"""
class TeachPictureScene(QtGui.QGraphicsScene):
	def __init__(self, *args, **kwargs):
		super(TeachPictureScene, self).__init__(*args, **kwargs)
	
	def mouseReleaseEvent(self, event):
		clickedObject = self.itemAt(event.lastScenePos().x(), event.lastScenePos().y())
		if clickedObject.__class__ == PlaceOnMap:
			base.teachWidget.lesson.checkAnswer(clickedObject.place)

"""
The map on the teach tab
"""
class TeachPictureMap(Map):
	def __init__(self, map, *args, **kwargs):
		super(TeachPictureMap, self).__init__(*args, **kwargs)
		# Not interactive
		self.interactive = False
		# Make sure everything is redrawn every time
		self.setViewportUpdateMode(0)
	
	"""
	Sets the arrow on the map to the right position
	"""
	def setArrow(self, x, y):
		self.centerOn(x-15,y-50)
		self.crosshair.setPos(x-15,y-50)
	
	"""
	Removes the arrow
	"""
	def removeArrow(self):
		self.scene.removeItem(self.crosshair)
	
	"""
	Overriding the base class _setPicture method with one using the TeachPictureScene
	"""
	def _setPicture(self,picture):
		# Create a new scene
		self.scene = TeachPictureScene()
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	"""
	Shows all the places without names
	"""
	def showPlaceRects(self):
		placesList = []
		
		for place in base.enterWidget.places.items:
			# Make the little rectangle
			rect = PlaceOnMap(place)
			# Place the rectangle in the list of items
			placesList.append(rect)
		
		self.placesGroup = self.scene.createItemGroup(placesList)
	
	def hidePlaceRects(self):
		try:
			for item in self.placesList:
				self.removeItem(item)
		except AttributeError:
			pass
	
	def setInteractive(self, val):
		if val:
			self.showPlaceRects()
			# Interactive
			self.interactive = True
			# Scrollbars
			self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
			self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
			self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		else:
			self.hidePlaceRects()
			# Not interactive
			self.interactive = False
			# No scrollbars
			self.setDragMode(QtGui.QGraphicsView.NoDrag)
			self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
			self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
			# Arrow
			crosshairPixmap = QtGui.QPixmap(base.api.resourcePath("resources/crosshair.png"))
			self.crosshair = QtGui.QGraphicsPixmapItem(crosshairPixmap)
			
			self.scene.addItem(self.crosshair)

"""
The teach tab
"""
class TeachWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		## GUI Drawing
		# Top
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Lesson type:")
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		label = QtGui.QLabel("Lesson order:")
		self.lessonOrderChooser = LessonOrderChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonOrderChooser)
		
		# Middle
		self.mapBox = TeachPictureMap(base.enterWidget.mapChooser.currentText())
		
		# Bottom
		bottom = QtGui.QHBoxLayout()
		
		self.label = QtGui.QLabel("Which place is here?")
		self.answerfield = QtGui.QLineEdit()
		self.checkanswerbutton = QtGui.QPushButton("Check")
		self.answerfield.returnPressed.connect(self.checkAnswerButtonClick)
		self.checkanswerbutton.clicked.connect(self.checkAnswerButtonClick)
		
		self.questionLabel = QtGui.QLabel("Please click this place:")
		
		self.progress = QtGui.QProgressBar()
		
		bottom.addWidget(self.label)
		bottom.addWidget(self.answerfield)
		bottom.addWidget(self.checkanswerbutton)
		bottom.addWidget(self.questionLabel)
		bottom.addWidget(self.progress)
		
		# Total
		layout = QtGui.QVBoxLayout()
		layout.addLayout(top)
		layout.addWidget(self.mapBox)
		layout.addLayout(bottom)
		
		self.setLayout(layout)
	
	"""
	Starts the lesson
	"""
	def initiateLesson(self):
		self.lesson = TopoLesson(base.enterWidget.places)
		self.answerfield.setFocus()
	
	"""
	Stops the lesson
	"""
	def stopLesson(self):
		self.lesson.endLesson()
		del self.lesson
	
	"""
	What happens when you click the check answer button
	"""
	def checkAnswerButtonClick(self):
		# Check the answer
		self.lesson.checkAnswer()
		# Clear the answer field
		self.answerfield.clear()
		# Focus the answer field
		self.answerfield.setFocus()
	
	"""
	What happens when you click the Teach tab
	"""
	def showEvent(self,event):
		# If there are no words
		if len(base.enterWidget.places.items) == 0:
			QtGui.QMessageBox.critical(self, "Not enough items", "You need to add items to your test first")
			base.fileTab.currentTab = base.enterWidget
		# If not in a lesson (so it doesn't start a lesson if you go back from a mistakingly click on the Enter tab)
		elif not base.inLesson:
			self.initiateLesson()
	
	"""
	Sets the bottom widgets to either the in-order version (False) or the inversed-order (True)
	"""
	def setWidgets(self, order):
		if order == Order.Inversed:
			self.label.setVisible(False)
			self.answerfield.setVisible(False)
			self.checkanswerbutton.setVisible(False)
			self.questionLabel.setVisible(True)
		else:
			self.label.setVisible(True)
			self.answerfield.setVisible(True)
			self.checkanswerbutton.setVisible(True)
			self.questionLabel.setVisible(False)

"""
The lesson itself
"""
class TopoLesson(object):
	def __init__(self, itemList, *args, **kwargs):
		super(TopoLesson, self).__init__(*args, **kwargs)
		# Set the map
		base.teachWidget.mapBox.setMap(base.enterWidget.mapChooser.currentText())
		base.teachWidget.mapBox.setInteractive(self.order)
		
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(itemList,range(len(itemList.items)))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(base.teachWidget.stopLesson)
		
		self.lessonType.start()
		
		base.inLesson = True
		
		# Reset the progress bar
		base.teachWidget.progress.setValue(0)
		
		base.teachWidget.setWidgets(self.order)
	
	"""
	Check whether the given answer was right or wrong
	"""
	def checkAnswer(self, answer=None):
		if self.order == Order.Inversed:
			if self.currentItem == answer:
				# Answer was right
				self.lessonType.setResult(Result("right"))
				# Progress bar
				self._updateProgressBar()
			else:
				# Answer was wrong
				self.lessonType.setResult(Result("wrong"))
		else:
			if self.currentItem.name == base.teachWidget.answerfield.text():
				# Answer was right
				self.lessonType.setResult(Result("right"))
				# Progress bar
				self._updateProgressBar()
			else:
				# Answer was wrong
				self.lessonType.setResult(Result("wrong"))
			
	"""
	What happens when the next question should be asked
	"""
	def nextQuestion(self, item):
		#set the next question
		self.currentItem = item
		if self.order == Order.Inversed:
			#set the question
			base.teachWidget.questionLabel.setText("Please click this place: " + self.currentItem.name)
		else:
			#set the arrow to the right position
			base.teachWidget.mapBox.setArrow(self.currentItem.x,self.currentItem.y)
	
	"""
	Ends the lesson
	"""
	def endLesson(self):
		base.inLesson = False
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		base.teachWidget.progress.setValue(self.lessonType.askedItems)
	
	@property
	def order(self):
		return base.teachWidget.lessonOrderChooser.currentIndex()

"""
The module
"""
class TopoLessonModule(object):
	def __init__(self, api, *args, **kwargs):
		super(TopoLessonModule, self).__init__(*args, **kwargs)
		global base
		base = self
		self.api = api
		self.counter = 1
		self.inLesson = False
		
		self.type = "lesson"

	def enable(self):
		for module in self.api.mods("active", type="modules"):
			module.registerModule("Topo Lesson", self)

		self.dataType = "places"
		
		self.lessonCreated = self.api.createEvent()
		self.lessonCreationFinished = self.api.createEvent()
		
		for module in self.api.mods("active", type="ui"):
			event = module.addLessonCreateButton("Create topography lesson")
			event.handle(self.createLesson)
		
		self.active = True

	def disable(self):
		del self.dataType
		del self.lessonCreated
		del self.lessonCreationFinished
		self.active = False
	
	def createLesson(self):		
		lessons = set()
		
		for module in self.api.mods("active", type="ui"):
			self.enterWidget = EnterWidget()
			self.teachWidget = TeachWidget()
			
			self.fileTab = module.addFileTab(
				"Topo lesson %s" % self.counter,
				self.enterWidget,
				self.teachWidget
			)
			
			lesson = Lesson(self, self.fileTab, self.enterWidget, self.teachWidget)
			self.lessonCreated.emit(lesson)
			
			lessons.add(lesson)
		self.counter += 1
		self.lessonCreationFinished.emit()
		return lessons

class Lesson(object):
	def __init__(self, moduleManager, fileTab, enterWidget, teachWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		self.fileTab = fileTab
		self.stopped = base.api.createEvent()
		
		fileTab.closeRequested.handle(self.stop)
	
	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

def init(moduleManager):
	return TopoLessonModule(moduleManager)
