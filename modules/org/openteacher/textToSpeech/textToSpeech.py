#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2011, Milan Boers
#    Copyright 2011, Marten de Vries
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
import shlex

import sys

class DependencyError(Exception): pass

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
			nullDevice = open(os.devnull, "w")
			ret = subprocess.call(["espeak", self.text, "-v" + self.voiceid], stdout=nullDevice, stderr=nullDevice)

class TextToSpeech():
	autoPlay = True
	def __init__(self, pyttsx):
		if os.name == 'nt' or os.name == 'mac':
			self.engine = pyttsx.init(base._mm)
		elif os.name == 'posix':
			self.nullDevice = open(os.devnull, "w")
			#check if espeak was installed
			try:
				subprocess.call(["espeak","--help"], stdout=self.nullDevice, stderr=self.nullDevice)
			except OSError:
				raise DependencyError("Can't initiate text-to-speech. Espeak was not installed.")

	def getVoices(self):
		feedback = []
		if os.name == "nt" or os.name == "mac":
			voices = self.engine.getProperty("voices")
			for voice in voices:
				feedback.append((voice.name, voice.id))
		elif os.name == "posix":
			voices = subprocess.check_output(["espeak", "--voices"]).split("\n")
			for voice in voices:
				voiceProps = shlex.split(voice)
				try:
					int(voiceProps[0])
					feedback.append((voiceProps[3] + " (" + voiceProps[1] + ")", voiceProps[3]))
				except IndexError:
					# voiceProps[0] does not even exist
					pass
				except ValueError:
					# voiceProps[0] is not an int, so this is not a language
					pass
		return feedback
	
	def speak(self, text, rate, voiceid, thread=True):
		if os.name == 'nt' or os.name == 'mac':
			# Set voice
			self.engine.setProperty('voice', voiceid)
			self.engine.setProperty('rate', rate)
			self.engine.say(text)
			if thread:
				st = SpeakThread(self.engine,None,None)
				st.start()
			else:
				self.engine.runAndWait()
		elif os.name == 'posix':
			# Use espeak
			if thread:
				st = SpeakThread(None,voiceid,text)
				st.start()
			else:
				ret = subprocess.call(["espeak", text, "-v" + voiceid], stdout=self.nullDevice, stderr=self.nullDevice)

class TextToSpeechModule(object):
	voiceid = None
	def __init__(self, mm):
		self._mm = mm
		global base
		base = self

		self.type = "textToSpeech"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()
	
		# For Windows and Mac
		pyttsx = self._mm.importFrom(self._mm.resourcePath("tts"), "pyttsx")
		
		# Create text to speech engine
		try:
			self.tts = TextToSpeech(pyttsx)
		except DependencyError as e:
			QtGui.QMessageBox.critical(None, "Error", unicode(e))
		
		self._settings = self._modules.default("active", type="settings")
		
		# Add settings
		self._ttsVoice = self._settings.registerSetting(**{
			"internal_name": "org.openteacher.textToSpeech.voice",
			"name": "Voice",
			"type": "options",
			"category": "Pronounciation",
			"subcategory": "Voice",
			"defaultValue": self.tts.getVoices()[0][1],
			"options": self.tts.getVoices(),
		})
		self._ttsSpeed = self._settings.registerSetting(**{
			"internal_name": "org.openteacher.textToSpeech.speed",
			"name": "Speed",
			"type": "number",
			"category": "Pronounciation",
			"subcategory": "Voice",
			"defaultValue": 120,
		})

		# Create the say word event
		self.say = self._modules.default(type="event").createEvent()

		self.say.handle(self.newWord)
		
		self.active = True
		#self.newWord("Text to speech enabled")

	def _retranslate(self):
		#Translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

	def disable(self):
		del self._modules
		del name
		try:
			del self.tts
		except AttributeError:
			pass
		del self.say
		self.active = False
	
	def newWord(self, word, thread=True):
		# First voice as default/if none is selected
		voiceid = self.tts.getVoices()[0][1]
		# Get the selected voice
		if self._ttsVoice != None:
			voiceid = self._ttsVoice["value"]
		speed = 120
		# Get the selected speed
		if self._ttsSpeed:
			speed = self._ttsSpeed["value"]
		# Pronounce
		self.tts.speak(word,speed,voiceid,thread)

def init(moduleManager):
	return TextToSpeechModule(moduleManager)
