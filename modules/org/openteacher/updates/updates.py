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
import zipfile
import os

class UpdatesModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(UpdatesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "updates"
		self.requires = (
			self._mm.mods(type="metadata"),
			self._mm.mods(type="settings"),
			self._mm.mods(type="gpg"),
		)

	@staticmethod
	def _download(link, filename):
		local = open(filename, "w")
		online = urllib2.urlopen(link)
		for line in online:
			local.write(line)

	def _downloadUpdates(self):
		"""Raises IOError and ValueError"""
		self._download(self._metadata["updatesUrl"], self._mm.resourcePath("updates.json"))
		asc = urllib2.urlopen(self._metadata["updatesSignatureUrl"])
		if not self._gpg.verify_file(asc, self._mm.resourcePath("updates.json")):
			raise ValueError("No valid signature!")

	@property
	def updates(self):
		if self._updatesCache is not None:
			return self._updatesCache
		lastUpdate = datetime.datetime.min#datetime.datetime(2011, 9, 18, 17, 27, 16, 545688)#self._settings.value("org.openteacher.updates.lastUpdate")#FIXME
		self._downloadUpdates()
		updates = json.load(open(self._mm.resourcePath("updates.json")))
		for i in xrange(len(updates)):
			updates[i]["timestamp"] = datetime.datetime.strptime(
				updates[i]["timestamp"],
				"%Y-%m-%dT%H:%M:%S.%f"
			)
		result = filter(lambda x: x["timestamp"] > lastUpdate, updates)
		self._updatesCache = result
		return result

	def _installUpdate(self, link, signature):
		"""Raises IOError and ValueError"""
		self._download(link, self._mm.resourcePath("update.zip"))
		asc = urllib2.urlopen(signature)
		if not self._gpg.verify_file(asc, self._mm.resourcePath("update.zip")):
			raise ValueError("No valid signature!")
		#FIXME: use moduleInstaller?
		updatesZip = zipfile.ZipFile(self._mm.resourcePath("update.zip"), "r")
		updatesZip.extractall(self._mm.modulesPath) #FIXME: check if all paths aren't outside the path given, just in case.
		os.remove(self._mm.resourcePath("update.zip"))

	def update(self):
		for update in self.updates:
			self._installUpdate(update["link"], update["signature"])
		#FIXME: restart OpenTeacher

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._metadata = self._modules.default("active", type="metadata").metadata
		self._settings = self._modules.default("active", type="settings")
		self._gpg = self._modules.default("active", type="gpg").gpg
		self._updatesCache = None

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
		#FIXME: remove setting
		del self._settings
		del self._gpg
		del self._updatesCache

def init(moduleManager):
	return UpdatesModule(moduleManager)
