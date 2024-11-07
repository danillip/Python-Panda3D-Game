#!/usr/bin/python
# coding=windows-1251

# settings_menu.py
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel


class SettingsMenu:
    def __init__(self, main, show_main_menu):
        self.main = main
        self.music_manager = self.main.music_manager  # ������ �� �������� ������
        
        self.show_main_menu=show_main_menu

        # ������������� �����
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        # ������� ����� ��� ��� ����
        self.create_background()

        # ������� ��� ��� ������ ����
        self.background_label = DirectLabel(
            text="���������", scale=0.1, pos=(0, 0, 0.8), 
            text_font=self.text_font, frameColor=(1, 1, 1, 0)
        )

          # ������ "�����"
        self.back_button = DirectButton(
            text="�����", 
            scale=0.1, 
            pos=(0, 0, 0.5), 
            command=self.close_settings, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

       # ������ ��� ���������� ���������
        self.increase_volume_button = DirectButton(
            text="��������� ���������", 
            scale=0.1, 
            pos=(0, 0, 0.3), 
            command=self.increase_volume, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        # ������ ��� ���������� ���������
        self.decrease_volume_button = DirectButton(
            text="��������� ���������", 
            scale=0.1, 
            pos=(0, 0, 0.2), 
            command=self.decrease_volume, 
            text_font=self.text_font,  
            frameColor=(0.5, 0.5, 0.5, 1)
        )

        self.volume_display = DirectLabel(
            text=f"���������: {self.main.music_manager.base.sfxManagerList[0].getVolume():.2f}", 
            scale=0.05,
            pos=(0, 0, 0.4), 
            text_font=self.text_font, 
            frameColor=(1, 1, 1, 0)
        )



         # ������ ���� ������ ��� ���������
        self.buttons2 = [ self.back_button,  self.increase_volume_button, self.decrease_volume_button ]

         # ��������� ��������� ��������� ������
        self.current_button_index = 0
        self.update_button_colors()
        
        # ��������� ����������� ������� ������ ����� ������ main
        self.main.accept("arrow_up", self.move_up)
        self.main.accept("arrow_down", self.move_down)
        self.main.accept("enter", self.select_button)
        
    def create_background(self):
        """������� ����� ��� ��� ����."""
        # ������� ����� ���
        self.background = DirectFrame(frameColor=(0.5, 0.5, 0.5, 1), 
                                      frameSize=(-1, 1, -1, 1))  # ��������� ���� �����

    def increase_volume(self):
        """����������� ��������� �� 10%."""
        current_volume = self.main.music_manager.base.sfxManagerList[0].getVolume()
        new_volume = min(current_volume + 0.05, 1.0)  # ������������ �������� 1.0
        self.set_volume(new_volume)

    def decrease_volume(self):
        """��������� ��������� �� 10%."""
        current_volume = self.main.music_manager.base.sfxManagerList[0].getVolume()
        new_volume = max(current_volume - 0.05, 0.0)  # ������������ ������� 0.0
        self.set_volume(new_volume)

    def set_volume(self, volume):
        """������������� ��������� ������."""
        self.main.music_manager.base.sfxManagerList[0].setVolume(volume)
        self.volume_display['text'] = f"���������: {volume:.2f}"

    def move_up(self):
        """����������� ����� �� �������."""
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons2)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # ��������������� ����� ������

    def move_down(self):
        """����������� ���� �� �������."""
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons2)
        self.update_button_colors()
        self.music_manager.play_interface_select()  # ��������������� ����� ������

    def update_button_colors(self):
        """��������� ����� ������ � ����������� �� ������� ��������� ������."""
        for i, button in enumerate(self.buttons2):
            if i == self.current_button_index:
                button['frameColor'] = (0.7, 0.7, 0.7, 1)  # ���� ��� ��������� ������
            else:
                button['frameColor'] = (0.5, 0.5, 0.5, 1)

    def select_button(self):
        """����� ������� ������."""
        selected_button = self.buttons2[self.current_button_index]
        selected_button['command']()  # �������� ������� ������� ������
        self.music_manager.play_interface_confirm()  # ��������������� ����� �������������

    def close_settings(self):
        """��������� ���� �������� � ���������� � ������� ����."""
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
       

   
   

