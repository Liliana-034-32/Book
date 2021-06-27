import sys
from PyQt5 import QtGui, QtWidgets, QtWebEngineWidgets, QtMultimedia, QtMultimediaWidgets
import sqlite3 as lite
from PyQt5 import uic, QtSql, QtCore
import re

global object_name
object_name = ''
player = QtMultimedia.QMediaPlayer()
player.setVolume(34)

class QCustomQWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.playlistLayout = QtWidgets.QHBoxLayout()

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.IDQLabel = QtWidgets.QLabel()
        self.textNameQLabel = QtWidgets.QLabel()
        self.textAuthorQLabel = QtWidgets.QLabel()
        self.MusicQLabel = QtWidgets.QLabel()

        self.edit_button = QtWidgets.QPushButton()
        self.edit_button.setIcon(QtGui.QIcon('edit_book.png'))
        self.edit_button.setIconSize(QtCore.QSize(35, 35))
        self.edit_button.setFlat(True)
        self.edit_button.setToolTip('Редактировать аудиозапись')
        self.edit_button.clicked.connect(self.editBook)
        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setIcon(QtGui.QIcon('delete_book.png'))
        self.delete_button.setIconSize(QtCore.QSize(35, 35))
        self.delete_button.setFlat(True)
        self.delete_button.setToolTip('Удалить аудиозапись')
        self.delete_button.clicked.connect(self.deleteBook)
        self.play_button = QtWidgets.QPushButton()
        self.play_button.setIcon(QtGui.QIcon("play_button.png"))
        self.play_button.setIconSize(QtCore.QSize(25, 25))
        self.play_button.setFlat(True)
        self.play_button.clicked.connect(self.playMusic)

        self.buttonLayout.addWidget(self.edit_button)
        self.buttonLayout.addWidget(self.delete_button)

        self.playlistLayout.addWidget(self.play_button)
        self.playlistLayout.setAlignment(QtCore.Qt.AlignLeft)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.textQVBoxLayout.addWidget(self.textNameQLabel)
        self.textQVBoxLayout.addWidget(self.textAuthorQLabel)
        self.textQVBoxLayout.addWidget(spacer)
        self.textQVBoxLayout.addLayout(self.playlistLayout)

        self.iconQLabel = QtWidgets.QLabel()
        self.mainLayout.addWidget(self.iconQLabel, 0)
        self.mainLayout.addLayout(self.textQVBoxLayout, 1)
        self.mainLayout.addLayout(self.buttonLayout, 0)

        self.setLayout(self.mainLayout)

    def playMusic(self):
        global object_name
        if self.play_button.objectName() != object_name:
            player.stop()
            self.loadMusic()
            player.play()
            print(self.play_button.objectName())
            object_name = self.play_button.objectName()
            print(self.play_button.objectName())
        else:
            if player.mediaStatus() == QtMultimedia.QMediaPlayer.NoMedia:
                print(self.play_button.objectName())
                self.loadMusic()
                player.play()
            elif player.state() == QtMultimedia.QMediaPlayer.PlayingState:
                print(self.play_button.objectName())
                player.pause()
            elif player.state() == QtMultimedia.QMediaPlayer.PausedState:
                print(self.play_button.objectName())
                player.play()

    def loadMusic(self):
        url = QtCore.QUrl.fromLocalFile(self.MusicQLabel.text())
        content = QtMultimedia.QMediaContent(url)
        player.setMedia(content)

    def editBook(self):
        self.id = self.IDQLabel.text()
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM music WHERE ID=?", (self.id))
        row = cursor.fetchone()
        ID, Name, Author, image_path, music_path = row
        inputDialog = Dialog()
        inputDialog.line_edit_name.setText(Name)
        inputDialog.line_edit_author.setText(Author)
        inputDialog.line_edit_load.setText(image_path)
        inputDialog.line_edit_music.setText(music_path)
        rez = inputDialog.exec()
        if not rez:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Диалог сброшен.')
            pass
        name = inputDialog.line_edit_name.text()
        name = normalize_name(name)
        author = inputDialog.line_edit_author.text()
        author = normalize_name(author)
        image_path = inputDialog.line_edit_load.text()
        music_path = inputDialog.line_edit_music.text()
        if not name or not author or not image_path or not music_path:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Заполните пожалуйста все поля.')
            return
        cursor.execute(
            "UPDATE music SET Name=?, Author=?, image_path=?, music_path=? WHERE ID=?;",
            (name, author, image_path, music_path, self.id))
        conn.commit()
        window.myQListWidget.clear()
        window.completer_list.clear()
        window.search_completer()
        window.paint()

    def deleteBook(self):
        id = self.IDQLabel.text()
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        dialog = QtWidgets.QMessageBox.question(self, 'Удаление книги', "Вы действительно хотите удалить эту книгу?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if dialog == QtWidgets.QMessageBox.Yes:
            cursor.execute("DELETE FROM music WHERE ID=?;", (id))
            conn.commit()
        window.myQListWidget.clear()
        window.completer_list.clear()
        window.search_completer()
        window.paint()

    def setID(self, text):
        self.IDQLabel.setText(text)

    def setMusic(self, text):
        self.MusicQLabel.setText(text)

    def setTextName(self, text):
        self.textNameQLabel.setText(text)

    def setTextAuthor(self, text):
        self.textAuthorQLabel.setText(text)

    def setIcon(self, image_path):
        self.iconQLabel.setPixmap(QtGui.QPixmap(image_path).scaled(150, 150))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        con = lite.connect('test.db')
        cursor = con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS music(
           ID INTEGER PRIMARY KEY, 
           Name TEXT, Author TEXT, image_path TEXT, music_path TEXT)
           ''')
        con.commit()
        tool_bar = self.addToolBar('Панель инструментов')
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('Главное меню')

        addAction = QtWidgets.QAction(QtGui.QIcon('add_book.png'), 'Добавить музыку', self)
        addAction.triggered.connect(self.addBook)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.search_line = QtWidgets.QLineEdit()
        self.search_line.setFixedSize(250, 20)
        self.search_line.setPlaceholderText('Поиск музыки')
        self.search_line.setStyleSheet("border: 2px solid #abcdef; border-radius: 8px")
        self.completer_list = []
        self.search_completer()

        search_button = QtWidgets.QPushButton()
        search_button.setIcon(QtGui.QIcon('search_book.png'))
        search_button.setFlat(True)
        search_button.clicked.connect(self.search)

        tool_bar.addAction(addAction)
        tool_bar.addWidget(spacer)
        tool_bar.addWidget(self.search_line)
        tool_bar.addWidget(search_button)

        file_menu.setIcon(QtGui.QIcon('menu.png'))
        newAct = QtWidgets.QAction('Библиотека', self)
        newAct1 = QtWidgets.QAction('Плейлист', self)
        file_menu.addAction(newAct)
        file_menu.addAction(newAct1)

        self.myQListWidget = QtWidgets.QListWidget(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle('Плейлист')
        self.resize(900, 600)
        self.paint()

    def search_completer(self):
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Author FROM music")
        for i in [item for item in cursor.fetchall()]:
            for a in i:
                if a in self.completer_list:
                    continue
                else:
                    self.completer_list += [a]
        completer = QtWidgets.QCompleter(self.completer_list)
        self.search_line.setCompleter(completer)

    def search(self):
        search = self.search_line.text()
        if search > '':
            self.myQListWidget.clear()
            conn = lite.connect("test.db")
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM music WHERE Name=? OR Author=?", (search, search,))
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                    ID, Name, Author, image_path, music_path = row
                    myQCustomQWidget = QCustomQWidget()
                    myQCustomQWidget.setID(str(ID))
                    myQCustomQWidget.setTextName(Name)
                    myQCustomQWidget.setTextAuthor(Author)
                    myQCustomQWidget.setIcon(image_path)
                    myQCustomQWidget.setMusic(music_path)
                    myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
                    myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                    self.myQListWidget.addItem(myQListWidgetItem)
                    self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
                    self.setCentralWidget(self.myQListWidget)
        else:
            self.myQListWidget.clear()
            self.paint()

    def addBook(self):
        inputDialog = Dialog()
        rez = inputDialog.exec()
        if not rez:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Диалог сброшен.')
            return
        name = inputDialog.line_edit_name.text()
        name = normalize_name(name)
        author = inputDialog.line_edit_author.text()
        author = normalize_name(author)
        image_path = inputDialog.line_edit_load.text()
        music_path = inputDialog.line_edit_music.text()
        music_path = normalize_name(music_path)
        if not name or not author or not image_path or not music_path:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Заполните пожалуйста все поля.')
            return
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO music(Name, Author, image_path, music_path) VALUES(?, ?, ?, ?)",
            (name, author, image_path, music_path))
        conn.commit()
        window.search_completer()
        window.myQListWidget.clear()
        window.paint()

    def paint(self):
        con = lite.connect('test.db')
        con.commit()
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM music")

            while True:
                row = cur.fetchone()
                if row is None:
                    break
                ID, Name, Author, image_path, music_path = row
                myQCustomQWidget = QCustomQWidget()
                myQCustomQWidget.setID(str(ID))
                myQCustomQWidget.setTextName(Name)
                myQCustomQWidget.setTextAuthor(Author)
                myQCustomQWidget.setIcon(image_path)
                myQCustomQWidget.setMusic(music_path)
                myQCustomQWidget.play_button.setObjectName(str(ID))

                myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
                myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                self.myQListWidget.addItem(myQListWidgetItem)
                self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
        self.setCentralWidget(self.myQListWidget)


class Dialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('edit.png'))
        self.setWindowTitle('Редактирование/добавление музыки')

        self.path = ''

        self.line_edit_name = QtWidgets.QLineEdit()
        self.line_edit_author = QtWidgets.QLineEdit()

        self.load_music = QtWidgets.QPushButton()
        self.load_music.clicked.connect(self.file_open_music)
        self.line_edit_music = QtWidgets.QLineEdit()
        self.load_music.setText('Загрузить аудиозапись')
        self.line_edit_music.setDisabled(True)

        self.load = QtWidgets.QPushButton()
        self.load.clicked.connect(self.file_open_image)
        self.line_edit_load = QtWidgets.QLineEdit()
        self.load.setText('Загрузить обложку альбома')
        self.line_edit_load.setDisabled(True)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Название трека:", self.line_edit_name)
        form_layout.addRow("Исполнитель:", self.line_edit_author)
        form_layout.addRow('Путь к аудиозаписи:', self.line_edit_music)
        form_layout.addWidget(self.load_music)
        form_layout.addRow('Путь к изображению:', self.line_edit_load)
        form_layout.addWidget(self.load)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def file_open_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть файл", "", "Изображения (*.png; *.jpg; *.jpeg)")
        self.line_edit_load.setText(path)

    def file_open_music(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть файл", "", "Аудиозаписи (*.wav; *.mp3; *.aac)")
        self.line_edit_music.setText(path)


def normalize_name(name):
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
