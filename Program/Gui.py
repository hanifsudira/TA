from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class CopyMoveGUI(QMainWindow):
    def __init__(self):
        super(CopyMoveGUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(1000,1000,1000,800)
        self.setWindowTitle("Copy Move Detection")
        self.centerWindow()
        self.createAction()
        self.createMenuBar()

        self.widget = QWidget()
        #hbox = QHBoxLayout(self)
        #topleft = QFrame()
        #topleft.setFrameShape(QFrame.StyledPanel)
        #bottom = QFrame()
        #bottom.setFrameShape(QFrame.StyledPanel)

        #splitter1 = QSplitter(Qt.Horizontal)
        #splitter1.addWidget(topleft)
        #splitter1.addWidget(bottom)

        #splitter1.setCollapsible(0,False)

        #splitter2 = QSplitter(Qt.Horizontal)
        #splitter2.addWidget(splitter1)
        #splitter2.addWidget(bottom)
        #hbox.addWidget(splitter1)
        #QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        layout = QVBoxLayout()
        label = QLabel()
        layout.addWidget(label)
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

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