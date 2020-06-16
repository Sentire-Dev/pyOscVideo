# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyoscvideo/gui/resources/camera_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CameraView(object):
    def setupUi(self, CameraView):
        CameraView.setObjectName("CameraView")
        CameraView.resize(1100, 837)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CameraView.sizePolicy().hasHeightForWidth())
        CameraView.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(CameraView)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.selectCameraLabel_2 = QtWidgets.QLabel(CameraView)
        self.selectCameraLabel_2.setObjectName("selectCameraLabel_2")
        self.horizontalLayout_4.addWidget(self.selectCameraLabel_2)
        self.cameraSelectionComboBox = QtWidgets.QComboBox(CameraView)
        self.cameraSelectionComboBox.setObjectName("cameraSelectionComboBox")
        self.horizontalLayout_4.addWidget(self.cameraSelectionComboBox)
        spacerItem2 = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.frameRateLabel = QtWidgets.QLabel(CameraView)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameRateLabel.sizePolicy().hasHeightForWidth())
        self.frameRateLabel.setSizePolicy(sizePolicy)
        self.frameRateLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frameRateLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.frameRateLabel.setObjectName("frameRateLabel")
        self.horizontalLayout_4.addWidget(self.frameRateLabel)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.imageLabel = QtWidgets.QLabel(CameraView)
        self.imageLabel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setMinimumSize(QtCore.QSize(1, 1))
        self.imageLabel.setSizeIncrement(QtCore.QSize(0, 0))
        self.imageLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.imageLabel.setAutoFillBackground(False)
        self.imageLabel.setStyleSheet("background-color: black;")
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setText("")
        self.imageLabel.setScaledContents(False)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setObjectName("imageLabel")
        self.verticalLayout_2.addWidget(self.imageLabel)
        spacerItem4 = QtWidgets.QSpacerItem(13, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 3, 2)
        spacerItem5 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 1, 3, 1, 1)

        self.retranslateUi(CameraView)
        QtCore.QMetaObject.connectSlotsByName(CameraView)

    def retranslateUi(self, CameraView):
        _translate = QtCore.QCoreApplication.translate
        CameraView.setWindowTitle(_translate("CameraView", "Form"))
        self.selectCameraLabel_2.setText(_translate("CameraView", "Select Camera"))
        self.frameRateLabel.setText(_translate("CameraView", "Fps:"))
