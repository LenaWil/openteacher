#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Milan Boers
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

class SettingDict(dict):
	def __init__(self, executeCallback, *args, **kwargs):
		super(SettingDict, self).__init__(*args, **kwargs)
		
		# Set default values
		if not "advanced" in self:
			self["advanced"] = False
		
		self._executeCallback = executeCallback

	def __setitem__(self, name, value):
		super(SettingDict, self).__setitem__(name, value)
		if name == "value" and self.has_key("callback"):
			self._executeCallback(self["callback"])

class SettingsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "settings"

	def initialize(self):
		"""Connects to data store, should be called before doing
		   anything else but only once in each program run. Normally,
		   that's handled by the execute module.

		"""
		store = set(self._mm.mods(type="dataStore")).pop().store
		try:
			self._settings = store["org.openteacher.settings.settings"]
		except KeyError:
			self._settings = store["org.openteacher.settings.settings"] = {}

		#replace the dicts by SettingDicts
		for key, value in self._settings.iteritems():
			self._settings[key] = SettingDict(self._executeCallback, value)

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
		  * password
		  * options #FIXME: shouldn't this be singular? (the type of the setting value is an option)
		  * language
		  * profile
		  ... are available.
		 * defaultValue
		 * category=None,
		 * subcategory=None,
		 * advanced=False
		 * callback=None
		  * should have this format:
		    {
				"args": ("active",),
				"kwargs": {"type": "callback"},
				"method": "callbackMethod",
			}
		    Where args and kwargs are the same as in the following:
		    self._mm.mods(*args, **kwargs)

		The following argument should be included when type="options":
		 * options=[]
		  * options should have this format: ("label", data)

		This method returns a setting dict with the same properties as
		described above, with the difference that defaultValue is
		missing and that the 'value' key is added containing the actual
		current value of the setting. You're free to modify the object,
		as long as its values are valid.

		When a setting argument isn't given (e.g. category), then it
		also isn't in the setting dict that is returned, so for the
		non-obligatory ones (the one with default values above) check
		for a KeyError and if there is one, threat it like the default
		value is the current data.

		If a callback is added, it's called when the value is changed
		automatically by this module.

		"""
		if not internal_name in self._settings:
			setting["value"] = setting.pop("defaultValue")
			self._settings[internal_name] = SettingDict(self._executeCallback, setting)
		return self._settings[internal_name]
	
	def setting(self, internal_name):
		"""Method to return a setting from the internal name."""

		return self._settings[internal_name]

	@property
	def registeredSettings(self):
		return self._settings.values()

	def _executeCallback(self, callback):
		obj = self._modules.default(*callback["args"], **callback["kwargs"])
		getattr(obj, callback["method"])() #execute

def init(moduleManager):
	return SettingsModule(moduleManager)
