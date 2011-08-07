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
from PyQt4 import QtWebKit
from PyQt4 import QtNetwork
from PyQt4.phonon import Phonon

import os
import time
import mimetypes
import fnmatch
import tempfile

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
	
	def showMedia(self, path, remote):
		for module in base._mm.mods("active", type="mediaType"):
			if module.supports(path):
				module.showMedia(module.path(path, self.autoplay), self.mediaDisplay)
				self.activeModule = module
				break
		
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
		
		self.entername = QtGui.QLineEdit()
		self.entername.textChanged.connect(self.changeName)
		self.entername.setEnabled(False)
		
		nameL = QtGui.QHBoxLayout()
		nameL.addWidget(QtGui.QLabel(_("Name:")))
		nameL.addWidget(self.entername)
		
		descl = QtGui.QLabel(_("Description:"))
		
		self.enterdesc = QtGui.QTextEdit()
		self.enterdesc.textChanged.connect(self.changeDesc)
		self.enterdesc.setEnabled(False)
		
		desceditL = QtGui.QVBoxLayout()
		desceditL.addLayout(nameL)
		desceditL.addWidget(descl)
		desceditL.addWidget(self.enterdesc)
		
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
		filenames = QtGui.QFileDialog.getOpenFileNames(self,_("Select file(s)"),QtCore.QDir.homePath(),_("Media") + " (*.bmp *.jpg *.jpeg *.png *.wmv *.mp3 *.avi)")
		for filename in filenames:
			self.addItem(filename, False)
	
	"""
	Add items from the internet to the list
	"""
	def addRemoteItems(self):
		url, dialog = QtGui.QInputDialog.getText(self, _("File URL"), _("Enter the URL of your website or media item.\nSupported video sites: YouTube, Dailymotion, Vimeo."))
		if dialog:
			self.addItem(url, True)
	
	"""
	Add an item to the list
	"""
	def addItem(self,filename,remote=False):
		name = filename
		if not remote:
			name = os.path.splitext(os.path.basename(str(name)))[0]
		
		item = {
			"remote": remote,
			"filename": str(filename),
			"name": str(name),
			"hints": str(),
			"desc": str()
		}
		self.itemList["items"].append(item)
		self.enterItemList.update()
	
	"""
	Remove an item from the list
	"""
	def removeItem(self):
		self.itemList["items"].remove(self.activeitem)
		self.enterItemList.update()
		self.mediaDisplay.clear()
		self.entername.setText("")
		self.entername.setEnabled(False)
		self.enterdesc.setText("")
		self.enterdesc.setEnabled(False)
		self.enterItemList.setRightActiveItem()
	
	"""
	Change the active item
	"""
	def setActiveItem(self,item):
		self.activeitem = item
		self.entername.setEnabled(True)
		self.entername.setText(item["name"])
		self.enterdesc.setEnabled(True)
		self.enterdesc.setText(item["desc"])
		self.mediaDisplay.showMedia(item["filename"], item["remote"])
	
	"""
	Change the name of the active item
	"""
	def changeName(self):
		self.activeitem["name"] = str(self.entername.text())
		self.enterItemList.update()
	
	"""
	Change the description of the active item
	"""
	def changeDesc(self):
		self.activeitem["desc"] = unicode(self.enterdesc.toPlainText())
	
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
The dropdown menu to choose lesson type
"""
class LessonTypeChooser(QtGui.QComboBox):
	def __init__(self,*args,**kwargs):
		super(LessonTypeChooser, self).__init__(*args, **kwargs)
		
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
The teach tab
"""
class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		#draw the GUI
		
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel(_("Lesson type:"))
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		self.mediaDisplay = MediaControlDisplay(True)
		
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
		layout.addLayout(bottomL)
		
		self.setLayout(layout)
	
	"""
	Starts the lesson
	"""
	def initiateLesson(self):
		self.lesson = MediaLesson(base.enterWidget.itemList)
		self.answerField.setFocus()
	
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
The lesson itself
"""
class MediaLesson(object):
	def __init__(self,itemList,*args,**kwargs):
		super(MediaLesson, self).__init__(*args, **kwargs)
		
		#stop media playing in the enter widget
		base.enterWidget.mediaDisplay.clear()
		
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(itemList,range(len(itemList["items"])))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
		self.lessonType.start()
		
		base.inLesson = True
		
		# Reset the progress bar
		base.teachWidget.progress.setValue(0)
	
	"""
	Check whether the given answer was right or wrong
	"""
	def checkAnswer(self):
		if self.currentItem["name"] == base.teachWidget.answerField.text():
			# Answer was right
			self.lessonType.setResult("right")
			# Progress bar
			self._updateProgressBar()
		else:
			# Answer was wrong
			self.lessonType.setResult("wrong")
			
	"""
	What happens when the next question should be asked
	"""
	def nextQuestion(self, item):
		# set the next question
		self.currentItem = item
		# set the mediawidget to the right location
		base.teachWidget.mediaDisplay.showMedia(self.currentItem["filename"], self.currentItem["remote"])
	
	"""
	Ends the lesson
	"""
	def endLesson(self):
		base.inLesson = False
		# FIXME : message with results
		# stop media
		base.teachWidget.mediaDisplay.clear()
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget
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

	def enable(self):
		#setup translation
		global _
		global ngettext

		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		for module in self._mm.mods("active", type="modules"):
			module.registerModule(_("Media Lesson"), self)

		self.dataType = "media"
		
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
			
			self.fileTab = module.addFileTab(
				_("Media lesson %s") % self.counter,
				self.enterWidget,
				self.teachWidget
			)
			
			lesson = Lesson(self, self.fileTab, self.enterWidget, self.teachWidget)
			self.lessonCreated.emit(lesson)
			
			lessons.add(lesson)
		self.counter += 1
		self.lessonCreationFinished.emit()
		return lessons
	
	def loadFromList(self, list):
		for lesson in self.createLesson():
			for item in list["list"]["items"]:
				self.enterWidget.addItem(os.path.join(tempfile.gettempdir(), "openteacher\org\loaders\otmd\\" + list["resources"]["uuid"] + "\\" + item["filename"]), item["remote"])

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
