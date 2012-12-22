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

	BELGIAN_AZERTY_LAYOUT = [
		[u"²", "&", u"é", '"', "'", "(", u"§", u"è", "!", u"ç", u"à", ")", "-", "Back-\nspace"],
		["Tab", "a", "z", "e", "r", "t", "y", "u", "i", "o", "p", "^", "$", "Enter"],
		["Caps\nLock", "q", "s", "d", "f", "g", "h", "j", "k", "l", "m", u"ù", u"µ"],
		["Shift", "<", "x", "x", "c", "v", "b", "n", ",", ";", ":", "=", "Shift"],
		["Space"],
	]

	FRENCH_AZERTY_LAYOUT = [
		[u"²", "&", u"é", '"', "'", "(", "-", u"è", "_", u"ç", u"à", ")", "=", "Back-\nspace"],
		["Tab", "a", "z", "e", "r", "t", "y", "u", "i", "o", "p", "^", "$", "Enter"],
		["Caps\nLock", "q", "s", "d", "f", "g", "h", "j", "k", "l", "m", u"ù", u"µ"],
		["Shift", "<", "x", "x", "c", "v", "b", "n", ",", ";", ":", "!", "Shift"],
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

	QWERTZ_LAYOUT = [
		["^", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", u"ß", u"´", "Back-\nspace"],
		["Tab", "q", "w", "e", "r", "t", "z", "u", "i", "o", "p", u"ü", "+", "Enter"],
		["Caps\nLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", u"ö", u"ä", "#"],
		["Shift", "<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-", "Shift"],
		["Space"],
	]

	class UsernameEmptyError(ValueError):
		pass

	class UsernameTakenError(ValueError):
		pass

	def __init__(self, words, data, *args, **kwargs):
		super(TypeDataStore, self).__init__(*args, **kwargs)
		self._words = words
		self._users = data

		self._retranslate()

	def _retranslate(self):
		#FIXME
		_ = unicode
		self.layouts = sorted([
			("BELGIAN_AZERTY_LAYOUT", _("Belgian AZERTY")),
			("COLEMAK_LAYOUT", _("Colemak")),
			("DVORAK_LAYOUT", _("Dvorak Simplified Keyboard")),
			("FRENCH_AZERTY_LAYOUT", _("French AZERTY")),
			("QWERTY_LAYOUT", _("QWERTY")),
			("QWERTZ_LAYOUT", _("QWERTZ")),
		], key=lambda t: t[1])

	def registerUser(self, name, keyboardLayout=None):
		keyboardLayout = getattr(self, keyboardLayout, self.QWERTY_LAYOUT)
		name = name.strip()
		if not name:
			raise self.UsernameEmptyError()
		if name in self._users:
			raise self.UsernameTakenError()
		self._users[name] = {
			"level": 0,
			"results": [],
			"layout": keyboardLayout,
		}

	@staticmethod
	def _createRow(letters):
		row = list(letters * int(math.ceil(80.0 / len(letters))))
		random.shuffle(row)
		for i in range(-1, 80, 6):
			row.insert(i, " ")
		return u"".join(row[:59])

	def currentExercise(self, username):
		user = self._users[username]

		exercises = []

		#generate exercises to learn the most commonly used keys
		#automatically. This first learns letters in pairs, then in
		#larger groups.
		rows = [2, 1, 3, 0]
		for row in rows:
			exercises.extend([
				user["layout"][row][4] + user["layout"][row][7],
				user["layout"][row][3] + user["layout"][row][8],
				user["layout"][row][2] + user["layout"][row][9],
				user["layout"][row][1] + user["layout"][row][10],
				user["layout"][row][1:5],
				user["layout"][row][7:11],
				#<- FIXME: extra instruction required here (finger position)
				user["layout"][row][5:7],
				user["layout"][row][4:8],
				user["layout"][row][1:11],
			])
		#add an exercise which just uses all letters
		everything = "".join(["".join(user["layout"][row][1:11]) for row in rows])
		exercises.append(everything)

		if user["level"] < len(exercises):
			#first practise the keys needed
			letters = exercises[user["level"]]
			user["currentExercise"] = self._createRow(letters)
		else:
			#then practise typing words to improve speed.
			user["currentExercise"] = " ".join(random.sample(self._words, 8))

		return user["currentExercise"]

	def currentInstruction(self, username):
		user = self._users[username]

		#sentences are added to the instruction depending on how the
		#user did, what the current level is, how many results there are
		#already, etc.
		instr = ""

		if not user["results"]:
			instr += u"""Welcome, I'm your personal OpenTeacher typing tutor. We'll improve your typing skills by doing simple exercises. Between the exercises, I'll give instructions. Let's get started:

First place your fingers on the so-called home row: your fingers, from left to right, should always be on the keys '{a}', '{s}', '{d}', '{f}', '{space}', '{space}', '{j}', '{k}', '{l}' and '{;}' while not typing another character. When your fingers are in position, press {space} to start the first lesson. Work for accuracy at first, not speed.

""".format(**{
	"a": user["layout"][2][1],
	"s": user["layout"][2][2],
	"d": user["layout"][2][3],
	"f": user["layout"][2][4],
	"space": user["layout"][4][0].lower(),
	"j": user["layout"][2][7],
	"k": user["layout"][2][8],
	"l": user["layout"][2][9],
	";": user["layout"][2][10],
})

		if len(user["results"]) == 1:
			instr += "Congratulations, you finished your first exercise!\n\n"

		if user["results"] and user["results"][-1]["amountOfMistakes"] == 0:
			instr += "You made zero mistakes, so you can continue practising some new letters. Keep up the good work!\n\n"
		#FIXME: TODO. also check if it went wrong multiple times, and show a varying message then. So it stays a bit 'personal'.
		#Also for success.
		if user["results"] and user["results"][-1]["amountOfMistakes"] != 0:
			#TODO: ngettext required.
			instr += "You made %s mistakes, please try again until you can do it flawless. If that seems hard, try slowing down a bit." % user["results"][-1]["amountOfMistakes"]

		#check for last exercise

		return instr.strip()

	def layout(self, username):
		return self._users[username]["layout"]

	def setResult(self, username, time, amountOfMistakes):
		user = self._users[username]
		user["results"].append({
			"time": time,
			"amountOfMistakes": amountOfMistakes,
			"exercise": user["currentExercise"],
			"level": user["level"],
		})
		#calculate new level
		if amountOfMistakes == 0:
			user["level"] += 1

	@staticmethod
	def _wordsPerMinute(result):
		#a word is fixed to five chars, as is normal when calculating
		#words per minute.
		amountOfWords = len(result["exercise"]) / 5.0
		minutes = result["time"] / 60.0

		return int(round(amountOfWords / minutes))

	def amountOfMistakes(self, username):
		user = self._users[username]

		return user["results"][-1]["amountOfMistakes"]

	def speed(self, username):
		user = self._users[username]

		return self._wordsPerMinute(user["results"][-1])

	@property
	def usernames(self):
		return sorted(self._users.keys())

class TypingTutorModelModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTutorModelModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingTutorModel"
		self.filesWithTranslations = ("model.py",)

		self.requires = (
			self._mm.mods(type="dataStore"),
		)

	@property
	def _words(self):
		with open(self._mm.resourcePath("words.txt"), "r") as f:
			return [word.strip() for word in f]

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))

		store = self._modules.default("active", type="dataStore").store
		try:
			data = store["org.openteacher.typingTutor.model.data"]
		except KeyError:
			data = store["org.openteacher.typingTutor.model.data"] = {}

		self.model = TypeDataStore(self._words, data)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.model

def init(moduleManager):
	return TypingTutorModelModule(moduleManager)
