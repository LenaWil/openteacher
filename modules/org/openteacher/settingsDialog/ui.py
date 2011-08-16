from PyQt4 import QtCore, QtGui
import sys

class ModulesTab(QtGui.QWidget):
	def __init__(self, modules, *args, **kwargs):
		super(ModulesTab, self).__init__(*args, **kwargs)

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
		
		self.setWindowTitle(_("Modules"))

	def updateModuleState(self, state):
		module = self.modules[self.sender()]

		if state == QtCore.Qt.Checked:
			module.enable()
		else:
			module.disable()

class LessonTypeTab(QtGui.QWidget):
	def __init__(self, moduleManager, name, lessonType, *args, **kwargs):
		super(LessonTypeTab, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager
		self.setWindowTitle(name)
		vbox = QtGui.QVBoxLayout()

		for name, category in lessonType.iteritems():
			if name is None:
				name = _("Miscellaneous")

			w = self.createCategoryGroupBox(name, category)
			vbox.addWidget(w)
		
		self.setLayout(vbox)

	def createCategoryGroupBox(self, name, category):
		groupBox = QtGui.QGroupBox(name)
		groupBoxLayout = QtGui.QFormLayout()
		for setting in category.values():
			groupBoxLayout.addRow(
				setting["name"],
				self.createSettingWidget(setting)
			)
		groupBox.setLayout(groupBoxLayout)
		return groupBox
	
	def createSettingWidget(self, setting):
		if setting["type"] == "short_text":
			w = QtGui.QLineEdit()
			w.textChanged.connect(self.shortTextChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setText(setting["value"])
			
		elif setting["type"] == "options":
			w = QtGui.QComboBox()
			# Add the options
			for option in setting["options"]:
				w.addItem(option[0], option[1])
			w.currentIndexChanged.connect(self.optionsChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setCurrentIndex(w.findData(setting["value"]))
			
		elif setting["type"] == "long_text":
			w = QtGui.QTextEdit()
			w.textChanged.connect(self.longTextChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setText(setting["value"])
			
		elif setting["type"] == "number":
			w = QtGui.QSpinBox()
			w.setRange(0, sys.maxint)
			w.valueChanged.connect(self.numberChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setValue(setting["value"])
			
		elif setting["type"] == "boolean":
			w = QtGui.QCheckBox()
			w.stateChanged.connect(self.booleanChanged)
			
			w.setting = setting
			if setting["value"] != None:
				# *2 because 2 is checked and 0 is unchecked
				w.setCheckState(setting["value"] * 2)
			
		return w

	def shortTextChanged(self):
		w = self.sender()
		w.setting["value"] = unicode(w.text())

	def longTextChanged(self):
		w = self.sender()
		w.setting["value"] = unicode(w.toPlainText())

	def numberChanged(self):
		w = self.sender()
		w.setting["value"] = int(w.value())
	
	def booleanChanged(self, state):
		w = self.sender()
		# /2 because 2 is checked and 0 is unchecked
		w.setting["value"] = state / 2

	def optionsChanged(self):
		w = self.sender()
		w.setting["value"] = w.itemData(w.currentIndex()).toString()

class SettingsDialog(QtGui.QTabWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsDialog, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		#Setup widget
		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

		for module in self._mm.mods("active", type="modules"):
			self.modulesTab = ModulesTab(module.registeredModules)

		for module in self._mm.mods("active", type="settings"):
			for name, lessonType in module.registeredSettings().iteritems():
				if name is None:
					name = _("Miscellaneous")
				self.createLessonTypeTab(name, lessonType)

		self.advancedButton = QtGui.QPushButton(_("Advanced mode"))
		self.advancedButton.clicked.connect(self.advanced)

		self.simpleButton = QtGui.QPushButton(_("Simple mode"))
		self.simpleButton.clicked.connect(self.simple)

		self.setWindowTitle(_("Settings"))

		self.simple()

	def createLessonTypeTab(self, name, lessonType):
		tab = LessonTypeTab(self._mm, name, lessonType)
		self.addTab(tab, tab.windowTitle())

	def advanced(self):
		self.addTab(
			self.modulesTab,
			self.modulesTab.windowTitle()
		)

		self.setCornerWidget(
			self.simpleButton,
			QtCore.Qt.BottomRightCorner
		)
		self.simpleButton.show()

	def simple(self):
		self.removeTab(self.indexOf(self.modulesTab))

		self.setCornerWidget(
			self.advancedButton,
			QtCore.Qt.BottomRightCorner
		)
		self.advancedButton.show()
