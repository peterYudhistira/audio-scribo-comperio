# Form implementation generated from reading ui file 'ListenWindow.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(981, 415)
        Form.setStyleSheet("QLabel#label_title, #label_subtitle{ \n"
"    \n"
"    font: 63 28pt \"Bahnschrift SemiBold SemiConden\";\n"
"    color:rgb(255, 85, 0);\n"
"}\n"
"\n"
"QLabel{\n"
"    font: 63 20pt \"Bahnschrift SemiBold SemiConden\";\n"
"}\n"
"\n"
"QPushButton{\n"
"    font: 63 28pt \"Bahnschrift SemiBold SemiConden\";\n"
"    background:rgb(255, 85, 0);\n"
"    border: 2px solid gray;\n"
"    border-radius:10px;\n"
"     padding: 0 8px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"    background:rgb(255, 140, 0);\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    background: rgb(255, 170, 0);\n"
"}\n"
"\n"
"QPushButton#button_record{\n"
"    background:rgb(0, 255, 0);\n"
"    border-radius: 100px;\n"
"}\n"
"\n"
"QPushButton#button_record:checked{\n"
"    background:rgb(255, 0, 0);\n"
"}\n"
"\n"
"QPushButton#button_record:hover{\n"
"    background:rgb(0, 170, 0);\n"
"}\n"
"\n"
"QPushButton#button_record:checked:hover{\n"
"    background:rgb(255, 35, 28);\n"
"}")
        self.button_record = QtWidgets.QPushButton(parent=Form)
        self.button_record.setGeometry(QtCore.QRect(640, 90, 200, 200))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold SemiConden")
        font.setPointSize(28)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.button_record.setFont(font)
        self.button_record.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("asset/images/mic.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.button_record.setIcon(icon)
        self.button_record.setIconSize(QtCore.QSize(100, 100))
        self.button_record.setCheckable(True)
        self.button_record.setChecked(False)
        self.button_record.setObjectName("button_record")
        self.formLayoutWidget_2 = QtWidgets.QWidget(parent=Form)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(40, 190, 441, 190))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setHorizontalSpacing(20)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_session = QtWidgets.QLabel(parent=self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold SemiConden")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.label_session.setFont(font)
        self.label_session.setObjectName("label_session")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_session)
        self.line_title = QtWidgets.QLineEdit(parent=self.formLayoutWidget_2)
        self.line_title.setReadOnly(True)
        self.line_title.setObjectName("line_title")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.line_title)
        self.label_date = QtWidgets.QLabel(parent=self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold SemiConden")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.label_date.setFont(font)
        self.label_date.setObjectName("label_date")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_date)
        self.line_date = QtWidgets.QLineEdit(parent=self.formLayoutWidget_2)
        self.line_date.setReadOnly(True)
        self.line_date.setObjectName("line_date")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.line_date)
        self.label_speakers = QtWidgets.QLabel(parent=self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold SemiConden")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.label_speakers.setFont(font)
        self.label_speakers.setObjectName("label_speakers")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_speakers)
        self.combo_speakerList = QtWidgets.QComboBox(parent=self.formLayoutWidget_2)
        self.combo_speakerList.setObjectName("combo_speakerList")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.combo_speakerList)
        self.label_question = QtWidgets.QLabel(parent=self.formLayoutWidget_2)
        self.label_question.setObjectName("label_question")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_question)
        self.text_question = QtWidgets.QTextEdit(parent=self.formLayoutWidget_2)
        self.text_question.setObjectName("text_question")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.text_question)
        self.line = QtWidgets.QFrame(parent=Form)
        self.line.setGeometry(QtCore.QRect(40, 170, 441, 20))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(parent=Form)
        self.line_2.setGeometry(QtCore.QRect(500, 10, 20, 391))
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_record = QtWidgets.QLabel(parent=Form)
        self.label_record.setGeometry(QtCore.QRect(640, 290, 201, 31))
        self.label_record.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_record.setObjectName("label_record")
        self.button_back = QtWidgets.QPushButton(parent=Form)
        self.button_back.setGeometry(QtCore.QRect(40, 20, 101, 51))
        self.button_back.setObjectName("button_back")
        self.widget = QtWidgets.QWidget(parent=Form)
        self.widget.setGeometry(QtCore.QRect(40, 110, 441, 61))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_chooseEvent = QtWidgets.QLabel(parent=self.widget)
        self.label_chooseEvent.setObjectName("label_chooseEvent")
        self.verticalLayout.addWidget(self.label_chooseEvent)
        self.combo_eventList = QtWidgets.QComboBox(parent=self.widget)
        self.combo_eventList.setObjectName("combo_eventList")
        self.verticalLayout.addWidget(self.combo_eventList)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_session.setText(_translate("Form", "Session Title"))
        self.label_date.setText(_translate("Form", "Session Date"))
        self.label_speakers.setText(_translate("Form", "Speaker"))
        self.label_question.setText(_translate("Form", "Question"))
        self.label_record.setText(_translate("Form", "Press to Record"))
        self.button_back.setText(_translate("Form", "Back"))
        self.label_chooseEvent.setText(_translate("Form", "Choose Event"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())