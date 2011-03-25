from PyQt4 import QtCore, QtGui

class SettingsDialog(QtGui.QDialog):
	def __init__(self, modules, *args, **kwargs):
		super(SettingsDialog, self).__init__(*args, **kwargs)

		self.modules = {}

		vbox = QtGui.QVBoxLayout()
		for name, module in sorted(modules.items()):
			checkBox = QtGui.QCheckBox(name)
			if module.active:
				checkBox.setChecked(True)
			checkBox.stateChanged.connect(self.updateModuleState)
			self.modules[checkBox] = module
			vbox.addWidget(checkBox)
		self.setLayout(vbox)
		
		self.setWindowTitle(_("Settings"))

	def updateModuleState(self, state):
		module = self.modules[self.sender()]
		
		if state == QtCore.Qt.Checked:
			module.enable()
		else:
			module.disable()

class SettingsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsModule, self).__init__(*args, **kwargs)

		self.supports = ("settings",)
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def enable(self):
		self._modules = {}
		self.active = True

	def disable(self):
		self.active = False
		del self._modules

	def registerModule(self, name, module):
		self._modules[name] = module

	def show(self):
		for module in self._mm.activeMods.supporting("ui"):
			dialog = SettingsDialog(self._modules)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(tab.close)
			dialog.rejected.connect(tab.close)
			dialog.accepted.connect(tab.close)
			dialog.exec_()

def init(moduleManager):
	return SettingsModule(moduleManager)
