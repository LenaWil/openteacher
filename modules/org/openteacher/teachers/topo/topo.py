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
import weakref

class Order:
	Normal, Inversed = xrange(2)

class TeachLessonTypeChooser(QtGui.QComboBox):
	"""The dropdown menu to choose lesson type"""

	def __init__(self, teachWidget, *args, **kwargs):
		super(TeachLessonTypeChooser, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		
		self.retranslate()

	def retranslate(self):
		try:
			self.currentIndexChanged.disconnect(self.changeLessonType)
		except TypeError:
			#not yet connected (first pass)
			pass

		#save status
		i = self.currentIndex()

		#update data
		self.clear()
		self._lessonTypeModules = base._modules.sort("active", type="lessonType")
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)

		#restore status
		if i != -1:
			self.setCurrentIndex(i)

		#re-connect signal
		self.currentIndexChanged.connect(self.changeLessonType)

	def changeLessonType(self, index):
		"""What happens when you change the lesson type"""

		if self.teachWidget.inLesson:
			self.teachWidget.restartLesson()
	
	@property
	def currentLessonType(self):
		"""Get the current lesson type"""

		return self._lessonTypeModules[self.currentIndex()]

class TeachLessonOrderChooser(QtGui.QComboBox):
	"""The dropdown menu to choose lesson order"""

	def __init__(self, teachWidget, *args, **kwargs):
		super(TeachLessonOrderChooser, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		self.retranslate()

	def retranslate(self):
		try:
			self.currentIndexChanged.disconnect(self.changeLessonOrder)
		except TypeError:
			#not yet connected (first pass)
			pass

		i = self.currentIndex()
		self.clear()

		self.addItem(_("Place - Name"), 0)
		self.addItem(_("Name - Place"), 1)

		if i != -1:
			self.setCurrentIndex(i)

		self.currentIndexChanged.connect(self.changeLessonOrder)

	def changeLessonOrder(self, index):
		"""What happens when you change the lesson order"""

		if self.teachWidget.inLesson:
			self.teachWidget.restartLesson()

class TeachTopoLesson(object):
	"""The lesson itself"""

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
	
	def checkAnswer(self, answer=None):
		"""Check whether the given answer was right or wrong"""

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

	def nextQuestion(self, item):
		"""What happens when the next question should be asked"""

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
	
	def endLesson(self, showResults=True):
		"""Ends the lesson"""

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

	def _updateProgressBar(self):
		"""Updates the progress bar"""

		self.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		self.teachWidget.progress.setValue(self.lessonType.askedItems)
	
	@property
	def order(self):
		return self.teachWidget.lessonOrderChooser.currentIndex()

class TeachWidget(QtGui.QWidget):
	"""The teach tab"""

	lessonDone = QtCore.pyqtSignal()
	listChanged = QtCore.pyqtSignal([object])
	def __init__(self, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		self.inLesson = False
		
		## GUI Drawing
		# Top
		top = QtGui.QHBoxLayout()

		self.lessonTypeLabel = QtGui.QLabel()
		self.lessonTypeChooser = TeachLessonTypeChooser(self)
		
		top.addWidget(self.lessonTypeLabel)
		top.addWidget(self.lessonTypeChooser)

		self.lessonOrderLabel = QtGui.QLabel()
		self.lessonOrderChooser = TeachLessonOrderChooser(self)

		top.addWidget(self.lessonOrderLabel)
		top.addWidget(self.lessonOrderChooser)
		
		# Middle
		self.mapBox = base._modules.default("active", type="topoMaps").getTeachMap(self)
		
		# Bottom
		bottom = QtGui.QHBoxLayout()
		
		self.label = QtGui.QLabel()
		self.answerfield = QtGui.QLineEdit()
		self.checkanswerbutton = QtGui.QPushButton()
		self.answerfield.returnPressed.connect(self._checkAnswerButtonClick)
		self.answerfield.textEdited.connect(self._answerChanged)
		
		self.checkanswerbutton.clicked.connect(self._checkAnswerButtonClick)
		
		self.questionLabel = QtGui.QLabel()
		
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

		self.retranslate()

	def retranslate(self):
		self.lessonTypeLabel.setText(_("Lesson type:"))
		self.lessonOrderLabel.setText(_("Lesson order:"))
		self.label.setText(_("Which place is here?"))
		#TRANSLATORS: A button the user clicks to let the computer check the given answer.
		self.checkanswerbutton.setText(_("Check"))
		self.questionLabel.setText(_("Please click this place:"))

		self.lessonTypeChooser.retranslate()
		self.lessonOrderChooser.retranslate()

	def initiateLesson(self, places, mapPath):
		"""Starts the lesson"""

		self.places = places
		self.mapPath = mapPath
		
		self.lesson = TeachTopoLesson(places, mapPath, self)
		self.answerfield.setFocus()

	def restartLesson(self):
		"""Restarts the lesson"""

		self.initiateLesson(self.places, self.mapPath)
	
	def stopLesson(self, showResults=True):
		"""Stops the lesson"""

		self.lesson.endLesson(showResults)
		
		del self.lesson
	
	def _answerChanged(self):
		"""What happens when the answer in the textbox has changed"""

		try:
			self.lesson.endThinkingTime
		except AttributeError:
			self.lesson.endThinkingTime = datetime.datetime.now()
		else:
			if self.answerfield.text() == "":
				del self.lesson.endThinkingTime
	
	def _checkAnswerButtonClick(self):
		"""What happens when you click the check answer button"""

		# Check the answer
		self.lesson.checkAnswer()
		# Clear the answer field
		self.answerfield.clear()
		# Focus the answer field
		self.answerfield.setFocus()
	
	def setWidgets(self, order):
		"""Sets the bottom widgets to either the in-order version (False) or
		   the inversed-order (True)

		"""
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

		self._widgets = set()

		#setup translation
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
		
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		for ref in self._widgets:
			widget = ref()
			if widget is not None:
				#FIXME (>3.0): use the languageChangeDone event instead?
				#(and only for the stuff that depends on other modules?)
				#update next event loop iteration, because it depends on
				#some other modules.
				QtCore.QTimer.singleShot(0, widget.retranslate)

	def disable(self):
		self.active = False

		del self._modules
		del self._widgets
	
	def createTopoTeacher(self):
		tw = TeachWidget()
		self._widgets.add(weakref.ref(tw))
		return tw

def init(moduleManager):
	return TopoTeacherModule(moduleManager)
