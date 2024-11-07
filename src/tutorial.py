# coding=windows-1251
from direct.gui.DirectGui import DirectFrame, DirectLabel
from panda3d.core import TextNode

class Tutorial:
    def __init__(self, base):
        self.base = base
        self.step = 0
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        # �������������� ������ ��� ������
        self.background = DirectFrame(
            frameColor=(0, 0, 0, 0.5),  # ������ ��� � 50% �������������
            frameSize=(-0.6, 0.6, -0.2, 0.2),
            pos=(0, 0, -0.8)
        )

        # ����� ��� ������ ����� ��������
        self.label = DirectLabel(
            text="",
            scale=0.05,
            pos=(0, 0, 0),
            text_font=self.text_font,
            text_fg=(1, 1, 1, 1),  # ����� �����
            frameColor=(1, 1, 1, 0),  # ���������� ��� ��� ������
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # ��������� ��������� �������
        self.skip_label = DirectLabel(
            text="������� Z, ����� ���������� ��������",
            scale=0.04,
            pos=(0, 0, -0.15),  # ������������� ���� ��������� ������
            text_font=self.text_font,
            text_fg=(0.8, 0.8, 0.8, 1),  # ������-����� �����
            frameColor=(1, 1, 1, 0),  # ���������� ���
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # ��������� ��������� ���������
        self.continue_label = DirectLabel(
            text="������� F, ����� ����������",
            scale=0.04,
            pos=(0, 0, -0.2),  # ������������� ���� ��������� ������ � ��������
            text_font=self.text_font,
            text_fg=(0.8, 0.8, 0.8, 1),  # ������-����� �����
            frameColor=(1, 1, 1, 0),  # ���������� ���
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # ������������ ������� ������� F
        self.base.accept('f', self.next_step)

        # ������������ ������� ������� Z
        self.base.accept('z', self.skip_tutorial)

        # ������ ������� ����
        self.show_step()

    def show_step(self):
        """���������� ������� ��� ��������."""
        steps = [
            "����������� W, A, S, D ��� ������������.",
            "����������� ���� ��� �������� ������.",
            "��������� � ����� � ������� ������ + ���.",
            "������� Shift, ����� ����������."
        ]

        if self.step < len(steps):
            self.label['text'] = steps[self.step]
        else:
            self.end_tutorial()

    def next_step(self):
        """��������� � ���������� ���� ��������."""
        self.step += 1
        self.show_step()

    def skip_tutorial(self):
        """���������� �������� � ��������� ���."""
        self.end_tutorial()

    def end_tutorial(self):
        """����������� �������� � ������� ����."""
        self.background.destroy()
        self.label.destroy()
        self.skip_label.destroy()
        self.continue_label.destroy()  # ������� ����� ����� � �����������

# ����� � �������� �����:
# tutorial = Tutorial(base)
