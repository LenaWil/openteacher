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

import urllib2
try:
	import json
except ImportError:
	import simplejson as json
import datetime

class UpdatesModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UpdatesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "updates"
		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="settings"),
		)

	@property
	def updates(self):
		lastUpdate = datetime.datetime.min#datetime.datetime(2011, 9, 18, 17, 27, 16, 545688)#self._settings.value("org.openteacher.updates.lastUpdate")#FIXME
		try:
			jsonFile = urllib2.urlopen(self._metadata.updatesUrl)
		except urllib2.HTTPError:
			return
		updates = json.load(jsonFile)
		for i in xrange(len(updates)):
			updates[i]["timestamp"] = datetime.datetime.strptime(
				updates[i]["timestamp"],
				"%Y-%m-%dT%H:%M:%S.%f"
			)
		return filter(lambda x: x["timestamp"] > lastUpdate, updates)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._metadata = self._modules.default("active", type="metadata")
		self._settings = self._modules.default("active", type="settings")

		self._settings.registerSetting(
			"org.openteacher.updates.lastUpdate",
			"Last update"
		)#FIXME: should not be visible in the settings dialog
		#(17:16:18) commandoline: maybe we should just separate it: #i.e.: the settings stuff
		#(17:16:25) commandoline: - one module which actually saves settings
		#(17:16:32) commandoline: - one module that adds them for internal use
		#(17:16:45) commandoline: - one module that adds them if the user needs to see them
		#(17:16:58) commandoline: - one settingsDialog module
		#(17:17:26) commandoline: - one modules module that saves the preference of the user for a module in the first module

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._metadata
		del self._settings

def init(moduleManager):
	return UpdatesModule(moduleManager)
