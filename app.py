from PyQt6.QtWidgets import QWidget
from objects import (
    mainmenu as mm,
    listenwindow as lw,
    processwindow as pw,
    addwindow as aw,
    turntotexinator as ttt,
    db
)
from PyQt6 import (
    QtCore,
    QtWidgets as qtw,
    QtCore as qtc,
    QtGui as qtg,
    QtMultimedia as qtm
)
from datetime import datetime as dt
import wave
import pyaudio as pa


class RecorderThread(qtc.QThread):

    toggle_signal = qtc.pyqtSignal(str)

    def __init__(self, fileName=None):
        super().__init__()
        self.fileName = fileName
        self.is_running = True  # for toggling

    # this function will be called when QThread::start() is called.
    def run(self):
        audio = pa.PyAudio()
        frames = []
        stream = audio.open(format=pa.paInt16, channels=1,
                            rate=44100, input=True, frames_per_buffer=1024)
        # apparently the point is making a separate loop while keeping the GUI loop running.
        while self.is_running:
            data = stream.read(1024)
            frames.append(data)
        stream.close()
        wf = wave.open(self.fileName, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pa.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()

    # this here is what to do upon stopping
    def stop(self):
        self.is_running = False
        self.toggle_signal.emit(self.fileName)


class MainMenuWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        # set stuff here
        self.ui = mm.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle(
            "I hear, I write, I discover")
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        # thanks to Rueful on Discord for grammatical correction.
        self.ui.label_title.setText("Audio, Scribo, Comperio")
        # self.ui.label_icon.setPixmap(qtg.QPixmap("asset/images/Solaire.png"))

        # connect stuff here
        self.ui.button_listen.clicked.connect(self.button_startListening)
        self.ui.button_process.clicked.connect(self.button_startProcessing)
        self.ui.button_create.clicked.connect(self.button_startCreating)

    def button_startListening(self):
        self.listenWindow = ListenWindow(self)
        self.hide()
        self.listenWindow.show()

    def button_startProcessing(self):
        self.processWindow = ProcessWindow(self)
        self.hide()
        self.processWindow.show()

    def button_startCreating(self):
        self.addWindow = AddWindow(self)
        self.hide()
        self.addWindow.show()


class ListenWindow(qtw.QWidget):
    def __init__(self, mainwindow):
        super().__init__()

        # the mainwindow
        self.mainwindow = mainwindow

        # set stuff here
        self.ui = lw.Ui_Form()
        self.ui.setupUi(self)
        # whosoever has ears for hearing, let him hear!
        self.setWindowTitle("qui habet aurem audendi, audiat!")
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.eventID = 0
        self.speakerID = 0
        self.eventList = cursor.list_events()
        self.speakerList = cursor.list_speakers()
        self.LoadComboBox(self.ui.combo_eventList)
        self.LoadComboBox(self.ui.combo_speakerList)
        self.msgBox = qtw.QMessageBox()
        self.msgBox.setStandardButtons(qtw.QMessageBox.StandardButton.Ok)
        self.msgBox.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))

        # connect stuff here
        self.ui.button_back.clicked.connect(self.GoBack)
        self.ui.button_record.clicked.connect(self.ToggleRecord)
        self.ui.combo_eventList.currentIndexChanged.connect(self.ChangeEvent)
        self.ui.combo_speakerList.currentIndexChanged.connect(
            self.ChangeSpeaker)

    def GoBack(self):
        self.hide()
        self.mainwindow.show()

    def ToggleRecord(self):
        if self.ValidateRecord():
            if self.ui.button_record.isChecked():

                # file path
                filePath = "records/event{}/{}.wav".format(self.ui.combo_eventList.currentData(
                ), self.ui.combo_speakerList.currentText().split(" |")[0] + dt.now().strftime("%d%m%Y%H%M%S"))
                # begin record thread
                self.ui.rt = RecorderThread(filePath)
                self.ui.rt.start()

                # change label
                self.ui.label_record.setText("Recording...")
            else:
                # save in database
                self.ui.rt.toggle_signal.connect(self.SaveRecording)

                # stop thread
                self.ui.rt.stop()
                # change label
                self.ui.label_record.setText("Press to Record")

                # success
                self.MessageSuccess("Recording finished.")
        else:
            self.MessageFail("Fill the speaker and event data first.")
            self.ui.button_record.setChecked(False)

    def SaveRecording(self, fileName):
        cursor.create_record_audio(self.ui.combo_eventList.currentData(
        ), self.ui.combo_speakerList.currentData(), self.ui.text_question.toPlainText(), fileName)

    def LoadComboBox(self, comboBox):
        dataList = []
        if comboBox.objectName() == "combo_eventList":
            comboBox.setPlaceholderText("Select Event")
            dataList = self.eventList
        elif comboBox.objectName() == "combo_speakerList":
            comboBox.setPlaceholderText("Select Speaker")
            dataList = self.speakerList

        for item in dataList:
            if comboBox.objectName() == "combo_eventList":
                comboBox.addItem(item[1], item[0])
            elif comboBox.objectName() == "combo_speakerList":
                comboBox.addItem("{} | {}".format(item[2], item[1]), item[0])

    def ChangeEvent(self):
        self.eventID = self.ui.combo_eventList.itemData(
            self.ui.combo_eventList.currentIndex())
        event = cursor.get_event("id", self.eventID)
        self.ui.line_title.setText(event[1])
        self.ui.line_date.setText(event[2])

    def ChangeSpeaker(self):
        self.speakerID = self.ui.combo_speakerList.itemData(
            self.ui.combo_speakerList.currentIndex())

    def ValidateRecord(self):
        if self.eventID > 0 and self.speakerID > 0:
            return True
        return False

    def MessageSuccess(self, txt):
        # success
        self.msgBox.setWindowTitle("Good Job!")
        self.msgBox.setIcon(qtw.QMessageBox.Icon.Information)
        self.msgBox.setText("You dun did it\n{}".format(txt))
        self.msgBox.show()

    def MessageFail(self, txt):
        self.msgBox.setWindowTitle("What the hell, oh my god, no way")
        self.msgBox.setIcon(qtw.QMessageBox.Icon.Warning)
        self.msgBox.setText("You dun goofed\n{}".format(txt))
        self.msgBox.show()


