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
        self.music_manager = self.main.music_manager  # ������ �� �������� ������
        
        # �����
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        self.show_main_menu()
        self.settings_menu=None
    def show_main_menu(self):


        # ������� ����� ��� ��� ����
        self.create_background()

        # ������� ��� ��� ������ ����
        self.background_label = DirectLabel(
            text="������� ����", scale=0.1, pos=(0, 0, 0.5), 
            text_font=self.text_font, frameColor=(1, 1, 1, 0)
        )

        # ������ "������ ����" � "�����"
        self.start_button = DirectButton(
            text="������ ����", 
            scale=0.1, 
            pos=(0, 0, 0), 
            command=self.start_game, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)  
        )

        self.settings_button = DirectButton(
            text="���������", 
            scale=0.1, 
            pos=(0, 0, -0.2),  # ������� ���� ������ "������ ����"
            command=self.open_settings, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)  
        )

        self.exit_button = DirectButton(
            text="�����", 
            scale=0.1, 
            pos=(0, 0, -0.4),
            command=self.exit_game, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        # ������ ���� ������ ��� ���������
        self.buttons = [self.start_button, self.settings_button, self.exit_button]

         # ��������� ��������� ��������� ������
        self.current_button_index = 0
        self.update_button_colors()


        # ��������� ����������� ������� ������ ����� ������ main
        self.main.accept("arrow_up", self.move_up)
        self.main.accept("arrow_down", self.move_down)
        self.main.accept("enter", self.select_button)

         # ������������� ������ �������� ����
        self.music_manager.play_menu_music()

    def create_background(self):
        """������� ����� ��� ��� ����."""
        # ������� ����� ���
        self.background = DirectFrame(frameColor=(0.5, 0.5, 0.5, 1), 
                                      frameSize=(-1, 1, -1, 1))  # ��������� ���� �����

    def start_game(self):
         # ������������� ������ �������� ����
        self.music_manager.stop_track('Main Menu Music')

        """������� ��� �������� ���������� �������� ����, �������� ������ � �������� OSD."""
        self.background_label.destroy()
        self.start_button.destroy()
        self.settings_button.destroy()
        self.exit_button.destroy()  # ������� ������ ������
        self.background.destroy()    # ������� ����� ���
        self.main.disableMouse()      # �������� ������

        

        # �������� OSD � ��������� ������ ����
        self.main.osd.enabled = True
        self.music_manager.play_game_music()

        # ��������� ��������� �������
        self.tutorial_manager = Tutorial(self.main)  # ������� ������ ��������

    def open_settings(self):
        self.background_label.hide()
        self.background.hide()
        self.settings_button.hide()
        self.start_button.hide()
        self.exit_button.hide()
        
        self.settings_menu = SettingsMenu(self.main,self.show_main_menu)  # ��������� ���� ��������

    def exit_game(self):
        """��������� ����."""
        self.main.userExit()  # ���������� ����������

    def move_up(self):
        """����������� ����� �� �������."""
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # ��������������� ����� ������

    def move_down(self):
        """����������� ���� �� �������."""
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # ��������������� ����� ������

    def update_button_colors(self):
        """��������� ����� ������ � ����������� �� ������� ��������� ������."""
        for i, button in enumerate(self.buttons):
            if i == self.current_button_index:
                button['frameColor'] = (0.7, 0.7, 0.7, 1)  # ���� ��� ��������� ������
            else:
                button['frameColor'] = (0.5, 0.5, 0.5, 1)

    def select_button(self):
        """����� ������� ������."""
        selected_button = self.buttons[self.current_button_index]
        selected_button['command']()  # �������� ������� ������� ������
        self.music_manager.play_interface_confirm()  # ��������������� ����� �������������
