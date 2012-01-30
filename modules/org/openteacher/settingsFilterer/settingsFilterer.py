#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

class SettingsFiltererModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsFiltererModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "settingsFilterer"

	def byKey(self, key, items):
		catItems = dict()
		for item in items:
			if not key in item:
				if "Miscellaneous" not in catItems:
					catItems["Miscellaneous"] = []
				catItems["Miscellaneous"].append(item)
			else:
				if item[key] not in catItems:
					catItems[item[key]] = []
				catItems[item[key]].append(item)
		return catItems

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return SettingsFiltererModule(moduleManager)
