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

class ThemeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ThemeModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "theme"

	def enable(self):
		self.active = True
		
		self.installTheme()

	def installTheme(self):
		stylesheet = u"""
			* {
				color:white;
				background-color:#444;
				alternate-background-color:#555;
				selection-background-color:#888;
			}

			QToolBar, QToolButton {
				background-color:#333;
			}
		"""

		for module in self._mm.mods(type="ui"):
			module.addStyleSheetRules(stylesheet)
			module.setStyle("plastique")

	def disable(self):
		self.active = False

def init(moduleManager):
	return ThemeModule(moduleManager)
