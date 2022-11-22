import sys

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap

from ui import start_ui, guide_ui
from drum_machine import DrumMachine


# Начальное окно
class Start(QMainWindow, start_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_btn.clicked.connect(self.start)
        self.guide_btn.clicked.connect(self.show_guide)
        self.drum_machine = None
        self.guide = None

    def start(self):  # Открыть окно драм-машины
        self.drum_machine = DrumMachine(self)
        self.drum_machine.show()
        self.close()

    def show_guide(self):  # Открыть справку
        self.guide = Guide(self)
        self.guide.show()
        self.close()


# Окно справки
class Guide(QMainWindow, guide_ui.Ui_MainWindow):
    def __init__(self, start):
        super().__init__()
        self.setupUi(self)
        self.start = start
        self.back_btn.clicked.connect(self.back)
        self.forward_btn.clicked.connect(self.forward)
        self.set_guide('ui/drum_machine_guide.png')

    # Возможность вернуться к начальному окну как при нажатии специальной кнопки, так и при закрытии текущего окна
    def back(self):
        if self.forward_btn.isHidden():
            self.forward_btn.show()
            self.set_guide('ui/drum_machine_guide.png')
        else:
            self.start.show()
            self.close()

    def forward(self):
        self.forward_btn.hide()
        self.set_guide('ui/manage_guide.png')

    def set_guide(self, filename):
        guide = Image.open(filename)
        self.a = ImageQt(guide)
        self.pixmap = QPixmap.fromImage(self.a)
        self.guide.setPixmap(self.pixmap)

    def closeEvent(self, event):
        self.start.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec())
