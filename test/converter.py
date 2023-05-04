from PyQt6.QtWidgets import QApplication, QMainWindow
import mainwindow

# construct ui Object
if hasattr(mainwindow, 'Ui_MainWindow'):
    ui = mainwindow.Ui_MainWindow()
else:
    ui = mainwindow.Ui_Form()

app = QApplication([])
win = QMainWindow()

# init and parent ui
ui.setupUi(win)

win.show()
app.exec()