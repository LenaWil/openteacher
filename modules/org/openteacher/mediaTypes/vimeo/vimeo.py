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
		if fnmatch.fnmatch(str(path), "*vimeo.com/*"):
			return True
		else:
			return False
	
	def path(self, path, autoplay):
		# Vimeo URL
		path = path.split("vimeo.com/")[1]
		path = "http://player.vimeo.com/video/" + path + "?title=0&amp;byline=0&amp;portrait=0&amp;color=ffffff"
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