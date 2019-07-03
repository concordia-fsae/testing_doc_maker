# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\homepage_export.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 560)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.main_tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.main_tabs.setGeometry(QtCore.QRect(0, 0, 1111, 521))
        self.main_tabs.setObjectName("main_tabs")
        self.tab_main = QtWidgets.QWidget()
        self.tab_main.setObjectName("tab_main")
        self.btn_open_template = QtWidgets.QPushButton(self.tab_main)
        self.btn_open_template.setGeometry(QtCore.QRect(10, 10, 121, 23))
        self.btn_open_template.setObjectName("btn_open_template")
        self.btn_save_doc = QtWidgets.QPushButton(self.tab_main)
        self.btn_save_doc.setGeometry(QtCore.QRect(10, 40, 121, 23))
        self.btn_save_doc.setObjectName("btn_save_doc")
        self.main_tabs.addTab(self.tab_main, "")
        self.tab_roster = QtWidgets.QWidget()
        self.tab_roster.setObjectName("tab_roster")
        self.listView = QtWidgets.QListView(self.tab_roster)
        self.listView.setGeometry(QtCore.QRect(0, 0, 1095, 495))
        self.listView.setObjectName("listView")
        self.main_tabs.addTab(self.tab_roster, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1100, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Template_File = QtWidgets.QAction(MainWindow)
        self.actionOpen_Template_File.setObjectName("actionOpen_Template_File")
        self.actionSave_Testing_Doc = QtWidgets.QAction(MainWindow)
        self.actionSave_Testing_Doc.setObjectName("actionSave_Testing_Doc")
        self.menuFile.addAction(self.actionOpen_Template_File)
        self.menuFile.addAction(self.actionSave_Testing_Doc)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.main_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Testing Doc Maker"))
        self.btn_open_template.setText(_translate("MainWindow", "Choose Template File"))
        self.btn_save_doc.setText(_translate("MainWindow", "Save Testing Doc"))
        self.main_tabs.setTabText(self.main_tabs.indexOf(self.tab_main), _translate("MainWindow", "Main Page"))
        self.main_tabs.setTabText(self.main_tabs.indexOf(self.tab_roster), _translate("MainWindow", "Roster Management"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_Template_File.setText(_translate("MainWindow", "Open Template File"))
        self.actionOpen_Template_File.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave_Testing_Doc.setText(_translate("MainWindow", "Save Testing Doc"))
        self.actionSave_Testing_Doc.setShortcut(_translate("MainWindow", "Ctrl+S"))

