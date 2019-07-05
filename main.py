'''Testing Doc Maker program, used to help speed up making testing docs for FSAE testing sessions'''

import sys
from functools import partial
from dataclasses import dataclass
import json
import requests

#from PyQt5.QtCore import QRegExp, QDate, QTime, QObject
#from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTreeWidgetItem
from openpyxl import load_workbook
from windows.homepage import Ui_MainWindow
from windows.attendee import Ui_attendee_list
from windows.member import Ui_member_mod


### Form Response Vars

FORM_ID = "1FAIpQLSe1iCukrB_HYS1Dvl8rjtazTZyAza1ArFZ-d3HaE-5gXTyWKA"
FORM_RESP_URL = "https://docs.google.com/forms/u/2/d/e/" + FORM_ID + "/formResponse"


### Roster Section
@dataclass
class Member:
    '''Member helper dataclass'''
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
        self.attendee = AttendeeWindow(self)
        self.member = MemberWindow(self)

        today = QDate.currentDate()
        self.ui.date_session.setDate(today)
        self.ui.date_session.setMinimumDate(today)
        self.ui.time_start.editingFinished.connect(self.min_end_time)

        self.ui.label_save_doc.setVisible(False)
        self.ui.label_create_roster.setVisible(False)
        self.ui.label_roster.setVisible(False)

        self.ui.btn_save_doc.clicked.connect(self.save_file_dialog)
        self.ui.btn_open_template.clicked.connect(self.open_file_dialog)
        self.ui.btn_submit_form.clicked.connect(self.validate_input)
        self.ui.btn_open_roster.clicked.connect(self.open_roster)
        self.ui.btn_create_roster.clicked.connect(self.create_roster)
        self.ui.btn_save_roster.clicked.connect(self.save_roster)
        self.ui.btn_close_roster.clicked.connect(self.close_roster)
        self.ui.btn_modify_attending.clicked.connect(self.open_attendee)
        self.ui.btn_add_member.clicked.connect(partial(self.member_window, "add"))
        self.ui.btn_modify_member.clicked.connect(partial(self.member_window, "modify"))
        self.ui.btn_remove_member.clicked.connect(self.remove_member)

        self.ui.tree_roster.clicked.connect(self.member_selected)

        self.ui.actionOpen_Template_File.triggered.connect(self.open_file_dialog)
        self.ui.actionSave_Testing_Doc.triggered.connect(self.save_file_dialog)

        self.roster_file_path = ""
        self.roster = {}
        self.doc_template_path = self.doc_template = self.pc01 = None
        self.pc02 = self.pc08 = None

        self.radios = [self.ui.radio_type, self.ui.radio_loc]
        self.ui.radio_type.buttonClicked.connect(partial(self.process_radio_input))
        self.ui.radio_loc.buttonClicked.connect(partial(self.process_radio_input))

        self.alpha_fields = [self.ui.edit_requestor, self.ui.edit_lead, \
                                self.ui.edit_type_other, self.ui.edit_cat]
        self.alphanum_fields = [self.ui.edit_part, self.ui.edit_loc_other]
        self.num_fields = [self.ui.edit_doc_num]
        self.fields = self.alpha_fields + self.alphanum_fields + self.num_fields

        for field in self.fields:
            field.focusOutEvent = partial(self.process_input, field)
            field.focusInEvent = partial(self.reset_color, field)

        for field in self.alpha_fields:
            field.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\\s]*")))


        for field in self.alphanum_fields:
            field.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\\s\\d]*")))


        for field in self.num_fields:
            field.setValidator(QRegExpValidator(QRegExp("[\\d]{5}")))


        self.show()


    def open_file_dialog(self):
        '''Start the "open file" dialog for selecting the testing doc template'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Template File", \
            "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            # TODO protect this (try except)
            self.doc_template_path = file_name
            self.doc_template = load_workbook(filename=self.doc_template_path)
            self.pc01 = self.doc_template['General Information']
            self.pc02 = self.doc_template['PC02 - Safety']
            self.pc08 = self.doc_template['PC08 - Personnel List']
            self.ui.file_path.setText(self.doc_template_path)


    def save_file_dialog(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Testing Doc", \
            "", "Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            pass


    def open_roster(self):
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
                    self.ui.btn_add_member.setEnabled(True)

                    try:
                        self.roster = json.load(roster)
                        if self.roster:
                            for member in self.roster:
                                self.ui.tree_roster.addTopLevelItem(
                                    QTreeWidgetItem(
                                        [
                                            member, \
                                            self.roster[member]["first_name"], \
                                            self.roster[member]["last_name"], \
                                            self.roster[member]["cell_num"], \
                                            self.roster[member]["waiver"], \
                                            self.roster[member]["truck"], \
                                            self.roster[member]["trailer"], \
                                        ]
                                    ))
                    except json.decoder.JSONDecodeError:
                        QMessageBox.information(self, "Empty Roster", \
                            "Roster file contains no members")


            except IOError:
                QMessageBox.information(self, "Unable to open file", \
                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_roster.setText("Error opening file")


    def create_roster(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Create Roster File", \
            "", "JSON File (*.json)", options=options)
        if file_name:
            if not ".json" in file_name.lower():
                file_name = file_name + ".json"

            try:
                with open(file_name, "w+") as roster:
                    self.ui.label_roster.setText(self.roster_file_path)
                    self.ui.label_roster.setVisible(True)
                    self.ui.btn_open_roster.setText("Roster File Opened")
                    self.ui.btn_open_roster.setEnabled(False)
                    self.ui.btn_close_roster.setEnabled(True)
                    self.ui.btn_create_roster.setEnabled(False)
                    self.ui.btn_save_roster.setEnabled(True)
                    self.ui.btn_add_member.setEnabled(True)
            except IOError:
                QMessageBox.information(self, "Unable to open file", \
                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_create_roster.setText("Error creating Roster File")


    def save_roster(self):
        '''Save the roster file to disk'''
        self.update_json()

        with open(self.roster_file_path, "w") as roster:
            json.dump(self.roster, roster)


    def update_json(self):
        '''Update the json var containing the roster'''
        self.roster = {}
        for item in range(0, self.ui.tree_roster.topLevelItemCount()):
            member = self.ui.tree_roster.topLevelItem(item)
            self.roster[member.text(0)] = {"first_name":member.text(1), \
                "last_name":member.text(2), \
                "cell_num":member.text(3), \
                "waiver":member.text(4), \
                "truck":member.text(5), \
                "trailer":member.text(6)}


    def close_roster(self):
        '''Close the Roster File'''
        self.ui.btn_open_roster.setEnabled(True)
        self.ui.btn_open_roster.setText("Open Roster File")
        self.ui.btn_close_roster.setEnabled(False)
        self.ui.btn_save_roster.setEnabled(False)
        self.ui.btn_create_roster.setEnabled(True)
        self.ui.label_roster.setVisible(False)
        self.ui.btn_add_member.setEnabled(False)
        self.ui.btn_modify_member.setEnabled(False)
        self.ui.btn_remove_member.setEnabled(False)

        # TODO add confirmation before clearing list
        self.ui.tree_roster.clear()


    def member_window(self, purpose):
        '''Open the member mod window'''
        self.member.ui.buttonBox.rejected.connect(self.add_cancel)
        if purpose == "add":
            self.member.setWindowTitle("New Member")
            self.member.ui.buttonBox.accepted.connect(self.add_member)
            self.member.show()
        elif purpose == "modify":
            tree = self.ui.tree_roster
            if tree.selectedItems() == 1:
                selected = tree.topLevelItem(tree.selectedItems())

                self.member.ui.edit_first_name = selected.text(1)
                self.member.setWindowTitle("Modify Member")


    def add_member(self):
        '''Add a member to the roster'''
        tree = self.ui.tree_roster
        complete = True
        duplicate = False

        mn = self.member.ui.edit_id.text()
        fn = self.member.ui.edit_first_name.text()
        ln = self.member.ui.edit_last_name.text()
        cn = self.member.ui.edit_number.text()
        w = str(self.member.ui.check_waiver.isChecked())
        tu = str(self.member.ui.check_truck.isChecked())
        tl = str(self.member.ui.check_trailer.isChecked())
        valid = [self.member.ui.edit_id.hasAcceptableInput(), self.member.ui.edit_number.hasAcceptableInput()]

        if any(k in self.roster for k in (mn, cn)):
            complete = False
            duplicate = True

        if not (valid[0] and valid[1]):
            complete = False
            QMessageBox.information(self, "Value Error", \
                    "Member ID or Phone Number is invalid.")

        if duplicate:
            QMessageBox.information(self, "Duplicate Found", \
                    "Duplicate information found. Please double check all data.")

        if complete:
            tree.addTopLevelItem(QTreeWidgetItem([mn, fn, ln, cn, w, tu, tl]))
            self.update_json()
            self.member.close()
            self.member = MemberWindow(self)


    def modify_member(self):
        '''Modify the selected member(s)'''
        pass


    def member_selected(self):
        '''Runs when the selection in the tree is changed'''
        if not self.ui.tree_roster.selectedItems is None:
            self.ui.btn_modify_member.setEnabled(True)
            self.ui.btn_remove_member.setEnabled(True)
        else:
            self.ui.btn_modify_member.setEnabled(False)
            self.ui.btn_remove_member.setEnabled(False)


        if len(self.ui.tree_roster.selectedItems()) > 1:
            self.ui.btn_modify_member.setText("Modify Members")
        else:
            self.ui.btn_modify_member.setText("Modify Member")


    def remove_member(self):
        '''Remove a member from the attendee list'''
        tree = self.ui.tree_roster
        for member in tree.selectedItems():
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(member))
        self.update_json()


    def add_cancel(self):
        '''Action on cancelling member addition'''
        confirm = QMessageBox.warning(self, "Unsaved Changes", \
            "Are you sure you want to cancel?", QMessageBox.Yes, QMessageBox.No)

        if confirm == 16384:
            self.member.close()
            self.member = MemberWindow(self)



    def process_radio_input(self, field):
        '''Process the radio input'''
        self.ui.edit_loc_other.setEnabled(self.ui.radio_loc_other.isChecked())
        self.ui.edit_type_other.setEnabled(self.ui.radio_type_other.isChecked())

        if not self.ui.edit_type_other.isEnabled():
            self.ui.edit_type_other.setStyleSheet("")

        if not self.ui.edit_loc_other.isEnabled():
            self.ui.edit_loc_other.setStyleSheet("")

        for radio in self.radios:
            if radio.checkedButton() is None:
                for button in radio.buttons():
                    button.setStyleSheet("background-color: rgb(255, 143, 145);")
            else:
                for button in radio.buttons():
                    button.setStyleSheet("")


    def process_input(self, field, dis):
        '''Process the user input when they finish editing the given'''
        if(field.text() == "" or field.text() == " "):
            field.setStyleSheet("background-color: rgb(255, 143, 145);")
        else:
            field.setStyleSheet("")


    def reset_color(self, field, dis):
        '''Helper to reset the color of the given field'''
        field.setStyleSheet("")


    def validate_input(self):
        '''Validate the information that the user has entered'''
        complete = True
        ### validate alpha fields
        for field in self.alpha_fields:
            if(field.isEnabled() and (field.text() == "" \
                or field.text() == " " \
                or not field.hasAcceptableInput())):

                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                # print(field.objectName(), " is not filled out correctly")


        ### validate alphanumeric fields
        for field in self.alphanum_fields:
            if(field.isEnabled() and (field.text() == "" \
                or field.text() == " " \
                or not field.hasAcceptableInput())):

                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
                # print(field.objectName(), " is not filled out correctly")


        ### validate testing doc number
        doc_num = self.ui.edit_doc_num
        if doc_num.text() == "" or len(doc_num.text()) < 5:
            doc_num.setStyleSheet("background-color: rgb(255, 143, 145);")
            complete = False
            # print(doc_num.objectName(), " is not filled out correctly")


        ### validate radio buttons
        for radio in self.radios:
            if radio.checkedButton() is None:
                for button in radio.buttons():
                    button.setStyleSheet("background-color: rgb(255, 143, 145);")


        if complete:
            self.submit_form()
        else:
            print("Data is not complete")


    def submit_form(self):
        '''Submit the Google Form'''
        print("Submitting form")

        other_type_resp = other_loc_resp = ""
        other_type = self.ui.radio_type.checkedButton().text()
        other_loc = self.ui.radio_loc.checkedButton().text()

        if self.ui.radio_type_other.isEnabled():
            other_type_resp = self.ui.edit_type_other.text()
            other_type = "__other_option__"
        elif self.ui.radio_loc_other.isEnabled():
            other_loc_resp = self.ui.edit_loc_other.text()
            other_loc = "__other_option__"

        submission = {"entry.1000008":"Aero",                                     # team
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


    def min_end_time(self):
        '''Set the minimum end time when the start time changes'''
        min_end = self.ui.time_start.time()
        if self.ui.time_end.time().hour() < self.ui.time_start.time().hour() + 1:
            min_end.setHMS(min_end.hour()+1, min_end.minute(), min_end.second())
            self.ui.time_end.setMinimumTime(min_end)


    def open_attendee(self):
        '''Open the attendee list window'''
        self.attendee.show()

class AttendeeWindow(QDialog):
    '''Attendee list dialog'''
    def __init__(self, parent):
        super(AttendeeWindow, self).__init__(parent)
        self.ui = Ui_attendee_list()
        self.ui.setupUi(self)

        self.ui.btn_add_member.clicked.connect(self.add_member)
        self.ui.btn_remove_member.clicked.connect(self.remove_member)
        self.ui.tree_attendee.clicked.connect(self.member_selected)

        self.ui.tree_attendee.addTopLevelItem(QTreeWidgetItem(["asdf", "asdf", "1245", "asdf"]))
        self.ui.tree_attendee.addTopLevelItem(QTreeWidgetItem(["asdf", "asdf", "1245", "asdf"]))


    def add_member(self):
        '''Add a member to the attendee list'''
        pass


    def member_selected(self):
        '''Runs when the selection in the tree is changed'''
        if len(self.ui.tree_attendee.selectedItems()) > 1:
            self.ui.btn_modify_member.setText("Modify Members")
        else:
            self.ui.btn_modify_member.setText("Modify Member")


    def remove_member(self):
        '''Remove a member from the attendee list'''
        tree = self.ui.tree_attendee
        for member in tree.selectedItems():
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(member))


class MemberWindow(QDialog):
    '''Member add/modify dialog'''
    def __init__(self, parent):
        super(MemberWindow, self).__init__(parent)
        self.ui = Ui_member_mod()
        self.ui.setupUi(self)

        self.ui.edit_id.setValidator(QRegExpValidator(QRegExp("[\\d]{3}")))
        self.ui.edit_first_name.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\\s]*")))
        self.ui.edit_last_name.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\\s]*")))
        self.ui.edit_number.setValidator(QRegExpValidator(QRegExp( \
            "^((\\+?(\\d{2}))\\s?)?((\\d{2})|(\\((\\d{2})\\))\\s?)?(\\d{3,15})(\\-(\\d{3,15}))?$")))



if __name__ == '__main__':
    APP = QApplication(sys.argv)
    W = AppWindow()
    W.show()
    sys.exit(APP.exec_())
