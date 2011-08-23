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
from PyQt4 import QtWebKit
from PyQt4 import QtNetwork
from PyQt4.phonon import Phonon

import os
import time
import datetime
import mimetypes
import fnmatch
import tempfile

"""
WIDGETS ON BOTH ENTER AND TEACH TABS
"""

"""
The video player and web viewer combination widget with controls
"""
class MediaControlDisplay(QtGui.QWidget):
	def __init__(self,autoplay=True,*args, **kwargs):
		super(MediaControlDisplay, self).__init__(*args, **kwargs)
		
		self.autoplay = autoplay
		self.activeModule = None
		
		self.noPhonon = True
		
		for module in base._mm.mods("active", type="mediaType"):
			if module.phononControls == True:
				self.noPhonon = False
		
		self.mediaDisplay = MediaDisplay(self.autoplay, self.noPhonon)
		# Do not add the Phonon widget if it is not necessary
		if not self.noPhonon:
			self.mediaDisplay.videoPlayer.mediaObject().stateChanged.connect(self._playPauseButtonUpdate)
		
		layout = QtGui.QVBoxLayout()
		
		# Do not add the controls if there is not going to be any Phonon
		if not self.noPhonon:
			buttonsLayout = QtGui.QHBoxLayout()
			
			self.pauseButton = QtGui.QPushButton()
			self.pauseButton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause",QtGui.QIcon(base._mm.resourcePath("icons/player_pause.png"))))
			self.pauseButton.clicked.connect(self.playPause)
			buttonsLayout.addWidget(self.pauseButton)
			
			self.seekSlider = Phonon.SeekSlider(self.mediaDisplay.videoPlayer.mediaObject())
			buttonsLayout.addWidget(self.seekSlider)
			
			self.volumeSlider = Phonon.VolumeSlider(self.mediaDisplay.videoPlayer.audioOutput())
			self.volumeSlider.setMaximumWidth(100)
			buttonsLayout.addWidget(self.volumeSlider)
		
		# Add the stacked widget
		layout.addWidget(self.mediaDisplay)
		
		if not self.noPhonon:
			layout.addLayout(buttonsLayout)
		
		self.setLayout(layout)
		
		# Disable the controls
		self.setControls()
	
	def showMedia(self, path, remote, autoplay):
		priority = 0
		
		for module in base._mm.mods("active", type="mediaType"):
			if module.supports(path):
				if module.priority > priority:
					chosenModule = module
		
		chosenModule.showMedia(chosenModule.path(path, self.autoplay), self.mediaDisplay, autoplay)
		self.activeModule = chosenModule
		
		self.setControls()
	
	def setControls(self):
		# Only if there are controls
		if not self.noPhonon:
			if self.activeModule == None or not self.activeModule.phononControls:
				self._setControlsEnabled(False)
			else:
				self._setControlsEnabled(True)
	
	def playPause(self, event):
		if not self.noPhonon:
			if self.mediaDisplay.videoPlayer.isPaused():
				self.mediaDisplay.videoPlayer.play()
			else:
				self.mediaDisplay.videoPlayer.pause()
	
	def stop(self):
		if not self.noPhonon:
			self.mediaDisplay.videoPlayer.stop()
	
	def clear(self):
		self.mediaDisplay.clear()
	
	def _playPauseButtonUpdate(self, newstate, oldstate):
		if self.mediaDisplay.videoPlayer.isPaused():
			self.pauseButton.setIcon(QtGui.QIcon.fromTheme("media-playback-play",QtGui.QIcon(base._mm.resourcePath("icons/player_play.png"))))
		else:
			self.pauseButton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause",QtGui.QIcon(base._mm.resourcePath("icons/player_pause.png"))))
	
	def _setControlsEnabled(self, enabled):
		self.pauseButton.setEnabled(enabled)
		self.volumeSlider.setEnabled(enabled)
		self.seekSlider.setEnabled(enabled)

