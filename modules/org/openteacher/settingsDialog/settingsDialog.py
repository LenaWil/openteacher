class SettingsDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "settingsDialog"

	def enable(self):
		self._ui = self._mm.import_("ui")
		#install translator
		translator = set(self._mm.mods("active", type="translator")).pop()
		self._ui._, self._ui.ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.active = True

########## DEMO CONTENT
		for module in self._mm.mods("active", type="settings"):
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
		for umod in self._mm.mods("active", type="ui"):
			dialog = self._ui.SettingsDialog(self._mm)
			tab = umod.addCustomTab(dialog.windowTitle(), dialog)
			for mmod in self._mm.mods("active", type="modules"):
				tab.closeRequested.handle(mmod.modulesUpdated.emit)
			tab.closeRequested.handle(tab.close)

########## DEMO CONTENT
		for module in self._mm.mods("active", type="settings"):
			print module.value("org.openteacher.settings.test")
			print module.value("org.openteacher.settings.test2")
			print module.value("org.openteacher.settings.test3")
			print module.value("org.openteacher.settings.test4")
########## END DEMO CONTENT

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
