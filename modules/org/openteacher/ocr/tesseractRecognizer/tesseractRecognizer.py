#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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

import os
import tempfile
import subprocess

class TesseractOCRModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TesseractOCRModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "ocrRecognizer"
		self.priorities = {
			"default": 333,
		}

	def toHocr(self, path):
		hocrPath = tempfile.mkstemp(".html")[1]
		self._callTesseract(path, os.path.splitext(hocrPath)[0], "hocr")
		with open(hocrPath) as f:
			hocr = unicode(f.read(), encoding="UTF-8")

		os.remove(hocrPath)
		return hocr

	def _callTesseract(self, *args):
		with open(os.devnull, "w") as f:
			return subprocess.call(["tesseract"] + list(args), stdout=f, stderr=subprocess.STDOUT)

	def enable(self):
		try:
			self._callTesseract("-v")
		except OSError:# pragma: no cover
			#remain inactive
			return

		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return TesseractOCRModule(moduleManager)
