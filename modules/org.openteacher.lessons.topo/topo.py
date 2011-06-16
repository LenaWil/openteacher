#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2008-2011, Milan Boers
#    Copyright 2009-2011, Marten de Vries
#    Copyright 2008, Roel Huybrechts
#    Copyright 2010-2011, Cas Widdershoven
#    Copyright 2010, David D. Lowe
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

class Place(object):
	def __init__(self, name = "None", x = 0, y = 0):
		self.name = name
		if x > 0 and y > 0:
			self.x = int(x)
			self.y = int(y)

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

class EnterPlacesWidget(QtGui.QListWidget):
	def __init__(self):
		QtGui.QListWidget.__init__(self)
	
	def update(self):
		self.clear()
		for place in base.enterWidget.places.items:
			self.addItem(place.name + " (" + str(place.x) + "," + str(place.y) + ")")

class EnterMapScene(QtGui.QGraphicsScene):
	def __init__(self,parent):
		QtGui.QGraphicsScene.__init__(self,parent)
		self.parent = parent
	
	def mouseDoubleClickEvent(self,gsme):
		x = gsme.lastScenePos().x()
		y = gsme.lastScenePos().y()
		if x > 0 and y > 0:
			self.controlPressed = False
			name = QtGui.QInputDialog.getText(self.parent, "Name for this place", "What's this place's name?")
			if name[1] and str(name[0]).strip() != "":
				place = Place(name[0], x, y)
				base.enterWidget.addPlace(place)

class EnterMap(QtGui.QGraphicsView):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
	
	def setPicture(self,picture):
		self.scene = EnterMapScene(self)
		self.pixmap = QtGui.QPixmap(picture)
		
		self.scene.addPixmap(self.pixmap)
		self.setScene(self.scene)
	
	def wheelEvent(self,wheelevent):
		if wheelevent.delta() > 0:
			self.scale(1.1,1.1)
		else:
			self.scale(0.9,0.9)
	
	def update(self):
		try:
			self.scene.removeItem(self.placesGroup)
		except AttributeError:
			pass
		
		placeslist = []
		
		for place in base.enterWidget.places.items:
			rect = QtGui.QGraphicsRectItem(place.x,place.y,6,6)
			rect.setBrush(QtGui.QBrush(QtGui.QColor("red")))
			
			shadow = QtGui.QGraphicsTextItem(place.name)
			shadow.setFont(QtGui.QFont("sans-serif",15,75))
			shadow.setPos(place.x+2,place.y+2)
			shadow.setDefaultTextColor(QtGui.QColor("black"))
			shadow.setOpacity(0.5)
			
			placeslist.append(shadow)
			
			item = QtGui.QGraphicsTextItem(place.name)
			item.setFont(QtGui.QFont("sans-serif",15,75))
			item.setPos(place.x,place.y)
			item.setDefaultTextColor(QtGui.QColor("red"))
			
			placeslist.append(item)
			placeslist.append(rect)
		
		self.placesGroup = self.scene.createItemGroup(placeslist)

class EnterMapChooser(QtGui.QComboBox):
	def __init__(self,parent,mapwidget):
		QtGui.QComboBox.__init__(self,parent)
		self.mapwidget = mapwidget
		self.parent = parent
		self.currentIndexChanged.connect(self.otherMap)
		
		self.fillBox()
		self.otherMap()

	def fillBox(self):
		mapPaths = base.api.resourcePath("resources/maps")
		for name in os.listdir(mapPaths):
			self.addItem(os.path.splitext(name)[0], name)
	
	def otherMap(self):
		if len(self.parent.places.items) > 0:
			warningD = QtGui.QMessageBox()
			warningD.setIcon(QtGui.QMessageBox.Warning)
			warningD.setWindowTitle("Warning")
			warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
			warningD.setText("Are you sure you want to use another map? This will remove all your places!")
			feedback = warningD.exec_()
			if feedback == QtGui.QMessageBox.Ok:
				# Clear the entered items
				self.parent.places = List()
				# Update the list
				self.parent.currentPlaces.update()
			else:
				self.ask = False
				self.setCurrentIndex(self.prevIndex)
				return
		self.parent.map = self.currentText()
		mapsPath = base.api.resourcePath("resources/maps")
		picturePath = os.path.join(mapsPath, unicode(self.parent.map + ".gif"))
		self.mapwidget.setPicture(picturePath)
		self.prevIndex = self.currentIndex()

