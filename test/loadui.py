from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

app = QApplication([])

window = uic.loadUi("Mainwindow.ui") # this speeds things up.
window.show()

app.exec()