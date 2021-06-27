import sys
import os
from PyQt5 import QtGui, QtWidgets, QtWebEngineWidgets
import sqlite3 as lite
from PyQt5 import uic, QtSql, QtCore
import re
from PyQt5.QtWidgets import QFileDialog
#from music import MainWindow
from PyQt5.QtWidgets import QMessageBox
import music


class QCustomQWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(QCustomQWidget, self).__init__(parent)

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout = QtWidgets.QVBoxLayout()

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.IDQLabel = QtWidgets.QLabel()
        self.textNameQLabel = QtWidgets.QLabel()
        self.textAuthorQLabel = QtWidgets.QLabel()
        self.textGenreQLabel = QtWidgets.QLabel()
        self.textYearQLabel = QtWidgets.QLabel()
        self.textPublisherQLabel = QtWidgets.QLabel()
        self.textDescriptionQLabel = QtWidgets.QLabel()
        self.textDescriptionQLabel.setAlignment(QtCore.Qt.AlignJustify)
        self.textDescriptionQLabel.setWordWrap(True)

        self.edit_button = QtWidgets.QPushButton()
        self.edit_button.setIcon(QtGui.QIcon('edit_book.png'))
        self.edit_button.setIconSize(QtCore.QSize(30, 30))
        self.edit_button.setFlat(True)
        self.edit_button.clicked.connect(self.editBook)
        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setIcon(QtGui.QIcon('delete_book.png'))
        self.delete_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_button.setFlat(True)
        self.delete_button.clicked.connect(self.deleteBook)
        self.web_button = QtWidgets.QPushButton()
        self.web_button.setIcon(QtGui.QIcon('readonline_book.png'))
        self.web_button.setIconSize(QtCore.QSize(30, 30))
        self.web_button.setFlat(True)
        self.web_button.clicked.connect(self.web)

        self.buttonLayout.addWidget(self.edit_button)
        self.buttonLayout.addWidget(self.delete_button)
        self.buttonLayout.addWidget(self.web_button)
        self.buttonLayout.setContentsMargins(0, 0, 10, 120)

        self.textQVBoxLayout.addWidget(self.textNameQLabel)
        self.textQVBoxLayout.addWidget(self.textAuthorQLabel)
        self.textQVBoxLayout.addWidget(self.textGenreQLabel)
        self.textQVBoxLayout.addWidget(self.textYearQLabel)
        self.textQVBoxLayout.addWidget(self.textPublisherQLabel)
        self.textQVBoxLayout.addWidget(self.textDescriptionQLabel)

        self.iconQLabel = QtWidgets.QLabel()

        self.mainLayout.addWidget(self.IDQLabel, 0)
        self.mainLayout.addWidget(self.iconQLabel, 0)
        self.mainLayout.addLayout(self.textQVBoxLayout, 1)
        self.mainLayout.addLayout(self.buttonLayout, 0)

        self.setLayout(self.mainLayout)

    def web(self):
        self.id = self.IDQLabel.text()
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE ID=?", (self.id))
        row = cursor.fetchone()
        ID, Name, Author, Genre, Year, Publisher, Description, image_path, link = row
        self.view.load(QtCore.QUrl(link))
        self.view.show()

    def editBook(self):
        self.id = self.IDQLabel.text()
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE ID=?", (self.id))
        row = cursor.fetchone()
        ID, Name, Author, Genre, Year, Publisher, Description, image_path, link = row
        inputDialog = Dialog()
        inputDialog.line_edit_name.setText(Name)
        inputDialog.line_edit_author.setText(Author)
        inputDialog.line_edit_genre.setText(Genre)
        inputDialog.line_edit_year.setText(str(Year))
        inputDialog.line_edit_publisher.setText(Publisher)
        inputDialog.line_edit_description.setPlainText(Description)
        inputDialog.line_edit_load.setText(image_path)
        inputDialog.line_edit_link.setText(link)
        rez = inputDialog.exec()
        if not rez:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Диалог сброшен.')
            pass
        name = inputDialog.line_edit_name.text()
        name = normalize_name(name)
        author = inputDialog.line_edit_author.text()
        author = normalize_name(author)
        genre = inputDialog.line_edit_genre.text()
        genre = normalize_name(genre)
        year = inputDialog.line_edit_year.text()
        year = normalize_name(year)
        publisher = inputDialog.line_edit_publisher.text()
        publisher = normalize_name(publisher)
        description = inputDialog.line_edit_description.toPlainText()
        description = normalize_name(description)
        image_path = inputDialog.line_edit_load.text()
        link = inputDialog.line_edit_link.text()
        if not name or not author or not genre or not year or not publisher or not description or not image_path or not link:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Заполните пожалуйста все поля.')
            return
        cursor.execute(
            "UPDATE books SET Name=?, Author=?, Genre=?, Year=?, Publisher=?, Description=?, image_path=?, link=? WHERE ID=?;",
            (name, author, genre, year, publisher, description, image_path, link, self.id))
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
            cursor.execute("DELETE FROM books WHERE ID=?;", (id))
            conn.commit()
        window.myQListWidget.clear()
        window.completer_list.clear()
        window.search_completer()
        window.paint()

    def setID(self, text):
        self.IDQLabel.setText(text)

    def setTextName(self, text):
        self.textNameQLabel.setText(text)

    def setTextAuthor(self, text):
        self.textAuthorQLabel.setText(text)

    def setTextGenre(self, text):
        self.textGenreQLabel.setText(text)

    def setTextYear(self, text):
        self.textYearQLabel.setText(text)

    def setTextPublisher(self, text):
        self.textPublisherQLabel.setText(text)

    def setTextDescription(self, text):
        self.textDescriptionQLabel.setText(text)

    def setIcon(self, image_path):
        self.iconQLabel.setPixmap(QtGui.QPixmap(image_path).scaled(130, 200))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        con = lite.connect('test.db')
        cursor = con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books(
           ID INTEGER PRIMARY KEY, 
           Name TEXT, Author TEXT, Genre TEXT, 
           Year INT, Publisher TEXT,
           Description TEXT,  image_path TEXT, link TEXT)
           ''')
        con.commit()

        tool_bar = self.addToolBar('Панель инструментов')
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('Главное меню')

        addAction = QtWidgets.QAction(QtGui.QIcon('add_book.png'), 'Добавить книгу', self)
        addAction.triggered.connect(self.addBook)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.search_line = QtWidgets.QLineEdit()
        self.search_line.setFixedSize(250, 20)
        self.search_line.setPlaceholderText('Поиск книги')
        self.search_line.setStyleSheet("border: 2px solid gray; border-radius: 8px")
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
        file_menu.addAction('Библиотека', self.actionClicked)
        file_menu.addAction('Плейлист', self.actionClicked)


        self.myQListWidget = QtWidgets.QListWidget(self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle('Библиотека')
        self.resize(900, 600)
        self.paint()


    def actionClicked(self):
        action = self.sender()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(None,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
        print('открываем: ', action.text())

    def search_completer(self):
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Author FROM books")
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
                cursor.execute("SELECT * FROM books WHERE Name=? OR Author=?", (search, search,))
                while True:
                    row = cursor.fetchone()
                    if row is None:
                        break
                    ID, Name, Author, Genre, Year, Publisher, Description, image_path, link = row
                    myQCustomQWidget = QCustomQWidget()
                    myQCustomQWidget.setID(str(ID))
                    myQCustomQWidget.setTextName('<b>Название книги</b>:   ' + Name)
                    myQCustomQWidget.setTextAuthor('<b>Автор</b>:   ' + Author)
                    myQCustomQWidget.setTextGenre('<b>Жанр</b>:   ' + Genre)
                    myQCustomQWidget.setTextYear('<b>Год написания</b>:   ' + str(Year))
                    myQCustomQWidget.setTextPublisher('<b>Издательство</b>:   ' + Publisher)
                    myQCustomQWidget.setTextDescription('<b>Описание</b>:   ' + Description)
                    myQCustomQWidget.setIcon(image_path)
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
        genre = inputDialog.line_edit_genre.text()
        genre = normalize_name(genre)
        year = inputDialog.line_edit_year.text()
        year = normalize_name(year)
        publisher = inputDialog.line_edit_publisher.text()
        publisher = normalize_name(publisher)
        description = inputDialog.line_edit_description.toPlainText()
        description = normalize_name(description)
        image_path = inputDialog.line_edit_load.text()
        link = inputDialog.line_edit_link.text()
        link = normalize_name(link)
        if not name or not author or not year or not publisher or not description or not image_path or not genre or not link:
            QtWidgets.QMessageBox.information(self, 'Внимание', 'Заполните пожалуйста все поля.')
            return
        conn = lite.connect("test.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books(Name, Author, Genre, Year, Publisher, Description, image_path, link) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (name, author, genre, year, publisher, description, image_path, link))
        conn.commit()
        window.search_completer()
        window.myQListWidget.clear()
        window.paint()

    def paint(self):
        con = lite.connect('test.db')
        con.commit()
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM books")

            while True:
                row = cur.fetchone()
                if row is None:
                    break
                ID, Name, Author, Genre, Year, Publisher, Description, image_path, link = row
                myQCustomQWidget = QCustomQWidget()
                myQCustomQWidget.setID(str(ID))
                myQCustomQWidget.setTextName('<b>Название книги</b>:   ' + Name)
                myQCustomQWidget.setTextAuthor('<b>Автор</b>:   ' + Author)
                myQCustomQWidget.setTextGenre('<b>Жанр</b>:   ' + Genre)
                myQCustomQWidget.setTextYear('<b>Год написания</b>:   ' + str(Year))
                myQCustomQWidget.setTextPublisher('<b>Издательство</b>:   ' + Publisher)
                myQCustomQWidget.setTextDescription('<b>Описание</b>:   ' + Description)
                myQCustomQWidget.setIcon(image_path)
                myQListWidgetItem = QtWidgets.QListWidgetItem(self.myQListWidget)
                myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                self.myQListWidget.addItem(myQListWidgetItem)
                self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)
        self.setCentralWidget(self.myQListWidget)


class Dialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('edit.png'))
        self.setWindowTitle('Редактирование/добавление книги')

        self.path = ''

        self.line_edit_name = QtWidgets.QLineEdit()
        self.line_edit_author = QtWidgets.QLineEdit()
        self.line_edit_genre = QtWidgets.QLineEdit()
        completer = QtWidgets.QCompleter(genre_completer)
        self.line_edit_genre.setCompleter(completer)
        self.line_edit_year = QtWidgets.QLineEdit()
        self.line_edit_publisher = QtWidgets.QLineEdit()
        self.line_edit_description = QtWidgets.QPlainTextEdit()
        self.load = QtWidgets.QPushButton()
        self.line_edit_link = QtWidgets.QLineEdit()
        self.load.clicked.connect(self.file_open)
        self.line_edit_load = QtWidgets.QLineEdit()
        self.load.setText('Загрузить изображение')
        self.line_edit_load.setDisabled(True)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Название книги:', self.line_edit_name)
        form_layout.addRow('Автор:', self.line_edit_author)
        form_layout.addRow('Жанр:', self.line_edit_genre)
        form_layout.addRow('Год написания:', self.line_edit_year)
        form_layout.addRow('Издательство:', self.line_edit_publisher)
        form_layout.addRow('Описание:', self.line_edit_description)
        form_layout.addRow('Ссылка на книгу в Интернете:', self.line_edit_link)
        form_layout.addRow('Путь к изображению:', self.line_edit_load)
        form_layout.addWidget(self.load)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def file_open(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть файл", "", "Изображения (*.png; *.jpg; *.jpeg)")
        self.line_edit_load.setText(path)


def normalize_name(name):
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name


genre_completer = ['Проза', 'Современная проза', 'Классическая проза', 'Военная проза', 'Эпистолярная проза',
                   'Сентиментальная проза', 'Эпопея', 'Роман', 'Рассказ', 'Повесть', 'Эссе, очерк, этюд, набросок',
                   'Новелла', 'Магический реализм', 'Семейный роман, семейная сага', 'Контркультура',
                   'Антисоветская литература', 'Афоризмы', 'Феерия', 'Научная фантастика', 'Философская фантастика',
                   'Боевая фантастика', 'Ужасы', 'Юмористическая фантастика', 'Историческая фантастика',
                   'Альтернативная история', 'Стимпанк', 'Киберпанк', '«Тёмная» фантастика', 'Социальная фанстастика',
                   'Комическая фантастика', 'Любовная фантастика', 'Детско-юношеская фантастика',
                   'Героическая фантастика',
                   'Детективная фантастика', 'Эпическая фантастика', 'Постапокалипсис', 'Мистика', 'Попаданцы',
                   'Приключенческая фантастика', 'Космическая опера', 'Сказочная фантастика', 'Ненаучная фантастика',
                   'Ироническая фантастика', 'Готический роман', 'Мифологическая фантастика', 'Фантасмагория',
                   'Эротическая фантастика', 'Авантюрная фантастика', 'Фантастическая конспирология', 'Фэнтези',
                   'Юмористическое фэнтези', 'Городское фэнтези', 'Ироническое фэнтези', 'Историческое фэнтези',
                   'Технофэнтези', 'Эпическое фэнтези', 'Героическое фэнтези', 'Приключенческое фэнтези',
                   'Повседневное фэнтези', 'Короткие любовные романы', 'Современные любовные романы',
                   'Исторические любовные романы',
                   'Любовная фантастика', 'Романтика', 'Любовные детективы', 'Дамский детективный роман',
                   'Эротика', 'Детектив', 'Триллер', 'Классический детектив', 'Боевик',
                   'Полицейский детектив', 'Детские остросюжетные', 'Любовные детективы', 'Криминальный детектив',
                   'Исторический детектив', 'Иронический детектив', 'Шпионский детектив', 'Крутой детектив',
                   'Дамский детективный роман', 'Детективная фантастика', 'Политический детектив', 'Маньяки',
                   'Юридический триллер', 'Медицинский триллер', 'Техно триллер', 'Биографии и мемуары',
                   'Публицистика', 'Путешествия и география', 'Научно-популярная литература',
                   'Документальная литература',
                   'Природа и животные', 'Критика', 'Военная документалистика', 'Драматургия', 'Комедия',
                   'Драма', 'Трагедия', 'Киносценарии', 'Сценарии', 'Водевиль', 'Мистерия', 'Детская литература',
                   'Сказка', 'Детская проза', 'Детская фантастика', 'Детские остросюжетные', 'Детские стихи',
                   'Образовательная литература', 'Детские приключения', 'Книга-игра', 'Детский фольклор',
                   'Подростковая литература', 'Мифы', 'Легенды', 'Эпос', 'Античная литература',
                   'Древневосточная литература', 'Древнеевропейская литература', 'Древнерусская литература',
                   'Старинная литература']


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