class EnterWidget(QtGui.QSplitter):
	def __init__(self,*args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self.places = List()
		self.map = "World"
		
		#create the GUI
		
		#left side
		leftSide = QtGui.QVBoxLayout()
		
		#left side - top
		mapLabel = QtGui.QLabel("Map:")
		
		#left side - middle
		self.pictureBox = EnterMap()
		
		#left side - top
		comboBox = EnterMapChooser(self, self.pictureBox)
		
		chooseMap = QtGui.QHBoxLayout()
		chooseMap.addWidget(mapLabel)
		chooseMap.addWidget(comboBox)
		
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
		if base.inlesson:
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

class LessonTypeChooser(QtGui.QComboBox):
	def __init__(self):
		QtGui.QComboBox.__init__(self)
		
		self.currentIndexChanged.connect(self.changeLessonType)
		
		self._lessonTypeModules = list(
			base.api.mods.supporting("lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	"""
	What happens when you change the lesson type
	"""
	def changeLessonType(self, index):
		if base.inlesson:
			base.teachWidget.initiateLesson()
	
	"""
	Get the current lesson type
	"""
	@property
	def currentLessonType(self):
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype

class TeachPictureBox(QtGui.QGraphicsView):
	def __init__(self,map,*args, **kwargs):
		super(TeachPictureBox, self).__init__(*args, **kwargs)
		self.interactive = False
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setViewportUpdateMode(0)
		
		mapsPath = base.api.resourcePath("resources/maps")
		picturePath = os.path.join(mapsPath, unicode(map + ".gif"))
		self.setPicture(picturePath)
	
	def wheelEvent(self,wheelevent):
		if wheelevent.delta() > 0:
			self.scale(1.1,1.1)
		else:
			self.scale(0.9,0.9)
	
	def setPicture(self,picture):
		self.scene = QtGui.QGraphicsScene()
		self.pixmap = QtGui.QPixmap(picture)
		
		crosshairPixmap = QtGui.QPixmap(base.api.resourcePath("resources/crosshair.png"))
		self.crosshair = QtGui.QGraphicsPixmapItem(crosshairPixmap)
		
		self.scene.addPixmap(self.pixmap)
		self.scene.addItem(self.crosshair)
		self.setScene(self.scene)

class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		## GUI Drawing
		# Top
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Lesson type:")
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		# Middle
		self.mapbox = TeachPictureBox(base.enterWidget.map)
		
		# Bottom
		bottom = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Which place is here?")
		self.answerfield = QtGui.QLineEdit()
		checkanswerbutton = QtGui.QPushButton("Check")
		self.answerfield.returnPressed.connect(self.checkAnswerButtonClick)
		checkanswerbutton.clicked.connect(self.checkAnswerButtonClick)
		self.progress = QtGui.QProgressBar()
		
		bottom.addWidget(label)
		bottom.addWidget(self.answerfield)
		bottom.addWidget(checkanswerbutton)
		bottom.addWidget(self.progress)
		
		# Total
		layout = QtGui.QVBoxLayout()
		layout.addLayout(top)
		layout.addWidget(self.mapbox)
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
		elif not base.inlesson:
			self.initiateLesson()

class TopoLesson(object):
	def __init__(self,itemList):
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(itemList,range(len(itemList.items)))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(base.teachWidget.stopLesson)
		
		self.lessonType.start()
		
		base.inlesson = True
		
		# Reset the progress bar
		base.teachWidget.progress.setValue(0)
	
	"""
	Check whether the given answer was right or wrong
	"""
	def checkAnswer(self):
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
		#set the arrow to the right position
		self._setArrow(self.currentItem.x,self.currentItem.y)
	
	"""
	Ends the lesson
	"""
	def endLesson(self):
		base.inlesson = False
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		base.teachWidget.progress.setValue(self.lessonType.askedItems)
	
	"""
	Sets the arrow on the map to the right position
	"""
	def _setArrow(self, x, y):
		base.teachWidget.mapbox.centerOn(x-15,y-50)
		base.teachWidget.mapbox.crosshair.setPos(x-15,y-50)

class TopoLessonModule(object):
	def __init__(self, api):
		global base
		base = self
		self.api = api
		self.counter = 1
		self.inlesson = False
		
		self.supports = ("lesson", "list", "loadList", "initializing")
		self.requires = (1, 0)
	
	def initialize(self):
		for module in self.api.activeMods.supporting("modules"):
			module.registerModule("Topo Lesson", self)
	
	def enable(self):
		self.type = "Places"
		
		self.lessonCreated = self.api.createEvent()
		
		for module in self.api.mods.supporting("ui"):
			event = module.addLessonCreateButton("Create topography lesson")
			event.handle(self.createLesson)
		
		self.active = True

	def disable(self):
		del self.type
		self.active = False

	def close(self):
		print "Closed!"
	
	def createLesson(self):		
		lessons = set()
		
		for module in self.api.activeMods.supporting("ui"):
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
