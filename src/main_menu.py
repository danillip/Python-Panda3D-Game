#!/usr/bin/python
# coding=windows-1251
# main_menu.py

from direct.gui.DirectGui import DirectButton, DirectLabel, DirectFrame
from panda3d.core import Loader
from direct.showbase.ShowBase import ShowBase
from tutorial import Tutorial
from setting_menu import SettingsMenu

class MainMenu:
    def __init__(self, main):
        self.main = main
        self.music_manager = self.main.music_manager  # Ссылка на менеджер музыки
        
        # шрифт
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        self.show_main_menu()
        self.settings_menu=None
    def show_main_menu(self):


        # Создаем серый фон для меню
        self.create_background()

        # Создаем фон для текста меню
        self.background_label = DirectLabel(
            text="Главное Меню", scale=0.1, pos=(0, 0, 0.5), 
            text_font=self.text_font, frameColor=(1, 1, 1, 0)
        )

        # Кнопки "Начать игру" и "Выход"
        self.start_button = DirectButton(
            text="Начать игру", 
            scale=0.1, 
            pos=(0, 0, 0), 
            command=self.start_game, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)  
        )

        self.settings_button = DirectButton(
            text="Настройки", 
            scale=0.1, 
            pos=(0, 0, -0.2),  # Позиция ниже кнопки "Начать игру"
            command=self.open_settings, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)  
        )

        self.exit_button = DirectButton(
            text="Выход", 
            scale=0.1, 
            pos=(0, 0, -0.4),
            command=self.exit_game, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        # Список всех кнопок для навигации
        self.buttons = [self.start_button, self.settings_button, self.exit_button]

         # Установка начальной выбранной кнопки
        self.current_button_index = 0
        self.update_button_colors()


        # Назначаем обработчики нажатия клавиш через объект main
        self.main.accept("arrow_up", self.move_up)
        self.main.accept("arrow_down", self.move_down)
        self.main.accept("enter", self.select_button)

         # Воспроизводим музыку главного меню
        self.music_manager.play_menu_music()

    def create_background(self):
        """Создает серый фон для меню."""
        # Создаем серый фон
        self.background = DirectFrame(frameColor=(0.5, 0.5, 0.5, 1), 
                                      frameSize=(-1, 1, -1, 1))  # Заполняем весь экран

    def start_game(self):
         # Останавливаем музыку главного меню
        self.music_manager.stop_track('Main Menu Music')

        """Удаляет все элементы интерфейса главного меню, скрывает курсор и включает OSD."""
        self.background_label.destroy()
        self.start_button.destroy()
        self.settings_button.destroy()
        self.exit_button.destroy()  # Удаляем кнопку выхода
        self.background.destroy()    # Удаляем серый фон
        self.main.disableMouse()      # Скрываем курсор

        

        # Включаем OSD и запускаем музыку игры
        self.main.osd.enabled = True
        self.music_manager.play_game_music()

        # Запускаем обучающий контент
        self.tutorial_manager = Tutorial(self.main)  # Создаем объект обучения

    def open_settings(self):
        self.background_label.hide()
        self.background.hide()
        self.settings_button.hide()
        self.start_button.hide()
        self.exit_button.hide()
        
        self.settings_menu = SettingsMenu(self.main,self.show_main_menu)  # Открываем меню настроек

    def exit_game(self):
        """Закрывает игру."""
        self.main.userExit()  # Завершение приложения

    def move_up(self):
        """Перемещение вверх по кнопкам."""
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # Воспроизведение звука выбора

    def move_down(self):
        """Перемещение вниз по кнопкам."""
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # Воспроизведение звука выбора

    def update_button_colors(self):
        """Обновляет цвета кнопок в зависимости от текущей выбранной кнопки."""
        for i, button in enumerate(self.buttons):
            if i == self.current_button_index:
                button['frameColor'] = (0.7, 0.7, 0.7, 1)  # Цвет для выбранной кнопки
            else:
                button['frameColor'] = (0.5, 0.5, 0.5, 1)

    def select_button(self):
        """Выбор текущей кнопки."""
        selected_button = self.buttons[self.current_button_index]
        selected_button['command']()  # Вызываем команду текущей кнопки
        self.music_manager.play_interface_confirm()  # Воспроизведение звука подтверждения
