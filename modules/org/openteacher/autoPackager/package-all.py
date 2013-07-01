import subprocess
import contextlib
import time
import os

#utils
@contextlib.contextmanager
def current_working_directory(directory):
	cwd = os.getcwd()
	os.chdir(directory)
	try:
		yield
	finally:
		os.chdir(cwd)

#ssh
def block_until_ssh_connection(hostname):
	while True:
		p = subprocess.Popen(["ssh", hostname], stdin=subprocess.PIPE)
		with contextlib.ignored(OSError):
			#the with statement handles the rare case of a broken pipe
			p.communicate("exit 0")
			p.wait()
			if p.returncode == 0:
				break

def run_ssh(hostname, script):
	process = subprocess.Popen(["ssh", hostname], stdin=subprocess.PIPE)
	process.communicate(script)
	process.wait()

def run_sftp(hostname, script):
	process = subprocess.Popen(["sftp", hostname], stdin=subprocess.PIPE)
	process.communicate(script)
	process.wait()

class VmBuilder(object):
	def build_all(self):
		self.build_for_ubuntu_and_source_files()
		self.build_for_arch()
		self.build_for_opensuse()
		self.build_for_fedora()
		self.build_for_mac()
		self.build_for_windows()

	@contextlib.contextmanager
	def _vm(self, name, shutdown_gracefully):
		subprocess.check_call(["VBoxManage", "startvm", name, "--type", "headless"])
		try:
			yield
		finally:
			if shutdown_gracefully:
				subprocess.check_call(["VBoxManage", "controlvm", name, "acpipowerbutton"])
			else:
				subprocess.check_call(["VBoxManage", "controlvm", name, "poweroff"])

	#platform dependent build scripts
	def build_for_arch(self):
		ip = "192.168.1.40"
		with self._vm("ArchBang", shutdown_gracefully=True):
			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				bzr pull --overwrite
				python2 openteacher.py -p package-arch `bzr revno` arch.pkg.tar.xz
			""")
			run_sftp(ip, """
				cd 3.x
				get arch.pkg.tar.xz
				rm arch.pkg.tar.xz
			""")

	def build_for_fedora(self):
		ip = "192.168.1.41"
		with self._vm("Fedora", shutdown_gracefully=False):
			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				bzr pull --overwrite
				python openteacher.py -p package-rpm `bzr revno` fedora.rpm
			""")
			run_sftp(ip, """
				cd 3.x
				get fedora.rpm
				rm fedora.rpm
			""")

	def build_for_opensuse(self):
		ip = "192.168.1.42"
		with self._vm("openSUSE", shutdown_gracefully=False):
			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				bzr pull --overwrite
				python openteacher.py -p package-rpm `bzr revno` opensuse.rpm
			""")
			run_sftp(ip, """
				cd 3.x
				get opensuse.rpm
				rm opensuse.rpm
			""")

	def build_for_mac(self):
		ip = "192.168.1.43"
		vm_name = "Mac OS X Mountain Lion (iATKOS ML2)"
		with self._vm(vm_name, shutdown_gracefully=False):
			#wait to reach the boot menu
			time.sleep(10)

			#1c == enter == starting OS X
			subprocess.check_call(["VBoxManage", "controlvm", vm_name, "keyboardputscancode", "1c"])

			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				/opt/local/bin/bzr pull --overwrite
				/opt/local/bin/python openteacher.py -p package-mac mac.dmg
			""")
			run_sftp(ip, """
				cd 3.x
				get mac.dmg
				rm mac.dmg
			""")

	def build_for_windows(self):
		ip = "192.168.1.44"
		vm_name = "Windows 7"
		with self._vm(vm_name, shutdown_gracefully=False):
			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				bzr pull --overwrite
				python openteacher.py -p package-windows-portable windows-portable.zip
				python openteacher.py -p package-windows-msi windows-installer.msi
			""")
			run_sftp(ip, """
				cd 3.x
				get windows-portable.zip
				rm windows-portable.zip
				get windows-installer.msi
				rm windows-installer.msi
			""")

	def build_for_ubuntu_and_source_files(self):
		ip = "192.168.1.45"
		with self._vm("Ubuntu", shutdown_gracefully=False):
			block_until_ssh_connection(ip)
			run_ssh(ip, """
				cd 3.x
				bzr pull --overwrite
				python openteacher.py -p package-debian 0rev`bzr revno` debian.deb false
				python openteacher.py -p package-source-with-setup linux.tar.gz
				python openteacher.py -p package-source source.zip
			""")
			run_sftp(ip, """
				cd 3.x
				get debian.deb
				rm debian.deb
				get linux.tar.gz
				rm linux.tar.gz
				get source.zip
				rm source.zip
			""")

def upload():
	run_sftp("web.openteacher.org", """
		cd www/web.openteacher.org/www-root/regular-builds
		put *
	""")

def main(outputDir):
	with current_working_directory(outputDir):
		VmBuilder().build_all()
		upload()

if __name__ == "__main__":
	main("results")
