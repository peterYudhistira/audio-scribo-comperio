# Form implementation generated from reading ui file 'ui/PresentWindow.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1210, 800)
        Form.setStyleSheet("QLabel#label_title, #label_subtitle{ \n"
"    \n"
"    font: 63 28pt \"Bahnschrift SemiBold SemiConden\";\n"
"    color:rgb(255, 85, 0);\n"
"}\n"
"\n"
"QPushButton{\n"
"    font: 63 28pt \"Bahnschrift SemiBold SemiConden\";\n"
"    background:rgb(255, 85, 0);\n"
"    border: 2px solid gray;\n"
"      border-radius: 10px;\n"
"     padding: 0 8px;\n"
"}\n"
"\n"
"QPushButton#button_addSpeaker, QPushButton#button_addEvent, QPushButton#button_toggle_widget{\n"
"    font: 63 20pt \"Bahnschrift SemiBold SemiConden\";\n"
"}\n"
"QPushButton:hover{\n"
"    background:rgb(255, 140, 0);\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background: rgb(255, 170, 0);\n"
"}\n"
"\n"
"QPushButton:disabled{\n"
"    background: rgb(150, 150, 150);\n"
"}\n"
"\n"
"QLabel{\n"
"    font: 63 16pt \"Bahnschrift SemiBold\";\n"
"}    \n"
"\n"
"QLabel{\n"
"    \n"
"    font: 63 12pt \"Bahnschrift SemiBold\";\n"
"}\n"
"\n"
"QCheckBox{\n"
"    font: 63 12pt \"Bahnschrift SemiBold\";\n"
"}\n"
"\n"
"QTableWidget{\n"
"    font: 14pt \"Bahnschrift\";\n"
"}\n"
"\n"
"QHeaderView{\n"
"    font: 63 18pt \"Bahnschrift SemiBold SemiConden\";\n"
"}")
        self.button_saveInFile = QtWidgets.QPushButton(parent=Form)
        self.button_saveInFile.setGeometry(QtCore.QRect(1010, 720, 191, 41))
        self.button_saveInFile.setObjectName("button_saveInFile")
        self.label_title = QtWidgets.QLabel(parent=Form)
        self.label_title.setGeometry(QtCore.QRect(21, 11, 1200, 45))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        self.label_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.tableWidget = QtWidgets.QTableWidget(parent=Form)
        self.tableWidget.setGeometry(QtCore.QRect(11, 80, 1191, 631))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.button_saveInFile.setText(_translate("Form", "Save In File"))
        self.label_title.setText(_translate("Form", "Title"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Speaker"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Question"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Answer"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
