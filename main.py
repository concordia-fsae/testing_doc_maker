import sys
import requests
import re

from functools import partial
from PyQt5.QtCore import QRegExp, QDate, QTime
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QTextEdit, QLineEdit
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

        today = QDate.currentDate()
        self.ui.date_session.setDate(today)
        self.ui.date_session.setMinimumDate(today)
        
        self.ui.time_start.editingFinished.connect(self.minEndTime)

        self.ui.btn_save_doc.clicked.connect(self.saveFileDialog)
        self.ui.btn_open_template.clicked.connect(self.openFileNameDialog)
        self.ui.btn_submit_form.clicked.connect(self.validateInput)
        
        self.ui.actionOpen_Template_File.triggered.connect(self.openFileNameDialog)
        self.ui.actionSave_Testing_Doc.triggered.connect(self.saveFileDialog)

        self.ui.radio_type.buttonClicked.connect(partial(self.processRadioInput))
        self.ui.radio_loc.buttonClicked.connect(partial(self.processRadioInput))

        self.alpha_fields = [self.ui.edit_requestor, self.ui.edit_lead, self.ui.edit_type_other, self.ui.edit_cat]
        self.alphanum_fields = [self.ui.edit_part, self.ui.edit_loc_other]
        self.num_fields = [self.ui.edit_doc_num]
        self.fields = self.alpha_fields + self.alphanum_fields + self.num_fields


        for field in self.fields:
            field.focusOutEvent = partial(self.processInput, field)
            field.focusInEvent = partial(self.resetColor, field)

        for field in self.alpha_fields:
            field.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\s]*")))

        for field in self.alphanum_fields:
            field.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\s\d]*")))

        for field in self.num_fields:
            field.setValidator(QRegExpValidator(QRegExp("[\d]{5}")))

        
        self.show()

    def openFileNameDialog(self):
        '''Start the "open file" dialog for selecting the testing doc template'''
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
            self.ui.file_path.setText(doc_template_path)
            
            
    def saveFileDialog(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"Save Testing Doc","","Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            print(file_name)


    def processRadioInput(self, field):
        self.ui.edit_loc_other.setEnabled(self.ui.radio_loc_other.isChecked())
        self.ui.edit_type_other.setEnabled(self.ui.radio_type_other.isChecked())

        if(not self.ui.edit_type_other.isEnabled()):
            self.ui.edit_type_other.setStyleSheet("")

        if(not self.ui.edit_loc_other.isEnabled()):
            self.ui.edit_loc_other.setStyleSheet("")


    def processInput(self, field, dis):
        if(field.text() == "" or field.text() == " "):
            field.setStyleSheet("background-color: rgb(255, 143, 145);")
        else:
            field.setStyleSheet("")
        #if(not complete):
        #    print("One or more fields are either not complete, or contain invalid characters")

    
    def resetColor(self, field, dis):
        field.setStyleSheet("")


    def validateInput(self):
        complete = True
        ### validate alpha fields
        for field in self.alpha_fields:
            if(field.isEnabled() and (field.text() == "" or field.text() == " " or not field.hasAcceptableInput())):
                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                print(field.objectName(), " is not filled out correctly")

        ### validate alphanumeric fields
        for field in self.alphanum_fields:
            if(field.isEnabled() and (field.text() == "" or field.text() == " " or not field.hasAcceptableInput())):
                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                print(field.objectName(), " is not filled out correctly")

        ### validate testing doc number
        doc_num = self.ui.edit_doc_num
        if(doc_num.text() == "" or len(doc_num.text()) < 5):
            doc_num.setStyleSheet("background-color: rgb(255, 143, 145);")            
            complete = False
            print(doc_num.objectName(), " is not filled out correctly")

        if(complete):
            self.submitForm()
        else:
            print("Data is not complete")


    def submitForm(self):
        print("Submitting form")

        submission = {"entry.1000008":"Aero", "entry.1000011":"person submitting", "entry.1000013_month":"1", "entry.1000013_day":"2", "entry.1000013_year":"2019", "entry.1000014_hour":"1",
                "entry.1000014_minute":"2", "entry.1000015_hour":"3", "entry.1000015_minute":"4", "entry.1000003.other_option_response":"", "entry.1000003":"Track", 
                "entry.1000009.other_option_response":"", "entry.1000009":"CAGE", "entry.1000006":"lead", "entry.1000007":"attending", "entry.1450814088":"number", "entry.1000010":"additional"}
        #requests.post(form_resp_url, submission)


    def minEndTime(self):
        min_end = self.ui.time_start.time()
        min_end.setHMS(min_end.hour()+1, min_end.minute(), min_end.second())
        self.ui.time_end.setMinimumTime(min_end)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())