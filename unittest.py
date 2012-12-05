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

#abstracts the unittest importing process. Hackish so this file can be
#named unittest.py, but it works! :D

import sys as _sys

_path = _sys.path.pop(0)
#keep a reference so this module isn't garbage collected
_this = _sys.modules["unittest"]
del _sys.modules["unittest"]

if _sys.version < "2.7":
	_sys.modules["unittest"] = __import__("unittest2")
else:
	_sys.modules["unittest"] = __import__("unittest")

_sys.path.insert(0, _path)
