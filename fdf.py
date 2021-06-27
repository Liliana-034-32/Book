import os
import vlc  # version 3.0.10114
from PyQt5 import QtCore, QtGui, QtWidgets
from tkinter import Tk, filedialog  # 8.6
from time import sleep
from pygame import mixer  # version 1.9.6


class UiMainWindow:
    def __init__(self, main_window):
        self.main_window = main_window
        mixer.init()  # For the volume
        self.vlc_instance = vlc.Instance()
        media = self.vlc_instance.media_new('')
        self.player = self.vlc_instance.media_player_new()
        self.player.set_media(media)
        self.main_window.setStyleSheet('background-color: gray')
        self.main_window.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self.main_window)
        # Initiating the buttons and labels
        self.add_new_song_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_new_song_button.setGeometry(QtCore.QRect(690, 50, 80, 24))
        self.add_new_song_button.clicked.connect(self.add_song)
        self.time_slider = QtWidgets.QSlider(self.centralwidget)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(10000)
        self.time_slider.setValue(0)
        self.time_slider.setSingleStep(1)
        self.time_slider.setOrientation(QtCore.Qt.Horizontal)
        self.time_slider.sliderMoved.connect(self.slider_moved)
        # self.time_slider.valueChanged.connect(self.slider_changed)
        self.time_slider.setGeometry(QtCore.QRect(200, 80, 400, 20))
        # Initiating the lists and music
        self.ui_song_list = QtWidgets.QListWidget(self.centralwidget)
        self.ui_song_list.setGeometry(QtCore.QRect(10, 120, 780, 480))
        self.ui_song_list.setEnabled(True)
        self.ui_song_list.setStyleSheet('background-color: lightblue;')
        self.current_audio = ''  # To prevent errors when trying to play nothing
        self.audio_paths = {}
        self.ui_song_list.itemClicked.connect(self.play_song)
        self.retranslate_ui(self.main_window)
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

    def config_audio(self, audio=''):  # Changes the song of the player
        if not audio:
            media = self.vlc_instance.media_new(audio)
        else:
            media = self.vlc_instance.media_new(self.audio_paths[audio])
        self.player = self.vlc_instance.media_player_new()
        self.player.set_media(media)

    def play_song(self, song):  # This is called when a song is clicked
        self.current_audio = song.text()
        self.player.stop()
        self.config_audio(audio=self.current_audio)
        self.player.play()

    def add_song(self):
        Tk().withdraw()  # Creating the interface for choosing songs
        filetypes = [('mp3 files', '*.mp3'), ('wav files', '*.wav')]  # Only audio should pe added
        list_of_chosen_audio = filedialog.askopenfilenames(title='Choose audio files', filetypes=filetypes)
        for audio_path in list_of_chosen_audio:
            audio_name = audio_path[:-4].split('/')[-1]  # taking only the audio name without mp3 and audio_paths
            self.audio_paths[audio_name] = audio_path
            self.ui_song_list.addItem(audio_name)
        self.all_songs = self.ui_song_list.findItems('', QtCore.Qt.MatchContains)

    def slider_moved(self):
        try:
            self.player.set_position(self.time_slider.value()/10000)  # / 10000 because the slider didnt work if lowered the maximum value
        except Exception as e:
            print(e)

    def slider_changed(self):
        if self.player.is_playing():
            print(round(self.player.get_position()*10000, 2))
            self.time_slider.setValue(round(self.player.get_position()*10000, 2))
            self.player.set_position(self.time_slider.value()/10000)

    def retranslate_ui(self, main_window):  # Setting the text for all the buttons and labels
        main_window.setCentralWidget(self.centralwidget)
        main_window.setWindowTitle("MP3 Player")
        self.add_new_song_button.setText("Add Songs")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())