class ProcessWindow(qtw.QWidget):
    def __init__(self, mainwindow) -> None:
        super().__init__()

        # set mainwindow
        self.mainwindow = mainwindow

        # set stuff
        self.ui = pw.Ui_Form()
        self.ui.setupUi(self)
        self.eventList = cursor.list_events()
        self.audioPlayer = qtm.QMediaPlayer()
        self.audioOutput = qtm.QAudioOutput()
        self.audioPlayer.setAudioOutput(self.audioOutput)
        self.audioOutput.setVolume(100)
        # whosoever has power over the machine, let him discover!
        self.setWindowTitle("qui habet potentia super machina, comperiat!")
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.LoadComboBox(self.ui.combo_eventList)

        # connect stuff here
        self.ui.button_back.clicked.connect(self.GoBack)
        self.ui.combo_eventList.currentIndexChanged.connect(self.ChangeEvent)
        # i forgot the existence of lambda ENTIRELY.
        self.ui.button_process.clicked.connect(
            lambda: self.StartProcessing(15))

    def GoBack(self):
        self.hide()
        self.mainwindow.show()

    def LoadComboBox(self, comboBox):
        comboBox.setPlaceholderText("Select Event")
        for item in self.eventList:
            comboBox.addItem(item[1], item[0])

    def ChangeEvent(self):
        eventID = self.ui.combo_eventList.currentData()
        currentEvent = cursor.get_event("id", eventID)
        self.LoadTables(self.ui.table_recordData, eventID)
        self.ui.label_theme.setText(str(currentEvent[1]))
        self.ui.label_date.setText(str(currentEvent[2]))

    def LoadTables(self, table, eventID):
        # fetch data
        dataList = cursor.get_recordDataJoined("event_id", eventID)
        # clear table first
        table.clearContents()
        table.setRowCount(0)
        # put in table
        for i in range(len(dataList)):
            table.insertRow(i)
            table.setItem(i, 0, qtw.QTableWidgetItem(
                str(dataList[i][0])))  # id
            table.setItem(i, 1, qtw.QTableWidgetItem(
                str(dataList[i][4])))  # question
            table.setItem(i, 2, qtw.QTableWidgetItem(
                str(dataList[i][3])))  # speaker

            # for audio transcript, each row has a button which plays the recording if it is clicked.
            self.button_play = qtw.QPushButton("▶".format(i), self)
            self.button_play.setCheckable(True)
            # for some reason, we need to specify two things in the lambda. first one probably goes to the signal slot.
            self.button_play.clicked.connect(
                lambda ch, filePath=dataList[i][5]: self.TogglePlayRecord(filePath))
            table.setCellWidget(i, 3, self.button_play)
            table.setItem(i, 4, qtw.QTableWidgetItem(
                str(dataList[i][6])))  # text
        # resize
        table.resizeRowsToContents()
        table.horizontalHeader().setSectionResizeMode(
            1, qtw.QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            4, qtw.QHeaderView.ResizeMode.Stretch)

    def StartProcessing(self, magicNumber):
        print("Hi, your magic number is {}".format(magicNumber))

    def TogglePlayRecord(self, filePath):
        sender = self.sender()
        if sender.isChecked():
            self.audioPlayer.setSource(qtc.QUrl.fromLocalFile(filePath))
            self.audioPlayer.play()
            sender.setText("■")
        else:
            self.audioPlayer.stop()
            sender.setText("▶")


