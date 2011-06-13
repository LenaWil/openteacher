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

class Place():
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

class EnterPlacesWidget(QtGui.QListWidget):
	def __init__(self):
		QtGui.QListWidget.__init__(self)
	
	def update(self):
		self.clear()
		for place in base.enterWidget.places.words:
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
		
		#self.show()
	
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
		
		for place in base.enterWidget.places.words:
			rect = QtGui.QGraphicsRectItem(place.x,place.y,6,6)
			rect.setBrush(QtGui.QBrush(QtGui.QColor("red")))
			
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
		#ask the user if they really want to use another map?
		self.ask = True
		
		self.fillBox()
		self.otherMap()

	def fillBox(self):
		mapPaths = base.api.resourcePath(__file__, "resources/maps")
		for name in os.listdir(mapPaths):
			self.addItem(os.path.splitext(name)[0], name)
	
	def otherMap(self):
		if self.ask:
			if len(self.parent.places.words) > 0:
				warningD = QtGui.QMessageBox()
				warningD.setIcon(QtGui.QMessageBox.Warning)
				warningD.setWindowTitle("Warning")
				warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
				warningD.setText("Are you sure you want to use another map? This will remove all your places!")
				feedback = warningD.exec_()
				if feedback == QtGui.QMessageBox.Ok:
					self.parent.places = []
					self.parent.currentPlaces.update()
				else:
					self.ask = False
					self.setCurrentIndex(self.prevIndex)
					return
			self.parent.map = self.currentText()
			mapsPath = base.api.resourcePath(__file__, "resources/maps")
			picturePath = os.path.join(mapsPath, unicode(self.parent.map + ".gif"))
			self.mapwidget.setPicture(picturePath)
			self.prevIndex = self.currentIndex()
		self.ask = True

class TeachPictureBox(QtGui.QGraphicsView):
	def __init__(self,map,*args, **kwargs):
		super(TeachPictureBox, self).__init__(*args, **kwargs)
		self.interactive = False
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setViewportUpdateMode(0)
		
		mapsPath = base.api.resourcePath(__file__, "resources/maps")
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
		
		crosshairPixmap = QtGui.QPixmap(base.api.resourcePath(__file__, "resources/crosshair.png"))
		self.crosshair = QtGui.QGraphicsPixmapItem(crosshairPixmap)
		
		self.scene.addPixmap(self.pixmap)
		self.scene.addItem(self.crosshair)
		self.setScene(self.scene)

class List(object):
	def __init__(self, *args, **kwargs):
		super(List, self).__init__(*args, **kwargs)
		
		self.words = []
		self.tests = []

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
	
	def addPlace(self,place):
		self.places.words.append(place)
		self.pictureBox.update()
		self.currentPlaces.update()
	
	def removePlace(self):
		for placeItem in self.currentPlaces.selectedItems():
			for place in self.places.words:
				if placeItem.text() == str(place.name + " (" + str(place.x) + "," + str(place.y) + ")"):
					self.places.words.remove(place)
		self.pictureBox.update()
		self.currentPlaces.update()
	
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
				base.api.setCurrentTab(self.parent.teachWidget)
				return

class LessonTypeChooser(QtGui.QComboBox):
	def __init__(self):
		QtGui.QComboBox.__init__(self)
		
		self.currentIndexChanged.connect(self.changeLessonType)
		
		self._lessonTypeModules = list(
			base.api.mods.supporting("lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	def currentLessonType(self):
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype
		
	def changeLessonType(self, index):
		try:
			base.teachWidget.initiateLesson()
		except AttributeError:
			pass

class TopoLesson(object):
	def __init__(self,items):
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType().createLessonType(items,range(len(items.words)))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
		self.lessonType.start()
		
		#set the progress bar
		base.teachWidget.progress.setMinimum(0)
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems)
		base.teachWidget.progress.setValue(0)
	
	def checkAnswer(self):
		if self.currentItem.name == base.teachWidget.answerfield.text():
			# Answer was right
			self.lessonType.setResult(Result("right"))
			# Progress bar
			base.teachWidget.progress.setValue(self.lessonType.askedItems)
		else:
			# Answer was wrong
			self.lessonType.setResult(Result("wrong"))
			
	
	def nextQuestion(self, item):
		#set the next question
		self.currentItem = item
		#set the arrow to the right position
		self.setArrow(self.currentItem.x,self.currentItem.y)
	
	"""
	Sets the arrow on the map to the right position
	"""
	def setArrow(self, x, y):
		base.teachWidget.mapbox.centerOn(x-15,y-50)
		base.teachWidget.mapbox.crosshair.setPos(x-15,y-50)
	
	def endLesson(self):
		# FIXME : message with results
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget

class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)				
		#draw the GUI
		#top
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Lesson type:")
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		#middle
		self.mapbox = TeachPictureBox(base.enterWidget.map)
		
		#bottom
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
		
		#total
		layout = QtGui.QVBoxLayout()
		layout.addLayout(top)
		layout.addWidget(self.mapbox)
		layout.addLayout(bottom)
		
		self.setLayout(layout)
	
	def initiateLesson(self):
		self.lesson = TopoLesson(base.enterWidget.places)
	
	def stopLesson(self):
		self.lesson.endLesson(False)
		del self.lesson
	
	def checkAnswerButtonClick(self):
		self.lesson.checkAnswer()
		self.answerfield.clear()
		self.answerfield.setFocus()
	
	def showEvent(self,event):
		self.initiateLesson()

class TopoLessonModule(object):
	def __init__(self, api):
		global base
		base = self
		self.api = api
		self.counter = 1
		# is the lesson going on?
		self.inlesson = False
		
		self.supports = ("lesson", "list", "loadList", "initializing")
		self.requires = (1, 0)
	
	def initialize(self):
		for module in self.api.activeMods.supporting("settings"):
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
				"Word lesson %s" % self.counter,
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

def init(moduleManager):
	return TopoLessonModule(moduleManager)
