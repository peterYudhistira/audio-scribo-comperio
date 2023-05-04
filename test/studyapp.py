from PyQt6 import (
    QtWidgets as qtw,
    QtGui as qtg,
    QtCore as qtc
)

class SearchWidget(qtw.QWidget):

    submitted = qtc.pyqtSignal(str, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(qtw.QFormLayout())
        self.term_input = qtw.QLineEdit()
        self.case_checkbox = qtw.QCheckBox('Match case')
        self.submit_button = qtw.QPushButton(
            'Submit',
            clicked=self.on_submit
        )

        self.layout().addRow('Search', self.term_input)
        self.layout().addRow(self.case_checkbox)
        self.layout().addRow('', self.submit_button)

    def on_submit(self):
        term = self.term_input.text()
        do_case = (
            self.case_checkbox.checkState() == qtc.Qt.Checked
        )
        self.submitted.emit(term, do_case)

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # main UI code

        # set a central widget first
        self.textEdit = qtw.QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.show()

        # top menu bar (if needed)
        menubar = self.menuBar()
        menu_file = menubar.addMenu('File')
        menu_file.addAction("New")
        menu_file.addAction("Open", self.menu_Open)
        menu_file.addAction("Save")
        menu_file.addSeparator()
        menu_file.addAction("Boogie", self.menu_startBoogie)
        menu_file.addSeparator()
        menu_file.addAction("Quit", self.close)

        # toolbar (if needed)
        toolbar_edit = self.addToolBar("Edit")
        toolbar_edit.addAction("Copy", self.textEdit.copy)
        toolbar_edit.addAction("Paste", self.textEdit.paste)
        toolbar_edit.addAction("Undo", self.textEdit.undo)
        toolbar_edit.addAction("Redo", self.textEdit.redo)

        # dock widget (if necessary)
        search_dock = qtw.QDockWidget("search")
        search_widget = SearchWidget()
        search_dock.setWidget(search_widget)
        self.addDockWidget()



    def menu_startBoogie(self):
        print("is time to boogie")
    
    def menu_New(self):
        pass

    def menu_Open(self):
        filename, _ = qtw.QFileDialog.getOpenFileName()
        if filename:
            with open(filename, 'r', encoding="utf-8") as handle:
                text = handle.read()
                print(text)
            self.textEdit.clear()
            self.textEdit.insertPlainText(text)
            self.textEdit.moveCursor(qtg.QTextCursor.MoveOperation.Start)
            self.statusBar().showMessage("Now editing {}".format(filename))

    def menu_Save(self):
        pass
        

if __name__ == "__main__":
    app = qtw.QApplication([])
    mw = MainWindow()
    app.exec()