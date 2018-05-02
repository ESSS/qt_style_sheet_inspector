# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import types
from contextlib import contextmanager
from textwrap import dedent

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeySequence, QTextCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QMessageBox, \
    QPushButton, QShortcut, QTextEdit, QVBoxLayout, QWidget, qApp, QMenuBar, QAction, QPushButton, \
    QTreeView, QSplitter
from PyQt5.uic.properties import QtGui


class StyleSheetInspector(QDialog):
    """
    An inspector window that tries to aid developers inspecting current style
    sheet used by a Qt application.

    It provides a few features:

    * a search bar to search for occurrences in style sheet
    * apply style sheet changes to app in run time, without the necessity of
        regenerating Qt resource files for every change in QSS, which can
        speed the design of a style sheet a lot.
    * undo/redo of applied style sheets

    Press `F1` to see all available shortcuts.

    About code style
    ----------------

    Since it is an specialization of a Qt widget, it reuses its code style so
    its API is consistent.

    Known issues
    ------------

    * Inspector window still reuses app style sheet, which can be annoying
    when testing styles. Is there a way to avoid reusing style sheets?

    Reference
    ---------

    Inspired by
    http://doc.qt.io/qt-5/qtwidgets-widgets-stylesheet-example.html.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Qt Style Sheet Inspector')
        self.widget = StyleSheetWidget()
        self.model_explorer = ModelExplorerDialog()
        layout = QHBoxLayout()
        layout.addWidget(self.widget)

        self.add_menu_bar()
        layout.setMenuBar(self.menu_bar)
        self.setLayout(layout)

    def event(self, event):
        """
        Overridden to show shortcuts on `?` button of dialog.
        """
        if event.type() == QEvent.EnterWhatsThisMode:
            from PyQt5.QtWidgets import QWhatsThis
            QWhatsThis.leaveWhatsThisMode()
            self.widget.onHelp()
            return True
        return QDialog.event(self, event)

    def add_menu_bar(self):
        self.menu_bar = QMenuBar()
        # self.menu_bar.addMenu("Menu")
        self.open_action = QAction('Open', self)
        self.open_action.setStatusTip('Open a file into Template.')
        self.open_action.setShortcut('CTRL+M')
        self.open_action.triggered.connect(lambda: self.model_explorer.exec_())
        self.menu_bar.addAction(self.open_action)


class ModelExplorerDialog(QDialog):

    def __init__(self, parent=None):
        super(ModelExplorerDialog, self).__init__(parent)

        tree = {'root': {
            "1": ["A", "B", "C"],
            "2": {
                "2-1": ["G", "H", "I"],
                "2-2": ["J", "K", "L"]},
            "3": ["D", "E", "F"]}
        }

        self.tree = QTreeView(self)
        self.editor = QTextEdit(self)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.editor)
        self.last_item_clicked = None
        self.last_item_clicked_style = None

        layout = QHBoxLayout(self)
        layout.addWidget(self.splitter)

        self.editor.setText(" Values ")
        root_model = QStandardItemModel()
        root_model.objectName()
        self.tree.setModel(root_model)
        self.tree.clicked.connect(self._item_on_tree_view_selected)
        self.tree.expandAll()
        self._set_tree_view_widgets(root_model)



    def _item_on_tree_view_selected(self, index):
        import inspect

        self.restore_style_from_last_clicked_item()

        current_item = index.model().itemFromIndex(self.tree.selectedIndexes()[0]).data()
        self.last_item_clicked_style = current_item.styleSheet()

        self.editor.clear()
        self.editor.append("Object Name: {} \n\n".format(current_item.objectName()))
        self.editor.append("Location: {} \n\n".format(inspect.getmodule(current_item)))
        self.editor.append("Specific style sheet: {} \n\n".format(current_item.styleSheet()))

        current_item.setStyleSheet(current_item.styleSheet() + ' ' + """
                    border: 1px solid red;
                """)
        self.last_item_clicked = current_item

    def restore_style_from_last_clicked_item(self):
        if self.last_item_clicked:
            self.last_item_clicked.setStyleSheet(self.last_item_clicked_style)

    def _set_tree_view_widgets(self, item_model):
        from PyQt5.QtCore import QCoreApplication
        core = QCoreApplication.instance()
        top_level_widgets = core.topLevelWidgets()


        self._populate_tree(top_level_widgets, item_model)


    def _populate_tree(self, list_with_widgets, parent):
        print("current_list: ", list_with_widgets)
        for current_widget in list_with_widgets:
            print("current_item: ", current_widget)
            name = ' {} - ( {} )'.format(current_widget.objectName(), current_widget.__class__.__name__)

            item = QStandardItem(name)
            item.setData(current_widget)
            parent.appendRow(item)
            print(name)
            if current_widget.children():
                print("Sending this children: ", current_widget.children())
                print("item model :", parent)
                print("name : ", name)
                # print("item model[name] :", parent[name])
                self._populate_tree(current_widget.children(), item)

    def _populateTree(self, children, parent):
        for child in children:
            child_item = QStandardItem(child)
            child_item.custom = 'oi'
            parent.appendRow(child_item)

            if isinstance(children, dict):
                self._populateTree(children[child], child_item)

        push = QPushButton()
        layout = QHBoxLayout()
        layout.addWidget(push)
        self.setLayout(layout)



class StyleSheetWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.tape = []
        self.tape_pos = -1

        self.style_sheet = None

        self.search_bar = QLineEdit(self)
        self.search_bar.textChanged.connect(self.onSearchTextChanged)

        self.style_text_edit = QTextEdit(self)
        self.style_text_edit.textChanged.connect(self.onStyleTextChanged)
        # To prevent messing with contents when pasted from an IDE, for
        # instance.
        self.style_text_edit.setAcceptRichText(False)

        self.apply_button = QPushButton('Apply', self)
        self.apply_button.clicked.connect(self.onApplyButton)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.style_text_edit)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

        next_hit_shortcut = QShortcut(QKeySequence(Qt.Key_F3), self)
        next_hit_shortcut.activated.connect(self.onNextSearchHit)

        search_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self)
        search_shortcut.activated.connect(self.onFocusSearchBar)

        apply_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        apply_shortcut.activated.connect(self.applyStyleSheet)

        undo_shortcut = QShortcut(
            QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Z), self)
        undo_shortcut.activated.connect(self.onUndo)

        redo_shortcut = QShortcut(
            QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Y), self)
        redo_shortcut.activated.connect(self.onRedo)

        help_shortcut = QShortcut(
            QKeySequence(Qt.Key_F1), self)
        help_shortcut.activated.connect(self.onHelp)

        self.loadStyleSheet()

    def onUndo(self, checked=False):
        """
        Undo last applied style sheet, if there is any.
        """
        assert self.tape_pos >= 0
        if self.tape_pos == 0:
            return
        self.tape_pos -= 1
        self.style_text_edit.setPlainText(self.tape[self.tape_pos])
        self.applyStyleSheet(stateless=True)

    def onRedo(self, checked=False):
        """
        Redo last reverted style sheet, if there is any.
        """
        assert self.tape_pos >= 0
        if self.tape_pos == len(self.tape) - 1:
            return
        self.tape_pos += 1
        self.style_text_edit.setPlainText(self.tape[self.tape_pos])
        self.applyStyleSheet(stateless=True)

    def onHelp(self):
        """
        Shows a dialog with available shortcuts.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Help")
        msg_box.setText("Available shortcuts:")
        msg_box.setInformativeText(dedent("""\
            F1: show help dialog
            Ctrl+S: apply current changes
            Ctrl+F: go to search bar
            F3: go to next search hit
            Ctrl+Alt+Z: revert to last applied style sheet
            Ctrl+Alt+Y: redo last reverted style sheet
        """))
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.exec_()

    def onSearchTextChanged(self, text):
        """
        When search bar text changes, try to find text in style sheet text.
        If there is a match, color search bar text green, otherwise goes back
        to start of style sheet text and text is colored red.
        """
        search = self.search_bar.text()
        if not self.style_text_edit.find(search):
            self.search_bar.setStyleSheet("color: red;")
            self.style_text_edit.moveCursor(QTextCursor.Start)
        else:
            self.search_bar.setStyleSheet("color: green;")

    def onNextSearchHit(self):
        """
        Goes to next match to search text. If there isn't any, cycles back to
        first occurrence.
        """
        search = self.search_bar.text()
        if not self.style_text_edit.find(search):
            # Cycle back to first hit
            self.style_text_edit.moveCursor(QTextCursor.Start)
            self.style_text_edit.find(search)

    def onFocusSearchBar(self):
        """
        Focus search bar.
        """
        self.search_bar.setFocus()

    def onStyleTextChanged(self):
        """
        Enable apply button when there are style text changes.
        """
        self.apply_button.setEnabled(True)

    def onApplyButton(self, checked=False):
        """
        Apply style sheet changes in running app when apply button pressed.
        """
        self.applyStyleSheet()

    def loadStyleSheet(self):
        """
        Load app style sheet and displays its text in inspector widget.
        """
        style_sheet = self.style_sheet = qApp.styleSheet()
        self.tape.append(style_sheet)
        self.tape_pos = 0

        self.style_text_edit.setPlainText(style_sheet)
        self.apply_button.setEnabled(False)

    def applyStyleSheet(self, stateless=False):
        """
        Apply style sheet changes in running app.

        :param bool stateless: If true, style sheet state tape isn't updated.
        """
        self.style_sheet = self.style_text_edit.toPlainText()
        qApp.setStyleSheet(self.style_sheet)
        if not stateless:
            if self.tape_pos + 1 < len(self.tape):
                self.tape = self.tape[:self.tape_pos + 1]
            self.tape.append(self.style_sheet)
            self.tape_pos += 1
        self.apply_button.setEnabled(False)
