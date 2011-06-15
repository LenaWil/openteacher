#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

class SettingsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("settings",)
		self.requires = (1, 0)
		self.active = False

	def enable(self):
		self._modules = {}
		self._settings = {}
		self.modulesUpdated = self._mm.createEvent()
		self.active = True

	def disable(self):
		self.active = False
		del self.modulesUpdated
		del self._modules
		del self._settings

	def registerModule(self, name, module):
		self._modules[name] = module

	def registerSetting(self, internal_name, name, type="short_text", lessonType=None, category=None):
		try:
			self._settings[lessonType]
		except KeyError:
			self._settings[lessonType] = {}
		try:
			self._settings[lessonType][category]
		except KeyError:
			self._settings[lessonType][category] = {}
		setting = self._settings[lessonType][category][internal_name] = {}
		setting["value"] = None
		setting["name"] = name
		setting["type"] = type

	def value(self, internal_name):
		for lessonType in self._settings.values():
			for category in lessonType.values():
				try:
					return category[internal_name]["value"]
				except KeyError:
					pass

	@property
	def registeredModules(self):
		return self._modules.copy()

	def registeredSettings(self, lessonType=None, category=None):
		if lessonType:
			if category:
				return self._settings[lessonType][category].copy()
			return self._settings[lessonType].copy()
		return self._settings.copy()

def init(moduleManager):
	return SettingsModule(moduleManager)
