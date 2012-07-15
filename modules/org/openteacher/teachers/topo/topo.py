#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
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

import datetime

class Order:
	Normal, Inversed = xrange(2)

"""
The dropdown menu to choose lesson type
"""
class TeachLessonTypeChooser(QtGui.QComboBox):
	def __init__(self, teachWidget, *args, **kwargs):
		super(TeachLessonTypeChooser, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		
		self.currentIndexChanged.connect(self.changeLessonType)
		
		self._lessonTypeModules = list(
			base._mm.mods("active", type="lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	"""
	What happens when you change the lesson type
	"""
	def changeLessonType(self, index):
		if self.teachWidget.inLesson:
			self.teachWidget.restartLesson()
	
	"""
	Get the current lesson type
	"""
	@property
	def currentLessonType(self):
		return self._lessonTypeModules[self.currentIndex()]

"""
The dropdown menu to choose lesson order
"""
class TeachLessonOrderChooser(QtGui.QComboBox):
	def __init__(self, teachWidget, *args, **kwargs):
		super(TeachLessonOrderChooser, self).__init__(*args, **kwargs)
		
		self.currentIndexChanged.connect(self.changeLessonOrder)
		self.teachWidget = teachWidget
		
		self.addItem(_("Place - Name"), 0)
		self.addItem(_("Name - Place"), 1)
	
	"""
	What happens when you change the lesson order
	"""
	def changeLessonOrder(self, index):
		if self.teachWidget.inLesson:
			self.teachWidget.restartLesson()

"""
The lesson itself
"""
class TeachTopoLesson(object):
	def __init__(self, itemList, mapPath, teachWidget, *args, **kwargs):
		super(TeachTopoLesson, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		
		# Set the map
		self.teachWidget.mapBox.setMap(mapPath)
		self.teachWidget.mapBox.setInteractive(self.order)
		
		self.itemList = itemList
		self.lessonType = self.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(self.itemList,range(len(itemList["items"])))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.teachWidget.stopLesson)
		
		self.lessonType.start()
		
		self.teachWidget.inLesson = True
		
		#self.startThinkingTime
		#self.endThinkingTime
		
		# Reset the progress bar
		self.teachWidget.progress.setValue(0)
		
		self.teachWidget.setWidgets(self.order)
	
	"""
	Check whether the given answer was right or wrong
	"""
	def checkAnswer(self, answer=None):
		# Set endThinkingTime if it hasn't been set yet (this is in Name - Place mode)
		try:
			self.endThinkingTime
		except AttributeError:
			self.endThinkingTime = datetime.datetime.now()
		
		active = {
			"start": self.startThinkingTime,
			"end": self.endThinkingTime
		}
		
		if self.order == Order.Inversed:
			if self.currentItem == answer:
				# Answer was right
				self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "right",
					"active": active
				})
				# Progress bar
				self._updateProgressBar()
			else:
				# Answer was wrong
				self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "wrong",
					"active": active
				})
		else:
			if self.currentItem["name"] == self.teachWidget.answerfield.text():
				# Answer was right
				self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "right",
					"active": active
				})
				# Progress bar
				self._updateProgressBar()
			else:
				# Answer was wrong
				self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "wrong",
					"active": active
				})
		
		self.teachWidget.listChanged.emit(self.itemList)
			
	"""
	What happens when the next question should be asked
	"""
	def nextQuestion(self, item):
		#set the next question
		self.currentItem = item
		if self.order == Order.Inversed:
			#set the question
			self.teachWidget.questionLabel.setText(_("Please click this place: ") + self.currentItem["name"])
		else:
			#set the arrow to the right position
			self.teachWidget.mapBox.setArrow(self.currentItem["x"],self.currentItem["y"])
		# Set the start of the thinking time to now
		self.startThinkingTime = datetime.datetime.now()
		# Delete the end of the thinking time
		try:
			del self.endThinkingTime
		except AttributeError:
			pass
	
	"""
	Ends the lesson
	"""
	def endLesson(self, showResults=True):
		self.teachWidget.inLesson = False
		
		# Update and go to results widget, only if the test is progressing
		try:
			self.itemList["tests"][-1]
		except IndexError:
			pass
		else:
			if showResults:
				try:
					# Go to results widget
					module = base._modules.default("active", type="resultsDialog")
					module.showResults(self.itemList, "topo", self.itemList["tests"][-1])
				except IndexError:
					pass
		
		self.teachWidget.lessonDone.emit()
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		self.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		self.teachWidget.progress.setValue(self.lessonType.askedItems)
	
	@property
	def order(self):
		return self.teachWidget.lessonOrderChooser.currentIndex()

"""
The teach tab
"""
class TeachWidget(QtGui.QWidget):
	lessonDone = QtCore.pyqtSignal()
	listChanged = QtCore.pyqtSignal([object])
	def __init__(self, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		self.inLesson = False
		
		## GUI Drawing
		# Top
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel(_("Lesson type:"))
		self.lessonTypeChooser = TeachLessonTypeChooser(self)
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		label = QtGui.QLabel(_("Lesson order:"))
		self.lessonOrderChooser = TeachLessonOrderChooser(self)
		
		top.addWidget(label)
		top.addWidget(self.lessonOrderChooser)
		
		# Middle
		self.mapBox = base._modules.default("active", type="topoMaps").getTeachMap(self)
		
		# Bottom
		bottom = QtGui.QHBoxLayout()
		
		self.label = QtGui.QLabel(_("Which place is here?"))
		self.answerfield = QtGui.QLineEdit()
		self.checkanswerbutton = QtGui.QPushButton(_("Check"))
		self.answerfield.returnPressed.connect(self._checkAnswerButtonClick)
		self.answerfield.textEdited.connect(self._answerChanged)
		
		self.checkanswerbutton.clicked.connect(self._checkAnswerButtonClick)
		
		self.questionLabel = QtGui.QLabel(_("Please click this place:"))
		
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
	def initiateLesson(self, places, mapPath):
		self.places = places
		self.mapPath = mapPath
		
		self.lesson = TeachTopoLesson(places, mapPath, self)
		self.answerfield.setFocus()
	
	"""
	Restarts the lesson
	"""
	def restartLesson(self):
		self.initiateLesson(self.places, self.mapPath)
	
	"""
	Stops the lesson
	"""
	def stopLesson(self, showResults=True):
		self.lesson.endLesson(showResults)
		
		del self.lesson
	
	"""
	What happens when the answer in the textbox has changed
	"""
	def _answerChanged(self):
		try:
			self.lesson.endThinkingTime
		except AttributeError:
			self.lesson.endThinkingTime = datetime.datetime.now()
		else:
			if self.answerfield.text() == "":
				del self.lesson.endThinkingTime
	
	"""
	What happens when you click the check answer button
	"""
	def _checkAnswerButtonClick(self):
		# Check the answer
		self.lesson.checkAnswer()
		# Clear the answer field
		self.answerfield.clear()
		# Focus the answer field
		self.answerfield.setFocus()
	
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

class TopoTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TopoTeacherModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		
		self._mm = moduleManager
		
		self.type = "topoTeacher"
		self.priorities = {
			"student@home": 504,
			"student@school": 504,
			"teacher": 504,
			"wordsonly": -1,
			"selfstudy": 504,
			"testsuite": 504,
			"codedocumentation": 504,
			"all": 504,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="resultsDialog"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="topoMaps"),
		)
		self.filesWithTranslations = ("topo.py",)
	
	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.active = True
		#FIXME: retranslate!
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
	
	def createTopoTeacher(self):
		return TeachWidget()

def init(moduleManager):
	return TopoTeacherModule(moduleManager)
