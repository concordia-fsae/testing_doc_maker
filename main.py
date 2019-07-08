'''Testing Doc Maker program, used to help speed up making testing docs for FSAE testing sessions'''

import sys
from functools import partial
import json
import requests

#from PyQt5.QtCore import QRegExp, QDate, QTime, QObject
#from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, QDate, QTime
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


### PyQT Section

class AppWindow(QMainWindow):
    '''Program Main Window'''
    def __init__(self):
        super(AppWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.attendee = AttendeeWindow(self)
        self.member.ui.buttonBox.rejected.connect(self.add_cancel)
        self.member = MemberWindow(self)

        today = QDate.currentDate()
        self.ui.date_session.setDate(today)
        self.ui.date_session.setMinimumDate(today)
        self.ui.time_start.editingFinished.connect(self.min_end_time)

        self.ui.label_save_doc.setVisible(False)
        self.ui.label_create_roster.setVisible(False)
        self.ui.label_roster.setVisible(False)

        self.ui.btn_save_doc.clicked.connect(self.save_testing_doc_dialog)
        self.ui.btn_open_template.clicked.connect(self.open_testing_doc_dialog)
        self.ui.btn_submit_form.clicked.connect(self.submit_form)
        self.ui.btn_export.clicked.connect(self.export_general)
        self.ui.btn_import.clicked.connect(self.import_general)
        self.ui.btn_open_roster.clicked.connect(self.open_roster_dialog)
        self.ui.btn_create_roster.clicked.connect(self.create_roster_dialog)
        self.ui.btn_save_roster.clicked.connect(self.save_roster)
        self.ui.btn_close_roster.clicked.connect(self.close_roster)
        self.ui.btn_modify_attending.clicked.connect(self.open_attendee)
        self.ui.btn_add_member.clicked.connect(partial(self.member_window, "add"))
        self.ui.btn_modify_member.clicked.connect(partial(self.member_window, "modify"))
        self.ui.btn_remove_member.clicked.connect(self.remove_member)

        self.ui.tree_roster.itemActivated.connect(partial(self.member_window, "modify"))
        self.ui.tree_roster.itemSelectionChanged.connect(self.member_selected)
        self.ui.tree_roster.sortByColumn(0, 0)


        self.ui.actionOpen_Template_File.triggered.connect(self.open_testing_doc_dialog)
        self.ui.actionSave_Testing_Doc.triggered.connect(self.save_testing_doc_dialog)

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


    def open_testing_doc_dialog(self):
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


    def save_testing_doc_dialog(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Testing Doc", \
            "", "Excel File (*.xlsx);;All Files (*)", options=options)
        if file_name:
            pass


    def open_roster_dialog(self):
        '''Start the "open file" dialog for selecting the roster file'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Roster File", \
            "", "JSON Files (*.json)", options=options)
        if file_name:
            self.roster_file_path = file_name
            try:
                with open(self.roster_file_path, "r") as roster:

                    try:
                        self.roster = json.load(roster)
                    except json.decoder.JSONDecodeError:
                        pass

                    if self.roster and not self.roster == {}:
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
                    else:
                        QMessageBox.information(self, "Empty Roster", \
                            "Roster file contains no members")
                    
                    ui = self.ui
                    ui.label_roster.setText(self.roster_file_path)
                    ui.label_roster.setVisible(True)
                    ui.btn_open_roster.setText("Roster File Opened")
                    ui.btn_open_roster.setEnabled(False)
                    ui.btn_create_roster.setEnabled(False)
                    ui.btn_close_roster.setEnabled(True)
                    ui.btn_save_roster.setEnabled(True)
                    ui.btn_add_member.setEnabled(True)   

            except TypeError:
                QMessageBox.critical(self, "Improperly Formatted File", \
                    "The selected JSON file " \
                    "is corrupt or improperly formatted.")

            except IOError:
                QMessageBox.critical(self, "Unable to open file", \
                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_roster.setText("Error opening file")


    def create_roster_dialog(self):
        '''Start the "save file" dialog for saving the completed testing doc'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Create Roster File", \
            "", "JSON File (*.json)", options=options)
        if file_name:
            if not ".json" in file_name.lower():
                file_name += ".json"

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
                QMessageBox.critical(self, "Unable to open file", \
                    "There was an error opening \"%s\"" % file_name)
                self.ui.label_create_roster.setText("Error creating Roster File")


    def export_general_dialog(self):
        '''Start the "save file" dialog for saving the General Info template file'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save General Info", \
            "", "JSON File (*.json)", options=options)
        if file_name:
            if not ".json" in file_name.lower():
                file_name += ".json"
                self.ui.btn_export.setEnabled(False)
                return file_name
            else:
                return None


    def import_general_dialog(self):
        '''Start the "open file" dialog for selecting a General Info JSON file'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Template File", \
            "", "JSON Files (*.json)", options=options)
        if file_name:
            try:
                with open(file_name, "r") as template_file:
                    return json.load(template_file)
            except IOError:
                QMessageBox.critical(self, "Couldn't open file", \
                    "Couldn't open %s file for reading", file_name)
        else:
            return None


    def export_general(self):
        '''Export all the information from the General Info page
            for later re-importing'''
        if self.validate_input():
            return
        path = self.export_general_dialog()
        if path is None:
            return

        export = {}
        export["requestor"] = self.ui.edit_requestor.text()
        export["lead"] = self.ui.edit_lead.text()
        export["date"] = self.ui.date_session.date().toString()
        export["start_time"] = self.ui.time_start.time().toString()
        export["end_time"] = self.ui.time_end.time().toString()
        export["type"] = self.ui.radio_type.checkedButton().text()
        export["type_other"] = self.ui.radio_type_other.text()
        export["loc"] = self.ui.radio_loc.checkedButton().text()
        export["loc_other"] = self.ui.radio_loc_other.text()
        export["part"] = self.ui.edit_part.text()
        export["cat"] = self.ui.edit_cat.text()
        export["doc_num"] = self.ui.edit_doc_num.text()
        export["desc"] = self.ui.edit_desc.toPlainText()

        try:
            with open(path, "w+") as export_file:
                json.dump(export, export_file)
        except IOError:
            QMessageBox.critical(self, "Unable to write file", \
                "There was an error writing \"%s\"" % path)


    def import_general(self):
        '''Import all the information on the General Info page from
            a JSON file'''


        general = self.import_general_dialog()
        if general is None:
            return

        try:
            self.ui.edit_requestor.setText(general["requestor"])
            self.ui.edit_lead.setText(general["lead"])
            self.ui.date_session.setDate(QDate().fromString(general["date"]))
            self.ui.time_start.setTime(QTime().fromString(general["start_time"]))
            self.ui.time_end.setTime(QTime().fromString(general["end_time"]))
            self.ui.radio_type_other.setText(general["type_other"])
            self.ui.radio_loc_other.setText(general["loc_other"])
            self.ui.edit_part.setText(general["part"])
            self.ui.edit_cat.setText(general["cat"])
            self.ui.edit_doc_num.setText(general["doc_num"])
            self.ui.edit_desc.setText(general["desc"])

            if general["type"] == "Dyno":
                self.ui.radio_dyno.setChecked(True)
            elif general["type"] == "Track":
                self.ui.radio_track.setChecked(True)
            else:
                self.ui.radio_loc_other.setChecked(True)

            if general["loc"] == "Cage":
                self.ui.radio_loc_cage.setChecked(True)
            elif general["loc"] == "Loading Dock":
                self.ui.radio_loc_loading.setChecked(True)
            elif general["loc"] == "Casino":
                self.ui.radio_loc_casino.setChecked(True)

        except KeyError:
            QMessageBox.critical(self, "Improperly Formatted File", "The selected JSON file is corrupt or improperly formatted.")

        self.validate_input()

        
    def save_roster(self):
        '''Save the roster file to disk'''
        self.update_json()

        with open(self.roster_file_path, "w") as roster:
            json.dump(self.roster, roster)

        self.ui.btn_save_roster.setEnabled(False)


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
        self.ui.btn_create_roster.setEnabled(True)
        self.ui.label_roster.setVisible(False)

        for member in [self.ui.btn_close_roster, self.ui.btn_save_roster, \
            self.ui.btn_add_member, self.ui.btn_modify_member, self.ui.btn_remove_member]:
            member.setEnabled(False)

        # TODO add confirmation before clearing list
        self.ui.tree_roster.clear()


    def member_window(self, purpose):
        '''Open the member add/modify window'''
        if purpose == "add":
            self.member.setWindowTitle("New Member")
            self.member.ui.buttonBox.accepted.connect(self.add_member)
            self.member.show()
        elif purpose == "modify":
            tree = self.ui.tree_roster
            m = self.member.ui
            if len(tree.selectedItems()) == 1:
                selected = tree.selectedItems()[0]

                members = [m.edit_id, m.edit_first_name, m.edit_last_name, m.edit_number]
                for ind in range(0, len(members)):
                    members[ind].setText(selected.text(ind))

                m.check_waiver.setChecked(bool(selected.text(4)))
                m.check_truck.setChecked(bool(selected.text(5)))
                m.check_trailer.setChecked(bool(selected.text(6)))

                self.member.setWindowTitle("Modify Member")
                m.buttonBox.accepted.connect(partial(self.save_member, selected))
                self.member.show()
            else:
                selected = tree.selectedItems()
                for member in [m.edit_id, m.edit_first_name, m.edit_last_name, m.edit_number]:
                    member.setDisabled(True)

                for member in [m.check_waiver, m.check_truck, m.check_trailer]:
                    member.setTristate(True)
                    member.setCheckState(1)

                self.member.setWindowTitle("Modify Members")
                m.buttonBox.accepted.connect(partial(self.save_member, selected))
                self.member.show()
                


    def add_member(self):
        '''Add a member to the roster'''
        tree = self.ui.tree_roster
        m = self.member.ui
        complete = True
        duplicate = False

        e_mn = m.edit_id.text()
        e_fn = m.edit_first_name.text()
        e_ln = m.edit_last_name.text()
        e_cn = m.edit_number.text()
        c_w = str(m.check_waiver.isChecked())
        c_tu = str(m.check_truck.isChecked())
        c_tl = str(m.check_trailer.isChecked())
        valid = [m.edit_id.hasAcceptableInput(), m.edit_number.hasAcceptableInput()]

        if any(k in self.roster for k in (e_mn, e_cn)):
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
            tree.addTopLevelItem(QTreeWidgetItem([e_mn, e_fn, e_ln, e_cn, c_w, c_tu, c_tl]))
            self.update_json()
            self.member.close()
            self.member = MemberWindow(self)


    def save_member(self, member):
        '''Save the member(s) that was/were modified'''
        if type(member) != list:
            '''Add a member to the roster'''
            tree = self.ui.tree_roster
            m = self.member.ui
            complete = True
            duplicate = False

            e_mn = m.edit_id.text()
            e_fn = m.edit_first_name.text()
            e_ln = m.edit_last_name.text()
            e_cn = m.edit_number.text()
            c_w = str(m.check_waiver.isChecked())
            c_tu = str(m.check_truck.isChecked())
            c_tl = str(m.check_trailer.isChecked())
            data = [e_mn, e_fn, e_ln, e_cn, c_w, c_tu, c_tl]
            valid = [m.edit_id.hasAcceptableInput(), m.edit_number.hasAcceptableInput()]

            curr = self.roster.pop(e_mn)

            if any(k in self.roster for k in (e_mn, e_cn)):
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
                #tree.addTopLevelItem(QTreeWidgetItem([e_mn, e_fn, e_ln, e_cn, c_w, c_tu, c_tl]))
                for ind in enumerate(data):
                    member.setText(ind[0], ind[1])

                self.update_json()
                self.member.close()
                self.member = MemberWindow(self)
        elif len(member) > 1:
            pass


    def modify_member(self):
        '''Modify the selected member(s)'''
        pass


    def member_selected(self, dis=""):
        '''Runs when the selection in the tree is changed'''
        if self.ui.tree_roster.selectedItems():
            self.ui.btn_modify_member.setEnabled(True)
            self.ui.btn_remove_member.setEnabled(True)
        else:
            self.ui.btn_modify_member.setEnabled(False)
            self.ui.btn_remove_member.setEnabled(False)

        self.ui.btn_save_roster.setEnabled(True)

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


    def process_radio_input(self, field=""):
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

        self.ui.btn_save_doc.setEnabled(True)


    def process_input(self, field, dis):
        '''Process the user input when they finish editing the given'''
        if(field.text() == "" or field.text() == " "):
            field.setStyleSheet("background-color: rgb(255, 143, 145);")
        else:
            field.setStyleSheet("")
        
        self.ui.btn_save_doc.setEnabled(True)


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
            else:
                field.setStyleSheet("")

        ### validate alphanumeric fields
        for field in self.alphanum_fields:
            if(field.isEnabled() and (field.text() == "" \
                or field.text() == " " \
                or not field.hasAcceptableInput())):

                complete = False
                field.setStyleSheet("background-color: rgb(255, 143, 145);")
            else:
                field.setStyleSheet("")

        ### validate testing doc number
        doc_num = self.ui.edit_doc_num
        if doc_num.text() == "" or len(doc_num.text()) < 5:
            doc_num.setStyleSheet("background-color: rgb(255, 143, 145);")
            complete = False
        else:
            doc_num.setStyleSheet("")


        ### validate radio buttons
        for radio in self.radios:
            if radio.checkedButton() is None:
                for button in radio.buttons():
                    button.setStyleSheet("background-color: rgb(255, 143, 145);")

        self.process_radio_input()

        if complete:
            return 0
        else:
            return 1
            print("Data is not complete")


    def submit_form(self):
        '''Submit the Google Form'''

        if self.validate_input():
            return
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
        if self.ui.btn_close_roster.isEnabled():
            self.attendee.show()
        else:
            QMessageBox.information(self, "Roster Not Open", \
                "Please open a Roster first by going to the \"Roster Management\" tab.", )

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
