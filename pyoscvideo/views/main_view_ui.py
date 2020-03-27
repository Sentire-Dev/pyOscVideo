# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyoscvideo/ressources/main_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(704, 583)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame_rate_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_rate_label.sizePolicy().hasHeightForWidth())
        self.frame_rate_label.setSizePolicy(sizePolicy)
        self.frame_rate_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_rate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.frame_rate_label.setObjectName("frame_rate_label")
        self.horizontalLayout_2.addWidget(self.frame_rate_label)
        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.imageLabel = FixedAspectLabel(self.centralwidget)
        self.imageLabel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setMinimumSize(QtCore.QSize(1, 1))
        self.imageLabel.setSizeIncrement(QtCore.QSize(0, 0))
        self.imageLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.imageLabel.setAutoFillBackground(True)
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setText("")
        self.imageLabel.setScaledContents(False)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setObjectName("imageLabel")
        self.verticalLayout.addWidget(self.imageLabel)
        spacerItem = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.camera_selection_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.camera_selection_comboBox.setObjectName("camera_selection_comboBox")
        self.horizontalLayout.addWidget(self.camera_selection_comboBox)
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
        self.horizontalLayout.addWidget(self.recordButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem4, 0, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 1, 0, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem6, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 704, 22))
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
        self.frame_rate_label.setText(_translate("MainWindow", "Fps:"))
        self.recordButton.setText(_translate("MainWindow", "Record"))
from views.fixed_aspect_label import FixedAspectLabel
