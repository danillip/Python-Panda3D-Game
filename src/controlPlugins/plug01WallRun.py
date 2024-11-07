#!/usr/bin/python
# -*- coding: utf-8 -*-

"""ќтот плагин реализует логику запуска стены для игрока"""

#
# PYTHON IMPORTS
#
import math

#
# PANDA3D IMPORTS
#
from panda3d.core import NodePath

class Plugin:
    STATE_WALL_RUN = "WallRun"
    STATE_RUN_TO_WALL_RUN = "RunToWallRun"
    STATE_SPRINT_TO_WALL_RUN = "SprintToWallRun"

    WALLRUN_LEFT = "WR_Left"
    WALLRUN_RIGHT = "WR_Right"
    WALLRUN_UP = "WR_Up"

    def __init__(self, core, pid):
        self.pluginID = pid
        self.core = core
        self.do_wall_run = False

        #
        # УСТАНОВКА СОСТОЯНИЙ
        #
        # все состояния работы стен
        self.wall_run_states = [
            self.STATE_WALL_RUN,
            self.STATE_RUN_TO_WALL_RUN,
            self.STATE_SPRINT_TO_WALL_RUN,
            ]

        # регаем шаги для бега по стенам
        self.core.plugin_registerState(
            self.STATE_WALL_RUN,[
                self.core.STATE_IDLE,
                self.core.STATE_WALK,
                self.core.STATE_RUN,
                self.core.STATE_SPRINT,
                self.core.STATE_JUMP,
                self.core.STATE_LAND]
                + ["*"] #TODO: Реализовать логику для любых состояний плагина
                + self.core.jump_and_fall_states
                + self.wall_run_states,
            isOnGround=False,
            isFlying=True)

        self.core.plugin_registerState(
            self.STATE_RUN_TO_WALL_RUN,[
                self.core.STATE_IDLE,
                self.core.STATE_RUN,
                self.core.STATE_SPRINT]
                + ["*"] #TODO: Реализовать логику для любых состояний плагина
                + self.core.jump_and_fall_states
                + self.wall_run_states,
            isFlying=True)

        self.core.plugin_registerState(
            self.STATE_SPRINT_TO_WALL_RUN,[
                self.core.STATE_IDLE,
                self.core.STATE_RUN,
                self.core.STATE_SPRINT]
                + ["*"] #TODO: Реализовать логику для любых состояний плагина
                + self.core.jump_and_fall_states
                + self.wall_run_states,
            isFlying=True)


        # просто список, содержащий все состояния, из которых можно установить настенный снаряд
        self.wall_run_possible_states = self.wall_run_states \
            + self.core.run_states \
            + self.core.sprint_states \
            + self.core.jump_and_fall_states

        # добавление перехода ко всем состояниям, которые должны иметь возможность переходить к состояниям выполнения стены
        for state in self.wall_run_possible_states:
            self.core.plugin_addStateTransition(state, self.wall_run_states)

        #
        # ФУНКЦИИ СОСТОЯНИЯ АНИМАЦИИ
        #
        self.ease_in_wall_run_up = self.core.createEaseIn(self.WALLRUN_UP)
        self.ease_in_wall_run_l = self.core.createEaseIn(self.WALLRUN_LEFT)
        self.ease_in_wall_run_r = self.core.createEaseIn(self.WALLRUN_RIGHT)

        self.core.enterWallRun = self.enterWallRun
        self.core.enterRunToWallRun = self.enterRunToWallRun
        self.core.exitRunToWallRun = self.exitRunToWallRun
        self.core.enterSprintToWallRun = self.enterSprintToWallRun
        self.core.exitSprintToWallRun = self.exitSprintToWallRun
        self.core.enterJumpToWallRun = self.enterJumpToWallRun
        self.core.exitJumpToWallRun = self.exitJumpToWallRun
        self.core.enterFallToWallRun = self.enterFallToWallRun
        self.core.exitFallToWallRun = self.exitFallToWallRun

        #
        # ЗАГРУЗКА АНИМАЦИИ
        #
        self.updateAnimations(self.core.plugin_isFirstPersonMode())

        #
        # НАСТРОЙКА ОБНАРУЖЕНИЯ СТОЛКНОВЕНИЙ
        #
        # Проверка лучей на стене спереди, слева и справа от проигрывателя
        point_a = (0,0,self.core.player_height/2.0)
        point_b = (0, -self.core.wall_run_forward_check_dist, self.core.player_height/2.0)
        self.forward_ray = "wall_run_forward_ray-{}".format(self.pluginID)
        self.core.plugin_registerCharacterRayCheck(self.forward_ray, point_a, point_b)

        # Left side collision
        point_b = (self.core.wall_run_sideward_check_dist, 0, self.core.player_height/2.0)
        self.left_ray = "wall_run_left_ray-{}".format(self.pluginID)
        self.core.plugin_registerCharacterRayCheck(self.left_ray, point_a, point_b, True)

        # Right side collision
        point_b = (-self.core.wall_run_sideward_check_dist, 0, self.core.player_height/2.0)
        self.right_ray = "wall_run_right_ray-{}".format(self.pluginID)
        self.core.plugin_registerCharacterRayCheck(self.right_ray, point_a, point_b, True)

        #
        # АКТИВАЦИЯ ПЛАГИНА
        #
        self.active = True

    def updateAnimations(self, firstPersonMode):
        if firstPersonMode:
            self.core.loadAnims({
                self.WALLRUN_LEFT: self.core.anim_wallrun_left_fp,
                self.WALLRUN_RIGHT: self.core.anim_wallrun_right_fp,
                self.WALLRUN_UP: self.core.anim_wallrun_up_fp,})
        else:
            self.core.loadAnims({
                self.WALLRUN_LEFT: self.core.anim_wallrun_left,
                self.WALLRUN_RIGHT: self.core.anim_wallrun_right,
                self.WALLRUN_UP: self.core.anim_wallrun_up,})
        # «Предварительная загрузка» всех анимаций персонажа
        self.core.bindAllAnims()

    def action(self, intel_action):
        if not self.core.wall_run_enabled: return
        #
        # ПРОВЕРКА СТОЛКНОВЕНИЯ СО СТЕНОЙ ПРОВЕРКА ВОЛЛ РАНА
        #
        char_front_collision_entry = self.core.getFirstCollisionEntryInLine(self.forward_ray)
        char_left_collision_entry = self.core.getFirstCollisionEntryInLine(self.left_ray)
        char_right_collision_entry = self.core.getFirstCollisionEntryInLine(self.right_ray)

        #
        # ЛОГИКА ВОЛЛ РАНА
        #
        # получить левое/правое направление движения игрока
        self.move_left = self.core.plugin_getMoveDirection().getX() < 0
        self.move_right = self.core.plugin_getMoveDirection().getX() > 0

        # рассчитать время падения, так как бег по стене не должен быть цепным
        # сразу, а только через определенное время после прыжка/падения
        checked_fall_time = True
        if self.core.state is self.core.jump_and_fall_states:
            checked_fall_time = self.core.fall_time > self.core.wall_run_min_fall_time

        #
        # ПРОБЕЖКА ПО СТЕНЕ ВОЗМОЖНАЯ ПРОВЕРКА
        #
        # проверить, происходят ли столкновения со стеной слева
        # слева, справа или спереди от игрока.
        # Нажата ли клавиша интеллектуального действия.
        # Находимся ли мы в состоянии, позволяющем перейти к бегу по стене
        # Время падения в порядке
        # Не нажал ли игрок клавишу прыжка
        if (
            char_front_collision_entry is not None \
            or char_left_collision_entry is not None \
            or char_right_collision_entry is not None \
        ) \
        and intel_action \
        and self.core.state in self.wall_run_possible_states \
        and checked_fall_time \
        and not self.core.do_jump:
            if self.core.state not in self.wall_run_states:
                # мы должны быть в состоянии нормально спрыгнуть со стены всякий раз, когда
                # мы инициируем бег от стены, поэтому сбросьте все переменные, связанные с прыжком
                # основные переменные
                self.core.resetAfterJump()

            # некоторые заготовки
            wall_normal = None
            prev_jump_direction = self.core.jump_direction

            # проверка, в каком направлении мы соприкасаемся со стеной
            #
            # ПЕРЕДНЯЯ СТЕНА
            #
            if char_front_collision_entry:
                # Перед нами стена, по которой мы можем пройти.
                if self.core.hasSurfaceNormal(char_front_collision_entry):
                    wall_normal = self.core.getSurfaceNormal(char_front_collision_entry, render)
                    self.setWallRunDirection(self.WALLRUN_UP)
                    self.core.jump_direction = self.core.wall_run_up_jump_direction

            #
            # ЛЕВЫЙ ВОЛЛ РАН
            #
            elif char_left_collision_entry:
                # Слева от нас есть стена, вдоль которой мы можем идти.
                if self.core.hasSurfaceNormal(char_left_collision_entry):
                    wall_normal = self.core.getSurfaceNormal(char_left_collision_entry, render)
                    wall_normal.setY(-wall_normal.getY())
                    wall_normal.setX(-wall_normal.getX())
                    self.setWallRunDirection(self.WALLRUN_LEFT)
                    if self.move_right:
                        self.core.jump_direction = self.core.wall_run_left_jump_direction
                    else:
                        self.core.jump_direction = self.core.wall_run_forward_jump_direction

                    # убедитесь, что мы всегда находимся как можно ближе к стене
                    # получить положение стены
                    pos = char_left_collision_entry.getSurfacePoint(render)
                    posA = NodePath("WALL-COL-TEMP")
                    posA.setPos(pos)
                    # получить положение ГГ
                    posB = NodePath("CHAR-TEMP")
                    posB.setPos(self.core.plugin_getPos())
                    # вычислите расстояние между стеной и ГГ
                    diff = posA.getPos() - posB.getPos()
                    # очистка временных узлов
                    posA.removeNode()
                    posB.removeNode()
                    # вычисление новой позицию с учетом радиуса игроков,
                    # небольшого пуффера в 0,5 единиц и расстояния
                    # стены до игрока
                    newPos = (-(-diff.length() + self.core.player_radius + 0.5), 0, 0)
                    # Наконец, установите игрока в точно такую позицию.
                    # как видно у него самого
                    self.core.updatePlayerPosFix(newPos, self.core.mainNode)

            #
            # ПРАВАЯ СТЕНА
            #
            elif char_right_collision_entry:
                # Справа от нас есть стена, вдоль которой мы можем идти.
                if self.core.hasSurfaceNormal(char_right_collision_entry):
                    wall_normal = self.core.getSurfaceNormal(char_right_collision_entry, render)
                    self.setWallRunDirection(self.WALLRUN_RIGHT)
                    if self.move_left:
                        self.core.jump_direction = self.core.wall_run_right_jump_direction
                    else:
                        self.core.jump_direction = self.core.wall_run_forward_jump_direction
                    # следить за тем, чтобы мы всегда находились как можно ближе к стене
                    pos = char_right_collision_entry.getSurfacePoint(render)
                    posA = NodePath("WALL-COL-TEMP")
                    posA.setPos(pos)
                    posB = NodePath("CHAR-TEMP")
                    posB.setPos(self.core.plugin_getPos())
                    diff = posA.getPos() - posB.getPos()
                    posA.removeNode()
                    posB.removeNode()
                    newPos = (-diff.length() + self.core.player_radius + 0.5, 0, 0)
                    self.core.updatePlayerPosFix(newPos, self.core.mainNode)

            #
            # КОРАБКАНЬЕ
            #
            # установить заголовок символов, если это возможно
            if wall_normal is not None:
                zx = math.atan2(wall_normal.getZ(), wall_normal.getX())*180/math.pi
                zy = math.atan2(wall_normal.getZ(), wall_normal.getY())*180/math.pi
                zx = abs(zx-90)
                zy = abs(zy-90)
                if zy >= self.core.min_wall_angle_for_wall_run and zx >= self.core.min_wall_angle_for_wall_run:
                    if self.wall_run_direction == self.WALLRUN_UP:
                        # лицом к стене
                        h = math.atan2(-wall_normal.getX(), wall_normal.getY())*180/math.pi
                    else:
                        # лицо вдоль стены
                        h = math.atan2(wall_normal.getY(), wall_normal.getX())*180/math.pi

                    if self.core.mainNode.getH() != h:
                        #
                        # КАМЕРА ОБНОВЛЯТОР
                        #
                        # Убедитесь, что камера следует за игроком
                        # соответственно.
                        # поэтому мы используем временный узел, переназначенный на
                        # игроку, который будет просто двигаться вместе с ним.
                        tempNP = NodePath("tempCamNP")
                        tempNP.reparentTo(self.core.mainNode)
                        tempNP.setPos(camera.getPos(self.core.mainNode))
                        self.core.updatePlayerHpr((h, 0, 0))
                        # теперь используй позицию временных нодепаутов в качестве новой
                        # положение камеры
                        self.core.camera_handler.requestReposition(tempNP.getPos(render))
                        # очистка
                        tempNP.remove_node()
                    # аннулировать другие движения self.core.rotational, которые были заданы до этого
                    self.core.rotation = None

            #
            # ФИНАЛЬНАЯ ЧАСТЬ
            #
            self.do_wall_run = True
            self.core.pre_jump_state = self.core.STATE_RUN
            if self.core.state not in [self.STATE_WALL_RUN, self.STATE_RUN_TO_WALL_RUN, self.STATE_SPRINT_TO_WALL_RUN]:
                # в зависимости от нашего текущего состояния мы начинаем с разных
                # переход к бегу по стене
                if self.core.state in [self.core.run_states]:
                    #
                    # БЕГ ОТ СТЕНЫ К СТЕНЕ
                    #
                    self.core.plugin_requestNewState(self.STATE_RUN_TO_WALL_RUN)
                elif self.core.state in  [self.core.sprint_states]:
                    #
                    # БЕГ ОТ СТЕНЫ К СТЕНЕ
                    #
                    self.core.plugin_requestNewState(self.STATE_SPRINT_TO_WALL_RUN)
                else:
                    #
                    # ЧТО-НИБУДЬ ЕЩЕ ДЛЯ БЕГА ПО СТЕНАМ
                    #
                    self.core.plugin_requestNewState(self.STATE_WALL_RUN)
                self.core.jump_strength = self.core.wall_run_off_jump_strength
            else:
                # Нам не нужно переходить к какой-либо другой анимации
                self.core.plugin_requestNewState(None)

        # проверить, находимся ли мы в состоянии выполнения стены, но не должны
        # на самом деле мы в нем уже не находимся
        if ((
            char_front_collision_entry is None \
            and char_left_collision_entry is None \
            and char_right_collision_entry is None \
        ) or not intel_action) \
        and self.core.state in self.wall_run_states:
            # запросить состояние анимации падения
            self.core.plugin_requestNewState(self.core.STATE_FALL)

        # возвращает False, так как мы не хотим, чтобы другие плагины были пропущены
        return False

    def useStamina(self):
        # Этот плагин не использует выносливость
        return False

    def moveRestriction(self):
        if self.do_wall_run and not self.core.wasJumping:
            # если мы бежим по стене, добавьте немного скорости к оси Z
            # движение игрока
            wr_speed = self.core.wall_run_speed * self.core.current_accleration
            if wr_speed > self.core.max_wall_run_speed:
                wr_speed = self.core.max_wall_run_speed
            #if wr_speed <= 0:
            #    wr_speed = self.core.min_wall_run_speed
            self.core.update_speed.setZ(wr_speed * self.core.dt)
            # Добавьте немного скорости вперед, чтобы персонаж мог легче бегать по стенам.
            self.core.update_speed.setY(self.core.update_speed.getY() * self.core.wall_run_forward_speed_multiplier)
            self.do_wall_run = False

    #
    # ПОМОЩНИК РАСШИРЕНИЯ FSM
    #
    def setWallRunDirection(self, direction):
        self.wall_run_direction = direction

    def startWRSeq(self, animFrom, easeOut):
        """Запускает последовательность прогонов по стене, зависящую от направления
        заданного в self.wall_run_direction. Кроме того, запускается
        звуковой эффект"""
        base.messenger.send(self.core.audio_play_run_evt)
        if self.wall_run_direction == self.WALLRUN_UP:
            self.core.startCurSeq(animFrom, self.WALLRUN_UP, self.ease_in_wall_run_up, easeOut, self.STATE_WALL_RUN)
        elif self.wall_run_direction == self.WALLRUN_LEFT:
            self.core.startCurSeq(animFrom, self.WALLRUN_LEFT, self.ease_in_wall_run_l, easeOut, self.STATE_WALL_RUN)
        elif self.wall_run_direction == self.WALLRUN_RIGHT:
            self.core.startCurSeq(animFrom, self.WALLRUN_RIGHT, self.ease_in_wall_run_r, easeOut, self.STATE_WALL_RUN)

    #
    # FSM EXTENSION
    #
    def enterWallRun(self):
        self.core.current_animations = [self.wall_run_direction]
        if not self.core.getCurrentAnim() == self.wall_run_direction:
            self.core.loop(self.wall_run_direction)

    def enterRunToWallRun(self):
        self.startWRSeq(self.core.RUN, self.core.ease_out_run)
    def exitRunToWallRun(self):
        self.core.endCurSeq()

    def enterSprintToWallRun(self):
        self.startWRSeq(self.core.SPRINT, self.core.ease_out_sprint)
    def exitSprintToWallRun(self):
        self.core.endCurSeq()

    def enterJumpToWallRun(self):
        self.startWRSeq(self.core.JUMP_START, self.core.ease_out_jump)
    def exitJumpToWallRun(self):
        self.core.endCurSeq()

    def enterFallToWallRun(self):
        self.startWRSeq(self.core.FALL, self.core.ease_out_fall)
    def exitFallToWallRun(self):
        self.core.endCurSeq()
