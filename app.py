import typing
from datetime import datetime
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget
from objects import (
    mainmenu as mm,
    listenwindow as lw,
    processwindow as pw,
    addwindow as aw,
    presentwindow as prw,
    turntotexinator as ttt,
    anomalydetector as ad,
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


class TurnToTextinatorThread(qtc.QThread):  # tttt for short
    transcribe_signal = qtc.pyqtSignal(list)

    def __init__(self, filePathList: list = []) -> None:
        super().__init__()
        self.filePathList = filePathList

    def setFilePath(self, filePathList: list):
        self.filePathList = filePathList

    def run(self):
        filePath_transcriptList = []
        print("huh?")
        for row in range(len(self.filePathList)):
            # conditions for transcribing
            if self.filePathList[row][2].lower() == "id":
                # if indonesian, hit it with the two for one special (transcribe as ID, then translate ID to EN)
                transcript = ttt.TwoForOneSpecial(
                    fileName=self.filePathList[row][1], transcribeLang="id", translateLang="en")
            elif self.filePathList[row][2].lower() == "en":
                # if english, only return the transcription
                transcript = ttt.TranscribeText(
                    fileName=self.filePathList[row][1], transcribeLang="en")
            filePath_transcriptList.append(
                (self.filePathList[row][0], self.filePathList[row][1], transcript))
        print("hoh?")
        # returns a list of (row, filePath, transcript)
        self.transcribe_signal.emit(filePath_transcriptList)


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

# please NOT ANOTHER THREAD.
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
        self.ui.button_record.setIcon(qtg.QIcon("asset/images/mic.png"))
        self.ui.button_toggleLang.setText("ID")

        # connect stuff here
        self.ui.button_back.clicked.connect(self.GoBack)
        self.ui.button_record.clicked.connect(self.ToggleRecord)
        self.ui.combo_eventList.currentIndexChanged.connect(self.ChangeEvent)
        self.ui.combo_speakerList.currentIndexChanged.connect(
            self.ChangeSpeaker)
        self.ui.button_toggleLang.clicked.connect(self.ToggleLang)

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
                self.ui.button_toggleLang.setDisabled(
                    True)  # disable toggle language
            else:
                # save in database
                self.ui.rt.toggle_signal.connect(self.SaveRecording)

                # stop thread
                self.ui.rt.stop()
                # change label
                self.ui.label_record.setText("Press to Record")

                # success
                self.MessageSuccess("Recording finished.")
                self.ui.button_toggleLang.setDisabled(
                    False)  # re-enable toggle language
        else:
            self.MessageFail("Fill the speaker and event data first.")
            self.ui.button_record.setChecked(False)

    def ToggleLang(self):
        sender = self.sender()
        if sender.isChecked():
            sender.setText("ID")
        else:
            sender.setText("EN")

    def SaveRecording(self, fileName):
        cursor.create_record_audio(self.ui.combo_eventList.currentData(
        ), self.ui.combo_speakerList.currentData(), self.ui.text_question.toPlainText(), fileName, self.ui.button_toggleLang.text())

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
        self.presentWindow = None  # Funni little workaround
        # whosoever has power over the machine, let him discover!
        self.setWindowTitle("qui habet potentia super machina, comperiat!")
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.LoadComboBox(self.ui.combo_eventList)
        self.ui.check_saveTranscriptToDatabase.setChecked(True)
        # we disable this for now.
        self.ui.check_saveTranscriptToDatabase.setDisabled(True)
        self.ui.button_process.setDisabled(True) # will only enable after loading a table.
        self.ui.button_transcribe_all.setDisabled(True)
        self.ui.check_nerdMode.setChecked(True)
        self.ui.featureExtractionGroup = qtw.QButtonGroup(self)
        self.ui.featureExtractionGroup.addButton(self.ui.radio_Embed)
        self.ui.featureExtractionGroup.addButton(self.ui.radio_LDA)
        self.ui.anomalyDetectionGroup = qtw.QButtonGroup(self)
        self.ui.anomalyDetectionGroup.addButton(self.ui.radio_DBSCAN)
        self.ui.anomalyDetectionGroup.addButton(self.ui.radio_LOF)
        self.ui.anomalyDetectionGroup.addButton(self.ui.radio_IF)
        # for now, disable LOF and IF
        self.ui.radio_LOF.setDisabled(True)
        self.ui.radio_IF.setDisabled(True)
        self.msgBox = qtw.QMessageBox()
        self.msgBox.setStandardButtons(qtw.QMessageBox.StandardButton.Ok)
        self.msgBox.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.buttonPlayList = []

        # connect stuff here
        self.ui.button_back.clicked.connect(self.GoBack)
        self.ui.combo_eventList.currentIndexChanged.connect(self.ChangeEvent)
        # i forgot the existence of lambda ENTIRELY.
        self.ui.button_process.clicked.connect(
            lambda: self.StartProcessing())
        self.ui.button_transcribe_all.clicked.connect(self.TranscribeAll)
        self.ui.check_nerdMode.toggled.connect(self.ToggleNerdMode)

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
        self.dataList = cursor.get_recordDataJoined("event_id", eventID)
        # clear table first
        table.clearContents()
        table.setRowCount(0)
        # put in table
        for i in range(len(self.dataList)):
            table.insertRow(i)
            table.setItem(i, 0, qtw.QTableWidgetItem(
                str(self.dataList[i][0])))  # id
            table.setItem(i, 1, qtw.QTableWidgetItem(
                str(self.dataList[i][4])))  # question
            table.setItem(i, 2, qtw.QTableWidgetItem(
                str(self.dataList[i][3])))  # speaker

            # make audio button. if audio path doesn't exist, disable it.
            self.button_play = qtw.QPushButton("▶".format(i), self)
            self.button_play.setObjectName(str(self.dataList[i][5]))
            self.button_play.setCheckable(True)
            self.button_play.clicked.connect(
                lambda ch, filePath=self.button_play.objectName(): self.TogglePlayRecord(filePath))
            if self.dataList[i][5] == "":
                self.button_play.setDisabled(True)
                self.button_play.setText("🙅")
            self.buttonPlayList.append(self.button_play)
            table.setCellWidget(i, 3, self.button_play)

            table.setItem(i, 4, qtw.QTableWidgetItem(
                str(self.dataList[i][6])))  # text
            table.setItem(i, 5, qtw.QTableWidgetItem(
                str(self.dataList[i][7])))  # language code
        # resize
        table.horizontalHeader().setSectionResizeMode(
            1, qtw.QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            4, qtw.QHeaderView.ResizeMode.Stretch)
        # do this AFTER stretching.
        self.ui.table_recordData.resizeRowsToContents()

        # enable the buttons
        self.ui.button_process.setDisabled(False)
        self.ui.button_transcribe_all.setDisabled(False)

    # toggle the params. I will surely regret this later.
    def ToggleNerdMode(self):
        sender = self.sender()
        if sender.isChecked():
            self.ui.radio_Embed.setDisabled(False)
            self.ui.radio_LDA.setDisabled(False)
            self.ui.radio_DBSCAN.setDisabled(False)
            self.ui.radio_LOF.setDisabled(False)
            self.ui.radio_IF.setDisabled(False)
            self.ui.check_isWeighted.setDisabled(False)
            self.ui.line_epsilon.setDisabled(False)
            self.ui.line_minSamp.setDisabled(False)
            self.ui.line_nTopics.setDisabled(False)
        else:
            self.ui.radio_Embed.setDisabled(True)
            self.ui.radio_LDA.setDisabled(True)
            self.ui.radio_DBSCAN.setDisabled(True)
            self.ui.radio_LOF.setDisabled(True)
            self.ui.radio_IF.setDisabled(True)
            self.ui.check_isWeighted.setDisabled(True)
            self.ui.line_epsilon.setDisabled(True)
            self.ui.line_minSamp.setDisabled(True)
            self.ui.line_nTopics.setDisabled(True)

    def StartProcessing(self):
        currentEventID = self.ui.combo_eventList.currentData()
        ad.SetDFFromDB(eventID=currentEventID,
                        splitBySentences=self.ui.check_isSplit.isChecked())
        # i'll implement nerd mode tonight... today.
        nerdOK = True
        if self.ui.check_nerdMode.isChecked():
            if self.ValidateNerdModeParams():
                featureExtractor = self.ui.featureExtractionGroup.checkedButton().text()
                ad.SetFeatureExtractionParam("method", featureExtractor)

                anomalyDetector = self.ui.anomalyDetectionGroup.checkedButton().text()
                ad.SetAnomalyDetectionParam("algorithm", anomalyDetector)

                isWeighted = self.ui.check_isWeighted.isChecked()
                ad.SetFeatureExtractionParam("weighted", isWeighted)
                
                if self.ui.line_epsilon.text() != '':
                    epsilon = float(self.ui.line_epsilon.text())
                    ad.SetAnomalyDetectionParam("epsilon", epsilon)

                if self.ui.line_minSamp.text() != '':
                    minSamp = int(self.ui.line_minSamp.text())
                    ad.SetAnomalyDetectionParam("minsamp", minSamp)

                if self.ui.line_neighbors.text() != '':
                    nNeighbors = int(self.ui.line_neighbors.text())
                    ad.SetAnomalyDetectionParam("neighbors", nNeighbors)

                if self.ui.line_contamination.text() != '':
                    contaminationRate = float(self.ui.line_contamination.text())
                    ad.SetAnomalyDetectionParam("contamination", contaminationRate)

                if self.ui.line_estimators.text() != '':
                    nEstimators = int(self.ui.line_estimators.text())
                    ad.SetAnomalyDetectionParam("estimators", nEstimators)

                if self.ui.line_nTopics.text() != '':
                    LDAnTopic = int(self.ui.line_nTopics.text())
                    ad.SetFeatureExtractionParam("n_topics", LDAnTopic)
                print(ad.FeatureExtractionParams)
                print(ad.AnomalyDetectionParams)
                myResult = ad.GetAnomalies(isReturnSeparate=False)
            else:
                nerdOK = False
        else:
            print(ad.FeatureExtractionParams)
            print(ad.AnomalyDetectionParams)
            myResult = ad.GetAnomalies(isReturnSeparate=False)
        if nerdOK:
            self.presentWindow = PresentWindow(
                myResult, self.ui.label_theme.text(), self)
            self.presentWindow.show()

    def ValidateNerdModeParams(self):
        # we will use the elimination method as we have learned in that god-forsaken place.
        if not (self.ui.featureExtractionGroup.checkedButton() and self.ui.anomalyDetectionGroup.checkedButton()):
            self.MessageFail("one or both of the radio button groups are unchecked.")
            return False
        else:
            # in the case of LDA, make sure the nTopics is filled.
            if self.ui.featureExtractionGroup.checkedButton().text() == "LDA":
                if not self.ui.line_nTopics.text():
                    self.MessageFail("You doing LDA without the number of topics")
                    return False
            else:
                # in the case of DBSCAN
                if self.ui.anomalyDetectionGroup.checkedButton().text() == "DBSCAN": 
                    # make sure that epsilon and minsamp is filled.
                    if not (self.ui.line_epsilon.text() and self.ui.line_minSamp.text()):
                        self.MessageFail("You doing DBSCAN without the epsilon and/or minsamp")
                        return False
                # in the case of LOF
                elif self.ui.anomalyDetectionGroup.checkedButton().text() == "LOF":
                    if not(self.ui.line_contamination.text() and self.ui.line_neighbors.text()):
                        self.MessageFail("You doing LOF without the contamination and/or n_neighbors")
                        return False
                # in the case of IF
                elif self.ui.anomalyDetectionGroup.checkedButton().text() == "IF":
                    if not(self.ui.line_contamination.text() and self.ui.line_estimators.text()):
                        self.MessageFail("You doing IF without the contamination and/or n_estimators") 
                        return False
        return True
    
    def MessageFail(self, txt):
        self.msgBox.setIcon(qtw.QMessageBox.Icon.Warning)
        self.msgBox.setText("You dun goofed\n{}".format(txt))
        self.msgBox.show()
    
    def TranscribeAll(self):
        ttttt = []  # i am funny
        for row in range(self.ui.table_recordData.rowCount()):
            button = self.ui.table_recordData.cellWidget(row, 3)
            if button.objectName() != "":  # shitty condition to stand-in for "does this object have an audio file path"
                # i'm about to get even funnier
                ttttt.append((row, button.objectName(),
                             self.ui.table_recordData.item(row, 5).text()))
        print("the list contains : {}".format(ttttt))
        # pass the value over to a TTTThread then let it run.
        self.tttt = TurnToTextinatorThread()
        self.tttt.setFilePath(ttttt)
        self.tttt.transcribe_signal.connect(self.GetTranscript)
        self.tttt.start()
        # to prevent unwanted consequences...
        self.ui.button_back.setDisabled(True)
        self.ui.button_process.setDisabled(True)
        self.ui.button_transcribe_all.setDisabled(True)

    # TranscribeAll's thread will run this after transcription is finished.
    def GetTranscript(self, transcriptResult: list):
        print("im here now??")
        print(transcriptResult)
        # display it and write to DB and/or CSV if needed.
        for row in range(len(transcriptResult)):
            self.ui.table_recordData.setItem(
                int(transcriptResult[row][0]), 4, qtw.QTableWidgetItem(transcriptResult[row][2]))
            if self.ui.check_saveTranscriptToDatabase.isChecked():
                print("we are updating the db with : {} || {}".format(
                    self.ui.table_recordData.item(row, 0).text(), transcriptResult[row][2]))
                cursor.update_recordData_text(ID=int(self.ui.table_recordData.item(transcriptResult[row][0], 0).text()), text=str(
                    transcriptResult[row][2]))  # at times like this i miss GORM.

        self.ui.table_recordData.resizeRowsToContents()
        self.ui.table_recordData.horizontalHeader().setSectionResizeMode(
            1, qtw.QHeaderView.ResizeMode.Stretch)
        self.ui.table_recordData.horizontalHeader().setSectionResizeMode(
            4, qtw.QHeaderView.ResizeMode.Stretch)
        self.ui.button_back.setDisabled(False)  # unfreeze
        self.ui.button_process.setDisabled(False)
        self.ui.button_transcribe_all.setDisabled(False)

    def TogglePlayRecord(self, filePath):
        sender = self.sender()
        if sender.isChecked():
            self.audioPlayer.setSource(qtc.QUrl.fromLocalFile(filePath))
            self.audioPlayer.play()
            sender.setText("■")
        else:
            self.audioPlayer.stop()
            sender.setText("▶")

    def closeEvent(self, event):
        if self.presentWindow:
            self.presentWindow.close()


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


class PresentWindow(qtw.QWidget):
    def __init__(self, df: db.pd.DataFrame, eventTitle: str, processWindow: ProcessWindow) -> None:
        super().__init__()
        # the processwindow here
        self.processWindow = processWindow

        # set stuff here
        self.ui = prw.Ui_Form()
        self.ui.setupUi(self)
        self.df = df
        self.ui.label_title.setText(eventTitle)
        self.setWindowIcon(qtg.QIcon("asset/images/Solaire.png"))
        self.setWindowTitle("Qui habet oculi vidiendi, videat!")
        # connect stuff here
        self.LoadTable(self.df)
        self.ui.button_saveInFile.clicked.connect(self.SaveInFile)

    # functions
    def SaveInFile(self):
        print("haha, jonathan, you are banging my daughter")

    def LoadTable(self, df: db.pd.DataFrame):
        self.ui.tableWidget.verticalScrollBar().setSingleStep(1)
        self.ui.tableWidget.setRowCount(0)
        for i in range(len(self.df.index)):
            self.ui.tableWidget.insertRow(i)
            self.ui.tableWidget.setItem(
                i, 0, qtw.QTableWidgetItem(str(self.df.loc[i]["id"])))
            self.ui.tableWidget.setItem(
                i, 1, qtw.QTableWidgetItem(str(self.df.loc[i]["speaker"])))
            self.ui.tableWidget.setItem(
                i, 2, qtw.QTableWidgetItem(str(self.df.loc[i]["question"])))
            self.ui.tableWidget.setItem(
                i, 3, qtw.QTableWidgetItem(str(self.df.loc[i]["answer"])))
            # if outlier, color red
            if self.df.loc[i]["Cluster Assignment"] == -1:
                for j in range(self.ui.tableWidget.columnCount()):
                    self.ui.tableWidget.item(i, j).setBackground(
                        qtg.QColor(232, 52, 39, 255))
        # resize
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(
            3, qtw.QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(
            2, qtw.QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget.resizeRowsToContents()  # do this AFTER stretching.
        # do this AFTER stretching.
        self.ui.tableWidget.resizeColumnsToContents()
        # unfuck the scrollbar
        self.ui.tableWidget.setVerticalScrollMode(
            qtw.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.ui.tableWidget.verticalScrollBar().setSingleStep(5)
        # self.ui.tableWidget()


if __name__ == "__main__":
    cursor = db.DatabaseHandler("database/testdb.db")
    app = qtw.QApplication([])
    t0 = datetime.utcnow()
    # ttt = ttt.TurnToTextinator()  # you think i'm funny?
    # please PLEASE don't make me have to use multithreading again PLEASE glove-wiki-gigaword-300
    ad = ad.AnomalyDetector(dh=cursor, modelName="")
    ad.SetDefaultParams()
    t1 = datetime.utcnow()
    print("duration : {}".format(t1-t0))
    menu_widget = MainMenuWindow()
    menu_widget.show()
    app.exec()  # the program loops here.
    cursor.cursor.close()  # gentle aftercare after rough use
