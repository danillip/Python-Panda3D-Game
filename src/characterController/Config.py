#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

from panda3d.core import KeyboardButton, MouseButton, ButtonHandle, Point3F, Vec3
from panda3d.core import InputDevice, Filename


# Deside which physics engine to use
# Panda3D internal engine
USEINTERNAL = True
# Bullet engine
USEBULLET = not USEINTERNAL

#
# PLAYER CONFIGURATIONS
#
class Config:
    def __init__(self, configFile):
        # Make sure, the given path is in the correct form
        osSpecificConfigPath = Filename(configFile).toOsSpecific()
        with open(osSpecificConfigPath) as json_data_file:
            self.config = json.load(json_data_file)

        self.used_device = None
        for device in base.devices.getDevices(InputDevice.DeviceClass.gamepad):
            if device.name == self.config["selectedDevice"]:
                self.used_device = device

        self.config["win_width_half"] = base.win.getXSize() // 2
        self.config["win_height_half"] = base.win.getYSize() // 2

    def getConfig(self, configString):
        return self.config[configString]

    def setConfig(self, configString, value):
        self.config[configString] = value

    def saveConfig(self, configFile):
        # Make sure, the given path is in the correct form
        osSpecificConfigPath = Filename(configFile).toOsSpecific()
        with open(osSpecificConfigPath) as json_data_file:
            json.dump(self.config, json_data_file)
