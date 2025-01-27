from PyQt5.QtCore import (Qt,
    QThread,
    pyqtSignal,
    pyqtSlot,
    QPoint)
from PyQt5.QtWidgets import (QWidget,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QScrollArea)

from PyQt5.QtGui import (QPixmap, QImage)
import fitz  # PyMuPDF
from multiprocessing import Pool,cpu_count
from functools import partial
import math
import os


class PageLoaderThread(QThread):
    page_loaded = pyqtSignal(int, QPixmap)  # Emit page number and pixmap

    def __init__(self, file_path, scale_factor=1.0):
        super().__init__()
        self.file_path = file_path
        self.scale_factor = scale_factor

    def run(self):
        doc = fitz.open(self.file_path)
        for i in range(len(doc)):
            page = doc[i]
            # Re-render the page at the desired scale factor
            mat = fitz.Matrix(self.scale_factor, self.scale_factor)
            pix = page.get_pixmap(matrix=mat)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.page_loaded.emit(i, pixmap)  # Emit page number and pixmap
        doc.close()

class PDFView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.current_scale_factor = 1.0
        # Other initialization...
        self.pdf_page = QWidget()
        self.pdf_layout = QVBoxLayout(self.pdf_page)
        self.pdf_layout.setAlignment(Qt.AlignCenter)

        # Scroll area to contain the PDF page
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.pdf_page)
        self.scroll_area.setWidgetResizable(True)

        # Main layout for the entire PDFView widget
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

        # Zoom buttons
        self.zoom_in_button = QPushButton("+", self)
        self.zoom_in_button.clicked.connect(self.zoomInClicked)
        self.zoom_in_button.setObjectName("zoomButton")
        self.zoom_out_button = QPushButton("-", self)
        self.zoom_out_button.clicked.connect(self.zoomOutClicked)
        self.zoom_out_button.setObjectName("zoomButton")
        self.zoom_in_button.setFixedSize(50, 50)
        self.zoom_out_button.setFixedSize(50, 50)

        # Place buttons at the bottom-right of the scroll area
        self.zoom_in_button.move(self.scroll_area.width() - self.zoom_in_button.width() ,
                                 self.scroll_area.height() - 2 * self.zoom_in_button.height())
        self.zoom_out_button.move(self.scroll_area.width() - self.zoom_out_button.width(),
                                  self.scroll_area.height() - self.zoom_out_button.height() )

        # Ensure buttons stay on top of the scroll area
        self.zoom_out_button.raise_()

        # Handle window resizing to keep buttons at the correct position
        self.resizeEvent = self._on_resize
    def _on_resize(self, event):
        #Update button positions when the window is resized.
        self.zoom_in_button.move(self.scroll_area.width() - self.zoom_in_button.width() - 10,
                                 self.scroll_area.height() - 2 * self.zoom_in_button.height() - 10)
        self.zoom_out_button.move(self.scroll_area.width() - self.zoom_out_button.width() - 10,
                                  self.scroll_area.height() - self.zoom_out_button.height() - 10)
        self.zoom_in_button.show()
        self.zoom_out_button.show()

    def zoomInClicked(self):
        self.current_scale_factor += 0.2
        self.startLoadingPDF(self.current_file_path)

    def zoomOutClicked(self):
        self.current_scale_factor = max(0.2, self.current_scale_factor - 0.2)
        self.startLoadingPDF(self.current_file_path)

    def startLoadingPDF(self, file_path):

        if not file_path:
            return

        self.current_file_path = file_path

        # Clear previous pages
        for i in reversed(range(self.pdf_layout.count())):
            widget = self.pdf_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Display initial "Loading" message
        self.loading_label = QLabel("Loading pages...")
        self.pdf_layout.addWidget(self.loading_label)

        # Start the thread to load PDF pages
        self.page_loader_thread = PageLoaderThread(file_path, self.current_scale_factor)
        self.page_loader_thread.page_loaded.connect(self.displayPage)
        self.page_loader_thread.start()


    @pyqtSlot(int, QPixmap)
    def displayPage(self, page_number, pixmap):
        # Remove the loading label after the first page
        if hasattr(self, 'loading_label'):
            self.loading_label.deleteLater()
            del self.loading_label

        # Display the actual page
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        self.pdf_layout.addWidget(image_label)

class Library(QWidget):
    def __init__(self):
        super().__init__()

        self._b_folder_open = QPushButton('Folders')
        self._b_folder_open.setObjectName('folder')
        self._b_folder_open.clicked.connect(self.open_folder)

        #creating an object of pdf class
        self._pdf_view = PDFView()

        self._file_tree = QTreeWidget()
        self._file_tree.setHeaderHidden(True)
        #loading pdf based on click
        self._file_tree.itemClicked.connect(self.view_pdf)
        self._file_tree.setObjectName('tree_view')

        self._left_side_layout = QVBoxLayout()
        self._left_side_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self._left_side_layout.addWidget(self._b_folder_open)
        self._left_side_layout.addWidget(self._file_tree)


        self.library_layout = QHBoxLayout()
        self.library_layout.addLayout(self._left_side_layout,20)
        self.library_layout.addWidget(self._pdf_view,80)
        self.setLayout(self.library_layout)

    def view_pdf(self,item,col):

        texts = []
        try:
            while item is not None:

            # Inserting the text of the tree item at the beginning of the list.
                texts.insert(0, item.text(0))

                item = item.parent()  # Getting the parent item.

        # Joining the text of the tree items to create the file name.
            filename = "/".join(texts[1:])

        # Creating the full path of the file.
            filepath = os.path.join(self.folder, filename)
            if filename.endswith("pdf"):
                self._pdf_view.startLoadingPDF(filepath)
        except Exception as e:
            print(e)

    def open_folder(self):
        self.folder = QFileDialog.getExistingDirectory(self, 'Select Folder')

        if self.folder:
            self._file_tree.clear()
            self.populate_tree(self.folder)

    def populate_tree(self, folder_path):
        root_item = QTreeWidgetItem(self._file_tree)
        root_item.setText(0, os.path.basename(folder_path))

        root_item.setData(0, Qt.UserRole, folder_path)
        self.add_tree_items(root_item, folder_path)
        root_item.setExpanded(True)

    def add_tree_items(self, parent_item, path):
        extension = ['.pdf']
        for item_name in os.listdir(path):
            item_path = os.path.join(path, item_name)

            if os.path.isdir(item_path):
                tree_item = QTreeWidgetItem(parent_item)
                tree_item.setText(0, item_name)
                tree_item.setData(0, Qt.UserRole, item_path)
                self.add_tree_items(tree_item, item_path)
                tree_item.setExpanded(False)
            else:
                if any(item_name.endswith(ext) for ext in extension):
                    tree_item = QTreeWidgetItem(parent_item)
                    tree_item.setText(0, item_name)
                    tree_item.setData(0,Qt.UserRole , item_path)