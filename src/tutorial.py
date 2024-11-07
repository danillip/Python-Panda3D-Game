# coding=windows-1251
from direct.gui.DirectGui import DirectFrame, DirectLabel
from panda3d.core import TextNode

class Tutorial:
    def __init__(self, base):
        self.base = base
        self.step = 0
        self.font_path = "data/UbuntuMono-R.ttf"
        self.text_font = loader.loadFont(self.font_path)

        # Полупрозрачное окошко для текста
        self.background = DirectFrame(
            frameColor=(0, 0, 0, 0.5),  # черный фон с 50% прозрачностью
            frameSize=(-0.6, 0.6, -0.2, 0.2),
            pos=(0, 0, -0.8)
        )

        # Текст для вывода шагов обучения
        self.label = DirectLabel(
            text="",
            scale=0.05,
            pos=(0, 0, 0),
            text_font=self.text_font,
            text_fg=(1, 1, 1, 1),  # белый текст
            frameColor=(1, 1, 1, 0),  # прозрачный фон для текста
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # Добавляем маленькую надпись
        self.skip_label = DirectLabel(
            text="Нажмите Z, чтобы пропустить обучение",
            scale=0.04,
            pos=(0, 0, -0.15),  # позиционируем ниже основного текста
            text_font=self.text_font,
            text_fg=(0.8, 0.8, 0.8, 1),  # светло-серый текст
            frameColor=(1, 1, 1, 0),  # прозрачный фон
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # Добавляем маленькую подсказку
        self.continue_label = DirectLabel(
            text="Нажмите F, чтобы продолжить",
            scale=0.04,
            pos=(0, 0, -0.2),  # позиционируем ниже основного текста и пропуска
            text_font=self.text_font,
            text_fg=(0.8, 0.8, 0.8, 1),  # светло-серый текст
            frameColor=(1, 1, 1, 0),  # прозрачный фон
            text_align=TextNode.ACenter,
            parent=self.background
        )

        # Отслеживание нажатия клавиши F
        self.base.accept('f', self.next_step)

        # Отслеживание нажатия клавиши Z
        self.base.accept('z', self.skip_tutorial)

        # Запуск первого шага
        self.show_step()

    def show_step(self):
        """Отображает текущий шаг обучения."""
        steps = [
            "Используйте W, A, S, D для передвижения.",
            "Используйте мышь для поворота камеры.",
            "Подойдите к стене и нажмите прыжок + ЛКМ.",
            "Нажмите Shift, чтобы ускориться."
        ]

        if self.step < len(steps):
            self.label['text'] = steps[self.step]
        else:
            self.end_tutorial()

    def next_step(self):
        """Переходит к следующему шагу обучения."""
        self.step += 1
        self.show_step()

    def skip_tutorial(self):
        """Пропускает обучение и завершает его."""
        self.end_tutorial()

    def end_tutorial(self):
        """Заканчивает обучение и убирает окно."""
        self.background.destroy()
        self.label.destroy()
        self.skip_label.destroy()
        self.continue_label.destroy()  # Удаляем также текст о продолжении

# Вызов в основном файле:
# tutorial = Tutorial(base)
