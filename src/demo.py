#!/usr/bin/python
# coding=windows-1251
# -*- coding: utf-8 -*-


import logging
import json
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectLabel
from main_menu import MainMenu
from setting_menu import SettingsMenu
from music_manager import MusicManager
from panda3d.core import loadPrcFileData
from panda3d.core import (
    loadPrcFileData,
    Vec3,
    Point3,
    DirectionalLight,
    VBase4,
    AmbientLight,
    CollisionTraverser,
    CollisionPlane,
    CollisionBox,
    CollisionNode,
    Plane,
    TextNode,
    BitMask32,

    # ���� ��� ������� ��������� BULLET
    Geom,
    GeomTriangles,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter)
from panda3d.bullet import (
    BulletWorld,
    BulletDebugNode,
    BulletPlaneShape,
    BulletBoxShape,
    BulletRigidBodyNode,
    BulletGhostNode,
    BulletTriangleMesh,
    BulletTriangleMeshShape,
    BulletHelper)
from panda3d.physics import ForceNode, LinearVectorForce
from direct.interval.IntervalGlobal import Sequence, Wait

# ���������� ����������� ��������
from characterController.PlayerController import PlayerController

# ������������� ��� ���� ����� ��������� ������������ ������ ��� bullet
# ����� �����������, �������� ����
from characterController.Config import USEBULLET, USEINTERNAL

# ��� �����, �������� ������ ����� ������, � �� ������� ����� ��������� ���
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    filename="./demo.log",
    datefmt="%d-%m-%Y %H:%M:%S",
    filemode="w")


loadPrcFileData("","""
show-frame-rate-meter #t
model-path $MAIN_DIR/testmodel
cursor-hidden 1
on-screen-debug-enabled #f
want-pstats #f
want-tk #f
fullscreen #f
#win-size 1920 1080
win-size 1080 720
#win-size 840 720
frame-rate-meter-milliseconds #t

#side-by-side-stereo 1
""")

#���������� �� ���� ����
def load_selected_level():
    config_path = "data/configmap.json"

    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)
        return config_data.get("selected_level")

