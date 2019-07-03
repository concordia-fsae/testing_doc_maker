import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from homepage import Ui_MainWindow
from openpyxl import load_workbook

### Excel stuff

doc_template = load_workbook(filename = 'CFRxxxxx - Base Testing Checklist.xlsx')
doc_template_path = ""
pc01 = doc_template['General Information']
pc02 = doc_template['PC02 - Safety']
pc08 = doc_template['PC08 - Personnel List']


### PyQT Stuff

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_save_doc.clicked.connect(self.saveFileDialog)
        self.ui.btn_open_template.clicked.connect(self.openFileNameDialog)
        self.ui.actionOpen_Template_File.triggered.connect(self.openFileNameDialog)
        self.ui.actionSave_Testing_Doc.triggered.connect(self.saveFileDialog)
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Template File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            doc_template_path = file_name

    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"Save Testing Doc","","Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            print(file_name)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())