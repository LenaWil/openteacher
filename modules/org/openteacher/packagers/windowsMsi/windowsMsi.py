#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

import zipfile
import sys
import os
import shutil
import uuid
import subprocess
import itertools
import string

wxs = """
<?xml version="1.0" encoding="UTF-8" ?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi" xmlns:netfx="http://schemas.microsoft.com/wix/NetFxExtension">
    <Product Name="OpenTeacher" Id="6795c2ff-d23f-4a2c-a130-0556d4314254" UpgradeCode="6fbe08a3-4545-45b8-b6d1-4eaf00083835" Language="1033" Codepage="1252" Version="3.0.0" Manufacturer="OpenTeacher Maintainers">
	<Package Id="*" Keywords="Installer" Manufacturer="OpenTeacher Maintainers" InstallerVersion="100" Languages="1033" Compressed="yes" />

	<!-- check for .NET 2.0 -->
	<PropertyRef Id="NETFRAMEWORK20" />
	<Condition Message="OpenTeacher requires .NET Framework 2.0. Please install the .NET Framework and then run this installer again.">
	    <![CDATA[Installed OR NETFRAMEWORK20]]>
	</Condition>

	<!-- files -->
	<Media Id="1" Cabinet="OpenTeacher.cab" EmbedCab="yes" />
	<Directory Id="TARGETDIR" Name="SourceDir">
	    <Directory Id="ProgramFilesFolder" Name="PFiles">
		<Directory Id="INSTALLDIR" Name="OpenTeacher">
		    <Component Id="MainFiles" Guid="{uuid1}">
			<File Id="openteacher.exe" KeyPath="yes" Name="openteacher.exe" Source="openteacher.exe" DiskId="1">
			    <Shortcut Id="StartmenuShortcut" Directory="ProgramMenuDir" Name="OpenTeacher" WorkingDirectory="INSTALLDIR" Icon="openteacher.ico" Advertise="yes" />
			    <Shortcut Id="DesktopShortcut" Directory="DesktopFolder" Name="OpenTeacher" WorkingDirectory="INSTALLDIR" Icon="openteacher.ico" Advertise="yes" />
			</File>
			<File Id="openteacher.ico" Name="openteacher.ico" Source="openteacher.ico" DiskId="1" />
			<File Id="start.py" Name="start.py" Source="start.py" DiskId="1" />

			<!-- File associations -->
			<!-- otwd -->
			<ProgId Id="OpenTeacher.otwd" Description="Open Teaching Words" Icon="openteacher.ico">
			    <Extension Id="otwd" ContentType="application/x-openteachingwords">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
			<!-- ottp -->
			<ProgId Id="OpenTeacher.ottp" Description="Open Teaching Topography" Icon="openteacher.ico">
			    <Extension Id="ottp" ContentType="application/x-openteachingtopography">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
			<!-- otmd -->
			<ProgId Id="OpenTeacher.otmd" Description="Open Teaching Media" Icon="openteacher.ico">
			    <Extension Id="otmd" ContentType="application/x-openteachingmedia">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
			<!-- ot -->
			<ProgId Id="OpenTeacher.ot" Description="Open Teacher 2.x" Icon="openteacher.ico">
			    <Extension Id="ot" ContentType="application/x-openteacher">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
			<!-- t2k -->
			<ProgId Id="OpenTeacher.t2k" Description="Teach 2000" Icon="openteacher.ico">
			    <Extension Id="t2k" ContentType="application/x-teach2000">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
			<!-- wrts -->
			<ProgId Id="OpenTeacher.wrts" Description="WRTS" Icon="openteacher.ico">
			    <Extension Id="wrts" ContentType="application/x-wrts">
				<Verb Id="open" Command="open" TargetFile="openteacher.exe" Argument="&quot;%%1&quot;" />
			    </Extension>
			</ProgId>
		    </Component>
		    {files}
		</Directory>
	    </Directory>
	    <Directory Id="ProgramMenuFolder" Name="Programs">
		<Directory Id="ProgramMenuDir" Name="OpenTeacher">
		    <Component Id="ProgramMenuDir" Guid="{uuid2}">
			<RemoveFolder Id="ProgramMenuDir" On="uninstall" />
			<RegistryValue Root="HKCU" Key="Software\[Manufacturer]\[ProductName]" Type="string" Value="" KeyPath="yes" /> 
			<!-- Uninstall shortcut -->
			<Shortcut Id="UninstallShortcut" Name="Uninstall OpenTeacher" Target="[SystemFolder]msiexec.exe" Arguments="/x [ProductCode]" Description="Uninstalls OpenTeacher" />
		    </Component>
		</Directory>
	    </Directory>
	    <Directory Id="DesktopFolder" Name="Desktop" />
	</Directory>
	<Feature Id="Complete" Level="1">
	    <ComponentRef Id="MainFiles" />
	    <ComponentRef Id="ProgramMenuDir" />
	    {components}
	</Feature>

	<!-- UI -->
	<UI>
	    <UIRef Id="WixUI_InstallDir" />
	    <UIRef Id="WixUI_ErrorProgressText" />
	    <Publish
		Dialog="ExitDialog"
		Control="Finish"
		Event="DoAction"
		Value="LaunchApplication"
	    >WIXUI_EXITDIALOGOPTIONALCHECKBOX = 1 and NOT Installed</Publish>
	</UI>
	<Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />
	<WixVariable Id="WixUIBannerBmp" Value="topbanner.bmp" />
	<WixVariable Id="WixUIDialogBmp" Value="leftbanner.bmp" />
	<WixVariable Id="WixUILicenseRtf" Value="COPYING.rtf" />

	<!-- Launch after install -->
	<Property Id="WIXUI_EXITDIALOGOPTIONALCHECKBOXTEXT" Value="Launch OpenTeacher" />
	<Property Id="WixShellExecTarget" Value="[#openteacher.exe]" />
	<CustomAction Id="LaunchApplication" BinaryKey="WixCA" DllEntry="WixShellExec" Impersonate="yes" />

	<Property Id="ARPPRODUCTICON" Value="openteacher.ico" />
	<Icon Id="openteacher.ico" SourceFile="openteacher.ico" />
    </Product>
</Wix>
"""

class WindowsMsiPackagerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WindowsMsiPackagerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "windowsMsiPackager"
		self.requires = (
			self._mm.mods(type="pydistInterface"),
			self._mm.mods(type="execute"),
		)
		self.priorities = {
			"package-windows-msi": 0,
			"default": -1,
		}

                self._ids = {}
                self._idCounter = itertools.count()

        def _toId(self, path):
                if path not in self._ids:
                        self._ids[path] = "generated_%s" % next(self._idCounter)
                return self._ids[path]

        def _gatherFiles(self, root):
                """gather all files in the python and src directories. Output as xml ready to insert into the main snippet"""

                components = '<ComponentRef Id="%sComponent" />' % self._toId(root)

                result = '<Directory Id="{id}Directory" Name="{name}">'.format(id=self._toId(root), name=os.path.basename(root))
                result += '<Component Id="{id}Component" Guid="{uuid}">'.format(id=self._toId(root), uuid=uuid.uuid4())

                for file in os.listdir(root):
                        if not os.path.isfile(os.path.join(root, file)):
                            continue
                        result += '<File Id="{id}" Source="{source}" Name="{name}" DiskId="1" />'.format(
                            id=self._toId(os.path.join(root, file)),
                            source=os.path.join(root, file),
                            name=file,
                        )
                result += '</Component>'
                for dir in os.listdir(root):
                        if not os.path.isdir(os.path.join(root, dir)):
                            continue
                        components2, result2 = self._gatherFiles(os.path.join(root, dir))
                        components += components2
                        result += result2
                result += '</Directory>'
                return components, result

	def _run(self):
		try:
			dataZipLoc = sys.argv[1]
			msiLoc = sys.argv[2]
		except IndexError:
			sys.stderr.write("Please specify the data tar file and the resultive msi file name as last command line parameters. (e.g. windowsdata.tar AppName.msi)\n")
			return
		#build to exe, dll etc.
		resultDir = self._pydist.build(dataZipLoc, "windows")

		#copying in files needed to create the msi.
		shutil.copy(
			self._mm.resourcePath("openteacher.ico"),
			os.path.join(resultDir, "openteacher.ico")
		)
		shutil.copy(
			self._mm.resourcePath("leftbanner.bmp"),
			os.path.join(resultDir, "leftbanner.bmp")
		)
		shutil.copy(
			self._mm.resourcePath("topbanner.bmp"),
			os.path.join(resultDir, "topbanner.bmp")
		)
		shutil.copy(
			self._mm.resourcePath("COPYING.rtf"),
			os.path.join(resultDir, "COPYING.rtf")
		)

		#Build msi
                cwd = os.getcwd()
                os.chdir(resultDir)
                #complete the template and write it to the hard disk

                components, files = self._gatherFiles("python")
                components2, files2 = self._gatherFiles("src")

                components += components2
                files += files2

                with open("OpenTeacher.wxs", "w") as f:
                    f.write(wxs.strip().format(
                        files=files,
                        components=components,
                        uuid1=uuid.uuid4(),
                        uuid2=uuid.uuid4()
                    ))

                wixPath = "C:/Program Files/Windows Installer XML v3.5/bin/"

                subprocess.check_call(wixPath + "candle.exe OpenTeacher.wxs")
                subprocess.check_call(wixPath + "light.exe -ext WixUtilExtension -ext WixUIExtension -ext WiXNetFxExtension OpenTeacher.wixobj")

                os.chdir(cwd)

		shutil.copy(
			os.path.join(resultDir, "OpenTeacher.msi"),
			msiLoc
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._pydist = self._modules.default("active", type="pydistInterface")

		self._modules.default(type="execute").startRunning.handle(self._run)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._pydist

def init(moduleManager):
	return WindowsMsiPackagerModule(moduleManager)
