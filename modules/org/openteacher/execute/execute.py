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

class ExecuteModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ExecuteModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "execute"
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="settings"),
		)

	def _getMod(self, *args, **kwargs):
		mods = set(self._mm.mods(*args, **kwargs))
		if len(mods) != 1:
			raise ValueError("There has to be exactly one module installed with signature %s." % ((args, kwargs)))
		return mods.pop()

	def execute(self):
		#do the only-one check. FIXME: move into settings maybe? (discuss!)
		self._getMod(type="dataStore")

		settings = self._getMod(type="settings")
		settings.initialize()

		profileSetting = settings.registerSetting(**{
			"internal_name": "Profile",
			"type": "short_text", #FIXME: profiles type?
			"defaultValue": "all",
			"subcategory": "Profile",
		})

		parser = argparse.ArgumentParser()
		parser.add_argument("-p", "--profile", **{
			"nargs": "?",
			"default": profileSetting["value"],
			"type": unicode,
			"help": "Start OpenTeacher with the PROFILE profile.",
			"metavar": "PROFILE",
		})
		args = parser.parse_args()

		modules = self._getMod(type="modules")
		modules.profile = args.profile

		event = modules.default(type="event")

		self.startRunning = event.createEvent()
		self.aboutToExit = event.createEvent()

		modules.updateToProfile()

		self.startRunning.send()
		self.aboutToExit.send()

def init(moduleManager):
	return ExecuteModule(moduleManager)
