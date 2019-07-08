# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\windows\attendee_export.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_attendee_list(object):
    def setupUi(self, attendee_list):
        attendee_list.setObjectName("attendee_list")
        attendee_list.resize(555, 314)
        attendee_list.setMinimumSize(QtCore.QSize(555, 314))
        attendee_list.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(attendee_list)
        self.gridLayout.setObjectName("gridLayout")
        self.tree_attendee = QtWidgets.QTreeWidget(attendee_list)
        self.tree_attendee.setMinimumSize(QtCore.QSize(431, 238))
        self.tree_attendee.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tree_attendee.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tree_attendee.setAlternatingRowColors(True)
        self.tree_attendee.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree_attendee.setUniformRowHeights(False)
        self.tree_attendee.setHeaderHidden(False)
        self.tree_attendee.setObjectName("tree_attendee")
        self.tree_attendee.header().setCascadingSectionResizes(True)
        self.tree_attendee.header().setHighlightSections(False)
        self.gridLayout.addWidget(self.tree_attendee, 1, 0, 1, 1)
        self.label_attendee_list = QtWidgets.QLabel(attendee_list)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_attendee_list.setFont(font)
        self.label_attendee_list.setObjectName("label_attendee_list")
        self.gridLayout.addWidget(self.label_attendee_list, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btn_modify_member = QtWidgets.QPushButton(attendee_list)
        self.btn_modify_member.setMaximumSize(QtCore.QSize(110, 16777215))
        self.btn_modify_member.setObjectName("btn_modify_member")
        self.verticalLayout.addWidget(self.btn_modify_member)
        self.btn_add_member = QtWidgets.QPushButton(attendee_list)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_add_member.sizePolicy().hasHeightForWidth())
        self.btn_add_member.setSizePolicy(sizePolicy)
        self.btn_add_member.setMaximumSize(QtCore.QSize(110, 16777215))
        self.btn_add_member.setObjectName("btn_add_member")
        self.verticalLayout.addWidget(self.btn_add_member)
        self.btn_remove_member = QtWidgets.QPushButton(attendee_list)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_remove_member.sizePolicy().hasHeightForWidth())
        self.btn_remove_member.setSizePolicy(sizePolicy)
        self.btn_remove_member.setMaximumSize(QtCore.QSize(110, 16777215))
        self.btn_remove_member.setObjectName("btn_remove_member")
        self.verticalLayout.addWidget(self.btn_remove_member)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(attendee_list)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(attendee_list)
        QtCore.QMetaObject.connectSlotsByName(attendee_list)

    def retranslateUi(self, attendee_list):
        _translate = QtCore.QCoreApplication.translate
        attendee_list.setWindowTitle(_translate("attendee_list", "Attendee List"))
        self.tree_attendee.setSortingEnabled(True)
        self.tree_attendee.headerItem().setText(0, _translate("attendee_list", "First Name"))
        self.tree_attendee.headerItem().setText(1, _translate("attendee_list", "Last Name"))
        self.tree_attendee.headerItem().setText(2, _translate("attendee_list", "Cell Phone Number"))
        self.tree_attendee.headerItem().setText(3, _translate("attendee_list", "Waiver Signed"))
        self.label_attendee_list.setText(_translate("attendee_list", "Attendee List:"))
        self.btn_modify_member.setText(_translate("attendee_list", "Modify Member"))
        self.btn_add_member.setText(_translate("attendee_list", "Add Member"))
        self.btn_remove_member.setText(_translate("attendee_list", "Remove Member(s)"))

