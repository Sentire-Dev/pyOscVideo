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
        MainWindow.resize(994, 785)
        MainWindow.setMinimumSize(QtCore.QSize(400, 300))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(200, 100))
        self.centralwidget.setAccessibleName("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.camerasLayout = QtWidgets.QGridLayout()
        self.camerasLayout.setObjectName("camerasLayout")
        self.verticalLayout_2.addLayout(self.camerasLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.recordButton = QtWidgets.QPushButton(self.centralwidget)
        self.recordButton.setEnabled(True)
        self.recordButton.setAutoFillBackground(False)
        self.recordButton.setStyleSheet("QPushButton#recordButton {\n"
"}\n"
"QPushButton#recordButton:disabled {\n"
"    color: grey;\n"
"}\n"
"QPushButton#recordButton:pressed {\n"
"}\n"
"QPushButton#recordButton:focus:pressed {\n"
" }\n"
"QPushButton#recordButton:focus {\n"
"}\n"
"QPushButton#recordButton:hover {\n"
" }\n"
"QPushButton#recordButton:checked {\n"
"    background-color: red;\n"
" }")
        self.recordButton.setCheckable(True)
        self.recordButton.setChecked(False)
        self.recordButton.setAutoRepeat(False)
        self.recordButton.setAutoDefault(False)
        self.recordButton.setDefault(False)
        self.recordButton.setFlat(False)
        self.recordButton.setObjectName("recordButton")
        self.horizontalLayout_2.addWidget(self.recordButton)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 0, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 994, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pyOscVIdeo"))
        self.recordButton.setText(_translate("MainWindow", "Record"))
