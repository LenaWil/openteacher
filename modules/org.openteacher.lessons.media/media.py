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
from PyQt4 import QtWebKit
from PyQt4 import QtNetwork
from PyQt4.phonon import Phonon

import os
import time
import mimetypes
import fnmatch

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

class Item(object):
	def __init__(self,filename,remote,hints = "",desc = ""):
		if remote == False:
			self.name = os.path.splitext(os.path.basename(str(filename)))[0]
		else:
			self.name = filename
		self.filename = filename
		self.remote = remote
		self.hints = hints
		self.desc = desc

class MediaControlDisplay(QtGui.QWidget):
	def __init__(self,autoplay=True,*args, **kwargs):
		super(MediaControlDisplay, self).__init__(*args, **kwargs)
		
		self.mediadisplay = MediaDisplay()
		self.mediadisplay.videoplayer.mediaObject().stateChanged.connect(self._playPauseButtonUpdate)
		
		layout = QtGui.QVBoxLayout()
		
		buttonsLayout = QtGui.QHBoxLayout()
		
		self.pausebutton = QtGui.QPushButton()
		self.pausebutton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause",QtGui.QIcon(base.api.resourcePath("icons/player_pause.png"))))
		self.pausebutton.clicked.connect(self.playPause)
		buttonsLayout.addWidget(self.pausebutton)
		
		self.seekslider = Phonon.SeekSlider(self.mediadisplay.videoplayer.mediaObject())
		buttonsLayout.addWidget(self.seekslider)
		
		self.volumeslider = Phonon.VolumeSlider(self.mediadisplay.videoplayer.audioOutput())
		self.volumeslider.setMaximumWidth(100)
		buttonsLayout.addWidget(self.volumeslider)
		
		layout.addWidget(self.mediadisplay)
		layout.addLayout(buttonsLayout)
		
		self.setLayout(layout)
	
	def showLocalMedia(self, path):
		self.mediadisplay.showLocalMedia(path)
		self.setControls()
	
	def showRemoteMedia(self, path):
		self.mediadisplay.showRemoteMedia(path)
		self.setControls()
	
	def _playPauseButtonUpdate(self, newstate, oldstate):
		if self.mediadisplay.videoplayer.isPaused():
			self.pausebutton.setIcon(QtGui.QIcon.fromTheme("media-playback-play",QtGui.QIcon(base.api.resourcePath("icons/player_play.png"))))
		else:
			self.pausebutton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause",QtGui.QIcon(base.api.resourcePath("icons/player_pause.png"))))
	
	def setControls(self):
		if self.mediadisplay.activeType == 2 or self.mediadisplay.activeType == 0 or self.mediadisplay.activeType == 4:
			self.setControlsEnabled(False)
		else:
			self.setControlsEnabled(True)
	
	def setControlsEnabled(self, enabled):
		self.pausebutton.setEnabled(enabled)
		self.volumeslider.setEnabled(enabled)
		self.seekslider.setEnabled(enabled)
	
	def playPause(self, event):
		if self.mediadisplay.videoplayer.isPaused():
			self.mediadisplay.videoplayer.play()
		else:
			self.mediadisplay.videoplayer.pause()
	
	def clear(self):
		self.mediadisplay.clear()
		
