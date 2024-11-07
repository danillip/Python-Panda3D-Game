#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from panda3d.core import (
    InputDevice,
    GamepadButton,
    KeyboardButton,
    MouseButton)


class InputMapping(object):
    """Контейнерный класс для хранения отображения строкового действия на
    оси или кнопке. Можно расширить его дополнительными методами для загрузки
    сопоставления по умолчанию из файла конфигурации. """
    # Определитель всех возможных действий.
    actions = (
        # Движения, связанные с клавиатурой и другими кнопками
        "forward",
        "backward",
        "left",
        "right",
        # Действия, связанные с движением аналогового стика/оси
        "axis-left-x",
        "axis-left-y",
        # Действия при движении камеры Кнопки
        "camera-up",
        "camera-down",
        "camera-left",
        "camera-right",
        # Действия при движении камеры Аналоговый стик/ось
        "axis-right-x",
        "axis-right-y",
        # Другие кнопки, связанные
        "jump",
        "intel-action",
        "action1",
        "sprint",
        "walk",
        "crouch",
        "crawl",
        "center-camera",
        # Калибровка
        "recalibrate"
    )

    def __init__(self):
        self.__map = dict.fromkeys(self.actions)

    def setDefaultMappingKeyboardAndMouse(self):
        # Сопоставление по умолчанию для использования клавиатуры и мыши
        self.mapButton("forward", KeyboardButton.asciiKey(b"w"))
        self.mapButton("backward", KeyboardButton.asciiKey(b"s"))
        self.mapButton("left", KeyboardButton.asciiKey(b"a"))
        self.mapButton("right", KeyboardButton.asciiKey(b"d"))
        self.mapButton("camera-up", KeyboardButton.page_up())
        self.mapButton("camera-down", KeyboardButton.end())
        self.mapButton("camera-left", KeyboardButton._del())
        self.mapButton("camera-right",KeyboardButton.page_down())
        self.mapButton("jump", KeyboardButton.space())
        self.mapButton("intel-action", MouseButton.one())
        self.mapButton("action1", MouseButton.one())
        self.mapButton("sprint", KeyboardButton.shift())
        self.mapButton("walk", KeyboardButton.control())
        self.mapButton("crouch", KeyboardButton.asciiKey(b"c"))
        self.mapButton("crawl", KeyboardButton.asciiKey(b"x"))
        self.mapButton("center-camera", KeyboardButton.home())

    def setDefaultMappingGamepadWiiRemote(self):
        # арты по умолчанию для пультов Wii
        self.mapAxis("axis-left-x", InputDevice.Axis.left_x)
        self.mapAxis("axis-left-y", InputDevice.Axis.left_y)
        self.mapAxis("axis-right-x", InputDevice.Axis.right_x)
        self.mapAxis("axis-right-y", InputDevice.Axis.right_y)
        self.mapButton("camera-up", GamepadButton.arrow_up())
        self.mapButton("camera-down", GamepadButton.arrow_down())
        self.mapButton("camera-left", GamepadButton.arrow_left())
        self.mapButton("camera-right",GamepadButton.arrow_right())
        self.mapButton("jump", GamepadButton.face_a())
        self.mapButton("intel-action", GamepadButton.face_b())
        self.mapButton("action1", GamepadButton.face_a())
        self.mapButton("sprint", GamepadButton.face_c())
        self.mapButton("center-camera", GamepadButton.face_z())

    def setDefaultMappingGenericGamepad(self):
        # Сопоставление по умолчанию для общих устройств геймпада
        self.mapAxis("axis-left-x", InputDevice.Axis.left_x)
        self.mapAxis("axis-left-y", InputDevice.Axis.left_y)
        self.mapAxis("axis-right-x", InputDevice.Axis.right_x)
        self.mapAxis("axis-right-y", InputDevice.Axis.right_y)
        self.mapAxis("camera-up", InputDevice.Axis.right_y)
        self.mapAxis("camera-down", InputDevice.Axis.right_y)
        self.mapAxis("camera-left", InputDevice.Axis.right_x)
        self.mapAxis("camera-right", InputDevice.Axis.right_x)
        self.mapButton("jump", GamepadButton.face_a())
        self.mapButton("intel-action", GamepadButton.face_b())
        self.mapButton("action1", GamepadButton.face_a())
        self.mapButton("sprint", GamepadButton.rtrigger())
        self.mapButton("walk", GamepadButton.lshoulder())
        self.mapButton("crouch", GamepadButton.ltrigger())
        self.mapButton("crawl", GamepadButton.face_x())
        self.mapButton("center-camera", GamepadButton.rshoulder())
        self.mapButton("recalibrate", GamepadButton.back())

    def mapButton(self, action, button):
        self.__map[action] = ("button", str(button))

    def mapAxis(self, action, axis):
        self.__map[action] = ("axis", axis.name)

    def unmap(self):
        self.__map[action] = None

    def formatMapping(self, action):
        """Returns a string label describing the mapping for a given action,
        for displaying in a GUI. """
        mapping = self.__map.get(action)
        if not mapping:
            return "Unmapped"

        # Красиво отформатируй символьную строку из Panda.  В реальной игре,
        # ты, возможно, захочешь посмотреть их в таблице перевода, или так.
        label = mapping[1].replace('_', ' ').title()
        if mapping[0] == "axis":
            return "Axis: " + label
        else:
            return "Button: " + label

    def unformatedMapping(self, action):
        """Возвращает имя сопоставленной клавиши/оси в виде строки или Unmapped
        если действие еще не было отображено."""
        mapping = self.__map.get(action)
        return mapping[1] if mapping else "Unmapped"

    def getValue(self, action, device):
        """Возвращает значение с плавающей точкой состояния указанного действия """
        mapping = self.__map.get(action)
        if not mapping:
            return 0
        if mapping[0] == "axis":
            for axis in device.axes:
                if axis.axis.name == mapping[1]:
                    return axis.value
            return 0
        else:
            for button in device.buttons:
                if button.handle.name == mapping[1]:
                    return button.pressed
            return False

    def getMappingJSON(self):
        """Запишите отображение в формате JSON"""
        return json.dumps(self.__map)

    def readMappingJSON(self, jsonString):
        """Чтение отображения из JSON"""
        self.__map = json.loads(jsonString)
