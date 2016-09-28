========================
Qt Style Sheet Inspector
========================

.. image:: https://img.shields.io/travis/ESSS/qt_style_sheet_inspector.svg
        :target: https://travis-ci.org/ESSS/qt_style_sheet_inspector


A inspector widget to view and modify style sheet of a Qt app in runtime.


* Free software: MIT license


Observation
-----------

It need PyQt5 to work but it doesn't have it as a dependency, as testing with PyQt5 pypi proved
unreliable (may be changed in the future).


Features
--------

* Can view current style sheet of application during runtime
* Style sheet can be changed in runtime, facilitating the process of designing a custom GUI
* Has a search bar to help find specific types or names
* Can undo/redo changes
