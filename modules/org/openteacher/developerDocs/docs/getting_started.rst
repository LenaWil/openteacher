===============
Getting started
===============

Introduction
============

So, you want to work on OpenTeacher? Great! This document aims to
describe how to get started, and also offers a reference on how to
accomplish things that are often needed.

OpenTeacher's logic is written in Python and JavaScript. For the main
UI, PyQt4 is used. This tutorial assumes you're familiar with those
three techniques.

.. figure:: modules.jpg
   :width: 300px
   :figwidth: 300px
   :align: right

   OpenTeacher is built completely out of modules.

OpenTeacher, a modularized program
==================================

Most Python programs are organized in Python packages and modules. For
OpenTeacher, we wanted something more flexible. Something which would
allow us to just take out pieces of code, leaving the remaining code
in a working state. Also, we wanted it to be very easy to make multiple
implementations, of which the one to use can be chosen at runtime.

To accomplish this, we developed the module manager. It's in the files
``moduleManager.py`` and ``moduleFilterer.pyx``, in the root of the
OpenTeacher source. The module manager manages, as the name implies,
modules.

What is a module?
-----------------

A module is a Python object defined inside a Python file that is loaded
by the module manager. It gets passed an instance of that same module
manager to access the other modules. That should be enough to understand
`the first file template's structure <file_templates.rst>`_, excluding
the ``enable()``, ``disable()`` and ``type`` properties.. (``init()`` is
called by the module manager to collect the file's module object.)

Where do I store my module?
---------------------------

The main Python file is named the same as the directory it is in, with
the extension ".py" added. There can be additional python files inside
which can be imported via the ``ModuleManager.import_()`` method. If you
want to access non-Python files in the same module, you can do so via
the ``ModuleManager.resourcePath()`` function.

The module's directory may be put inside other directories, as long as
it's placed somewhere in the modules directory next to
``openteacher.py``. In OpenTeacher, we use the 'reversed domain'
naming strategy to ensure modules their names won't conflict with each
other. When writing a module that implements, say, a game for the words
lesson as an OpenTeacher developer, you'd for example store it in here:
``modules/org/openteacher/games/words``.

Which attributes should an OpenTeacher module object have?
----------------------------------------------------------
Although not enforced by the module manager, (almost) all modules have
a few standard attributes:

- ``type``: the module's type specifies what the module does. It's used
  by other modules to find this module. If modules share the same type,
  they share the same (programmatic) interface. In other words, you can
  switch them. This doesn't always make sense though. (Switching a words
  saver with a media server works, but doesn't result in any saved
  file.) When other modules don't have to use your module, you can
  technically leave it out, but that's not recommended.
- ``active``: ``True`` if the module is ready to be used, otherwise
  ``False``. If it's ``False`` and your module has an ``enable()``
  method, that may be called to change this. (The same's true for
  ``disable()``, but then the other way around.) Note that the concept
  of being active is defined in a module, not in the module manager. The
  module that defines it (and some other modules that module needs)
  are just always 'enabled'. When using those modules (most notably the
  ``type=dataStore``, ``type=settings``, ``type=modules`` and
  ``type=execute`` modules), you need to keep this in mind.
- ``enable()``: see ``active``
- ``disable()``: see ``active``
- ``requires``: optional. Specifies a list of module selectors that all
  need to match at least one time before this modules' ``enable()`` may
  be called.
- ``uses``: optional. Specifies a list of module selectors that match
  modules this module can use, but aren't required by it. Before
  ``enable()`` is called, the ``modules`` module (which handles that)
  tries to ``enable()`` as much of them as possible first.
- ``priorities``: TODO

Useful modules
==============
When writing an OpenTeacher module, you have access to every other
module. In a lot of situations, you're only interested in a few. Next to
modules that your module directly needs to do it's job. (E.g. a module
that represents a word list as a string, needs the module that
represents a word as a string), there are a few modules that provide
services useful for a much broader set of modules. They are:

- modules_; can be used to query other modules based on their
  priorities (via ``default`` and ``sort``). There's guaranteed to be
  only one modules module. To get it, use this snippet:
  ``next(iter(self._mm.mods(type="modules")))`` (self._mm being the
  module manager.)
- execute_; modules that can control the program flow (e.g. GUIs, CLIs,
  webservers in OT), handle the ``startRunning`` event of this module.
  That way, they start running after all initialization handled by this
  module is complete. There's guaranteed to be only one execute module
  too, but it's still common to use the execute module to access it
  nonetheless. (snippet: ``self._modules.default(type="execute")`` with
  self._modules as the modules module.)
- dataStore_; allows storing data persistently accross program runs.
- settings_; allows registering settings (that are e.g. shown in the
  GUI.)
- metadata_; keeps all kind of info about the 'brand' OpenTeacher. Like
  the name, the logo, a description of what OT is/does, the license,
  etc.
- TODO: expand. (event, buttonRegister, javaScriptEvaluator?, authors?,
  qtApp?)

.. _modules: ../modules/org/openteacher/modules.html
.. _settings: ../modules/org/openteacher/settings.html
.. _execute: ../modules/org/openteacher/execute.html
.. _dataStore: ../modules/org/openteacher/dataStore.html
.. _settings: ../modules/org/openteacher/settings.html
.. _metadata: ../modules/org/openteacher/metadata.html
