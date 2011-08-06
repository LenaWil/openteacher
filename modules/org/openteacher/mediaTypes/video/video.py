import fnmatch
import mimetypes
from PyQt4.phonon import Phonon

class MediaTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.phononControls = True
		
		self.type = "mediaType"

	def enable(self):		
		self.active = True

	def disable(self):
		self.active = False
	
	def supports(self, path):
		try:
			if mimetypes.guess_type(str(path))[0].split('/')[0] == "video":
				return True
			else:
				return False
		except:
			return False
	
	def path(self, path, autoplay):
		return path
	
	def showMedia(self, path, mediaDisplay):
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
			mediaDisplay.webviewer.setHtml('''
			<html><head>
			<title>Video</title>
			<style type="text/css">
			body
			{
			margin: 0px;
			}
			</style>
			</head><body onresize="size()"><video id="player" src="''' + path + '''" autoplay="autoplay" controls="controls" />
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

def init(moduleManager):
	return MediaTypeModule(moduleManager)