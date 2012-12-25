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

import argparse
import sys
import glob
import os

class CommandLineInterfaceModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(CommandLineInterfaceModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "cli"
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="metadata"),
		)
		self.uses = (
			self._mm.mods(type="load"),
			self._mm.mods(type="save"),
		)
		self.priorities = {
			"cli": 0,
			"default": -1,
		}

	def _saveExts(self):
		yielded = set()
		for mod in self._modules.sort("active", type="save"):
			for exts in sorted(mod.saves.itervalues()):
				for ext in sorted(exts):
					if ext not in yielded:
						yielded.add(ext)
						yield ext

	def _convert(self, args):
		inputPaths = []
		for selector in args["input-files"]:
			inputPaths.extend(glob.iglob(selector))
		outputFormat = args["output_format"]

		for inputPath in inputPaths:
			#loading
			for mod in self._modules.sort("active", type="load"):
				type = mod.getFileTypeOf(inputPath)
				if type is None:
					#file not supported
					continue
				lesson = mod.load(inputPath)
				break
			else:
				print >> sys.stderr, "Couldn't load file '%s', not converting." % inputPath
				#next file
				continue

			class DummyLesson(object):
				list = lesson["list"]
				resources = lesson["resources"]

			done = False
			outputPath = os.path.splitext(inputPath)[0] + "." + outputFormat
			if os.path.exists(outputPath):
				print >> sys.stderr, "The file '{outfile}' already exists, so '{infile}' can't be converted.".format(outfile=outputPath, infile=inputPath)
				#next file
				continue

			for mod in self._modules.sort("active", type="save"):
				for modType, exts in mod.saves.iteritems():
					if modType == type and outputFormat in exts:
						mod.save(type, DummyLesson, outputPath)
						done = True
						break
				if done:
					break
			else:
				print >> sys.stderr, "Couldn't save file '{infile}' in the '{format}' format, not converting.".format(infile=inputPath, format=outputFormat)
				#next file. Not strictly necessary, but just in case more code's added later...
				continue
			print "Converted file '{infile}' to '{outfile}'.".format(infile=inputPath, outfile=outputPath)
		print "Done."

	def _run(self):
		#setup parser: using + instead of - to distinguish from the
		#execute module's argparse. (the one providing the -p arg).
		parser = argparse.ArgumentParser(**{
			"prog": sys.argv[0] + " -p cli",
			"prefix_chars": "+",
		})

		#--version
		version = self._metadata["name"] + " " + self._metadata["version"]
		parser.add_argument("+v", "++version", action="version", version=version)

		#convert
		subparsers = parser.add_subparsers()
		convert = subparsers.add_parser("convert", help="convert word, topo and media files", prefix_chars="+")

		convert.add_argument("+f", "++output-format", help="output format", default="otwd", choices=list(self._saveExts()))
		convert.add_argument("input-files", nargs="+", help="input files")
		convert.set_defaults(func=self._convert)

		#TODO: add more subparsers here...

		args = parser.parse_args()
		if not len(set(vars(args)) - set(["func"])):
			parser.print_usage()
			return
		args.func(vars(args))

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))
		self._modules.default("active", type="execute").startRunning.handle(self._run)

		self._metadata = self._modules.default("active", type="metadata").metadata

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._metadata

def init(moduleManager):
	return CommandLineInterfaceModule(moduleManager)