class MediaDisplay(QtGui.QStackedWidget):
	def __init__(self,*args, **kwargs):
		super(MediaDisplay, self).__init__(*args, **kwargs)
				
		"""
		0: No active media
		1: Video
		2: Image
		3: Audio
		4: Web site
		"""
		self.activeType = 0
		
		self.videoplayer = Phonon.VideoPlayer(Phonon.VideoCategory, self)
		self.webviewer = QtWebKit.QWebView()
		self.webviewer.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
		
		self.addWidget(self.webviewer)
		self.addWidget(self.videoplayer)
		
	def showLocalMedia(self, path):
		type = mimetypes.guess_type(str(path))[0].split('/')[0]
		
		# Check MIME-type and go to the right code
		if type == 'video':
			self._showVideo(path)
		elif type == 'image':
			self._showImage(path)
		elif type == 'audio':
			self._showAudio(path)
	
	def showRemoteMedia(self, path):
		# Check if this is a youtube video
		if fnmatch.fnmatch(str(path), "*youtube.*/watch?v=*"):
			# Youtube URL
			path = path.split("/watch?v=")[1]
			path = path.split("&")[0]
			path = "http://www.youtube.com/embed/" + path
		# Check if this is a vimeo video
		if fnmatch.fnmatch(str(path), "*vimeo.com/*"):
			# Vimeo URL
			path = path.split("vimeo.com/")[1]
			path = "http://player.vimeo.com/video/" + path + "?title=0&amp;byline=0&amp;portrait=0&amp;color=ffffff"
		# Check if this is a dailymotion video
		if fnmatch.fnmatch(str(path), "*dailymotion.com/video/*"):
			# Dailymotion URL
			path = path.split("dailymotion.com/video/")[1]
			path = path.split("_")[0]
			path = "http://www.dailymotion.com/embed/video/" + path
		self._showUrl(path)
	
	def _showImage(self, path):
		# Stop any media playing
		self.videoplayer.stop()
		# Set the widget to the web view
		self.setCurrentWidget(self.webviewer)
		# Go to the right URL
		self.webviewer.setUrl(QtCore.QUrl(path))
		# Set the active type
		self.activeType = 2
	
	def _showVideo(self, path):
		# Set the widget to video player
		self.setCurrentWidget(self.videoplayer)
		# Play the video
		self.videoplayer.play(Phonon.MediaSource(path))
		# Set the active type
		self.activeType = 1
	
	def _showAudio(self, path):
		# Set widget to web viewer
		self.setCurrentWidget(self.webviewer)
		# Set some nice html
		self.webviewer.setHtml('''
		<html><head><title>Audio</title></head><body>Playing audio</body></html>
		''')
		# Play the audio
		self.videoplayer.play(Phonon.MediaSource(path))
		# Set the active type
		self.activeType = 3
	
	def _showUrl(self, url):
		# Set widget to web viewer
		self.setCurrentWidget(self.webviewer)
		# Set the URL
		self.webviewer.setUrl(QtCore.QUrl(url))
		# Set the active type
		self.activeType = 4
	
	def clear(self):
		self.webviewer.setHtml('''
		<html><head><title>Nothing</title></head><body></body></html>
		''')
		self.videoplayer.stop()
		# Set the active type
		self.activeType = 0

class EnterItemListModel(QtCore.QAbstractListModel):
	def __init__(self,items,parent=None,*args):
		QtCore.QAbstractListModel.__init__(self,parent,*args)
		
		self.listdata = []
		
		for item in items.items:
			self.listdata.append(item.name)
	
	def update(self,items):
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
		
		self.listdata = []
		
		for item in items.items:
			self.listdata.append(item.name)
		
		self.endInsertRows()
	
	def rowCount(self,parent=QtCore.QModelIndex()):
		return len(self.listdata)

	def data(self,index,role):
		if index.isValid() and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.listdata[index.row()])
		else:
			return QtCore.QVariant()
	
	def textAtIndex(self,index):
		return self.listdata[index]

class EnterItemList(QtGui.QListView):
	def __init__(self,parent):
		QtGui.QListView.__init__(self,parent)
		self.parent = parent
		
		self.lm = EnterItemListModel(parent.itemList,self)
		self.setModel(self.lm)
	
	def update(self):
		self.lm.update(base.enterWidget.itemList)
	
	def selectionChanged(self,current,previous):
		current = self.lm.textAtIndex(self.selectedIndexes()[0].row())
		
		for item in base.enterWidget.itemList.items:
			if item.name == current:
				self.parent.setActiveItem(item)

