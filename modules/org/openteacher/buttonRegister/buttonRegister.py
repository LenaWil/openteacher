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

class Button(object):
	"""Represents a Button. UI modules should draw a button and handle
	   the events so they're updated on changes. User modules use it
	   as an abstract way of changing the buttons, by sending the change
	   events with arguments.

	   Properties:
	   - category (read-only)

	   Events:
	   - clicked() -> gui to user
	   - changeText(text) -> user to gui
	   - changeIcon(icon_path) -> user to gui
	   #piority is a number; 0 is high, inifinity low.
	   - changePriority(priority) -> user to gui
	   #can be: category, 
	   - changeCategory(category) -> user to gui

	"""
	def __init__(self, category, createEvent, *args, **kwargs):
		"""category must be either 'create' or 'load'"""

		super(Button, self).__init__(*args, **kwargs)

		self.category = category

		self.clicked = createEvent()
		self.changeText = createEvent()
		self.changeIcon = createEvent()
		self.changePriority = createEvent()

class ButtonRegisterModule(object):
	"""Module that provides a register of all 'buttons', a way for
	   features to present themselves to the user next to the menus.

	"""
	def __init__(self, moduleManager, *args, **kwargs):
		super(ButtonRegisterModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "buttonRegister"

		self.requires = (
			self._mm.mods(type="event"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._createEvent = self._modules.default(type="event").createEvent
		self.addButton = self._createEvent()
		self.removeButton = self._createEvent()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._createEvent
		del self.addButton
		del self.removeButton

	def registerButton(self, category):
		"""Creates a new Button object, and tells the world (mostly the
		   gui modules) it has been created. It returns the resulting
		   object to the user.

		"""
		b = Button(category, self._createEvent)
		self.addButton.send(b)
		return b

	def unregisterButton(self, b):
		"""Tell 'the world' the button b isn't in use anymore. User
		   responsibility to call this on disable."""
		self.removeButton.send(b)

def init(moduleManager):
	return ButtonRegisterModule(moduleManager)
