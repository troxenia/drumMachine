import sqlite3

from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QHBoxLayout
from PyQt5.QtCore import QUrl
from ui.drum_machine_ui import Ui_MainWindow
from track import Track, clear_file
from manage_samples import Manage


class DrumMachine(QMainWindow, Ui_MainWindow):
    def __init__(self, start):
        super().__init__()
        self.setupUi(self)
        self.start = start  # Чтобы вернуться к начальному окну после закрытия текущего
        self.manage_samples = None  # Чтобы открыть окно управления экземплярами драм-машины
        self.current = None
        self.track = Track()
        self.player = QMediaPlayer(self)
        self.con = sqlite3.connect('samples.sqlite')

        drums = self.con.cursor().execute('SELECT title FROM samples').fetchall()
        self.drums.addItems([drum[0] for drum in drums])

        # Подключение сигналов и функций
        self.save_btn.clicked.connect(self.save)
        self.discard_btn.clicked.connect(self.discard)
        self.upload_btn.clicked.connect(self.upload)
        self.close_btn.clicked.connect(self.close_file)
        self.play_btn.clicked.connect(self.play)
        self.add_btn.clicked.connect(self.add)
        self.manage_btn.clicked.connect(self.manage)
        self.progress.sliderMoved.connect(self.set_position)
        self.length.editingFinished.connect(self.check_length)
        self.player.positionChanged.connect(self.position_changed)
        self.player.mediaStatusChanged.connect(self.status_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.setNotifyInterval(200)

        self.track_name.hide()
        self.close_btn.hide()

    def save(self):  # Сохранить полученный трек
        self.statusbar.showMessage('')
        filename = QFileDialog.getSaveFileName(self, 'Сохранить трек', '', 'Треки (*.wav)')[0]
        track_files = self.get_track_files()
        try:
            files = self.con.cursor().execute('SELECT track FROM samples').fetchall()
            self.track.set_files(*(file[0] for file in files))
            self.track.make_track(filename, self.speed.value(), float(self.length.text()), self.volume.value(),
                                  *track_files)
        except FileNotFoundError:
            self.statusbar.showMessage('Проверьте существование файлов экземпляров драм-машины')

    def upload(self):  # Загрузить файл трека для наложения на него битов
        self.statusbar.showMessage('')
        filename = QFileDialog.getOpenFileName(self, 'Выбрать трек', '', 'Треки (*.wav)')[0]
        if filename:
            self.track_name.setText(filename.split('/')[-1])
            self.track_name.show()
            self.close_btn.show()
            speed, length = self.track.set_track(filename)
            self.speed.setValue(speed // 41000 * 100)
            self.length.setText(str(length))

    def close_file(self):  # Убрать файл для наложения
        self.statusbar.showMessage('')
        self.track_name.setText('')
        self.track_name.hide()
        self.close_btn.hide()
        self.track.set_track(None)

    def discard(self):  # Очистить все отмеченные биты
        self.statusbar.showMessage('')
        for i in range(self.beat_layout.count()):
            beats = self.beat_layout.itemAt(i).layout()
            for j in range(beats.count()):
                beat = beats.itemAt(j).widget()
                beat.setStyleSheet('background-color: #ffffff')

    def play(self):  # Воспроизвести полученный трек
        self.statusbar.showMessage('')
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_btn.setText('►')
        elif self.get_track_files():
            try:
                if self.current != [self.speed.value(), float(self.length.text()), self.volume.value(),
                                    self.get_track_files(), self.track.track_overlay]:
                    self.player.setMedia(QMediaContent())
                    self.current = [self.speed.value(), float(self.length.text()), self.volume.value(),
                                    self.get_track_files(), self.track.track_overlay]
                    files = self.con.cursor().execute('SELECT track FROM samples').fetchall()
                    self.track.set_files(*(file[0] for file in files))
                    self.track.make_track('temp.wav',
                                          *self.current[:3], *self.current[3])
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile('temp.wav')))
                self.player.play()
                self.play_btn.setText('▋▋')
            except FileNotFoundError:
                self.statusbar.showMessage('Проверьте существование файлов экземпляров драм-машины')

    def status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_btn.setText('►')
            self.progress.setValue(0)

    def duration_changed(self, duration):
        self.progress.setRange(0, duration)

    def position_changed(self, position):
        self.progress.setValue(position)

    def set_position(self, position):
        self.player.setPosition(position)

    def check_length(self):  # Длительность трека принимает только числовые значения
        self.statusbar.showMessage('')
        try:
            float(self.length.text())
        except ValueError:
            self.length.setText('10')

    def get_track_files(self):  # Получить соответствующую отмеченным битам последовательность файлов
        track_files = []
        for i in range(self.beat_layout.count()):
            beats = self.beat_layout.itemAt(i).layout()
            track_files.append([])
            for j in range(beats.count()):
                beat = beats.itemAt(j).widget()
                if beat.palette().button().color().name() == '#000000':
                    res = self.con.cursor().execute(f'SELECT track FROM samples WHERE title = '
                                                    f'"{self.drum_layout.itemAt(i).widget().text()}"').fetchone()[0]
                else:
                    res = ''
                track_files[i].append(res)
        return track_files

    def manage(self):  # открыть окно управления экземплярами драм-машины
        self.statusbar.showMessage('')
        self.manage_samples = Manage(self.drums)
        self.manage_samples.show()

    def add(self):  # добавить дорожку битов
        self.statusbar.showMessage('')
        res = self.con.cursor().execute(f'SELECT title, image FROM samples '
                                        f'WHERE title = "{self.drums.currentText()}"').fetchone()
        drum = QPushButton(res[0])
        drum.setIcon(QIcon(res[1]))
        drum.clicked.connect(self.remove_drum)
        self.drum_layout.addWidget(drum)
        beats = QHBoxLayout()
        for j in range(self.num.value()):
            beat = QPushButton('')
            beat.setStyleSheet('background-color: #ffffff')
            beat.clicked.connect(self.set_beat)
            beats.addWidget(beat)
        self.beat_layout.addLayout(beats)

    def set_beat(self):  # пометить желаемый бит для дальнейшего проигрывания
        self.statusbar.showMessage('')
        if self.sender().palette().button().color().name() == '#ffffff':
            self.sender().setStyleSheet('background-color: #000000')
        else:
            self.sender().setStyleSheet('background-color: #ffffff')

    def remove_drum(self):  # убрать дорожку битов
        self.statusbar.showMessage('')
        for i in range(self.drum_layout.count()):
            if self.drum_layout.itemAt(i).widget() == self.sender():
                self.sender().setParent(None)
                beats = self.beat_layout.itemAt(i).layout()
                for j in range(beats.count() - 1, -1, -1):
                    beats.itemAt(j).widget().setParent(None)
                beats.setParent(None)
                break

    def closeEvent(self, event):
        self.con.close()
        if self.manage_samples:
            self.manage_samples.close()
        self.player.setMedia(QMediaContent())
        clear_file('temp.wav')
        self.start.show()
