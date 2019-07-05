'''Testing Doc Maker program, used to help speed up making testing docs for FSAE testing sessions'''

import sys
from functools import partial
from dataclasses import dataclass
import requests
import json

from PyQt5.QtCore import QRegExp, QDate, QTime, QObject
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QInputDialog, QDialog
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QMessageBox, QTextEdit, QTreeWidgetItem
from openpyxl import load_workbook
from homepage import Ui_MainWindow
from attendee import Ui_attendee_list


### Form Response Vars

FORM_ID = "1FAIpQLSe1iCukrB_HYS1Dvl8rjtazTZyAza1ArFZ-d3HaE-5gXTyWKA"
FORM_RESP_URL = "https://docs.google.com/forms/u/2/d/e/" + FORM_ID + "/formResponse"


### Roster Section
@dataclass
class Member:
    first_name: str
    last_name: str
    phone_number: str
    signed_waiver: bool

### PyQT Section

class AppWindow(QMainWindow):
    '''Program Main Window'''
    def __init__(self):
        super(AppWindow, self).__init__()
        #super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        today = QDate.currentDate()
        self.ui.date_session.setDate(today)
        self.ui.date_session.setMinimumDate(today)
        self.ui.time_start.editingFinished.connect(self.minEndTime)

        self.ui.label_save_doc.setVisible(False)
        self.ui.label_create_roster.setVisible(False)
        self.ui.label_roster.setVisible(False)

        self.ui.btn_save_doc.clicked.connect(self.saveFileDialog)
        self.ui.btn_open_template.clicked.connect(self.openFileNameDialog)
        self.ui.btn_submit_form.clicked.connect(self.validateInput)
        self.ui.btn_open_roster.clicked.connect(self.openRoster)
        self.ui.btn_create_roster.clicked.connect(self.createRoster)
        self.ui.btn_save_roster.clicked.connect(self.saveRoster)
        self.ui.btn_close_roster.clicked.connect(self.closeRoster)
        self.ui.btn_modify_attending.clicked.connect(self.openAttendee)

        self.ui.actionOpen_Template_File.triggered.connect(self.openFileNameDialog)
        self.ui.actionSave_Testing_Doc.triggered.connect(self.saveFileDialog)

        self.roster_file_path = ""
        self.roster = {}

        self.radios = [self.ui.radio_type, self.ui.radio_loc]
        self.ui.radio_type.buttonClicked.connect(partial(self.processRadioInput))
        self.ui.radio_loc.buttonClicked.connect(partial(self.processRadioInput))

        self.alpha_fields = [self.ui.edit_requestor, self.ui.edit_lead, \
                                self.ui.edit_type_other, self.ui.edit_cat]
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Template File", \
            "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            # TODO protect this (try except)
            self.doc_template_path = file_name
            self.doc_template = load_workbook(filename = self.doc_template_path)
            self.pc01 = self.doc_template['General Information']
            self.pc02 = self.doc_template['PC02 - Safety']
            self.pc08 = self.doc_template['PC08 - Personnel List']
            self.ui.file_path.setText(self.doc_template_path)


    def saveFileDialog(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Testing Doc", \
            "", "Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            pass


    def openRoster(self):
        '''Start the "open file" dialog for selecting the roster file'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Roster File", \
            "", "JSON Files (*.json)", options=options)
        if file_name:
            self.roster_file_path = file_name
            try:
                with open(self.roster_file_path, "r") as roster:
                    self.ui.label_roster.setText(self.roster_file_path)
                    self.ui.label_roster.setVisible(True)
                    self.ui.btn_open_roster.setText("Roster File Opened")
                    self.ui.btn_open_roster.setEnabled(False)
                    self.ui.btn_close_roster.setEnabled(True)
                    self.ui.btn_create_roster.setEnabled(False)
                    self.ui.btn_save_roster.setEnabled(True)


                    try:
                        roster_json = json.load(roster)
                        if len(roster_json) > 0:
                            for member in roster_json:
                                pass
                                # TODO add members to tree view
                    except json.decoder.JSONDecodeError:
                        QMessageBox.information(self, "Empty Roster", \
                            "Roster file contains no members")


            except IOError:
                QMessageBox.information(self, "Unable to open file", \
                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_roster.setText("Error opening file")


    def createRoster(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Create Roster File", \
            "", "JSON File (*.json)", options=options)
        if file_name:
            if not ".json" in file_name.lower():
                file_name = file_name + ".json"

            try:
                print(file_name)
                with open(file_name, "w+") as roster:
                    self.ui.label_roster.setText(file_name)
                    self.ui.label_roster.setVisible(True)
                    self.ui.btn_open_roster.setText("Roster File Opened")
                    self.ui.btn_open_roster.setEnabled(False)
                    self.ui.btn_close_roster.setEnabled(True)
                    self.ui.btn_create_roster.setEnabled(False)
                    self.ui.btn_save_roster.setEnabled(True)
            except IOError:
                QMessageBox.information(self, "Unable to open file",
                                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_create_roster.setText("Error creating Roster File")


    def saveRoster(self):
        self.ui.tree_roster.addTopLevelItem(QTreeWidgetItem(["asdf", "asdf", "1245", "asdf"]))

        for item in range(0, self.ui.tree_roster.topLevelItemCount()):
            member = self.ui.tree_roster.topLevelItem(item)
            self.roster[member.text(0)] = {"first_name":member.text(1), "last_name":member.text(2), \
                "cell_num":member.text(3), "waiver":member.text(4), "truck":member.text(5), "trailer":member.text(6)}

        with open(self.roster_file_path, "w") as roster:
            json.dump(self.roster, roster)

    def closeRoster(self):
        self.ui.btn_open_roster.setEnabled(True)
        self.ui.btn_open_roster.setText("Open Roster File")
        self.ui.btn_close_roster.setEnabled(False)
        self.ui.btn_save_roster.setEnabled(False)
        self.ui.btn_create_roster.setEnabled(True)
        self.ui.label_roster.setVisible(False)

        for item in range(0, self.ui.tree_roster.topLevelItemCount()):
            self.ui.tree_roster.takeTopLevelItem(item)


    def processRadioInput(self, field):
        self.ui.edit_loc_other.setEnabled(self.ui.radio_loc_other.isChecked())
        self.ui.edit_type_other.setEnabled(self.ui.radio_type_other.isChecked())

        if(not self.ui.edit_type_other.isEnabled()):
            self.ui.edit_type_other.setStyleSheet("")

        if(not self.ui.edit_loc_other.isEnabled()):
            self.ui.edit_loc_other.setStyleSheet("")

        for radio in self.radios:
            if(radio.checkedButton() == None):
                for button in radio.buttons():
                    button.setStyleSheet("background-color: rgb(255, 143, 145);")
            else:
                for button in radio.buttons():
                    button.setStyleSheet("")


    def processInput(self, field, dis):
        if(field.text() == "" or field.text() == " "):
            field.setStyleSheet("background-color: rgb(255, 143, 145);")
        else:
            field.setStyleSheet("")

    
    def resetColor(self, field, dis):
        field.setStyleSheet("")


    def validateInput(self):
        complete = True
        ### validate alpha fields
        for field in self.alpha_fields:
            if(field.isEnabled() and (field.text() == "" or field.text() == " " or not field.hasAcceptableInput())):
                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                # print(field.objectName(), " is not filled out correctly")


        ### validate alphanumeric fields
        for field in self.alphanum_fields:
            if(field.isEnabled() and (field.text() == "" or field.text() == " " or not field.hasAcceptableInput())):
                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                # print(field.objectName(), " is not filled out correctly")


        ### validate testing doc number
        doc_num = self.ui.edit_doc_num
        if(doc_num.text() == "" or len(doc_num.text()) < 5):
            doc_num.setStyleSheet("background-color: rgb(255, 143, 145);")            
            complete = False
            # print(doc_num.objectName(), " is not filled out correctly")


        ### validate radio buttons
        for radio in self.radios:
            if(radio.checkedButton() == None):
                for button in radio.buttons():
                    button.setStyleSheet("background-color: rgb(255, 143, 145);")


        if(complete):
            self.submitForm()
        else:
            print("Data is not complete")


    def submitForm(self):
        print("Submitting form")

        other_type_resp = other_loc_resp = ""
        other_type = self.ui.radio_type.checkedButton().text()
        other_loc = self.ui.radio_loc.checkedButton().text()

        if(self.ui.radio_type_other.isEnabled()):
            other_type_resp = self.ui.edit_type_other.text()
            other_type = "__other_option__"
        elif(self.ui.radio_loc_other.isEnabled()):
            other_loc_resp = self.ui.edit_loc_other.text()
            other_loc = "__other_option__"

        submission = {"entry.1000008":"Aero",                                       # team
                        "entry.1000011":self.ui.edit_requestor.text(),              # person submitting form
                        "entry.1000013_month":self.ui.date_session.date().month(),  # test session month
                        "entry.1000013_day":self.ui.date_session.date().day(),      # test session day
                        "entry.1000013_year":self.ui.date_session.date().year(),    # test session year
                        "entry.1000014_hour":self.ui.time_start.time().hour(),      # start time hour
                        "entry.1000014_minute":self.ui.time_start.time().minute(),  # start time minute
                        "entry.1000015_hour":self.ui.time_end.time().hour(),        # end time hour
                        "entry.1000015_minute":self.ui.time_end.time().minute(),    # end time minute
                        "entry.1000003.other_option_response":other_type_resp,      # set to self.ui.edit_type_other.text() if self.ui.radio_type_other.isEnabled()
                        "entry.1000003":other_type,                                 # set to the selected type radio button text
                        "entry.1000009.other_option_response":other_loc_resp,       # set to self.ui.edit_loc_other.text() if self.ui.radio_loc_other.isEnabled()
                        "entry.1000009":other_loc,                                  # set to the selected location radio button text
                        "entry.1000006":self.ui.edit_lead.text(),                   # test lead
                        "entry.1000007":"attending",                                # list of other members attending
                        "entry.1450814088":self.ui.edit_doc_num,                    # testing doc number
                        "entry.1000010":""}                                         # additional info
        #requests.post(form_resp_url, submission)


    def minEndTime(self):
        min_end = self.ui.time_start.time()
        min_end.setHMS(min_end.hour()+1, min_end.minute(), min_end.second())
        self.ui.time_end.setMinimumTime(min_end)


    def openAttendee(self):
        self.attendee = AttendeeWindow(self)
        self.attendee.show()

class AttendeeWindow(QDialog):
    '''Attendee list window'''
    def __init__(self, parent):
        super(AttendeeWindow, self).__init__(parent)
        self.ui = Ui_attendee_list()
        self.ui.setupUi(self)

        self.ui.btn_add_member.clicked.connect(self.addMember)
        self.ui.btn_remove_member.clicked.connect(self.removeMember)
        self.ui.tree_attendee.clicked.connect(self.memberSelected)

        self.ui.tree_attendee.addTopLevelItem(QTreeWidgetItem(["asdf", "asdf", "1245", "asdf"]))
        self.ui.tree_attendee.addTopLevelItem(QTreeWidgetItem(["asdf", "asdf", "1245", "asdf"]))


    def addMember(self):
        pass


    def memberSelected(self):
        if len(self.ui.tree_attendee.selectedItems()) > 1:
            self.ui.btn_modify_member.setEnabled(False)
        else:
            self.ui.btn_modify_member.setEnabled(True)


    def removeMember(self):
        for member in self.ui.tree_attendee.selectedItems():
            self.ui.tree_attendee.takeTopLevelItem(self.ui.tree_attendee.indexOfTopLevelItem(member))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())