# coding=windows-1251
# music_manager.py

import sqlite3
from direct.showbase.Audio3DManager import Audio3DManager
from panda3d.core import AudioSound

class MusicManager:
    def __init__(self, base):
        self.base = base
        self.audio3d = Audio3DManager(base.sfxManagerList[0], base.camera)
        self.music_tracks = {}
        self.load_music()

        self.base.sfxManagerList[0].setVolume(0.0)

    def load_music(self):
        """Загружает все музыкальные треки и звуки из базы данных."""
        conn = sqlite3.connect('data/music.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, file_path, category FROM music')
        for row in cursor.fetchall():
            name, file_path, category = row
            sound = self.base.loader.loadSfx(file_path)
            self.music_tracks[name] = {'sound': sound, 'category': category}
        conn.close()

    def play_menu_music(self):
        """Воспроизводит музыку главного меню."""
        self.play_track('Main Menu Music')

    def play_game_music(self):
        """Воспроизводит музыку для игры."""
        self.play_track('Game Music')

    def play_interface_select(self):
        """Воспроизводит звук выбора в интерфейсе."""
        self.play_track('Interface Select Sound')

    def play_interface_confirm(self):
        """Воспроизводит звук подтверждения выбора в интерфейсе."""
        self.play_track('Interface Confirm Sound')

    def play_track(self, track_name):
        """Воспроизводит музыкальный трек или звук по имени."""
        if track_name in self.music_tracks:
            track = self.music_tracks[track_name]['sound']
            track.play()

    def stop_track(self, track_name):
        """Останавливает музыкальный трек по имени."""
        if track_name in self.music_tracks:
            track = self.music_tracks[track_name]['sound']
            track.stop()
