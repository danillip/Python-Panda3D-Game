import logging

from panda3d.core import Vec3

KBD = "Keyboard and Mouse"

class Plugin():
    """Этот плагин обеспечивает поддержку геймпадов arbitrarry."""
    def __init__(self, parent, pid):
        logging.debug("INIT KEYBOARD PLUGIN...")
        self.parent = parent
        self.pluginID = pid
        self.active = True

        actionKey = self.parent.deviceMaps[KBD].unformatedMapping("action1")
        self.parent.accept("{}".format(actionKey), base.messenger.send, ["doAction"])
        self.parent.accept("shift-{}".format(actionKey), base.messenger.send, ["doAction"])

        resetKey = self.parent.deviceMaps[KBD].unformatedMapping("reset")
        self.parent.accept("{}".format(resetKey), base.messenger.send, ["reset-Avatar"])

        self.isDown = base.mouseWatcherNode.isButtonDown
        logging.debug("INIT KEYBOARD PLUGIN DONE")

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def centerGamepadAxes(self):
        # Здесь не нужно ничего перекалибровать
        return

    def getMovementVec(self):
        movementVec = Vec3()

        # Move forward / backward
        y_vec = -1 if self.parent.first_pserson_mode else 1
        if self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("forward")):
            movementVec.setY(-y_vec)
        elif self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("backward")):
            movementVec.setY(y_vec)

        # Move left / right
        if self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("left")):
            movementVec.setX(-1)
        elif self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("right")):
            movementVec.setX(1)

        return movementVec

    def getRotationVec(self):
        return Vec3()

    def getCamButton(self, direction):
        #TODO: Возможно, нам нужно сделать эту проверку в функции unformatedMapping
        #if direction not in self.parent.deviceMapKeyboard: return 0.0
        if self.isDown(self.parent.deviceMaps[KBD].unformatedMapping(direction)): return 1.0
        return 0.0

    def getJumpState(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("jump"))

    def getCenterCamState(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("center-camera"))

    def getIntelActionState(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("intel-action"))

    def getAction1State(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("action1"))

    def getSprintState(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("sprint"))

    def getWalkState(self):
        return self.isDown(self.parent.deviceMaps[KBD].unformatedMapping("walk"))
