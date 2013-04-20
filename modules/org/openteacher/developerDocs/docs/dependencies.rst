============
Dependencies
============

This page contains a list of dependencies needed when you want to run
every single bit of OpenTeacher. In practise, only a subset is required
since most of the dependencies below are only used when developing.
Also, OpenTeacher nicely disables parts of itself when dependencies are
missing. In other words, running it with e.g. only Python and PyQt4
works just fine.

Dependencies for using OpenTeacher
==================================

* python
* python-qt4
* python-qt4-phonon
* python-qt4-gl
* python-pycountry
* python-enchant
* pyttsx (currently included)
* espeak
* tesseract-ocr | cuneiform

also (test server):
* python-django
* django-rest-framework

and if we ever implement updates:
* gpg
* python-gnupg?

Dependencies for developing OpenTeacher
=======================================

* python-flask
* python-cherrypy3
* python-pygments
* python-docutils
* python-launchpadlib
* python-polib
* python-pygraphviz
* python-twisted
* python-faulthandler
* gettext
* cython

(deb build only & optional:)

* python-all-dev
* build-essential

Alternative runtimes
====================

This list of dependencies can give problems on alternative Python
runtimes. (We're currently targetting CPython 2.6 & 2.7)

Incompatible dependencies: PyPy
-------------------------------

* python-qt4
* python-qt4-phonon
* python-qt4-gl
* python-pygraphviz
* python-faulthandler (although similar tools might exist)

unsure (but they probably work as they probably don't use C extensions):

* python-launchpadlib
* python-polib
* python-gnupg

Incompatible dependencies: CPython 3.x
--------------------------------------

* pyttsx (no detectable effort ongoing)
* python-flask (but: 'https://github.com/mitsuhiko/flask/issues/587')
* python-launchpadlib (https://bugs.launchpad.net/launchpadlib/+bug/1060734)
* python-twisted (but: http://twistedmatrix.com/trac/milestone/Python-3.x & http://twistedmatrix.com/trac/wiki/Plan/Python3)
