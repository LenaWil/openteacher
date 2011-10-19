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

		self.type = "settings"
		self.requires = (
			self._mm.mods(type="dataStore"),
		)

	def registerSetting(self, internal_name, **setting):
		"""Adds a setting. internal_name should be unique and describe
		what the setting contains, we *strongly recommmend* to use the
		'reverse domain' naming	strategy because of the first property.
		(E.g. com.example.moduleName.settingName).

		The other arguments, describing the setting, should be:
		 * name,
		 * type="short_text",
		  * boolean
		  * short_text
		  * long_text
		  * number
		  * options
		  ... are available. #FIXME: correct?
		 * category=None,
		 * subcategory=None,
		 * defaultValue=None

		The following argument should be included when type="options"
		 * options=[]
		  * options should have this format: ("label", data)

		This method returns a setting dict with the same properties as
		described above, with the difference that defaultValue is
		missing and that the 'value' key is added containing the actual
		current value of the setting. You're free to modify the object,
		as long as its values are valid.

		"""
		if not self._settings.has_key(internal_name):
			setting["value"] = setting.pop("defaultValue")
			self._settings[internal_name] = setting
		return self._settings[internal_name]
	
	def setting(self, internal_name):
		"""
		Method to return a setting from the internal name.
		"""
		return self._settings[internal_name]

	@property
	def registeredSettings(self):
		return self._settings.values()

	def enable(self):
		modules = set(self._mm.mods("active", type="modules")).pop()
		try:
			self._settings = modules.default(type="dataStore").store["org.openteacher.settings.settings"]
		except KeyError:
			self._settings = modules.default(type="dataStore").store["org.openteacher.settings.settings"] = {}

		self.active = True

	def disable(self):
		self.active = False

		del self._settings

def init(moduleManager):
	return SettingsModule(moduleManager)