class Main(ShowBase):
    def __init__(self):
        """initialise and start the Game"""
        ShowBase.__init__(self)
        selected_level = load_selected_level()

        self.accept("escape", exit)
        self.accept("f1", self.toggleDebug)
        self.accept("r", self.resetPlayer)
        self.accept("p", self.togglePause)
        self.accept("f2", self.toggleCamera)
        self.accept("f3", self.toggleOSD)
        # ����� ���� ��������
        self.accept("playerIdling", self.pause)
        self.accept("reset-Avatar", self.resetPlayer)

        base.win.movePointer(0, base.win.getXSize() // 2, base.win.getYSize() // 2)

        self.useBullet = USEBULLET
        self.useInternal = USEINTERNAL
        self.debugactive = True

        # ���� � ������, ���� � ��� ����� ��� �� ������� ������������ ������
        render.setShaderAuto(True)

        #
        # ��������� ������
        #
        self.music_manager = MusicManager(self)       
        self.main_menu = MainMenu(self) #����� Inser, Main menu
        
        self.settings_menu = None
        def open_settings(self):
            self.settings_menu = SettingsMenu(self)

        # self.level = loader.loadModel("../data/level/level")
        # self.level.reparentTo(render)

        self.level = loader.loadModel(f"../data/level/{selected_level }")
        self.level.reparentTo(render)

        # self.level.subdivideCollisions(4)
        #
        # �����
        #
        alight = AmbientLight("Ambient")
        alight.setColor(VBase4(0.5, 0.5, 0.5, 1))
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)
        sun = DirectionalLight("Sun")
        sun.setColor(VBase4(1.5, 1.5, 1.0, 1))
        sunnp = render.attachNewNode(sun)
        sunnp.setHpr(10, -60, 0)
        render.setLight(sunnp)
        #
        # ����� ��������� ������
        #

        #
        # ����������� ������
        #
        #
        # BULLET
        #
        if self.useBullet:
            self.world = BulletWorld()
            self.world.setGravity(Vec3(0, 0, -9.81))

            shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
            node = BulletRigidBodyNode("Ground")
            node.addShape(shape)
            node.setIntoCollideMask(BitMask32.allOn())
            np = render.attachNewNode(node)
            np.setPos(0, 0, -4)
            self.world.attachRigidBody(node)

            self.levelSolids = BulletHelper.fromCollisionSolids(self.level, True)
            for bodyNP in self.levelSolids:
                bodyNP.reparentTo(self.level)
                bodyNP.node().setDebugEnabled(False)
                if isinstance(bodyNP.node(), BulletRigidBodyNode):
                    bodyNP.node().setMass(0.0)
                    self.world.attachRigidBody(bodyNP.node())
                elif isinstance(bodyNP.node(), BulletGhostNode):
                    self.world.attachGhost(bodyNP.node())


            # �������������� ����� (���, ��������, � ������������� ��� ���������� ������)
            self.moveThroughBoxes = render.attachNewNode(BulletGhostNode("Ghosts"))
            self.moveThroughBoxes.setPos(0, 0, 1)
            box = BulletBoxShape((1, 1, 1))
            self.moveThroughBoxes.node().addShape(box)
            # should only collide with the event sphere of the character
            self.moveThroughBoxes.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.world.attachGhost(self.moveThroughBoxes.node())



            # �������������� ����� (���, ��������, � ������������� ��� ���������� ������)
            self.collideBox = render.attachNewNode(BulletRigidBodyNode("Ghosts"))
            self.collideBox.setPos(0, 2.5, 1)
            box = BulletBoxShape((1, 1, 1))
            self.collideBox.node().addShape(box)
            # ������ ������������ ������ �� ������ ������� ���������
            #self.collideBox.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.world.attachRigidBody(self.collideBox.node())


            self.accept("CharacterCollisions-in-Ghosts", print, ["ENTER"])
            self.accept("CharacterCollisions-out-Ghosts", print, ["EXIT"])


            # �������� ���������� ��������� ��� ������������ � ������
            self.debugactive = True
            debugNode = BulletDebugNode("Debug")
            debugNode.showWireframe(True)
            debugNode.showConstraints(True)
            debugNode.showBoundingBoxes(False)
            debugNode.showNormals(True)
            self.debugNP = render.attachNewNode(debugNode)
            self.debugNP.show()

            self.world.setDebugNode(debugNode)
            self.__taskName = "task_physicsUpdater_Bullet"
            taskMgr.add(self.updatePhysicsBullet, self.__taskName, priority=-20)
        #
        # ���������
        #
        if self.useInternal:
            # ���������� ������
            base.enableParticles()
            base.cTrav = CollisionTraverser("base collision traverser")
            base.cTrav.setRespectPrevTransform(True)

            # ��������� ��������� �������
            gravityFN = ForceNode("world-forces")
            gravityFNP = render.attachNewNode(gravityFN)
            gravityForce = LinearVectorForce(0, 0, -9.81)  # ���� �������
            gravityFN.addForce(gravityForce)
            base.physicsMgr.addLinearForce(gravityForce)

            # ����� �����
            plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -4)))
            self.ground = render.attachNewNode(CollisionNode("Ground"))
            self.ground.node().addSolid(plane)
            self.ground.show()

            # �������������� ����� (���, ��������, � ������������� ��� ���������� ������)
            self.moveThroughBoxes = render.attachNewNode(CollisionNode("Ghosts"))
            box = CollisionBox((0, 0, 0.5), 1, 1, 1)
            box.setTangible(False)
            self.moveThroughBoxes.node().addSolid(box)
            # ������ ������������ ������ �� ������ ������� ���������
            self.moveThroughBoxes.node().setFromCollideMask(BitMask32.allOff())
            self.moveThroughBoxes.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.moveThroughBoxes.show()

            self.accept("CharacterCollisions-in-Ghosts", print, ["ENTER"])
            self.accept("CharacterCollisions-out-Ghosts", print, ["EXIT"])

            # ��������� ����
            self.world = base.cTrav
        #
        # ����� ��������� ����
        #

        #
        # ��������
        #
        # ���������:  ����� �������� ����� �� �������� ����, ������!!!!
        #       ������ debugOSDUpdater ����, ����� �� ������ ���������� ��������
        #       ��� ��������� on-screen-debug-enabled � ����� loadPrcFileData
        #       ����������� � ������� ����� ����� �����
        from direct.showbase.OnScreenDebug import OnScreenDebug
        self.osd = OnScreenDebug()
        self.osd.enabled = False
        self.osd.append("Debug OSD\n")
        self.osd.append("Keys:\n")
        self.osd.append("escape        - Quit\n")
        self.osd.append("F1            - Toggle Debug Mode\n")
        self.osd.append("F2            - Toggle Camera Mode\n")
        self.osd.append("R             - Reset Player\n")
        self.osd.append("P             - Toggle Pause\n")
        self.osd.load()
        self.osd.render()
        taskMgr.add(self.debugOSDUpdater, "update OSD")

        #
        # ��������
        #
        self.playerController = PlayerController(self.world, "data/config.json")
        self.playerController.startPlayer()
        # ����� ��������� ������� ��� ��������� �� ����� 
        startpos = self.level.find("**/StartPos").getPos()
        if USEBULLET:
            # � ����� � ���������� � ������������ ����� ������������ ����
            # ����������, ��� ����� �������� ������ ����� �� �������� ���
            # ������.
            startpos.setZ(startpos.getZ() + self.playerController.getConfig("player_height")/2.0)
            startpos = (0,0,3)
        self.playerController.setStartPos(startpos)
        self.playerController.setStartHpr(self.level.find("**/StartPos").getHpr())

        self.pause = False

        self.playerController.camera_handler.centerCamera()

        # ��� ������� ������ ���������� ������ ���, ����� ����� ��
        # ������ �� ���������, ��� ��� ������ �� ����������.
        #self.playerController.stopPlayer()

    def toggleDebug(self):
        """dis- and enable the collision debug visualization"""
        if not self.debugactive:
            if self.useBullet:
                # ������������ ������� ����������� ��� ��������, ������ �������� ���������
                self.debugNP.show()
            if self.useInternal:
                self.moveThroughBoxes.show()
                self.playerController.charCollisions.show()
                self.playerController.shadowRay.show()
                self.playerController.charFutureCollisions.show()
                self.playerController.eventCollider.show()
                for rayID, ray in self.playerController.raylist.items():
                    ray.ray_np.show()
                base.cTrav.showCollisions(render)
            self.debugactive = True
        else:
            if self.useBullet:
                # ������������ ������� ����������� ��� ��������, ������ �������� ���������
                self.debugNP.hide()
            if self.useInternal:
                self.moveThroughBoxes.hide()
                self.playerController.charCollisions.hide()
                self.playerController.shadowRay.hide()
                self.playerController.charFutureCollisions.hide()
                self.playerController.eventCollider.hide()
                for rayID, ray in self.playerController.raylist.items():
                    ray.ray_np.hide()
                base.cTrav.hideCollisions()
            self.debugactive = False

    def resetPlayer(self):
        """��� ������� ������ ���������� ������ � �������� ���������
        � ���������� ������ ������ ����."""
        self.playerController.setStartPos(self.level.find("**/StartPos").getPos())
        self.playerController.setStartHpr(self.level.find("**/StartPos").getHpr())
        self.playerController.camera_handler.centerCamera()

    def pause(self):
        print("PAUSE")
        if not self.pause:
            self.togglePause()

    def togglePause(self):
        """��� ������� ����������, ��� ���������� ����� ���������������� � ������������ ������
        player"""
        if self.pause:
            # ��� ��������� ������� ���� �� ������������ ����������� ����������
            self.playerController.win_width_half = base.win.getXSize() // 2
            self.playerController.win_height_half = base.win.getYSize() // 2

            self.playerController.resumePlayer()
        else:
            self.playerController.pausePlayer()
        self.pause = not self.pause

    def toggleCamera(self):
        """��� ������� ����������, ��� ���������� ����� ����������� ������� �����.
        ����� ������� �� ������� � �������� ����"""
        if self.playerController.plugin_isFirstPersonMode():
            self.playerController.changeCameraSystem("thirdperson")
        else:
            self.playerController.changeCameraSystem("firstperson")

    def toggleOSD(self):
        self.osd.enabled = not self.osd.enabled
        if self.osd.onScreenText:
            if self.osd.enabled:
                self.osd.onScreenText.show()
            else:
                self.osd.onScreenText.hide()

    def debugOSDUpdater(self, task):
        """���������� ��������� ���� � ��������� ����������� ����������"""
        self.osd.add("stamina", "{:0.2f}".format(self.playerController.stamina))
        if USEINTERNAL:
            self.osd.add("velocity", "{X:0.4f}/{Y:0.4f}/{Z:0.4f}".format(
                X=self.playerController.actorNode.getPhysicsObject().getVelocity().getX(),
                Y=self.playerController.actorNode.getPhysicsObject().getVelocity().getY(),
                Z=self.playerController.actorNode.getPhysicsObject().getVelocity().getZ()))
        elif USEBULLET:
            self.osd.add("velocity", "{X:0.4f}/{Y:0.4f}/{Z:0.4f}".format(
                X=self.playerController.charCollisions.getLinearVelocity().getX(),
                Y=self.playerController.charCollisions.getLinearVelocity().getY(),
                Z=self.playerController.charCollisions.getLinearVelocity().getZ()))
        if taskMgr.hasTaskNamed(self.playerController.getConfig("idle_to_pause_task_name")):
            pause_task = taskMgr.getTasksNamed(self.playerController.getConfig("idle_to_pause_task_name"))[0]
            self.osd.add("pause in", "{:0.0f}".format(-pause_task.time))
        self.osd.add("state", "{}".format(self.playerController.state))
        self.osd.add("move vec", "{}".format(self.playerController.plugin_getMoveDirection()))

        self.osd.render()
        return task.cont

    def updatePhysicsBullet(self, task):
        """��� ������ ����� ���������� �������������
        ���������� ������� � ������ ����� ���
        ������ Bullet"""
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 1.0/180.0)
        return task.cont
APP = Main()
APP.run()
