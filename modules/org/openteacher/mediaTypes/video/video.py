#! /usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2008-2011, Milan Boers
#
#    This file is part of OpenTeacher.
#
#    OpenTeacher is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenTeacher is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.


import fnmatch
import mimetypes
from PyQt4.phonon import Phonon

class MediaTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.phononControls = True
		
		self.type = "mediaType"
		self.extensions = [".avi", ".wmv", ".flv", ".mp4", ".mpg", ".mpeg", ".mov"]
		self.priority = 5

	def enable(self):		
		self.active = True

	def disable(self):
		self.active = False
	
	def supports(self, path):
		try:
			if mimetypes.guess_type(str(path))[0] in Phonon.BackendCapabilities.availableMimeTypes() and \
			   mimetypes.guess_type(str(path))[0].split("/")[0] == "video":
				return True
			else:
				return False
		except:
			return False
	
	def path(self, path, autoplay):
		return path
	
	def showMedia(self, path, mediaDisplay, autoplay):
		html5 = False
		
		for module in self._mm.mods("active", type="settings"):
			if module.value("org.openteacher.lessons.media.videohtml5"):
				html5 = True
		
		if html5 or mediaDisplay.noPhonon:
			if not mediaDisplay.noPhonon:
				# Stop any media playing
				mediaDisplay.videoPlayer.stop()
			# Set the widget to the web view
			mediaDisplay.setCurrentWidget(mediaDisplay.webviewer)
			# Set the right html
			autoplayhtml = ""
			if autoplay:
				autoplayhtml = '''autoplay="autoplay"'''
			mediaDisplay.webviewer.setHtml('''
			<html><head>
			<title>Video</title>
			<style type="text/css">
			body
			{
			margin: 0px;
			}
			</style>
			</head><body onresize="size()"><video id="player" src="''' + path + '''" ''' + autoplayhtml + ''' controls="controls" />
			<script>
			function size()
			{
				document.getElementById('player').style.width = window.innerWidth;
				document.getElementById('player').style.height = window.innerHeight;
			}
			size()
			</script>
			</body></html>
			''')
		else:
			# Set the widget to video player
			mediaDisplay.setCurrentWidget(mediaDisplay.videoPlayer)
			# Play the video
			mediaDisplay.videoPlayer.play(Phonon.MediaSource(path))
			if not autoplay:
				# Immediately pause it
				mediaDisplay.videoPlayer.pause()

def init(moduleManager):
	return MediaTypeModule(moduleManager)