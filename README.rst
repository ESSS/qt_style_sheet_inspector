
========================
Qt Style Sheet Inspector
========================

.. image:: https://img.shields.io/travis/ESSS/qt_style_sheet_inspector.svg
    :target: https://travis-ci.org/ESSS/qt_style_sheet_inspector

.. image:: https://img.shields.io/appveyor/ci/ESSS/qt-style-sheet-inspector/master.svg
    :target: https://ci.appveyor.com/project/ESSS/qt-style-sheet-inspector

.. image:: https://img.shields.io/pypi/v/qt_style_sheet_inspector.svg
    :target: https://pypi.python.org/pypi/qt_style_sheet_inspector

.. image:: https://img.shields.io/pypi/pyversions/qt_style_sheet_inspector.svg
    :target: https://pypi.python.org/pypi/qt_style_sheet_inspector


An inspector widget to view and modify the style sheet of a Qt app at runtime.


Usage
-----

In order to use the inspector widget on your application, it's necessary to initialize the class :code:`style_sheet_inspector_class` passing the instance of the :code:`QMainWindow` from the application.

The repository demo_qt_inspector_ contains a full example of a Qt Application with an inspector widget being called by a shortcut action.

.. _demo_qt_inspector: https://github.com/williamjamir/demo_qt_inspector


See the demo in action:

.. image:: https://github.com/williamjamir/demo_qt_inspector/blob/master/images/qt_inspector_demo.gif
    :width: 10px
    :height: 10px
    :scale: 10 %


Features
--------
View current style sheet of an application during runtime
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The inspector only checks for style sheets that were applied to the QApplication, it's the topmost and any change here can be propagated to all children. 
    
Style sheets that applied to an individual widget will not appear on the inspector.


Style sheet can be changed at runtime (Pressing CTRL+S)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image::  https://github.com/williamjamir/demo_qt_inspector/blob/master/images/qt_inspector_runtime_changes.gif
    :width: 10px
    :height: 10px
    :scale: 10 %

Search bar to help find specific types or names (Pressing F3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: https://github.com/williamjamir/demo_qt_inspector/blob/master/images/qt_inspector_search.gif
    :width: 10px
    :height: 10px
    :scale: 10 %

Can undo/redo changes (Pressing CTRL+ALT+Z or CTRL+ALT+Y)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       
.. image:: https://github.com/williamjamir/demo_qt_inspector/blob/master/images/qt_inspector_undo_redo.gif
    :width: 10px
    :height: 10px
    :scale: 10 %
    
Observation
-----------

It needs PyQt5 to work, but it doesn't have it as a dependency.
    
* Free software: MIT license
