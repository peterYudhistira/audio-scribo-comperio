import sys
import wave

import pyaudio as pa
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import *


class RecordingThread(QThread):
    stopped = False
    sig_started = pyqtSignal()
    sig_stopped = pyqtSignal()

    def __init__(self, target_file):
        self.target_file = target_file
        super().__init__()

    def run(self) -> None:
        
        print("rt.run()")
        audio = pa.PyAudio()
        frames = []
        stream = audio.open(format=pa.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        self.stopped = False
        self.sig_started.emit("bruhlord")
        while not self.stopped:
            data = stream.read(1024)
            frames.append(data)
        stream.close()
        
        print("you tryna be on worldstar???")
        wf = wave.open(self.target_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pa.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        self.sig_stopped.emit()

    @pyqtSlot()
    def stop(self):
        print("we slotting and ending")
        self.stopped = True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rec Audio")

        # Create recording thread and attach slots to its signals
        self.recording_thread = RecordingThread(target_file='test_recording.wav')
        self.recording_thread.sig_started.connect(self.recording_started)
        self.recording_thread.sig_stopped.connect(self.recording_stopped)

        vbox = QVBoxLayout()

        self.labelRec = QLabel('')
        self.labelRec.setFixedSize(130, 15)

        hbox = QHBoxLayout()
        self.recbtn = QPushButton('▶ record')
        self.recbtn.setFixedSize(90, 30)
        # Connect signal "recbtn.clicked" to the slot "recording_thread.start" of our QThread
        # Never connect directly to the run, always to start!
        self.recbtn.clicked.connect(self.recording_thread.start)

        self.stopbtn = QPushButton('▪')
        self.stopbtn.setDisabled(True)
        self.stopbtn.setFixedSize(40, 30)
        # Connect signal "stopbtn.clicked" to the slot "recording_thread.stop" of our QThread
        self.stopbtn.clicked.connect(self.recording_thread.stop)

        hbox.addWidget(self.recbtn)
        hbox.addWidget(self.stopbtn)

        vbox.addWidget(self.labelRec)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    @pyqtSlot(str)
    def recording_started(self):
        """This slot is called when recording starts"""
        print("recording_started entered")
        self.labelRec.setText('◉ recording...')
        self.stopbtn.setDisabled(False)
        self.recbtn.setDisabled(True)

    @pyqtSlot()
    def recording_stopped(self):
        """This slot is called when recording stops"""
        print("we ending!!")
        self.labelRec.setText('recording stopped')
        self.recbtn.setDisabled(False)
        self.stopbtn.setDisabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec()
