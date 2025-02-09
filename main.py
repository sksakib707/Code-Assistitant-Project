from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QComboBox,
    QVBoxLayout,
    QStackedWidget
)
from PyQt5.QtGui import QIcon
from library import Library
from editor import EditorUI as Editor


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Assistant")
        self.setWindowIcon(QIcon("codeicon.ico"))
        self.resize(1080, 720)

        # Dropdown menu
        self.main_drop_down_box = QComboBox()
        self.main_drop_down_box.setObjectName("drop_down")
        self.main_drop_down_box.addItem("IDE")
        self.main_drop_down_box.addItem("LIBRARY")
        self.main_drop_down_box.activated.connect(self.changeOptions)

        # Widgets for different sections
        self.library_widget = Library()
        self.editor_widget = Editor()

        # QStackedWidget to manage switching between widgets
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.editor_widget)
        self.stacked_widget.addWidget(self.library_widget)

        # Layout for dropdown and stacked widget
        self.selection_layout = QVBoxLayout()
        self.selection_layout.addWidget(self.main_drop_down_box)
        self.selection_layout.addWidget(self.stacked_widget)
        self.selection_layout.setAlignment(Qt.AlignTop)

        # Set the layout for the main window
        self.setLayout(self.selection_layout)

    def changeOptions(self):
        # Switch to the corresponding widget in QStackedWidget
        current_index = self.main_drop_down_box.currentIndex()
        self.stacked_widget.setCurrentIndex(current_index)

