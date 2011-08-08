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

import zipfile
try:
	import json
except:
	import simplejson as json

class OpenTeachingWordsSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingWordsSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"

	def enable(self):		
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("Open Teaching Words (.otwd) saver", self)
		self.saves = {"words": ["otwd"]}
		
		self.active = True

	def disable(self):
		self.active = False

	def save(self, type, list, path, resources):
		otwdzip = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
		otwdzip.writestr("list.json", json.dumps(list))

def init(moduleManager):
	return OpenTeachingWordsSaverModule(moduleManager)
