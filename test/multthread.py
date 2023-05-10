import sys
import time
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class frmMain(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.btStart = QPushButton('Start')
        self.btStop = QPushButton('Stop')
        #self.counter = QSpinBox()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.btStart)
        self.layout.addWidget(self.btStop)
        #self.layout.addWidget(self.counter)
        self.setLayout(self.layout)
        self.btStart.clicked.connect(self.start_thread)
        self.btStop.clicked.connect(self.stop_thread)
        self.boxes = []
        self.threads = []

    def stop_thread(self):
        for th in self.threads:
            th.terminate()

    def loopfunction(self, n, index):
        self.boxes[index].setValue(n)

    def start_thread(self):
        index = len(self.threads)
        th = thread(index)
        th.loop.connect(self.loopfunction)
        th.setTerminationEnabled(True)
        th.start()
        self.threads.append(th)        
        self.boxes.append(QSpinBox())
        self.layout.addWidget(self.boxes[index])        


class thread(QThread):
    loop = pyqtSignal(int, int)

    def __init__(self, index):
        QThread.__init__(self)
        self.index = index

    def run(self):
        for n in range(20):
            self.loop.emit(n, self.index)
            time.sleep(0.5)


app = QApplication([])
win = frmMain()

win.show()
sys.exit(app.exec())