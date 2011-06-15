class SettingsDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsDialogModule, self).__init__(*args, **kwargs)

		self.supports = ("settingsDialog",)
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def enable(self):
		self._ui = self._mm.import_("ui")
		self.active = True

########## DEMO CONTENT
		for module in self._mm.activeMods.supporting("settings"):
			module.registerSetting(
				"org.openteacher.settings.test",
				"Test setting",
			)
			module.registerSetting(
				"org.openteacher.settings.test2",
				"Test setting 2",
				"number"
			)
			module.registerSetting(
				"org.openteacher.settings.test3",
				"Test setting 3",
				"long_text",
				"Words lesson",
				"Test"
			)
			module.registerSetting(
				"org.openteacher.settings.test4",
				"Test setting 4",
				"options",
				"Topo lesson",
				"Test category 2"
			)
########## END DEMO CONTENT

	def disable(self):
		self.active = False
		del self._ui

	def show(self):
		for umod in self._mm.activeMods.supporting("ui"):
			for smod in self._mm.activeMods.supporting("settings"):
				dialog = self._ui.SettingsDialog(self._mm)
				tab = umod.addCustomTab(dialog.windowTitle(), dialog)
				tab.closeRequested.handle(smod.modulesUpdated.emit)
				tab.closeRequested.handle(tab.close)

########## DEMO CONTENT
		for module in self._mm.activeMods.supporting("settings"):
			print module.value("org.openteacher.settings.test")
			print module.value("org.openteacher.settings.test2")
			print module.value("org.openteacher.settings.test3")
			print module.value("org.openteacher.settings.test4")
########## END DEMO CONTENT

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
