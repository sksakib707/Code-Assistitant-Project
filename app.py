from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QWidget
from  main import MainWindow
from library import Library

def load_stylesheet(file_name):
    with open(file_name,'r') as file:
        return file.read()

def main():
    app = QApplication([])
    main_context = MainWindow()
    
    stylesheet = load_stylesheet("styles/style.qss")
    app.setStyleSheet(stylesheet)
    main_context.show() 
    app.exec_()

if __name__ == "__main__":
    main()