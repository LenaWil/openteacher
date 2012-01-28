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

"""
The dropdown menu to choose lesson type
"""
class TeachLessonTypeChooser(QtGui.QComboBox):
	def __init__(self,*args,**kwargs):
		super(TeachLessonTypeChooser, self).__init__(*args, **kwargs)
		
		self._lessonTypeModules = list(
			base._mm.mods("active", type="lessonType")
		)
		
		for lessontype in self._lessonTypeModules:
			self.addItem(lessontype.name, lessontype)
	
	"""
	Get the current lesson type
	"""
	@property
	def currentLessonType(self):
		return self._lessonTypeModules[self.currentIndex()]

"""
The teach tab
"""
class TeachWidget(QtGui.QWidget):
	lessonDone = QtCore.pyqtSignal()
	listChanged = QtCore.pyqtSignal([object])
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		
		self.inLesson = False
		
		#draw the GUI
		
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel(_("Lesson type:"))
		self.lessonTypeChooser = TeachLessonTypeChooser()
		self.lessonTypeChooser.currentIndexChanged.connect(self.changeLessonType)
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		self.nameLabel = QtGui.QLabel()
		font = QtGui.QFont()
		font.setPointSize(14)
		self.nameLabel.setFont(font)
		
		self.mediaDisplay = base._modules.default("active", type="mediaDisplay").createDisplay(True)
		
		self.questionLabel = QtGui.QLabel()
		
		self.answerField = QtGui.QLineEdit()
		self.answerField.returnPressed.connect(self.checkAnswerButtonClick)
		
		checkButton = QtGui.QPushButton(_("Check"))
		checkButton.clicked.connect(self.checkAnswerButtonClick)
		
		self.progress = QtGui.QProgressBar()
		
		bottomL = QtGui.QHBoxLayout()
		bottomL.addWidget(self.answerField)
		bottomL.addWidget(checkButton)
		bottomL.addWidget(self.progress)
		
		layout = QtGui.QVBoxLayout()
		layout.addLayout(top)
		layout.addWidget(self.mediaDisplay)
		layout.addWidget(self.nameLabel)
		layout.addWidget(self.questionLabel)
		layout.addLayout(bottomL)
		
		self.setLayout(layout)
	
	"""
	Starts the lesson
	"""
	def initiateLesson(self, items):
		self.items = items
		self.lesson = TeachMediaLesson(items, self)
		self.answerField.setFocus()
	
	"""
	Restarts the lesson
	"""
	def restartLesson(self):
		self.initiateLesson(self.items)
	
	"""
	What happens when you change the lesson type
	"""
	def changeLessonType(self, index):
		if self.inLesson:
			self.restartLesson()
	
	"""
	Stops the lesson
	"""
	def stopLesson(self, showResults=True):
		self.lesson.endLesson(showResults)
		del self.lesson
	
	"""
	What happens when you click the check answer button
	"""
	def checkAnswerButtonClick(self):
		self.lesson.checkAnswer()
		self.answerField.clear()
		self.answerField.setFocus()

"""
The lesson itself (being teached)
"""
class TeachMediaLesson(object):	
	def __init__(self,itemList,teachWidget,*args,**kwargs):
		super(TeachMediaLesson, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		
		self.itemList = itemList
		self.lessonType = self.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(self.itemList,range(len(itemList["items"])))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
		self.lessonType.start()
		
		self.teachWidget.inLesson = True
		
		# Reset the progress bar
		self.teachWidget.progress.setValue(0)
	
	"""
	Check whether the given answer was right or wrong
	"""
	def checkAnswer(self):
		# Set the end of the thinking time
		self.endThinkingTime = datetime.datetime.now()
		
		active = {
			"start": self.startThinkingTime,
			"end": self.endThinkingTime
		}
		
		if self.currentItem["answer"] == self.teachWidget.answerField.text():
			# Answer was right
			self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "right",
					"givenAnswer": unicode(self.teachWidget.answerField.text()),
					"active": active
				})
			# Progress bar
			self._updateProgressBar()
		else:
			# Answer was wrong
			self.lessonType.setResult({
					"itemId": self.currentItem["id"],
					"result": "wrong",
					"givenAnswer": unicode(self.teachWidget.answerField.text()),
					"active": active
				})
		
		self.teachWidget.listChanged.emit(self.itemList)
			
	"""
	What happens when the next question should be asked
	"""
	def nextQuestion(self, item):
		# set the next question
		self.currentItem = item
		# set the question field
		self.teachWidget.questionLabel.setText(self.currentItem["question"])
		# set the name field
		self.teachWidget.nameLabel.setText(self.currentItem["name"])
		# set the mediawidget to the right location
		self.teachWidget.mediaDisplay.showMedia(self.currentItem["filename"], self.currentItem["remote"], True)
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

		# stop media
		self.teachWidget.mediaDisplay.clear()
		
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
					module.showResults(self.itemList, "media", self.itemList["tests"][-1])
				except IndexError:
					pass
		
		self.teachWidget.lessonDone.emit()
	
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		self.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		self.teachWidget.progress.setValue(self.lessonType.askedItems)


class MediaTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaTeacherModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		
		self._mm = moduleManager
		
		self.type = "mediaTeacher"
		
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="resultsDialog"),
		)
		self.requires = (
			self._mm.mods(type="mediaDisplay"),
		)
	
	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
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
	
	def createMediaTeacher(self):
		return TeachWidget()

def init(moduleManager):
	return MediaTeacherModule(moduleManager)