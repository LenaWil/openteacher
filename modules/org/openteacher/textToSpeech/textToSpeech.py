#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2011, Milan Boers
#    Copyright 2011-2012, Marten de Vries
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

import os
import subprocess
import threading
import shlex
import StringIO

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

class TextToSpeech(object):
	autoPlay = True
	def __init__(self, pyttsx, _mm):
		if os.name == 'nt' or os.name == 'mac':
			self.engine = pyttsx.init(_mm)
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
			#This doesn't use check_output() because that would break Python 2.6 compatibility.
			process = subprocess.Popen(["espeak", "--voices"], stdout=subprocess.PIPE)
			voices = process.communicate()[0].split("\n")
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

		self.type = "textToSpeech"
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="dialogShower"),
		)
		self.requires = (
			self._mm.mods(type="event"),
		)
		self.filesWithTranslations = ("textToSpeech.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()
		
		self.active = True
		
		#t = threading.Thread(target=self._enable)
		#t.start()
		self._enable()
		
	def _enable(self):
		# For Windows and Mac
		pyttsx = self._mm.importFrom(self._mm.resourcePath("tts"), "pyttsx")

		# Create text to speech engine
		try:
			self.tts = TextToSpeech(pyttsx, self._mm)
		except DependencyError as e:
			try:
				m = self._modules.default("active", type="dialogShower")
				m.showBigError.send(unicode(e))
			except IndexError:
				pass
		else:
			settings = self._modules.default(type="settings")
			
			# Add settings
			self._ttsVoice = settings.registerSetting(**{
				"internal_name": "org.openteacher.textToSpeech.voice",
				"type": "option",
				"defaultValue": self.tts.getVoices()[0][1],
				"options": self.tts.getVoices(),
			})
			self._ttsSpeed = settings.registerSetting(**{
				"internal_name": "org.openteacher.textToSpeech.speed",
				"type": "number",
				"defaultValue": 120,
				"minValue": 1,
			})
			self._retranslate()

			# Create the say word event
			self.say = self._modules.default(type="event").createEvent()

			self.say.handle(self.newWord)

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

		try:
			self._ttsVoice["name"] = _("Voice name (language)")
			self._ttsSpeed["name"] = _("Speed")

			categories = {
				"category": _("Pronounciation"),
				"subcategory": _("Voice"),
			}
			self._ttsVoice.update(categories)
			self._ttsSpeed.update(categories)
		except AttributeError:
			#first time retranslate
			pass

	def disable(self):
		del self._modules
		if hasattr(self, "tts"):
			del self.tts
		if hasattr(self, "say"):
			del self.say
		if hasattr(self, "_ttsVoice"):
			del self._ttsVoice
		if hasattr(self, "_ttsSpeed"):
			del self._ttsSpeed

		self.active = False
	
	def newWord(self, word, thread=True):
		# First voice as default/if none is selected
		voiceid = self.tts.getVoices()[0][1]
		# Get the selected voice
		if self._ttsVoice is not None:
			voiceid = self._ttsVoice["value"]
		speed = 120
		# Get the selected speed
		if self._ttsSpeed:
			speed = self._ttsSpeed["value"]
		# Pronounce
		self.tts.speak(word,speed,voiceid,thread)

def init(moduleManager):
	return TextToSpeechModule(moduleManager)
