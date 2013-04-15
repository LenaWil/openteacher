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

import subprocess
import os
import collections
import itertools

ComplexityResult = collections.namedtuple("ComplexityResult", "path position complexity")

def pythonPaths():
	for root, dir, files in os.walk("."):
		for file in files:
			if not file.endswith(".py"):
				continue
			if "pyinstaller" in root:
				continue
			if "pyratemp" in file:
				continue
			yield os.path.join(root, file)

def complexCode():
	for path in pythonPaths():
		output = subprocess.check_output(["python", "-m", "mccabe", "--min=10", path]).strip()
		if output:
			for line in output.split("\n"):
				result = ComplexityResult._make([path] + list(eval(line)))
				if not "installQt" in result.position:
					yield result

def main():
	results = reversed(sorted(complexCode(), key=lambda r: r.complexity))
	for path, results in itertools.groupby(results, key=lambda r: r.path):
		print path
		for result in results:
			print "Complexity:", result.complexity, "Position:", result.position
		print ""

if __name__ == "__main__":
	main()