class AddWindow(qtw.QWidget):
    def __init__(self, mainwindow):
        super().__init__()

        # set mainwindow
        self.mainwindow = mainwindow

        # set stuff
        self.ui = aw.Ui_Form()
        self.ui.setupUi(self)
        # whosoever has hands with which to write, let him write!
        self.setWindowTitle("qui habet manus scribendum, scribat!")
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.LoadTables(self.ui.table_speakers)
        self.LoadTables(self.ui.table_events)
        self.msgBox = qtw.QMessageBox()
        self.msgBox.setStandardButtons(qtw.QMessageBox.StandardButton.Ok)
        self.msgBox.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))

        # connect stuff here
        self.ui.button_back.clicked.connect(self.GoBack)
        self.ui.button_toggle_widget.clicked.connect(self.ToggleWidget)
        self.ui.button_addEvent.clicked.connect(self.AddEvent)
        self.ui.button_addSpeaker.clicked.connect(self.AddSpeaker)

    def GoBack(self):
        self.hide()
        self.mainwindow.show()

    def ToggleWidget(self):
        if self.ui.stackedWidget.currentIndex() == 0:
            self.ui.stackedWidget.setCurrentIndex(1)
            self.ui.button_toggle_widget.setText("To Speaker List")
        else:
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.button_toggle_widget.setText("To Event List")

    def LoadTables(self, table):
        # fetch data
        dataList = []
        if table.objectName() == "table_speakers":
            dataList = cursor.list_speakers()
        elif table.objectName() == "table_events":
            dataList = cursor.list_events()
        # put in table
        for i in range(len(dataList)):
            table.insertRow(i)
            for j in range(len(dataList[i])):
                table.setItem(
                    i, j, qtw.QTableWidgetItem(str(dataList[i][j])))

        # resize
        header = table.horizontalHeader()
        header.setSectionResizeMode(
            0, qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, qtw.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(
            2, qtw.QHeaderView.ResizeMode.ResizeToContents)

    def MessageSuccess(self, txt):
        # success
        self.msgBox.setIcon(qtw.QMessageBox.Icon.Information)
        self.msgBox.setText("You dun did it\n{}".format(txt))
        self.msgBox.show()

    def MessageFail(self, txt):
        self.msgBox.setIcon(qtw.QMessageBox.Icon.Warning)
        self.msgBox.setText("You dun goofed\n{}".format(txt))
        self.msgBox.show()

    def AddEvent(self):
        if self.ui.line_title.text() != "" and self.ui.line_date.text() != "":
            cursor.create_event(self.ui.line_title.text(),
                                self.ui.line_date.text())

            # success
            self.MessageSuccess("Event created")
            # clear lines
            self.ui.line_title.clear()
            self.ui.line_date.clear()
            # reload table
            self.ui.table_events.setRowCount(0)
            self.LoadTables(self.ui.table_events)

        else:
            self.MessageFail("Event not created")

    def AddSpeaker(self):
        if self.ui.line_name.text() != "" and self.ui.line_code.text() != "":
            cursor.create_speaker(self.ui.line_name.text(),
                                  self.ui.line_code.text())
            # success
            self.MessageSuccess("Speaker created")
            # clear lines
            self.ui.line_name.clear()
            self.ui.line_code.clear()
            # reload table
            self.ui.table_speakers.setRowCount(0)
            self.LoadTables(self.ui.table_speakers)
        else:
            self.MessageFail("Speaker not created")


if __name__ == "__main__":
    cursor = db.DatabaseHandler("database/testdb.db")
    app = qtw.QApplication([])
    menu_widget = MainMenuWindow()
    menu_widget.show()
    app.exec()
