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

* espeak
* pyratemp (currently included)
* python
* python-chardet
* python-enchant
* python-qt4
* python-qt4-gl
* python-qt4-phonon
* pyttsx (currently included)
* tesseract-ocr or cuneiform

also (test server):

* python-django
* django-rest-framework

also (command line interface)

* python-urwid

also (gtk ui)

* python-gi (gobject-introspection)

and if we ever implement updates:

* gpg
* python-gnupg?

Dependencies for developing OpenTeacher
=======================================

* couchdb
* cython
* gettext
* python-babel
* python-docutils
* python-faulthandler
* python-flask
* python-launchpadlib
* python-polib
* python-pygments
* python-pygraphviz
* python-twisted
* python-recaptcha
* python-feedparser

(deb build only & optional:)

* python-all-dev
* build-essential

(when building windows/mac packages only:)

* PyInstaller

(when running the package-all command, getting these requirements
satisfied takes time.)

* ssh
* VirtualBox
* the right network setup
* properly installed VM's.

Alternative runtimes
====================

This list of dependencies can give problems on alternative Python
runtimes. (We're currently targetting CPython 2.6 & 2.7)

Incompatible dependencies: PyPy
-------------------------------

* python-qt4
* python-qt4-phonon
* python-qt4-gl
* python-enchant
* python-pygraphviz
* python-faulthandler (although similar tools might exist, necessary?)
* python-gi
* PyInstaller
* python-bzrlib

unsure (but they probably work as they probably don't use C extensions):

* python-launchpadlib
* python-polib
* python-gnupg

Incompatible dependencies: CPython 3.x
--------------------------------------

* pyttsx (but: https://github.com/parente/pyttsx/issues/21)
* python-bzrlib (no visible effort ongoing)
* python-launchpadlib (https://bugs.launchpad.net/launchpadlib/+bug/1060734)
* python-twisted (but: http://twistedmatrix.com/trac/milestone/Python-3.x & http://twistedmatrix.com/trac/wiki/Plan/Python3)
* PyInstaller (but: http://www.pyinstaller.org/ticket/85)
