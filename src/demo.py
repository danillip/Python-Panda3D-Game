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

    # Либы для стройки геометрии BULLET
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

# Контроллер разширенный символов
from characterController.PlayerController import PlayerController

# Исключительно для того чтобы проверить использовать движок или bullet
# лучше используйте, касается Лехи
from characterController.Config import USEBULLET, USEINTERNAL

# Лог файлы, ошибочки чекаем когда ботаем, а то фиксить потом надоедает мне
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

#Подгружает из лога мапу
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
        # Пауза если афэкашим
        self.accept("playerIdling", self.pause)
        self.accept("reset-Avatar", self.resetPlayer)

        base.win.movePointer(0, base.win.getXSize() // 2, base.win.getYSize() // 2)

        self.useBullet = USEBULLET
        self.useInternal = USEINTERNAL
        self.debugactive = True

        # Леха и Андрей, если у Вас плохо все по фепесам закоменьтите строку
        render.setShaderAuto(True)

        #
        # НАСТРОЙКА УРОВНЯ
        #
        self.music_manager = MusicManager(self)       
        self.main_menu = MainMenu(self) #Вызов Inser, Main menu
        
        self.settings_menu = None
        def open_settings(self):
            self.settings_menu = SettingsMenu(self)

        # self.level = loader.loadModel("../data/level/level")
        # self.level.reparentTo(render)

        self.level = loader.loadModel(f"../data/level/{selected_level }")
        self.level.reparentTo(render)

        # self.level.subdivideCollisions(4)
        #
        # Света
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
        # КОНЕЦ НАСТРОЙКИ УРОВНЯ
        #

        #
        # НАСТРАИВАЕМ ФИЗИКУ
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


            # Нематериальные блоки (как, например, в коллекционных или событийных сферах)
            self.moveThroughBoxes = render.attachNewNode(BulletGhostNode("Ghosts"))
            self.moveThroughBoxes.setPos(0, 0, 1)
            box = BulletBoxShape((1, 1, 1))
            self.moveThroughBoxes.node().addShape(box)
            # should only collide with the event sphere of the character
            self.moveThroughBoxes.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.world.attachGhost(self.moveThroughBoxes.node())



            # Нематериальные блоки (как, например, в коллекционных или событийных сферах)
            self.collideBox = render.attachNewNode(BulletRigidBodyNode("Ghosts"))
            self.collideBox.setPos(0, 2.5, 1)
            box = BulletBoxShape((1, 1, 1))
            self.collideBox.node().addShape(box)
            # должны сталкиваться только со сферой событий персонажа
            #self.collideBox.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.world.attachRigidBody(self.collideBox.node())


            self.accept("CharacterCollisions-in-Ghosts", print, ["ENTER"])
            self.accept("CharacterCollisions-out-Ghosts", print, ["EXIT"])


            # показать отладочную геометрию для столкновений с пулями
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
        # ВНУТРЯНКА
        #
        if self.useInternal:
            # Подключаем физику
            base.enableParticles()
            base.cTrav = CollisionTraverser("base collision traverser")
            base.cTrav.setRespectPrevTransform(True)

            # Установка дефолтной графики
            gravityFN = ForceNode("world-forces")
            gravityFNP = render.attachNewNode(gravityFN)
            gravityForce = LinearVectorForce(0, 0, -9.81)  # Сила тяжести
            gravityFN.addForce(gravityForce)
            base.physicsMgr.addLinearForce(gravityForce)

            # Плейн земли
            plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -4)))
            self.ground = render.attachNewNode(CollisionNode("Ground"))
            self.ground.node().addSolid(plane)
            self.ground.show()

            # Нематериальные блоки (как, например, в коллекционных или событийных сферах)
            self.moveThroughBoxes = render.attachNewNode(CollisionNode("Ghosts"))
            box = CollisionBox((0, 0, 0.5), 1, 1, 1)
            box.setTangible(False)
            self.moveThroughBoxes.node().addSolid(box)
            # должны сталкиваться только со сферой событий персонажа
            self.moveThroughBoxes.node().setFromCollideMask(BitMask32.allOff())
            self.moveThroughBoxes.node().setIntoCollideMask(BitMask32(0x80))  # 1000 0000
            self.moveThroughBoxes.show()

            self.accept("CharacterCollisions-in-Ghosts", print, ["ENTER"])
            self.accept("CharacterCollisions-out-Ghosts", print, ["EXIT"])

            # Установка мира
            self.world = base.cTrav
        #
        # КОНЕЦ НАСТРОЙКИ МИРА
        #

        #
        # ДЕБАГИНГ
        #
        # ПИМЕЧАНИЕ:  Чтобы добавить вывод на экранное меню, смотри!!!!
        #       раздел debugOSDUpdater ниже, также не забудь установить значение
        #       для параметра on-screen-debug-enabled в вызов loadPrcFileData
        #       приведенный в верхней части этого файла
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
        # ПЕРСОНАЖ
        #
        self.playerController = PlayerController(self.world, "data/config.json")
        self.playerController.startPlayer()
        # найти начальную позицию для персонажа на карте 
        startpos = self.level.find("**/StartPos").getPos()
        if USEBULLET:
            # В связи с установкой и ограничением формы столкновения пуль
            # размещения, нам нужно сместить символ вверх на половину его
            # высоты.
            startpos.setZ(startpos.getZ() + self.playerController.getConfig("player_height")/2.0)
            startpos = (0,0,3)
        self.playerController.setStartPos(startpos)
        self.playerController.setStartHpr(self.level.find("**/StartPos").getHpr())

        self.pause = False

        self.playerController.camera_handler.centerCamera()

        # Эта функция должна вызываться всякий раз, когда игрок не
        # больше не требуется, как при выходе из приложения.
        #self.playerController.stopPlayer()

    def toggleDebug(self):
        """dis- and enable the collision debug visualization"""
        if not self.debugactive:
            if self.useBullet:
                # Активировать отладку физикальный или физичных, физико физичных устройств
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
                # Активировать отладку физикальный или физичных, физико физичных устройств
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
        """Эта функция просто возвращает игрока в исходное положение
        и центрирует камеру позади него."""
        self.playerController.setStartPos(self.level.find("**/StartPos").getPos())
        self.playerController.setStartHpr(self.level.find("**/StartPos").getHpr())
        self.playerController.camera_handler.centerCamera()

    def pause(self):
        print("PAUSE")
        if not self.pause:
            self.togglePause()

    def togglePause(self):
        """Эта функция показывает, как приложение может приостанавливать и возобновлять работу
        player"""
        if self.pause:
            # для изменения размера окна мы переназначем необходимые переменные
            self.playerController.win_width_half = base.win.getXSize() // 2
            self.playerController.win_height_half = base.win.getYSize() // 2

            self.playerController.resumePlayer()
        else:
            self.playerController.pausePlayer()
        self.pause = not self.pause

    def toggleCamera(self):
        """Эта функция показывает, как приложение может переключать систему камер.
        между режимом от первого и третьего лица"""
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
        """Обновление экранного меню с постоянно меняющимися значениями"""
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
        """Эта задача будет заниматься актуализацией
        физические расчеты в каждом кадре для
        движка Bullet"""
        dt = globalClock.getDt()
        self.world.doPhysics(dt, 10, 1.0/180.0)
        return task.cont
APP = Main()
APP.run()
