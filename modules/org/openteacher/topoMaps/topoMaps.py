#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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
from PyQt4 import QtCore
from PyQt4 import QtOpenGL

"""
Abstract class for the map widgets
"""
class Map(QtGui.QGraphicsView):
	def __init__(self,*args, **kwargs):
		super(Map, self).__init__(*args, **kwargs)
		
		module = base._modules.default("active", type="settings")
		if module.value("org.openteacher.lessons.topo.opengl"):
			self.setViewport(QtOpenGL.QGLWidget())
	
	def setMap(self, map):
		self._setPicture(map)
	
	def _setPicture(self,picture):
		# Create a new scene
		self.scene = QtGui.QGraphicsScene()
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	def wheelEvent(self,wheelevent):
		# Scrolling makes it zoom
		if wheelevent.delta() > 0:
			self.scale(1.1,1.1)
		else:
			self.scale(0.9,0.9)

"""
The graphics scene of the map where you enter
"""
class EnterMapScene(QtGui.QGraphicsScene):
	def __init__(self, enterMap, *args, **kwargs):
		super(EnterMapScene, self).__init__(*args, **kwargs)
		
		self.enterMap = enterMap
	
	def mouseDoubleClickEvent(self,gsme):
		# Get coordinates
		x = gsme.lastScenePos().x()
		y = gsme.lastScenePos().y()
		# If its in the map
		if x > 0 and y > 0:
			# Ask for the name
			name = QtGui.QInputDialog.getText(self.enterMap, _("Name for this place"), _("What's this place's name?"))
			if unicode(name[1]) and unicode(name[0]).strip() != u"":
				# Make the place
				place = {
					"id": int(),
					"name": unicode(name[0]),
					"x": int(x),
					"y": int(y)
				}
				# Set id
				try:
					place["id"] = self.enterMap.enterWidget.places["items"][-1]["id"] + 1
				except IndexError:
					place["id"] = 0
				# And add the place
				self.enterMap.enterWidget.addPlace(place)

"""
The map on the enter tab
"""
class EnterMap(Map):
	def __init__(self, enterWidget, *args, **kwargs):
		super(EnterMap, self).__init__(*args, **kwargs)
		# Make it scrollable and draggable
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		
		self.enterWidget = enterWidget
		
		self.placesList = []
		self.placesGroup = QtGui.QGraphicsItemGroup()
	
	"""
	Override base class _setPicture with one that uses an EnterMapScene instead of QGraphicsScene
	"""
	def _setPicture(self, picture):
		# Create a new scene
		self.scene = EnterMapScene(self)
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	def update(self):
		# Remove previous items
		for item in self.placesList:
			try:
				self.scene.removeItem(item)
			except RuntimeError:
				# Object already removed
				pass
		
		# Remove all previous items
		self.placesList = []
		
		# Add all the places
		for place in self.enterWidget.places["items"]:
			# Make the little rectangle
			rect = QtGui.QGraphicsRectItem(place["x"],place["y"],6,6)
			rect.setBrush(QtGui.QBrush(QtGui.QColor("red")))
			# Place the rectangle in the list of items
			self.placesList.append(rect)
			
			# Make the shadow of the text
			shadow = QtGui.QGraphicsTextItem(place["name"])
			shadow.setFont(QtGui.QFont("sans-serif",15,75))
			shadow.setPos(place["x"]+2,place["y"]+2)
			shadow.setDefaultTextColor(QtGui.QColor("black"))
			shadow.setOpacity(0.5)
			# Place the shadow in the list of items
			self.placesList.append(shadow)
			
			item = QtGui.QGraphicsTextItem(place["name"])
			item.setFont(QtGui.QFont("sans-serif",15,75))
			item.setPos(place["x"],place["y"])
			item.setDefaultTextColor(QtGui.QColor("red"))
			# Place the text in the list of items
			self.placesList.append(item)
		
		# Place the list of items on the map
		self.placesGroup = self.scene.createItemGroup(self.placesList)
	
	def getScreenshot(self):
		image = QtGui.QImage(self.scene.width(), self.scene.height(), QtGui.QImage.Format_RGB32)
		painter = QtGui.QPainter(image)
		self.scene.render(painter)
		painter.end()
		return image

