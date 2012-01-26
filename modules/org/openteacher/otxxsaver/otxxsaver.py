#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

try:
	import json
except ImportError:
	import simplejson as json
import zipfile

class OtxxSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OtxxSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "otxxSaver"

	def save(self, lesson, path, resourceFilenames={}, zipCompression=zipfile.ZIP_DEFLATED):
		with zipfile.ZipFile(path, 'w', zipCompression) as otxxzip:
			otxxzip.writestr("list.json", json.dumps(
				lesson.list, #the list to save
				separators=(',',':'), #compact encoding
				default=self._serialize #serialize datetime
			))
			for resourceKey, filename in resourceFilenames.iteritems():
				otxxzip.write(lesson.resources[resourceKey], filename)

	def _serialize(self, obj):
		try:
			return obj.strftime("%Y-%m-%dT%H:%M:%S.%f")
		except AttributeError:
			raise TypeError("The type '%s' isn't JSON serializable." % obj.__class__)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return OtxxSaverModule(moduleManager)
