from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QVBoxLayout)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class CopyMoveGUI(QMainWindow):
    def __init__(self):
        super(CopyMoveGUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(600,800,800,600)
        self.setWindowTitle("Copy Move Detection")
        self.centerWindow()
        self.createAction()
        self.createMenuBar()

    def centerWindow(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def about(self):
        QMessageBox.about(self, "Tentang Tugas Akhir","<p>Hanif Sudira - 5113100184</p>""<p>Teknik Informatika ITS 2013</p>")

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath(), "Images (*.png *.jpg)")
        print fileName
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % fileName)
                return
            else:
                self.image.setPixmap(QPixmap(fileName))

    def createAction(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QAction("&Keluar", self, shortcut="Ctrl+Q", triggered=self.close)
        self.aboutAct = QAction("Tentang &Penulis", self, triggered=self.about)
        self.aboutActQt = QAction("Tentang &Qt", self,triggered=QApplication.instance().aboutQt)

    def createMenuBar(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QMenu('&Help', self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutActQt)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.helpMenu)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    CopyMove = CopyMoveGUI()
    CopyMove.show()
    sys.exit(app.exec_())