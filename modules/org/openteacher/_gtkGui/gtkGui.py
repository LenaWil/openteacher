#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten  de Vries
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


def installGtkClasses():
	global EnterWindow, TeachWindow

	class EnterWindow(Gtk.Window):
		def __init__(self, Event, *args, **kwargs):
			super(EnterWindow, self).__init__(*args, **kwargs)

			edit = Gtk.TextView()
			self._textBuffer = edit.get_buffer()
			self._textBuffer.set_text("een = one\ntwee = two\nthree = drie\n")

			self.lessonStartRequested = Event()
			button = Gtk.Button(label="Start lesson")
			button.connect("clicked", self.on_button_clicked)

			box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
			box.pack_start(edit, True, True, 0)
			box.pack_start(button, False, True, 0)

			self.add(box)
			self.resize(400, 300)

		def on_button_clicked(self, widget):
			text = self._textBuffer.get_text(self._textBuffer.get_start_iter(), self._textBuffer.get_end_iter(), True).decode("UTF-8")
			self.lessonStartRequested.send(text)

	class TeachWindow(Gtk.Window):
		def __init__(self, *args, **kwargs):
			super(TeachWindow, self).__init__(*args, **kwargs)

class GtkGui(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(GtkGui, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "gtkGui"
		self.priorities = {
			"default": -1,
			"gtk": 0,
		}
		self.requires = (
			self._mm.mods(type="execute"),
			self._mm.mods(type="wordListStringParser"),
		)

	def _run(self):		
		self._enterWin = EnterWindow(self._createEvent)
		self._enterWin.connect("delete-event", Gtk.main_quit)
		self._enterWin.lessonStartRequested.handle(self._startLesson)
		self._enterWin.show_all()

		self._teachWin = TeachWindow()
		self._teachWin.connect("delete-event", Gtk.main_quit)
		self._teachWin.show_all()
		self._teachWin.hide()

		Gtk.main()

	def _startLesson(self, data):
		self._enterWin.hide()

		lessonData = self._modules.default("active", type="wordListStringParser").parseList(data)
		#FIXME: start an actual lesson
		print lessonData

		self._teachWin.show()

	def enable(self):
		global Gtk
		try:
			from gi.repository import Gtk
		except ImportError:
			return
		installGtkClasses()

		self._modules = next(iter(self._mm.mods(type="modules")))
		self._modules.default("active", type="execute").startRunning.handle(self._run)

		self._createEvent = self._modules.default("active", type="event").createEvent

		self.active = True

	def disable(self):
		self.active = False

		self._modules.default("active", type="execute").startRunning.unhandle(self._run)
		del self._createEvent
		del self._modules

def init(moduleManager):
	return GtkGui(moduleManager)