"""
Scene for the TeachPictureMap
"""
class TeachPictureScene(QtGui.QGraphicsScene):
	def __init__(self, pictureMap, *args, **kwargs):
		super(TeachPictureScene, self).__init__(*args, **kwargs)
		
		self.pictureMap = pictureMap
	
	def mouseReleaseEvent(self, event):
		# Clicked a place
		clickedObject = self.itemAt(event.lastScenePos().x(), event.lastScenePos().y())
		if clickedObject.__class__ == TeachPlaceOnMap:
			self.pictureMap.teachWidget.lesson.checkAnswer(clickedObject.place)

"""
The map on the teach tab
"""
class TeachPictureMap(Map):
	def __init__(self, teachWidget, *args, **kwargs):
		super(TeachPictureMap, self).__init__(*args, **kwargs)
		
		self.teachWidget = teachWidget
		
		# Not interactive
		self.interactive = False
		# Make sure everything is redrawn every time
		self.setViewportUpdateMode(0)
	
	"""
	Sets the arrow on the map to the right position
	"""
	def setArrow(self, x, y):
		self.centerOn(x-15,y-50)
		self.crosshair.setPos(x-15,y-50)
	
	"""
	Removes the arrow
	"""
	def removeArrow(self):
		self.scene.removeItem(self.crosshair)
	
	"""
	Overriding the base class _setPicture method with one using the TeachPictureScene
	"""
	def _setPicture(self,picture):
		# Create a new scene
		self.scene = TeachPictureScene(self)
		# Set the pixmap of the scene
		self.pixmap = QtGui.QPixmap(picture)
		self.scene.addPixmap(self.pixmap)
		# Set the scene
		self.setScene(self.scene)
	
	"""
	Shows all the places without names
	"""
	def showPlaceRects(self):
		placesList = []
		
		for place in self.teachWidget.places["items"]:
			# Make the little rectangle
			rect = TeachPlaceOnMap(place)
			# Place the rectangle in the list of items
			placesList.append(rect)
		
		self.placesGroup = self.scene.createItemGroup(placesList)
	
	def hidePlaceRects(self):
		try:
			for item in self.placesList:
				self.removeItem(item)
		except AttributeError:
			pass
	
	def setInteractive(self, val):
		if val:
			self.showPlaceRects()
			# Interactive
			self.interactive = True
			# Scrollbars
			self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
			self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
			self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		else:
			self.hidePlaceRects()
			# Not interactive
			self.interactive = False
			# No scrollbars
			self.setDragMode(QtGui.QGraphicsView.NoDrag)
			self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
			self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
			# Arrow
			crosshairPixmap = QtGui.QPixmap(base._mm.resourcePath("resources/crosshair.png"))
			self.crosshair = QtGui.QGraphicsPixmapItem(crosshairPixmap)
			
			self.scene.addItem(self.crosshair)

		
class TopoMapsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TopoMapsModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		
		self._mm = moduleManager
		
		self.type = "topoMaps"
		
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="settings"),
		)
	
	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.active = True
		
		#setup translation
		global _
		global ngettext
		
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		
		# Add settings
		for module in self._mm.mods("active", type="settings"):
			module.registerSetting(
				"org.openteacher.lessons.topo.opengl",
				"OpenGL Rendering",
				"boolean",
				"Topo lesson",
				"Rendering"
			)
	
	def disable(self):
		self.active = False
	
	def getEnterMap(self, enterWidget):
		return EnterMap(enterWidget)
	
	def getTeachMap(self, teachWidget):
		return TeachPictureMap(teachWidget)

def init(moduleManager):
	return TopoMapsModule(moduleManager)