class EnterWidget(QtGui.QSplitter):
	def __init__(self,*args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self.itemList = List()
		
		self.enterItemsList = EnterItemList(self)
		
		removeButton = QtGui.QPushButton("Remove")
		removeButton.clicked.connect(self.removeItem)
		addLocalButton = QtGui.QPushButton("Add local media")
		addLocalButton.clicked.connect(self.addLocalItems)
		addRemoteButton = QtGui.QPushButton("Add remote media")
		addRemoteButton.clicked.connect(self.addRemoteItems)
		
		leftBottom = QtGui.QHBoxLayout()
		leftBottom.addWidget(removeButton)
		leftBottom.addWidget(addLocalButton)
		leftBottom.addWidget(addRemoteButton)
		
		left = QtGui.QVBoxLayout()
		left.addWidget(self.enterItemsList)
		left.addLayout(leftBottom)
		leftW = QtGui.QWidget()
		leftW.setLayout(left)
		
		self.enterpreview = MediaControlDisplay(False)
		
		self.entername = QtGui.QLineEdit()
		self.entername.textChanged.connect(self.changeName)
		self.entername.setEnabled(False)
		
		nameL = QtGui.QHBoxLayout()
		nameL.addWidget(QtGui.QLabel("Name:"))
		nameL.addWidget(self.entername)
		
		descl = QtGui.QLabel("Description:")
		
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
		rightSplitter.addWidget(self.enterpreview)
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
		filenames = QtGui.QFileDialog.getOpenFileNames(self,"Select file(s)",QtCore.QDir.homePath(),"Media (*.bmp *.jpg *.jpeg *.png *.wmv *.mp3 *.avi)")
		for filename in filenames:
			self.addItem(filename, False)
	
	"""
	Add items from the internet to the list
	"""
	def addRemoteItems(self):
		url, dialog = QtGui.QInputDialog.getText(self, "File URL", "Enter the URL of your website or media item.\nSupported video sites: YouTube, Dailymotion, Vimeo.")
		if dialog:
			self.addItem(url, True)
	
	"""
	Add an item to the list
	"""
	def addItem(self,filename,remote=False):
		item = Item(filename,remote)
		self.itemList.items.append(item)
		self.enterItemsList.update()
	
	"""
	Remove an item from the list
	"""
	def removeItem(self):
		self.itemList.items.remove(self.activeitem)
		self.enterItemsList.update()
		self.enterpreview.clear()
		self.entername.setText("")
		self.entername.setEnabled(False)
		self.enterdesc.setText("")
		self.enterdesc.setEnabled(False)
	
	"""
	Change the active item
	"""
	def setActiveItem(self,item):
		self.activeitem = item
		self.entername.setEnabled(True)
		self.entername.setText(item.name)
		self.enterdesc.setEnabled(True)
		self.enterdesc.setText(item.desc)
		if item.remote:
			self.enterpreview.showRemoteMedia(item.filename)
		else:
			self.enterpreview.showLocalMedia(item.filename)
	
	"""
	Change the name of the active item
	"""
	def changeName(self):
		self.activeitem.name = self.entername.text()
		self.enterItemsList.update()
	
	"""
	Change the description of the active item
	"""
	def changeDesc(self):
		self.activeitem.desc = self.enterdesc.toPlainText()
	
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
		try:
			base.teachWidget.initiateLesson()
		except AttributeError:
			pass
	
	"""
	Get the current lesson type
	"""
	@property
	def currentLessonType(self):
		for lessontype in self._lessonTypeModules:
			if lessontype.name == self.currentText():
				return lessontype

class TeachWidget(QtGui.QWidget):
	def __init__(self,*args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		#draw the GUI
		
		top = QtGui.QHBoxLayout()
		
		label = QtGui.QLabel("Lesson type:")
		self.lessonTypeChooser = LessonTypeChooser()
		
		top.addWidget(label)
		top.addWidget(self.lessonTypeChooser)
		
		self.mediaDisplay = MediaControlDisplay()
		
		self.answerfield = QtGui.QLineEdit()
		self.answerfield.returnPressed.connect(self.checkAnswerButtonClick)
		checkButton = QtGui.QPushButton("Check")
		checkButton.clicked.connect(self.checkAnswerButtonClick)
		self.progress = QtGui.QProgressBar()
		
		bottomL = QtGui.QHBoxLayout()
		bottomL.addWidget(self.answerfield)
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
		self.lesson.checkAnswer()
		self.answerfield.clear()
		self.answerfield.setFocus()
	
	"""
	What happens when you click the Teach tab
	"""
	def showEvent(self,event):
		if len(base.enterWidget.itemList.items) == 0:
			QtGui.QMessageBox.critical(self, "Not enough items", "You need to add items to your test first")
			base.fileTab.currentTab = base.enterWidget
		elif not base.inlesson:
			self.initiateLesson()

class MediaLesson(object):
	def __init__(self,itemList):
		#stop media playing in the enter widget
		base.enterWidget.enterpreview.clear()
		
		self.lessonType = base.teachWidget.lessonTypeChooser.currentLessonType.createLessonType(itemList,range(len(itemList.items)))
		
		self.lessonType.newItem.handle(self.nextQuestion)
		self.lessonType.lessonDone.handle(self.endLesson)
		
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
		#set the mediawidget to the right location
		if self.currentItem.remote:
			base.teachWidget.mediaDisplay.showRemoteMedia(self.currentItem.filename)
		else:
			base.teachWidget.mediaDisplay.showLocalMedia(self.currentItem.filename)
	
	"""
	Ends the lesson
	"""
	def endLesson(self):
		base.inlesson = False
		# FIXME : message with results
		# stop media
		base.teachWidget.mediaDisplay.clear()
		# return to enter tab
		base.fileTab.currentTab = base.enterWidget
	
	"""
	Updates the progress bar
	"""
	def _updateProgressBar(self):
		base.teachWidget.progress.setMaximum(self.lessonType.totalItems+1)
		base.teachWidget.progress.setValue(self.lessonType.askedItems)

class MediaLessonModule(object):
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
			module.registerModule("Media Lesson", self)
	
	def enable(self):
		self.type = "Items"
		
		self.lessonCreated = self.api.createEvent()
		
		for module in self.api.mods.supporting("ui"):
			event = module.addLessonCreateButton("Create media lesson")
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
				"Media lesson %s" % self.counter,
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
	return MediaLessonModule(moduleManager)