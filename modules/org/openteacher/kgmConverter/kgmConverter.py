#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

import sys
import os

from etree import ElementTree

class Lesson(object):
	pass

class KgmConverterModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(KgmConverterModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "kgmConverter"

		self.priorities = {
			"default": -1,
			"convert-kgm": 0,
		}
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="save", saves={"topo": ["ottp"]}),
		)

	@property
	def _save(self):
		return self._modules.default("active", type="save", saves={"topo": ["ottp"]}).save

	def _kgm2lesson(self, kgmPath):
		#Feed the xml parser
		with open(kgmPath) as f:
			root = ElementTree.parse(f).getroot()
		#load the map, in various later needed formats
		mapPath = os.path.join(os.path.dirname(kgmPath), root.findtext("mapFile"))
		mapImage = Image.open(mapPath).convert("RGB")
		mapImageData = mapImage.load()

		items = []
		for counter, division in enumerate(root.findall("division")):
			#iterate over all places ('divisions')
			if division.findtext("ignore") == "yes":
				#unimportant division: skip
				continue
			item = {
				"id": counter,
				"name": division.findtext("name") or u"",
			}

			#get the color the place has on the map
			r = int(division.findtext("color/red"))
			g = int(division.findtext("color/green"))
			b = int(division.findtext("color/blue"))
			color = (r, g, b)

			#get the average pixel with that color. This is done by
			#iterating over all pixels and using them to calculate an
			#average if the color matches.
			sumX = 0
			sumY = 0
			count = 0
			for x in range(mapImage.size[0]):
				for y in range(mapImage.size[1]):
					if mapImageData[x, y] == color:
						sumX += x
						sumY += y
						count += 1
			#save the averages as coordinate.
			item["x"] = sumX / count
			item["y"] = sumY / count

			items.append(item)
		return mapPath, {"items": items}

	def _run(self):
		try:
			inputPath = sys.argv[1]
			outputPath = sys.argv[2]
		except IndexError:
			print >> sys.stderr, "Please specify a .kgm file and the path to save the .ottp file to as the last command line arguments."
			return

		#load the .kgm file
		mapPath, list = self._kgm2lesson(inputPath)

		#put it inside a lesson object needed to save it
		lesson = Lesson()
		lesson.list = list
		lesson.resources = {"mapPath": mapPath}

		#save it (to ottp)
		self._save("topo", lesson, outputPath)

	def enable(self):
                global Image
                try:
                        import Image
                except ImportError:
                        #remain inactive
                        return
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._modules.default("active", type="execute").startRunning.handle(self._run)

		self.active = True

	def disable(self):
		self.active = False

                del Image
		del self._modules

def init(moduleManager):
	return KgmConverterModule(moduleManager)