"""
The video player and web viewer combination widget
"""
class MediaDisplay(QtGui.QStackedWidget):
	def __init__(self,autoplay,noPhonon,*args, **kwargs):
		super(MediaDisplay, self).__init__(*args, **kwargs)
		
		#self.activeType = None
		self.autoplay = autoplay
		
		self.noPhonon = noPhonon
		
		if not self.noPhonon:
			self.videoPlayer = Phonon.VideoPlayer(Phonon.VideoCategory, self)
		
		self.webviewer = QtWebKit.QWebView()
		self.webviewer.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
		
		self.addWidget(self.webviewer)
		
		if not self.noPhonon:
			self.addWidget(self.videoPlayer)
	
	def clear(self):
		self.webviewer.setHtml('''
		<html><head><title>Nothing</title></head><body></body></html>
		''')
		if not self.noPhonon:
			self.videoPlayer.stop()
		# Set the active type
		self.activeModule = None

		
		
		
		
		
		
		
		
		
		
"""
WIDGETS ON ENTER TAB
"""

"""
The model for the list widget with media items (this construction because without model Qt produces a bug)
"""
class EnterItemListModel(QtCore.QAbstractListModel):
	def __init__(self,items,*args,**kwargs):
		super(EnterItemListModel, self).__init__(*args, **kwargs)
		
		self.listData = []
		
		for item in items["items"]:
			self.listData.append(item["name"])
	
	def update(self,items):
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
		
		self.listData = []
		
		for item in items["items"]:
			self.listData.append(item["name"])
		
		self.endInsertRows()
	
	def rowCount(self,parent=QtCore.QModelIndex()):
		return len(self.listData)

	def data(self,index,role):
		if index.isValid() and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.listData[index.row()])
		else:
			return QtCore.QVariant()
	
	def textAtIndex(self,index):
		return self.listData[index]

"""
The list widget with media items
"""
class EnterItemList(QtGui.QListView):
	def __init__(self,parent,*args,**kwargs):
		super(EnterItemList, self).__init__(*args, **kwargs)
		
		self.parent = parent
		
		self.lm = EnterItemListModel(parent.itemList,self)
		self.setModel(self.lm)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
	
	def update(self):
		self.lm.update(base.enterWidget.itemList)
	
	def selectionChanged(self,current,previous):
		self.setRightActiveItem()
	
	def setRightActiveItem(self):
		if len(base.enterWidget.itemList["items"]) > 0:
			self.parent.setActiveItem(base.enterWidget.itemList["items"][self.currentIndex().row()])

				
				
				
				
				
				
				
				
				
				
				
"""
WIDGETS ON TEACH TAB
"""

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
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype

				
				
				
				
				
				
				



"""
TABS
"""

