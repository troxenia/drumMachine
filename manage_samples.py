import sqlite3

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from ui.manage_ui import Ui_MainWindow


# управление экземплярами драм-машины
class Manage(QMainWindow, Ui_MainWindow):
    def __init__(self, drums):
        super().__init__()
        self.setupUi(self)
        self.drums = drums
        self.con = sqlite3.connect('samples.sqlite')
        self.add_btn.clicked.connect(self.add)
        self.save_btn.clicked.connect(self.save)
        self.delete_btn.clicked.connect(self.delete)
        self.display_data()

    def display_data(self):
        data = self.con.cursor().execute('SELECT * FROM samples').fetchall()
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        for i, row in enumerate(data):
            self.table.setRowCount(
                self.table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.table.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.table.resizeColumnsToContents()

    def add(self):  # Добавить экземпляр
        self.table.setRowCount(self.table.rowCount() + 1)

    def delete(self):  # Удалить запись об экземпляре
        self.table.removeRow(self.table.currentRow())

    def save(self):  # Сохранить изменения в базу данных
        self.con.cursor().execute('DELETE FROM samples')
        self.drums.clear()
        for row in range(self.table.rowCount()):
            items = []
            for col in range(self.table.columnCount()):
                if self.table.item(row, col):
                    item = (self.table.item(row, col).text() if self.table.item(row, col).text() else
                            'samples/drum_set.jpg' if col == 2 else 'samples/clave.wav' if col == 1 else 'My Drum')
                else:
                    item = 'samples/drum_set.jpg' if col == 2 else 'samples/clave.wav' if col == 1 else 'My Drum'
                items.append(item)
            self.con.cursor().execute(f'INSERT INTO samples VALUES {tuple(items)}')
        self.con.commit()
        res = self.con.cursor().execute('SELECT title FROM samples').fetchall()
        self.drums.addItems([x[0] for x in res])
        self.display_data()

    def closeEvent(self, event):
        self.con.close()
