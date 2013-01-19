#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012-2013, Marten de Vries
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
		["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "Enter"],
		["Caps\nLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "\\", ""],
		["Shift", "\\", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Shift"],
		["Space"],
	]

	BELGIAN_AZERTY_LAYOUT = [
		[u"²", "&", u"é", '"', "'", "(", u"§", u"è", "!", u"ç", u"à", ")", "-", "Back-\nspace"],
		["Tab", "a", "z", "e", "r", "t", "y", "u", "i", "o", "p", "^", "$", "Enter"],
		["Caps\nLock", "q", "s", "d", "f", "g", "h", "j", "k", "l", "m", u"ù", u"µ", ""],
		["Shift", "<", "x", "x", "c", "v", "b", "n", ",", ";", ":", "=", "Shift"],
		["Space"],
	]

	FRENCH_AZERTY_LAYOUT = [
		[u"²", "&", u"é", '"', "'", "(", "-", u"è", "_", u"ç", u"à", ")", "=", "Back-\nspace"],
		["Tab", "a", "z", "e", "r", "t", "y", "u", "i", "o", "p", "^", "$", "Enter"],
		["Caps\nLock", "q", "s", "d", "f", "g", "h", "j", "k", "l", "m", u"ù", u"µ", ""],
		["Shift", "<", "x", "x", "c", "v", "b", "n", ",", ";", ":", "!", "Shift"],
		["Space"],
	]

	COLEMAK_LAYOUT = [
		["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Back-\nspace"],
		["Tab", "q", "w", "f", "p", "g", "j", "l", "u", "y", ";", "[", "]", "Enter"],
		["Back-\nspace", "a", "r", "s", "t", "d", "h", "n", "e", "i", "o", "'", "\\", ""],
		["Shift", "\\", "z", "x", "c", "v", "b", "k", "m", ",", ".", "/", "Shift"],
		["Space"],
	]

	DVORAK_LAYOUT = [
		["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[", "]", "Back-\nspace"],
		["Tab", "'", ",", ".", "p", "y", "f", "g", "c", "r", "l", "/", "=", "Enter"],
		["Caps\nLock", "a", "o", "e", "u", "i", "d", "h", "t", "n", "s", "-", "\\", ""],
		["Shift", "\\", ";", "q", "j", "k", "x", "b", "m", "w", "v", "z", "Shift"],
		["Space"],
	]

	QWERTZ_LAYOUT = [
		["^", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", u"ß", u"´", "Back-\nspace"],
		["Tab", "q", "w", "e", "r", "t", "z", "u", "i", "o", "p", u"ü", "+", "Enter"],
		["Caps\nLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", u"ö", u"ä", "#", ""],
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

	def retranslate(self):
		"""You never have to call this manually. It's handled by the
		   module in which this class is defined. That module *does*
		   have to call this before it lets 'the world' interact with
		   its instances, though. Without it some other methods will
		   crash.

		"""
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
			"status": "start",
		}

	@staticmethod
	def _createRow(letters):
		row = list(letters * int(math.ceil(80.0 / len(letters))))
		random.shuffle(row)
		for i in range(-1, 80, 6):
			row.insert(i, " ")
		return u"".join(row[:59])

	def _letterExercises(self, user):
		exercises = []

		#generate exercises to learn the most commonly used keys
		#automatically. This first learns letters in pairs, then in
		#larger groups.
		rows = [2, 1, 3, 0]
		for row in rows:
			if row == 3:
				spacing = 1
			else:
				spacing = 0
			exercises.extend([
				user["layout"][row][spacing + 4] + user["layout"][row][spacing + 7],
				user["layout"][row][spacing + 3] + user["layout"][row][spacing + 8],
				user["layout"][row][spacing + 2] + user["layout"][row][spacing + 9],
				user["layout"][row][spacing + 1] + user["layout"][row][spacing + 10],
				user["layout"][row][spacing + 1:spacing + 5],
				user["layout"][row][spacing + 7:spacing + 11],
				#<- FIXME: extra instruction required here (finger position)
				user["layout"][row][spacing + 5:spacing + 7],
				user["layout"][row][spacing + 4:spacing + 8],
				user["layout"][row][spacing + 1:spacing + 11]
			])

		#add an exercise which just uses all letters.
		everything = "".join(["".join(user["layout"][row][1:11]) for row in rows])
		exercises.append(everything)

		return exercises

	def currentExercise(self, username):
		user = self._users[username]

		if user["level"] < len(self._letterExercises(user)):
			#first practise the keys needed
			letters = self._letterExercises(user)[user["level"]]
			user["currentExercise"] = self._createRow(letters)
		else:
			#then practise typing words to improve speed.
			user["currentExercise"] = " ".join(random.sample(self._words, 8))

		return user["currentExercise"]

	def currentInstruction(self, username):
		user = self._users[username]

		if user["status"] == "start":
			return _("""Welcome, I'm your personal OpenTeacher typing tutor. We'll improve your typing skills by doing simple exercises. Between the exercises, I'll give instructions. Let's get started:

First place your fingers on the so-called home row: your fingers, from left to right, should always be on the keys '{a}', '{s}', '{d}', '{f}', '{space}', '{space}', '{j}', '{k}', '{l}' and '{;}' while not typing another character. When your fingers are in position, press {space} to start the first lesson. Work for accuracy at first, not speed.""").format(**{
			"a": user["layout"][2][1],
			"s": user["layout"][2][2],
			"d": user["layout"][2][3],
			"f": user["layout"][2][4],
			"space": user["layout"][4][0].lower(),
			"j": user["layout"][2][7],
			"k": user["layout"][2][8],
			"l": user["layout"][2][9],
			";": user["layout"][2][10],
		}).strip()

		if user["status"] == "done":
			return _("Congratulations, you finished this typing course! If you want to continue, you can, but this is the end of the instructions. You did a great job!")

		#sentences are added to the instruction depending on how the
		#user did.
		instr = u""

		if len(user["results"]) == 1:
			instr += _("Congratulations, you finished your first exercise!") + "\n\n"

		if user["status"] == "next":
			#FIXME: make it know about letters/words
			instr += _("You made zero mistakes and are typing fast enough, so you can continue practising some new letters/words. Keep up the good work!") + "\n\n"

		if user["status"] == "mistakes":
			amountOfMistakes = user["results"][-1]["amountOfMistakes"]
			instr += ngettext(
				"You made %s mistake, please keep trying until you can do it flawless.",
				"You made %s mistakes, please keep trying until you can do it flawless.",
				amountOfMistakes
			) % amountOfMistakes + "\n\n"
			if self._wordsPerMinute(user["results"][-1]) >= 50:
				#FIXME: only true while practising letters. For words, the speed to aim for might be above 50.
				#
				#user is going a bit fast, which might be the cause for the mistakes.
				instr = instr.rstrip() + " " + _("To archieve that, you might try slowing down a bit.") + "\n\n"

		if user["status"] == "slow":
			instr += _("You made zero mistakes. Now try to improve your typing speed a bit.") + "\n\n"

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

		speed = self._wordsPerMinute(user["results"][-1])
		maxLevel = len(self._letterExercises(user)) + 20

		#calculate new level
		if user["level"] < len(self._letterExercises(user)):
			#user is practising letters
			if amountOfMistakes > 0:
				user["status"] = "mistakes"
				return
			if speed < 20:
				user["status"] = "slow"
				return

		elif user["level"] < maxLevel:
			#user is practising words

			if amountOfMistakes > 0:
				user["status"] = "mistakes"
				return
			#at the end the user needs to type at 80 words per minute.
			#work towards that.
			if speed < (float(user["level"]) / maxLevel * 60) + 20:
				user["status"] = "slow"
				return
		else:
			#user is done.
			user["status"] = "done"
			return
		user["status"] = "next"
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

	def level(self, username):
		user = self._users[username]

		return user["level"]

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
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("model.py",)

	@property
	def _words(self):
		with open(self._mm.resourcePath("words.txt"), "r") as f:
			return [word.strip() for word in f]

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
		self.model.retranslate()

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))

		store = self._modules.default("active", type="dataStore").store
		try:
			data = store["org.openteacher.typingTutor.model.data"]
		except KeyError:
			data = store["org.openteacher.typingTutor.model.data"] = {}

		self.model = TypeDataStore(self._words, data)

		#translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.model

def init(moduleManager):
	return TypingTutorModelModule(moduleManager)
