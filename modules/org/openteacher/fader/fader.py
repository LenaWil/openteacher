#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright %year(s)%, %full_name%
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

from PyQt4 import QtCore, QtGui

class FaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(FaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "fader"
		
	def fade(self, step, targets, color = None):
		if step <= 255:
			alpha = step
		elif step > 765:
			alpha = 1020 - step
		else:
			return

		palette = QtGui.QPalette()
		if color:
			pcolor = QtGui.QColor(color[0], color[1], color[2])
		else:
			pcolor = palette.windowText().color()
		pcolor.setAlpha(alpha)
		palette.setColor(QtGui.QPalette.WindowText, pcolor)

		for target in targets:
			target.setPalette(palette)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return FaderModule(moduleManager)
