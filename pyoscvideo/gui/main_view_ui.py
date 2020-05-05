# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyoscvideo/gui/resources/main_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(730, 576)
        MainWindow.setMinimumSize(QtCore.QSize(400, 300))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(200, 100))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.camerasLayout = QtWidgets.QGridLayout()
        self.camerasLayout.setObjectName("camerasLayout")
        self.verticalLayout.addLayout(self.camerasLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        self.recordButton = QtWidgets.QPushButton(self.centralwidget)
        self.recordButton.setEnabled(True)
        self.recordButton.setAutoFillBackground(False)
        self.recordButton.setStyleSheet("QPushButton#recordButton { \n"
"}\n"
"QPushButton#recordButton:disabled {\n"
"    color: grey; \n"
"}\n"
"QPushButton#recordButton:pressed {\n"
"}\n"
"QPushButton#recordButton:focus:pressed { \n"
" }\n"
"QPushButton#recordButton:focus { \n"
"}\n"
"QPushButton#recordButton:hover {\n"
" }\n"
"QPushButton#recordButton:checked { \n"
"    background-color: red;\n"
" }")
        self.recordButton.setCheckable(True)
        self.recordButton.setChecked(False)
        self.recordButton.setAutoRepeat(False)
        self.recordButton.setAutoDefault(False)
        self.recordButton.setDefault(False)
        self.recordButton.setFlat(False)
        self.recordButton.setObjectName("recordButton")
        self.verticalLayout_2.addWidget(self.recordButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem3, 3, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 1, 2, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 1, 0, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem6, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 730, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.recordButton.setText(_translate("MainWindow", "Record"))
