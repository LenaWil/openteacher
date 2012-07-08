#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

import argparse
import sys

class ExecuteModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ExecuteModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "execute"
		self.requires = (
			self._mm.mods(type="event"),

		)
		self.uses = (
			self._mm.mods(type="settings"),
		)
		self.active = True

	def _getMod(self, *args, **kwargs):
		mods = set(self._mm.mods(*args, **kwargs))
		if len(mods) != 1:
			raise ValueError("There has to be exactly one module installed with signature %s." % ((args, kwargs),))
		return mods.pop()

	def execute(self):
		#load the settings module's dependencies (currently one)
		try:
			self._getMod(type="dataStore")
			settings = self._getMod(type="settings")
			settings.initialize()
		except ValueError:
			profileSetting = dict()
			profileSetting["value"] = "all"
		else:
			profileSetting = settings.registerSetting(**{
				#FIXME: translations???
				"internal_name": "org.openteacher.execute.startup_profile",
				"name": "Profile",
				"type": "profile",
				"defaultValue": "all",
				"category": "General",
				"subcategory": "Profile",
				"callback": {
					"args": (),
					"kwargs": {"type": "execute"},
					"method": "_settingChanged",
				}
			})

		parser = argparse.ArgumentParser()
		parser.add_argument("-p", "--profile", **{
			"nargs": "?",
			"default": profileSetting["value"],
			"type": unicode,
			"help": "Start OpenTeacher with the PROFILE profile. Don't know which profiles are included? I'll give away one: 'help' ;).",
		})
		args, otherArgs = parser.parse_known_args(sys.argv)
		#remove the args we parsed from sys.argv
		del sys.argv[0:]
		sys.argv.extend(otherArgs)

		self._modules = self._getMod(type="modules")
		self._modules.profile = args.profile

		event = self._modules.default(type="event")

		self.startRunning = event.createEvent()
		self.aboutToExit = event.createEvent()

		self._modules.updateToProfile()

		self.startRunning.send()
		self.aboutToExit.send()

	def _settingChanged(self):
		try:
			dialogShower = self._modules.default("active", type="dialogShower")
			settingsDialog = self._modules.default("active", type="settingsDialog")
		except IndexError:
			pass #no guarantees can be made for these modules...
		dialogShower.showMessage.send(settingsDialog.tab, "Restart OpenTeacher for this setting to take effect.")

def init(moduleManager):
	return ExecuteModule(moduleManager)
