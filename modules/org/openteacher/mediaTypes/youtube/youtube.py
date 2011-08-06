import fnmatch
from PyQt4 import QtCore

class MediaTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.phononControls = False
		
		self.type = "mediaType"

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
	
	def supports(self, path):
		if fnmatch.fnmatch(str(path), "*youtube.*/watch?v=*"):
			return True
		else:
			return False
	
	def path(self, path, autoplay):
		# Youtube URLpath
		path = path.split("/watch?v=")[1]
		path = path.split("&")[0]
		path = "http://www.youtube.com/embed/" + path
		if autoplay:
			path += "?autoplay=1"
		return path
	
	def showMedia(self, path, mediaDisplay):
		if not mediaDisplay.noPhonon:
			# Stop any media playing
			mediaDisplay.videoPlayer.stop()
		# Set widget to web viewer
		mediaDisplay.setCurrentWidget(mediaDisplay.webviewer)
		# Set the URL
		mediaDisplay.webviewer.setUrl(QtCore.QUrl(path))

def init(moduleManager):
	return MediaTypeModule(moduleManager)