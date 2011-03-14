#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven, Marten de Vries
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

from PyQt4 import QtGui

class TypingTeachWidget(QtGui.QWidget):
    def __init__(self, lessonTypeModule, *args, **kwargs):
        super(TypingTeachWidget, self).__init__(*args, **kwargs)
        
        self.lessonTypeModule = lessonTypeModule
        
        self.lessonTypeModule.newItem.handle(self.newItem)
        self.lessonTypeModule.lessonDone.handle(self.lessonDone)
        
        vbox = QtGui.QVBoxLayout()
        self.wordsLabel = QtGui.QLabel("No words added")
        labelSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        
        vbox.addWidget(self.wordsLabel)
        
        self.setLayout(vbox)

    def newItem(self, item): pass

    def lessonDone(self): pass

class TypingTeachTypeModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self.supports = ("teachType")
		self.type = 'words'
		self.name = 'Normal lesson'
		self.manager = manager
		
	def getWidget(self, lessonTypeModule):
		return TypingTeachWidget(lessonTypeModule)

def init(manager):
	return TypingTeachTypeModule(manager)
