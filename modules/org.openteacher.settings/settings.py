class SettingsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsModule, self).__init__(*args, **kwargs)

		self.supports = ("settings",)
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def enable(self):
		self._modules = {}
		self._settings = {}
		self._ui = self._mm.import_(__file__, "ui")
		self.modulesUpdated = self._mm.createEvent()
		self.active = True

########## DEMO CONTENT
		self.registerSetting(
			"org.openteacher.settings.test",
			"Test setting",
		)
		self.registerSetting(
			"org.openteacher.settings.test2",
			"Test setting 2",
			"number"
		)
		self.registerSetting(
			"org.openteacher.settings.test3",
			"Test setting 3",
			"long_text",
			"Words lesson",
			"Test"
		)
		self.registerSetting(
			"org.openteacher.settings.test4",
			"Test setting 4",
			"options",
			"Topo lesson",
			"Test category 2"
		)
########## END DEMO CONTENT

	def disable(self):
		self.active = False
		del self.modulesUpdated
		del self._modules
		del self._settings
		del self._ui

	def registerModule(self, name, module):
		self._modules[name] = module

	def registerSetting(self, internal_name, name, type="short_text", lessonType=None, category=None):
		try:
			self._settings[lessonType]
		except KeyError:
			self._settings[lessonType] = {}
		try:
			self._settings[lessonType][category]
		except KeyError:
			self._settings[lessonType][category] = {}
		setting = self._settings[lessonType][category][internal_name] = {}
		setting["value"] = None
		setting["name"] = name
		setting["type"] = type

	def value(self, internal_name):
		for lessonType in self._settings.values():
			for category in lessonType.values():
				try:
					return category[internal_name]["value"]
				except KeyError:
					pass

	def show(self):
		for module in self._mm.activeMods.supporting("ui"):
			dialog = self._ui.SettingsDialog(self._modules, self._settings)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(self.modulesUpdated.emit)
			tab.closeRequested.handle(tab.close)

########## DEMO CONTENT
		print self.value("org.openteacher.settings.test")
		print self.value("org.openteacher.settings.test2")
		print self.value("org.openteacher.settings.test3")
		print self.value("org.openteacher.settings.test4")
########## END DEMO CONTENT

def init(moduleManager):
	return SettingsModule(moduleManager)
