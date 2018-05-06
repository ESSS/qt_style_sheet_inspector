# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import inspect
from textwrap import dedent

import PyQt5
from PyQt5.QtCore import QEvent, Qt, QCoreApplication
from PyQt5.QtGui import QKeySequence, QTextCursor, QStandardItemModel, QStandardItem, QPalette, \
    QColor, QPainter, QPen
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QMessageBox, \
    QShortcut, QTextEdit, QVBoxLayout, QWidget, qApp, QMenuBar, QAction, QPushButton, \
    QTreeView, QSplitter



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
        self.add_menu_bar()

        self.style_sheet_widget = StyleSheetWidget()
        self.element_inspect_widget = ElementInspectWidget()

        layout = QHBoxLayout()
        layout.addWidget(self.element_inspect_widget)
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

        self.style_sheet_action = QAction('Open Style Sheet Inspector', self)
        self.style_sheet_action.triggered.connect(self._open_style_sheet_inspector)

        self.element_inspector_action = QAction('Open Element Inspector', self)
        self.element_inspector_action.triggered.connect(self._open_element_inspector)
        self.element_inspector_action.setShortcut('CTRL+E')

        self.menu_bar.addAction(self.style_sheet_action)
        self.menu_bar.addAction(self.element_inspector_action)


    def _open_element_inspector(self):
        self.layout().removeWidget(self.style_sheet_widget)
        self.layout().addWidget(self.element_inspect_widget)
        self.layout().update()


    def _open_style_sheet_inspector(self):
        self.layout().removeWidget(self.element_inspect_widget)
        self.layout().addWidget(self.style_sheet_widget)
        self.layout().update()



class OverlayInspectWidget(QWidget):
    def __init__(self, parent=None):
        super(OverlayInspectWidget, self).__init__(parent)

        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.widget_geometry = None
        # Color that overlay the widget
        self.fillColor = QColor(102, 121, 163, 120)
        # Color of the border
        self.pen = QPen(QColor("#333333"), 3, Qt.SolidLine)


    def paintEvent(self, event):
        widget_size = self.size()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(self.pen)
        painter.setBrush(self.fillColor)

        if self.widget_geometry:
            painter.drawRect(self.widget_geometry)
        else:
            painter.drawRect(0, 0, widget_size.width(), widget_size.height())


    def SetGeometry(self, widget_geometry):
        self.widget_geometry = widget_geometry



class ElementInspectWidget(QWidget):

    def __init__(self, parent=None):
        super(ElementInspectWidget, self).__init__(parent)

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.tree = QTreeView(self)
        self.editor = QTextEdit(self)

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.editor)
        layout.addWidget(self.splitter)

        self.overlay = OverlayInspectWidget()
        self.overlay.hide()

        root_model = QStandardItemModel()
        self.tree.setModel(root_model)
        top_level_widgets = QCoreApplication.instance().topLevelWidgets()
        self._populate_tree(top_level_widgets,root_model)

        self.tree.clicked.connect(self._item_selected)
        self.tree.expandAll()


    def _item_selected(self, index):
        current_item = index.model().itemFromIndex(self.tree.selectedIndexes()[0]).data()
        self.overlay.SetGeometry(None)
        self.editor.clear()

        # I could not make isinstance to work in this case because all objects inherit from QObject
        if current_item.__class__.__name__ == 'QObject':
            return

        if current_item.isWidgetType():
            self.overlay.setParent(current_item)
            self.editor.append("Specific style sheet: {} \n\n".format(current_item.styleSheet()))
        else:
            self.overlay.setParent(current_item.parentWidget())

        self.editor.append("Object Name: {} \n\n".format(current_item.objectName()))
        self.editor.append("Location: {} \n\n".format(inspect.getmodule(current_item)))
        self.overlay.setVisible(True)


    def _populate_tree(self, list_with_widgets, tree_parent):
        for current_widget in list_with_widgets:
            if isinstance(current_widget, excluded_element_list):
                continue

            name = ' {} - ( {} )'.format(current_widget.objectName(), current_widget.__class__.__name__)
            tree_item = QStandardItem(name)
            tree_item.setData(current_widget)
            tree_parent.appendRow(tree_item)

            if current_widget.children():
                self._populate_tree(current_widget.children(), tree_item)



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



excluded_element_list = (StyleSheetInspector, StyleSheetWidget, OverlayInspectWidget, ElementInspectWidget)
