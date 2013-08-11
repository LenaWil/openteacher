import contextlib

@contextlib.contextmanager
def ignored(e):
	try:
		yield
	except e:
		pass