"""
The enter tab
"""
class EnterWidget(QtGui.QSplitter):
	def __init__(self,*args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self.itemList = {
			"items": list(),
			"tests": list()
		}
		
		self.enterItemList = EnterItemList(self)
		
		removeButton = QtGui.QPushButton(_("Remove"))
		removeButton.clicked.connect(self.removeItem)
		addLocalButton = QtGui.QPushButton(_("Add local media"))
		addLocalButton.clicked.connect(self.addLocalItems)
		addRemoteButton = QtGui.QPushButton(_("Add remote media"))
		addRemoteButton.clicked.connect(self.addRemoteItems)
		
		leftBottom = QtGui.QHBoxLayout()
		leftBottom.addWidget(removeButton)
		leftBottom.addWidget(addLocalButton)
		leftBottom.addWidget(addRemoteButton)
		
		left = QtGui.QVBoxLayout()
		left.addWidget(self.enterItemList)
		left.addLayout(leftBottom)
		leftW = QtGui.QWidget()
		leftW.setLayout(left)
		
		self.mediaDisplay = MediaControlDisplay(False)
		
		namel = QtGui.QLabel(_("Name:"))
		
		self.enterName = QtGui.QLineEdit()
		self.enterName.textChanged.connect(self.changeName)
		self.enterName.setEnabled(False)
		
		questionl = QtGui.QLabel(_("Question:"))
		
		self.enterQuestion = QtGui.QLineEdit()
		self.enterQuestion.textChanged.connect(self.changeQuestion)
		self.enterQuestion.setEnabled(False)
		
		answerl = QtGui.QLabel(_("Answer:"))
		
		self.enterAnswer = QtGui.QLineEdit()
		self.enterAnswer.textChanged.connect(self.changeAnswer)
		self.enterAnswer.setEnabled(False)
		
		desceditL = QtGui.QVBoxLayout()
		desceditL.addWidget(namel)
		desceditL.addWidget(self.enterName)
		desceditL.addWidget(questionl)
		desceditL.addWidget(self.enterQuestion)
		desceditL.addWidget(answerl)
		desceditL.addWidget(self.enterAnswer)
		
		desceditW = QtGui.QWidget()
		desceditW.setLayout(desceditL)
		
		rightSplitter = QtGui.QSplitter(2)
		rightSplitter.addWidget(self.mediaDisplay)
		rightSplitter.addWidget(desceditW)
		
		right = QtGui.QVBoxLayout()
		right.addWidget(rightSplitter)
		rightW = QtGui.QWidget()
		rightW.setLayout(right)
		
		splitter = QtGui.QSplitter(self)
		splitter.addWidget(leftW)
		splitter.addWidget(rightW)
		
		layout = QtGui.QHBoxLayout()
		layout.addWidget(splitter)
		
		self.setLayout(layout)
	
	"""
	Add items from the local disk to the list
	"""
	def addLocalItems(self):
		extensions = []
		for module in base._mm.mods("active", type="mediaType"):
			try:
				extensions.extend(module.extensions)
			except AttributeError:
				# No extensions
				pass
		
		extensionsStr = "("
		for extension in extensions:
			extensionsStr += "*" + extension + " "
		extensionsStr += ")"
		
		filenames = QtGui.QFileDialog.getOpenFileNames(self,_("Select file(s)"),QtCore.QDir.homePath(),_("Media") + " " + extensionsStr)
		for filename in filenames:
			self.addItem(str(filename), False)
	
	"""
	Add items from the internet to the list
	"""
	def addRemoteItems(self):
		sitenames = []
		for module in base._mm.mods("active", type="mediaType"):
			try:
				sitenames.extend(module.remoteNames)
			except AttributeError:
				# No name
				pass
		
		sitenamesStr = ""
		for sitename in sitenames:
			sitenamesStr += sitename + ", "
		sitenamesStr = sitenamesStr[:-2]
		
		url, dialog = QtGui.QInputDialog.getText(self, _("File URL"), _("Enter the URL of your website or media item.\nSupported video sites: " + sitenamesStr + "."))
		if dialog:
			self.addItem(str(url), True)
	
	"""
	Updates all the widgets if the list has changed
	"""
	def updateWidgets(self):
		self.enterItemList.update()
	
	"""
	Add an item to the list
	"""
	def addItem(self,filename,remote=False,name=None,question=None,answer=None):
		# Check if file is supported
		for module in base._mm.mods("active", type="mediaType"):
			if module.supports(filename):
				item = {
					"id": int(),
					"remote": remote,
					"filename": unicode(filename),
					"name": unicode(name),
					"question": unicode(),
					"answer": unicode()
				}
				# Set id
				try:
					item["id"] = self.itemList["items"][-1]["id"] +1
				except IndexError:
					item["id"] = 0
				
				if name != None:
					item["name"] = name
				else:
					if remote == False:
						item["name"] = os.path.basename(filename)
					else:
						item["name"] = filename
				if question != None:
					item["question"] = question
				if answer != None:
					item["answer"] = answer
				
				self.itemList["items"].append(item)
				self.updateWidgets()
				break
		else:
			QtGui.QMessageBox.critical(self, _("Unsupported file type"), _("This type of file is not supported:\n" + filename))
	
	"""
	Remove an item from the list
	"""
	def removeItem(self):
		self.itemList["items"].remove(self.activeitem)
		self.updateWidgets()
		self.mediaDisplay.clear()
		self.enterName.setText("")
		self.enterName.setEnabled(False)
		self.enterQuestion.setText("")
		self.enterQuestion.setEnabled(False)
		self.enterAnswer.setText("")
		self.enterAnswer.setEnabled(False)
		self.enterItemList.setRightActiveItem()
	
	"""
	Change the active item
	"""
	def setActiveItem(self,item):
		self.activeitem = item
		self.enterName.setEnabled(True)
		self.enterName.setText(item["name"])
		self.enterQuestion.setEnabled(True)
		self.enterQuestion.setText(item["question"])
		self.enterAnswer.setEnabled(True)
		self.enterAnswer.setText(item["answer"])
		self.mediaDisplay.showMedia(item["filename"], item["remote"], False)
	
	"""
	Change the name of the active item
	"""
	def changeName(self):
		self.activeitem["name"] = unicode(self.enterName.text())
		self.updateWidgets()
	
	
	"""
	Change the question of the active item
	"""
	def changeQuestion(self):
		self.activeitem["question"] = unicode(self.enterQuestion.text())
	
	"""
	Change the description of the active item
	"""
	def changeAnswer(self):
		self.activeitem["answer"] = unicode(self.enterAnswer.text())
	
	"""
	What happens when you click the Enter tab
	"""
	def showEvent(self, event):
		if base.inLesson:
			warningD = QtGui.QMessageBox()
			warningD.setIcon(QtGui.QMessageBox.Warning)
			warningD.setWindowTitle(_("Warning"))
			warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
			warningD.setText(_("Are you sure you want to go back to the enter tab? This will end your lesson!"))
			feedback = warningD.exec_()
			if feedback == QtGui.QMessageBox.Ok:
				base.teachWidget.stopLesson()
			else:
				base.fileTab.currentTab = base.teachWidget
	
"""
The teach tab
"""
class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
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
		
		self.mediaDisplay = MediaControlDisplay(True)
		
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
	def initiateLesson(self):
		self.lesson = MediaLesson(base.enterWidget.itemList)
		self.answerField.setFocus()
	
	"""
	What happens when you change the lesson type
	"""
	def changeLessonType(self, index):
		if base.inLesson:
			self.initiateLesson()
	
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
		self.lesson.checkAnswer()
		self.answerField.clear()
		self.answerField.setFocus()
	
	"""
	What happens when you click the Teach tab
	"""
	def showEvent(self,event):
		if len(base.enterWidget.itemList["items"]) == 0:
			QtGui.QMessageBox.critical(self, _("Not enough items"), _("You need to add items to your test first"))
			base.fileTab.currentTab = base.enterWidget
		elif not base.inLesson:
			self.initiateLesson()
				
				
			








			
"""
GENERAL CLASSES
"""

"""
The lesson itself (being teached)
"""
class MediaLesson(object):
	def __init__(self,itemList,*args,**kwargs):
		super(MediaLesson, self).__init__(*args, **kwargs)
		
		#stop media playing in the enter widget
		base.enterWidget.mediaDisplay.clear()
		
		self.itemList = itemList
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(self.itemList,range(len(itemList["items"])))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
		self.lessonType.start()
		
		base.inLesson = True
		
		#self.startThinkingTime
		#self.endThinkingTime
		
		# Reset the progress bar
		base.teachWidget.progress.setValue(0)
	
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
		
		if self.currentItem["answer"] == base.teachWidget.answerField.text():
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
			
	"""
	What happens when the next question should be asked
	"""
	def nextQuestion(self, item):
		# set the next question
		self.currentItem = item
		# set the question field
		base.teachWidget.questionLabel.setText(self.currentItem["question"])
		# set the name field
		base.teachWidget.nameLabel.setText(self.currentItem["name"])
		# set the mediawidget to the right location
		base.teachWidget.mediaDisplay.showMedia(self.currentItem["filename"], self.currentItem["remote"], True)
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
	def endLesson(self):
		base.inLesson = False

		for module in base._mm.mods("active", type="resultsDialog"): #FIXME: only one should remain
			if base.dataType in module.supports:
				module.showResults(self.itemList, self.itemList["tests"][-1])

		# stop media
		base.teachWidget.mediaDisplay.clear()
		# Update results widget
		base.resultsWidget.updateList(self.itemList)
		# Go to results widget
		base.fileTab.currentTab = base.resultsWidget
		# Set right active item
		base.enterWidget.enterItemList.setRightActiveItem()
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		base.teachWidget.progress.setValue(self.lessonType.askedItems)

"""
The module
"""
class MediaLessonModule(object):
	def __init__(self, mm,*args,**kwargs):
		super(MediaLessonModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		self._mm = mm
		self.counter = 1
		self.inLesson = False

		self.type = "lesson"
		self.dataType = "media"

	def enable(self):
		#setup translation
		global _
		global ngettext
		
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		for module in self._mm.mods("active", type="modules"):
			module.registerModule(_("Media Lesson"), self)
		
		self.lessonCreated = self._mm.createEvent()
		self.lessonCreationFinished = self._mm.createEvent()
		
		for module in self._mm.mods("active", type="ui"):
			event = module.addLessonCreateButton(_("Create media lesson"))
			event.handle(self.createLesson)
		
		# Add settings
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.lessons.media.videohtml5",
				"Use HTML5 for video",
				"boolean",
				"Media Lesson",
				"Output"
			)
			
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.lessons.media.audiohtml5",
				"Use HTML5 for audio",
				"boolean",
				"Media Lesson",
				"Output"
			)
		
		self.active = True

	def disable(self):
		self.active = False

		del self.dataType
		del self.lessonCreated
		del self.lessonCreationFinished
	
	def createLesson(self):		
		lessons = set()
		
		for module in self._mm.mods("active", type="ui"):
			self.enterWidget = EnterWidget()
			self.teachWidget = TeachWidget()
			self.resultsWidget = self._modules.chooseItem(
				set(self._mm.mods("active", type="testsViewer"))
			).createTestsViewer()
			
			self.fileTab = module.addFileTab(
				_("Media lesson %s") % self.counter,
				self.enterWidget,
				self.teachWidget,
				self.resultsWidget
			)
			
			lesson = Lesson(self, self.fileTab, self.enterWidget, self.teachWidget)
			self.lessonCreated.emit(lesson)
			
			lessons.add(lesson)
		self.counter += 1
		self.lessonCreationFinished.emit()
		return lessons
	
	def loadFromList(self, list, path):
		for lesson in self.createLesson():
			# Load the list
			self.enterWidget.itemList = list
			# Update the widgets
			self.enterWidget.updateWidgets()
			# Update the results widget
			self.resultsWidget.updateList(list)

"""
Lesson object (that means: this techwidget+enterwidget)
"""
class Lesson(object):
	def __init__(self, moduleManager, fileTab, enterWidget, teachWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		self.fileTab = fileTab
		self.stopped = base._mm.createEvent()
		
		self.module = self
		self.list = base.enterWidget.itemList
		self.resources = {}
		self.dataType = "media"
		
		fileTab.closeRequested.handle(self.stop)
	
	def stop(self):
		self.fileTab.close()
		# Stop media playing
		base.enterWidget.mediaDisplay.stop()
		base.teachWidget.mediaDisplay.stop()
		self.stopped.emit()

def init(moduleManager):
	return MediaLessonModule(moduleManager)
