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

ComplexityResult = collections.namedtuple("ComplexityResult", "position complexity")

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

def complexityInfo(output):
	for line in output.split("\n"):
		if not line:
			continue
		result = ComplexityResult._make(eval(line))
		if not "installQtClasses" in result.position:
			yield result

def complexityForPaths():
	for path in pythonPaths():
		output = subprocess.check_output(["python", "-m", "mccabe", "--min=10", path]).strip()
		info = list(complexityInfo(output))
		if info:
			yield path, info

def main():
	def highestComplexity((path, results)):
		return max(r.complexity for r in results)

	for path, results in reversed(sorted(complexityForPaths(), key=highestComplexity)):
		print path
		for result in reversed(sorted(results, key=lambda r: r.complexity)):
			print "Complexity:", result.complexity, "Position:", result.position
		print ""

if __name__ == "__main__":
	main()
