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

from PyQt4 import QtCore
from PyQt4 import QtGui

import os
import subprocess
import threading

import sys

class DependencyError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SpeakThread(threading.Thread):
	def __init__(self,engine,voiceid,text):
		threading.Thread.__init__(self)
		if os.name == 'nt' or os.name == 'mac':
			self.engine = engine
		elif os.name == 'posix':
			self.voiceid = voiceid
			self.text = text
			
	def run(self):
		if os.name == 'nt' or os.name == 'mac':
			self.engine.runAndWait()
		elif os.name == 'posix':
			ret = subprocess.call(["espeak", self.text, "-v" + self.voiceid])

class TextToSpeech():
	autoPlay = True
	def __init__(self, pyttsx):
		if os.name == 'nt' or os.name == 'mac':
			self.engine = pyttsx.init()
		elif os.name == 'posix':
			#check if espeak was installed
			try:
				subprocess.call(["espeak","--help"])
			except OSError:
				raise DependencyError("Can't initiate text-to-speech. Espeak was not installed.")
	
	def getVoices(self):
		feedback = []
		voiceids = []
		voicenames = []
		if os.name == 'nt' or os.name == 'mac':
			voices = self.engine.getProperty('voices')
			for voice in voices:
				 voicenames.append(voice.name)
				 voiceids.append(voice.id)
		elif os.name == 'posix':
			voiceids.append("en")
			voicenames.append("default")
		feedback.append(voicenames)
		feedback.append(voiceids)
		return feedback
	
	def speak(self, text, rate, voiceid, thread=True):
		if os.name == 'nt' or os.name == 'mac':
			# set voice
			self.engine.setProperty('voice', voiceid)
			self.engine.setProperty('rate',rate)
			self.engine.say(text)
			if thread:
				st = SpeakThread(self.engine,None,None)
				st.start()
			else:
				self.engine.runAndWait()
		elif os.name == 'posix':
			#use espeak
			if thread:
				st = SpeakThread(None,voiceid,text)
				st.start()
			else:
				ret = subprocess.call(["espeak", text, "-v" + voiceid])

class TextToSpeechModule(object):
	voiceid = None
	def __init__(self, mm):
		self.mm = mm
		self.supports = ("initializing", "textToSpeech")
		self.requires = (1,0)
		
		# Create the say word event
		self.say = self.mm.createEvent()
	
	def initialize(self):
		for module in self.mm.activeMods.supporting("modules"):
			module.registerModule("Text to speech", self)
	
	def enable(self):
		#For Windows and Mac
		tts = self.mm.import_("tts")
		from tts import pyttsx
		
		print "pyttsx" in sys.modules
		print "tts" in sys.modules
		
		#text to speech engine maken
		try:
			self.tts = TextToSpeech(pyttsx)
		except DependencyError as e:
			QtGui.QMessageBox.critical(None, "Error", QtCore.QString(e))
		
		self.voiceid = self.tts.getVoices()[1][0]
		
		self.say.handle(self.newWord)
		
		self.active = True
		self.newWord("Text to speech enabled")
	
	def disable(self):
		self.active = False
	
	def close(self):
		print "Closed!"
	
	def newWord(self, word, thread=True):
		if self.voiceid <> None:
			self.tts.speak(word,120,self.voiceid,thread)
		else:
			self.setVoice()
	
	def newWordNewThread(self,word):
		SpeakThread("lol").start()
	
	def setVoice(self, parent):
		voices = self.tts.getVoices()
		dialog = QtGui.QDialog(parent)
		ret = dialog.show()

def init(moduleManager):
	return TextToSpeechModule(moduleManager)
