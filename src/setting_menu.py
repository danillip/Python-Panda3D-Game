#!/usr/bin/python
# coding=windows-1251

# settings_menu.py
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel


class SettingsMenu:
    def __init__(self, main, show_main_menu):
        self.main = main
        self.music_manager = self.main.music_manager  # Ссылка на менеджер музыки
        
        self.show_main_menu=show_main_menu

        # Устанавливаем шрифт
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        # Создаем серый фон для меню
        self.create_background()

        # Создаем фон для текста меню
        self.background_label = DirectLabel(
            text="Настройки", scale=0.1, pos=(0, 0, 0.8), 
            text_font=self.text_font, frameColor=(1, 1, 1, 0)
        )

          # Кнопка "Назад"
        self.back_button = DirectButton(
            text="Назад", 
            scale=0.1, 
            pos=(0, 0, 0.5), 
            command=self.close_settings, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

       # Кнопка для увеличения громкости
        self.increase_volume_button = DirectButton(
            text="Увеличить громкость", 
            scale=0.1, 
            pos=(0, 0, 0.3), 
            command=self.increase_volume, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        # Кнопка для уменьшения громкости
        self.decrease_volume_button = DirectButton(
            text="Уменьшить громкость", 
            scale=0.1, 
            pos=(0, 0, 0.2), 
            command=self.decrease_volume, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        self.volume_display = DirectLabel(
            text=f"Громкость: {self.main.music_manager.base.sfxManagerList[0].getVolume():.2f}", 
            scale=0.05,
            pos=(0, 0, 0.4), 
            text_font=self.text_font, 
            frameColor=(1, 1, 1, 0)
        )



         # Список всех кнопок для навигации
        self.buttons2 = [ self.back_button,  self.increase_volume_button, self.decrease_volume_button ]

         # Установка начальной выбранной кнопки
        self.current_button_index = 0
        self.update_button_colors()
        
        # Назначаем обработчики нажатия клавиш через объект main
        self.main.accept("arrow_up", self.move_up)
        self.main.accept("arrow_down", self.move_down)
        self.main.accept("enter", self.select_button)
        
    def create_background(self):
        """Создает серый фон для меню."""
        # Создаем серый фон
        self.background = DirectFrame(frameColor=(0.5, 0.5, 0.5, 1), 
                                      frameSize=(-1, 1, -1, 1))  # Заполняем весь экран

    def increase_volume(self):
        """Увеличивает громкость на 10%."""
        current_volume = self.main.music_manager.base.sfxManagerList[0].getVolume()
        new_volume = min(current_volume + 0.05, 1.0)  # ограничиваем максимум 1.0
        self.set_volume(new_volume)

    def decrease_volume(self):
        """Уменьшает громкость на 10%."""
        current_volume = self.main.music_manager.base.sfxManagerList[0].getVolume()
        new_volume = max(current_volume - 0.05, 0.0)  # ограничиваем минимум 0.0
        self.set_volume(new_volume)

    def set_volume(self, volume):
        """Устанавливает громкость музыки."""
        self.main.music_manager.base.sfxManagerList[0].setVolume(volume)
        self.volume_display['text'] = f"Громкость: {volume:.2f}"

    def move_up(self):
        """Перемещение вверх по кнопкам."""
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons2)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # Воспроизведение звука выбора

    def move_down(self):
        """Перемещение вниз по кнопкам."""
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons2)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # Воспроизведение звука выбора

    def update_button_colors(self):
        """Обновляет цвета кнопок в зависимости от текущей выбранной кнопки."""
        for i, button in enumerate(self.buttons2):
            if i == self.current_button_index:
                button['frameColor'] = (0.7, 0.7, 0.7, 1)  # Цвет для выбранной кнопки
            else:
                button['frameColor'] = (0.5, 0.5, 0.5, 1)

    def select_button(self):
        """Выбор текущей кнопки."""
        selected_button = self.buttons2[self.current_button_index]
        selected_button['command']()  # Вызываем команду текущей кнопки
        self.music_manager.play_interface_confirm()  # Воспроизведение звука подтверждения

    def close_settings(self):
        """Закрывает меню настроек и возвращает в главное меню."""
        self.main.ignore("arrow_up")
        self.main.ignore("arrow_down")
        self.main.ignore("enter")
        self.background_label.destroy()
        self.back_button.destroy()
        self.increase_volume_button.destroy()
        self.decrease_volume_button.destroy()
        self.volume_display.destroy()
        self.background.destroy()

        self.show_main_menu()
       

   
   

