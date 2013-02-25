import subprocess

while True:
	if subprocess.call("python moduleTests.py".split(" ")):
		break
