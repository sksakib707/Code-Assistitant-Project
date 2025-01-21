from PyQt5.QtCore import (Qt,
    QThread, 
    pyqtSignal, 
    pyqtSlot)
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
import os

class PageLoaderThread(QThread):
    page_loaded = pyqtSignal(int, QPixmap)  # Signal for each loaded page

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        doc = fitz.open(self.file_path)
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap()
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.page_loaded.emit(i + 1, pixmap)  # Emit the page number and pixmap for each page
        doc.close()

class PDFView(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 720
        self.height = 720
        self.setWindowTitle('PDF Viewer')
        self.resize(self.width, self.height)
        self.layout = QVBoxLayout()

        self.pdf_page = QWidget()
        self.pdf_layout = QVBoxLayout(self.pdf_page)
        self.pdf_layout.setAlignment(Qt.AlignCenter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.pdf_page)
        self.scroll_area.setWidgetResizable(True)

        # self.button = QPushButton('Open PDF')
        # self.button.clicked.connect(self.getPdfFile)
         
        self.layout.addWidget(self.scroll_area)
        # self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def getPdfFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.startLoadingPDF(file_path)

    def startLoadingPDF(self, file_path):
        # Clear previous pages
        for i in reversed(range(self.pdf_layout.count())):
            widget = self.pdf_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Display initial "Loading" message
        self.loading_label = QLabel("Loading pages...")
        self.pdf_layout.addWidget(self.loading_label)

        # Start the thread to load PDF pages
        self.page_loader_thread = PageLoaderThread(file_path)
        self.page_loader_thread.page_loaded.connect(self.displayPage)
        self.page_loader_thread.start()

    @pyqtSlot(int, QPixmap)
    def displayPage(self, page_number, pixmap):
        # Remove the loading label after the first page
        if hasattr(self, 'loading_label'):
            self.loading_label.deleteLater()
            del self.loading_label

        # Display loading message for each page
        # page_number_label = QLabel(f'Loading page: {page_number}')
        # self.pdf_layout.addWidget(page_number_label)

        # Display the actual page
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        self.pdf_layout.addWidget(image_label)

class Library(QWidget):
    def __init__(self):
        super().__init__()
        # self.resize(1080,720)
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
        # print("this is view_pdf function")
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
        # self._b_folder_open.setText(os.path.basename(folder_path))
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

                    


