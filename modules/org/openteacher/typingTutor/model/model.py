#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

import random
import math

class TypeDataStore(object):
	#to generate:
	#>>> print str([x for x in "zxcvbnm,./"]).replace("'", '"')
	QWERTY_LAYOUT = [
		["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Back-\nspace"],
		["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
		["Caps\nLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
		["Shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Shift"],
		["Space"],
	]

	COLEMAK_LAYOUT = [
		["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Back-\nspace"],
		["Tab", "q", "w", "f", "p", "g", "j", "l", "u", "y", ";", "[", "]", "\\"],
		["Back-\nspace", "a", "r", "s", "t", "d", "h", "n", "e", "i", "o", "'", "Enter"],
		["Shift", "z", "x", "c", "v", "b", "k", "m", ",", ".", "/", "Shift"],
		["Space"],
	]

	DVORAK_LAYOUT = [
		["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[", "]", "Back-\nspace"],
		["Tab", "'", ",", ".", "p", "y", "f", "g", "c", "r", "l", "/", "=", "\\"],
		["Caps\nLock", "a", "o", "e", "u", "i", "d", "h", "t", "n", "s", "-", "Enter"],
		["Shift", ";", "q", "j", "k", "x", "b", "m", "w", "v", "z", "Shift"],
		["Space"],
	]

	def __init__(self, *args, **kwargs):
		#FIXME: load from sqlite database/dataStore OT module/whatever instead of dummy data.
		self._users = {}
		self.registerUser("commandoline")

	def registerUser(self, name, keyboardLayout=None):
		if not keyboardLayout:
			keyboardLayout = self.QWERTY_LAYOUT
		if name in self._users:
			raise ValueError("Username already in use.")
		self._users[name] = {
			"level": 0,
			"results": [],
			"layout": keyboardLayout,
		}
		self._setNewExerciseFor(self._users[name])

	@staticmethod
	def _createRow(letters):
		row = list(letters * int(math.ceil(80.0 / len(letters))))
		random.shuffle(row)
		for i in range(-1, 80, 6):
			row.insert(i, " ")
		return u"".join(row[:59])

	def currentExercise(self, username):
		return self._users[username]["currentExercise"]

	def currentInstruction(self, username):
		return self._users[username]["currentInstruction"]

	def layout(self, username):
		return self._users[username]["layout"]

	def setResult(self, username, time, amountOfMistakes):
		user = self._users[username]
		user["results"].append({
			"time": time,
			"amountOfMistakes": amountOfMistakes,
			"exercise": user["currentExercise"],
		})
		#calculate new level
		if amountOfMistakes == 0:
			user["level"] += 1

		#get new exercise
		self._setNewExerciseFor(user)

	def _setNewExerciseFor(self, user):
		user["currentExercise"] = self._createRow({
			0: user["layout"][2][4] + user["layout"][2][7],
			1: user["layout"][2][1:5],
			2: user["layout"][2][7:11],
			3: user["layout"][2][4:8],
			4: user["layout"][2][1:11],
		}[user["level"]])

		if user["level"] == 0 and not user["results"]:
			instr = """Welcome, I'm your personal OpenTeacher typing tutor. We'll improve your typing skills by doing simple exercises. Between the exercises, I'll give instructions. Let's get started:

First place your fingers on the so-called home row: your fingers, from left to right, should always be on the keys a, s, d, f, space, space, j, k, l and ; while not typing another character. When your fingers are in position, press
space to start the first lesson. Work for accuracy at first, not speed.
"""
		elif user["level"] == 0 and len(user["results"]) == 1:
			instr = """Congratulations, you finished your first exercise! You made %s mistake(s) though, so try again until you can do it flawless!""" % user["results"][-1]["amountOfMistakes"]
		elif user["level"] == 0:
			instr = "Almost there. %s mistakes left. Please try again." %  user["results"][-1]["amountOfMistakes"]
		elif user["level"] == 1 and len(user["results"]) == 1:
			instr = "Congratulations, you finished your first exercise! And apart from that, you also made no mistakes! Let's try the next two letters: a and s"
		elif user["level"] == 1:
			instr = "You made it, keep up the good work while practising a and s."
		else:
			instr = "Naah"
		user["currentInstruction"] = instr

	@staticmethod
	def wordsPerMinute(cls, result):
		amountOfWords = len(result["exercise"]) / 5.0
		minutes = result["time"] / 60.0

		return int(round(amountOfWords / minutes))

	@property
	def usernames(self):
		return sorted(self._users.keys())

class TypingTutorModelModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTutorModelModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingTutorModel"
		self.filesWithTranslations = ("model.py",)

	def enable(self):
		self.model = TypeDataStore()

		self.active = True

	def disable(self):
		self.active = False

		del self.model

def init(moduleManager):
	return TypingTutorModelModule(moduleManager)
