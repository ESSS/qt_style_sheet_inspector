#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import qApp
from qt_style_sheet_inspector import StyleSheetInspector


def test_load_style_sheet(inspector):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    """
    assert inspector.widget.style_text_edit.toPlainText() == qApp.styleSheet()


def test_apply(inspector):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    """
    assert not inspector.widget.apply_button.isEnabled()
    inspector.widget.style_text_edit.setPlainText(qApp.styleSheet() + """\
        QLabel {
            font-size: 14px;
        }
    """)
    assert inspector.widget.apply_button.isEnabled()
    inspector.widget.apply_button.click()
    assert inspector.widget.style_text_edit.toPlainText() == qApp.styleSheet()
    assert not inspector.widget.apply_button.isEnabled()


def test_search_hit(inspector):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    """
    # keyClick only works if window is shown
    inspector.show()

    assert inspector.widget.style_text_edit.textCursor().position() == 0

    # there are 3 occurrences of "0px" in style sheet, after that it should cycle back to first
    # occurrence
    inspector.widget.search_bar.setText("0px")
    assert inspector.widget.search_bar.styleSheet() == "color: green;"
    assert inspector.widget.style_text_edit.textCursor().position() == 35

    inspector.widget.onNextSearchHit()
    assert inspector.widget.search_bar.styleSheet() == "color: green;"
    assert inspector.widget.style_text_edit.textCursor().position() == 61

    inspector.widget.onNextSearchHit()
    assert inspector.widget.search_bar.styleSheet() == "color: green;"
    assert inspector.widget.style_text_edit.textCursor().position() == 86

    inspector.widget.onNextSearchHit()
    assert inspector.widget.search_bar.styleSheet() == "color: green;"
    assert inspector.widget.style_text_edit.textCursor().position() == 35


def test_search_miss(inspector):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    """
    # keyClick only works if window is shown
    inspector.show()

    assert inspector.widget.style_text_edit.textCursor().position() == 0

    inspector.widget.search_bar.setText("INVALID")
    assert inspector.widget.search_bar.styleSheet() == "color: red;"
    assert inspector.widget.style_text_edit.textCursor().position() == 0

    inspector.widget.onNextSearchHit()
    assert inspector.widget.search_bar.styleSheet() == "color: red;"
    assert inspector.widget.style_text_edit.textCursor().position() == 0


def test_focus_search_bar(inspector, mocker):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    :type mocker: pytest_mock.MockFixture
    """
    # keyClick only works if window is shown
    inspector.show()

    # testing focus is unreliable, especially when using multiprocessing
    mocker.patch.object(inspector.widget.search_bar, 'setFocus')
    inspector.widget.onFocusSearchBar()
    inspector.widget.search_bar.setFocus.assert_called_once_with()


def test_undo_redo(inspector):
    """
    :type inspector: qt_style_sheet_inspector.StyleSheetInspector
    """
    # keyClick only works if window is shown
    inspector.show()

    style_sheets = [qApp.styleSheet()]

    # Undo before changes doesn't have any effect
    inspector.widget.onUndo()
    assert inspector.widget.style_text_edit.toPlainText() == style_sheets[-1]

    # Undo after changes
    inspector.widget.style_text_edit.setPlainText(qApp.styleSheet() + """\
        QLabel {
            font-size: 14px;
        }
    """)
    inspector.widget.apply_button.click()
    current = qApp.styleSheet()
    assert inspector.widget.style_text_edit.toPlainText() == current
    assert current != style_sheets[-1]
    style_sheets.append(current)

    inspector.widget.onUndo()
    assert inspector.widget.style_text_edit.toPlainText() == style_sheets[-2]

    # Redo
    inspector.widget.onRedo()
    assert inspector.widget.style_text_edit.toPlainText() == style_sheets[-1]

    # Redo again, won't have any effect
    inspector.widget.onRedo()
    assert inspector.widget.style_text_edit.toPlainText() == style_sheets[-1]

    # Undo, change again then try to redo, won't have any effect, as state tape has been updated
    inspector.widget.onUndo()
    inspector.widget.style_text_edit.setPlainText(qApp.styleSheet() + """\
        QPushButton {
            background-color: #dcdddf;
        }
    """)
    inspector.widget.apply_button.click()
    current = qApp.styleSheet()
    assert inspector.widget.style_text_edit.toPlainText() == current
    assert current != style_sheets[-1]
    style_sheets.append(current)

    inspector.widget.onRedo()
    assert inspector.widget.style_text_edit.toPlainText() == style_sheets[-1]


@pytest.fixture
def initial_qss():
    return """\
        * {
            margin: 0px;
            padding: 0px;
            border: 0px;
            font-family: "Century Gothic";
        }
    """


@pytest.fixture
def inspector(qtbot, initial_qss):
    """
    :type qtbot: pytestqt.plugin.QtBot
    """
    qApp.setStyleSheet(initial_qss)

    inspector_ = StyleSheetInspector()
    qtbot.addWidget(inspector_)
    return inspector_
