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

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
