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

class TextToSpeechProviderWords(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TextToSpeechProviderWords, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
			self._mm.mods(type="textToSpeech"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		for module in self._mm.mods("active", type="lessonType"):
			module.newItem.handle(self.itemSent)
		
		self._settings = self._modules.default("active", type="settings")
		
		self._pronounceSetting = self._settings.registerSetting(**{
			"internal_name": "org.openteacher.ttsProviders.words.pronounce",
			"name": "Pronounce words",
			"type": "boolean",
			"category": "Pronounciation",
			"subcategory": "Pronounciation", #FIXME: translate this and stuff above
			"defaultValue": False,
		})
		
		self.active = True

	def disable(self):
		del self._modules
		for module in self._mm.mods("active", type="lessonType"):#FIXME
			module.newItem.unhandle(self.itemSent)

		self.active = False

	def itemSent(self, item):
		if self._pronounceSetting["value"]:
			try:
				text = self._modules.default(
					"active",
					type="wordsStringComposer"
				).compose(item["questions"])
			except KeyError:
				# No questions, I can't pronounce this
				pass
			else:
				self._modules.default(
					"active",
					type="textToSpeech"
				).say.send(text)

def init(moduleManager):
	return TextToSpeechProviderWords(moduleManager)
