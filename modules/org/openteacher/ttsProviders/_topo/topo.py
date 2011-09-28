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

class TextToSpeechProviderTopo(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TextToSpeechProviderTopo, self).__init__(*args, **kwargs)
		self._mm = moduleManager

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		for module in self._mm.mods("active", type="lessonType"):
			module.newItem.handle(self.itemEmitted)
		
		# Add settings
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.ttsProviders.topo.pronounce",
				"Pronounce places",
				"boolean",
				"Pronounciation",
				"Pronounciation",
				False
			)
		
		self.active = True

	def disable(self):
		self._modules
		for module in self._mm.mods("active", type="lessonType"):
			module.newItem.unhandle(self.itemEmitted)

		self.active = False
	
	def itemEmitted(self, item):
		for module in self._mm.mods("active", type="settings"):
			if(module.value("org.openteacher.ttsProviders.topo.pronounce")):
				ttss = set(self._mm.mods("active", type="textToSpeech"))
				try:
					tts = self._modules.chooseItem(ttss)
				except IndexError, e:
					#FIXME: nice error handling
					raise e
				else:
					tts.say.emit(item["name"])

def init(moduleManager):
	return TextToSpeechProviderTopo(moduleManager)
