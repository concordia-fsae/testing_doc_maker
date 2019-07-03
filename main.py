import sys
import requests

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from homepage import Ui_MainWindow
from openpyxl import load_workbook


### Excel Stuff

# doc_template = load_workbook(filename = 'CFRxxxxx - Base Testing Checklist.xlsx')
doc_template = ""
doc_template_path = ""
pc01 = ""
pc02 = ""
pc08 = ""


### Form Response Stuff

form_resp_url = "https://docs.google.com/forms/u/2/d/e/1FAIpQLSe1iCukrB_HYS1Dvl8rjtazTZyAza1ArFZ-d3HaE-5gXTyWKA/formResponse"
### submission layout: Team, Person submitting form, Month, Day, Year of proposed testing, start hour, start minute, end hour, end minute, type, loc, test lead, other people, doc number, other info


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
        self.file_path_label = self.ui.file_path
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Template File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            # TODO protect this (try except)
            doc_template_path = file_name
            doc_template = load_workbook(filename = doc_template_path)
            pc01 = doc_template['General Information']
            pc02 = doc_template['PC02 - Safety']
            pc08 = doc_template['PC08 - Personnel List']
            self.file_path_label.setText(doc_template_path)
            

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"Save Testing Doc","","Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            print(file_name)

    def submitForm(self):
        submission = {"entry.1000008":"Aero", "entry.1000011":"person submitting", "entry.1000013_month":"1", "entry.1000013_day":"2", "entry.1000013_year":"2019", "entry.1000014_hour":"1",
                "entry.1000014_minute":"2", "entry.1000015_hour":"3", "entry.1000015_minute":"4", "entry.1000003.other_option_response":"", "entry.1000003":"Track", 
                "entry.1000009.other_option_response":"", "entry.1000009":"CAGE", "entry.1000006":"lead", "entry.1000007":"attending", "entry.1450814088":"number", "entry.1000010":"additional"}
        requests.post(form_resp_url, submission)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())