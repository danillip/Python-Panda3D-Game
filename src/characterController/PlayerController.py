#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# PYTHON IMPORTS
#
import logging
import uuid

#
# PANDA3D ENGINE IMPORTS
#
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM, RequestDenied
from panda3d.core import WindowProperties, Vec3
from direct.gui.OnscreenImage import OnscreenImage

#
# CHARACTER SPECIFIC IMPORTS
#
from .Config import Config, USEBULLET, USEINTERNAL
from .Mover import Mover
if USEBULLET:
    from .PhysicsBullet import Physics
elif USEINTERNAL:
    from .PhysicsInternal import Physics
from .Animator import Animator

#
# PLUGIN IMPORTS
#
from .cameraPlugins.CameraThirdPerson import CameraThirdPerson
from .cameraPlugins.CameraFirstPerson import CameraFirstPerson
from .inputPlugins import plugKeyboard
from .inputPlugins import plugGamepad
from .controlPlugins import plug01WallRun
from .controlPlugins import plug02LedgeGrab
from .controlPlugins import plug03WallCollisionAvoidance
from .controlPlugins import plug04Climb

class PlayerController(FSM, Config, Physics, Actor, Mover, Animator):

    # Names of the animations of the actor class
    IDLE = "Idle"
    WALK = "Walk"
    RUN = "Run"
    SPRINT = "Sprint"
    JUMP_START = "JumpStart"
    JUMP_LAND = "JumpLand"
    FALL = "Fall"
    CROUCH = "Crouch"
    CROUCH_IDLE = "Crouch_Idle"
    CRAWL = "Crawl"
    CRAWL_IDLE = "Crawl_Idle"
    ROLL = "Roll"

    # PLAYER CLASS FSM STATES
    STATE_IDLE = "Idle"
    STATE_IDLE_TO_WALK = "IdleToWalk"
    STATE_IDLE_TO_RUN = "IdleToRun"
    STATE_IDLE_TO_SPRINT = "IdleToSprint"
    STATE_WALK = "Walk"
    STATE_WALK_TO_IDLE = "WalkToIdle"
    STATE_WALK_TO_RUN = "WalkToRun"
    STATE_RUN = "Run"
    STATE_RUN_TO_IDLE = "RunToIdle"
    STATE_RUN_TO_WALK = "RunToWalk"
    STATE_RUN_TO_SPRINT = "RunToSprint"
    STATE_SPRINT = "Sprint"
    STATE_SPRINT_TO_IDLE = "SprintToIdle"
    STATE_SPRINT_TO_RUN = "SprintToRun"
    STATE_JUMP = "Jump"
    STATE_LAND = "Land"
    STATE_FALL = "Fall"

    def __init__(self, physic_world, configFile):
        logging.info("INIT PLAYER...")
        # NOTE: this variable may be overwritten by the physics module
        #       by a node that is controlled by physics and will move
        #       the main node around
        self.main_node = self
        self.plugin_defined_character_state = None
        self.movementVec = Vec3()
        logging.info("INIT CONFIG...")
        Config.__init__(self, configFile)
        # additional initial configuration settings set by the outher application
        self.physic_world = physic_world
        logging.info("INIT PHYSICS...")
        Physics.__init__(self)
        logging.info("INIT MOVER...")
        Mover.__init__(self)
        logging.info("INIT CONTROL PLUGINS...")
        # load plugins
        self.control_plugs_list = []
        for i in range(len(self.control_plugs_list)):
            self.control_plugs_list[i].__init__(self)
        logging.info("INIT ANIMATOR...")
        Animator.__init__(self)
        logging.info("INIT PLAYER DONE")

        #
        # STATES SETUP
        #
        # used for the possible transition in the FSM
        self.defaultTransitions = {
            "*":[]
        }


        # setup state groups
        self.on_ground_states = []
        self.ignore_input_states = []
        self.flying_states = []
        self.prevent_rotation_states = []
        self.prevent_jump_states = []

        # physic control state groups
        self.prevent_slip_states = [
            self.STATE_IDLE]
        self.ignore_step_states = [
            self.STATE_IDLE,
            self.STATE_JUMP,
            ]
        self.ignore_pos_update_states = [
            self.STATE_JUMP
            ]

        # movement state groups
        self.walk_states = [
            self.STATE_WALK,
            self.STATE_WALK_TO_IDLE,
            self.STATE_WALK_TO_RUN,
            self.STATE_IDLE_TO_WALK,
            self.STATE_RUN_TO_WALK
            ]
        self.run_states = [
            self.STATE_RUN,
            self.STATE_RUN_TO_IDLE,
            self.STATE_RUN_TO_SPRINT,
            self.STATE_RUN_TO_WALK,
            self.STATE_IDLE_TO_RUN,
            self.STATE_WALK_TO_RUN,
            self.STATE_SPRINT_TO_RUN]
        self.sprint_states = [
            self.STATE_SPRINT,
            self.STATE_SPRINT_TO_IDLE,
            self.STATE_SPRINT_TO_RUN,
            self.STATE_IDLE_TO_SPRINT,
            self.STATE_RUN_TO_SPRINT]
        self.jump_and_fall_states = [
            self.STATE_JUMP,
            self.STATE_FALL]

        #
        # Register IDLE states
        #
        self.plugin_registerState(
            self.STATE_IDLE,[
                self.STATE_IDLE_TO_WALK,
                self.STATE_IDLE_TO_RUN,
                self.STATE_IDLE_TO_SPRINT,
                self.STATE_LAND
            ] + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_IDLE_TO_WALK,[
                self.STATE_IDLE,
                self.STATE_WALK
            ] + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_IDLE_TO_RUN,[
                self.STATE_IDLE,
                self.STATE_RUN,
                self.STATE_JUMP,
                self.STATE_FALL],
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_IDLE_TO_SPRINT,[
                self.STATE_IDLE,
                self.STATE_SPRINT,
                self.STATE_JUMP,
                self.STATE_FALL],
            isOnGround=True)

        #
        # Register WALK States
        #
        self.plugin_registerState(
            self.STATE_WALK,[
                self.STATE_IDLE,
                self.STATE_WALK_TO_IDLE,
                self.STATE_WALK_TO_RUN]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_WALK_TO_IDLE,[
                self.STATE_IDLE,
                self.STATE_RUN,
                self.STATE_WALK]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_WALK_TO_RUN,[
                self.STATE_IDLE,
                self.STATE_RUN]
                + self.jump_and_fall_states,
            isOnGround=True)

        #
        # Register RUN states
        #
        self.plugin_registerState(
            self.STATE_RUN,[
                self.STATE_IDLE,
                self.STATE_RUN_TO_IDLE,
                self.STATE_RUN_TO_WALK,
                self.STATE_RUN_TO_SPRINT]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_RUN_TO_WALK,[
                self.STATE_IDLE,
                self.STATE_WALK]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_RUN_TO_IDLE,[
                self.STATE_IDLE,
                self.STATE_WALK,
                self.STATE_RUN,
                self.STATE_RUN_TO_SPRINT]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_RUN_TO_SPRINT,[
                self.STATE_IDLE,
                self.STATE_RUN,
                self.STATE_SPRINT]
                + self.jump_and_fall_states,
            isOnGround=True)

        #
        # Register SPRINT states
        #
        self.plugin_registerState(
            self.STATE_SPRINT,[
                self.STATE_IDLE,
                self.STATE_SPRINT_TO_IDLE,
                self.STATE_SPRINT_TO_RUN]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_SPRINT_TO_IDLE,[
                self.STATE_IDLE,
                self.STATE_WALK,
                self.STATE_RUN,
                self.STATE_SPRINT,
                self.STATE_SPRINT_TO_RUN]
                + self.jump_and_fall_states,
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_SPRINT_TO_RUN,[
                self.STATE_IDLE,
                self.STATE_WALK,
                self.STATE_RUN,
                self.STATE_SPRINT]
                + self.jump_and_fall_states,
            isOnGround=True)

        #
        # Register AIRBORN states
        #
        self.plugin_registerState(
            self.STATE_JUMP,[
                self.STATE_FALL,
                self.STATE_LAND])
        self.plugin_registerState(
            self.STATE_LAND,[
                self.STATE_IDLE,
                self.STATE_WALK,
                self.STATE_RUN,
                self.STATE_SPRINT,
                self.STATE_FALL,
                self.STATE_JUMP],
            isOnGround=True)
        self.plugin_registerState(
            self.STATE_FALL,[
                self.STATE_LAND,
                self.STATE_JUMP])

        #
        # ACTOR SETUP
        #
        Actor.__init__(
            self,
            self.getConfig("model"))
        self.setBlend(frameBlend=self.getConfig("enable_interpolation"))
        logging.info("INIT FSM...")
        FSM.__init__(self, "FSM-Player")
        self.prev_state = None

        #
        # Init camera mode and respective animations
        #
        logging.info("INIT CAMERA HANDLER...")
        if self.getConfig("first_pserson_mode"):
            logging.info("INIT FIRST PERSON CAMERA...")
            self.changeCameraSystem("firstperson", True)
        else:
            logging.info("INIT THIRD PERSON CAMERA...")
            self.changeCameraSystem("thirdperson", True)

        #
        # SHADOW SETUP
        #
        if self.getConfig("use_simple_shadow"):
            # setup simple shadow
            logging.info("Setup simple shadow...")
            self.shadow = OnscreenImage(self.getConfig("simple_shadow_image"))
            self.shadow.setP(-90)
            self.shadow.setScale(self.getConfig("max_shadow_scale"))
            self.shadow.setPos(0,0,0.01)
            self.shadow.setTransparency(True)
            self.shadow.setBin("fixed", 10)
            self.shadow.reparentTo(render)

        logging.info("Setup control plugins...")
        #
        # CONTROLS SETUP
        #
        self.isDown = base.mouseWatcherNode.isButtonDown

        #
        # Load Plugins
        #
        #TODO: write generic python file loader
        self.inputPlugins = [
            plugKeyboard.Plugin(self, uuid.uuid4()),
            plugGamepad.Plugin(self, uuid.uuid4())
        ]
        # this dict will hold all plugins. The key will be used for
        # setting the priority and the value will be a list of plugins
        # in that specific priority
        self.controlPlugins = {
            5:[plug04Climb.Plugin(self, uuid.uuid4())],
            10:[plug02LedgeGrab.Plugin(self, uuid.uuid4())],
            20:[plug01WallRun.Plugin(self, uuid.uuid4())],
            50:[plug03WallCollisionAvoidance.Plugin(self, uuid.uuid4())]
        }
        logging.info("INIT PLAYER DONE")

    # OVERRIDE THE defaultFilter FROM FSM

    def defaultFilter(self, request, args):

        if request == 'Off':
            # We can always go to the "Off" state.
            return (request,) + args

        if self.defaultTransitions is None:
            # If self.defaultTransitions is None, it means to accept
            # all requests whose name begins with a capital letter.
            # These are direct requests to a particular state.
            if request[0].isupper():
                return (request,) + args
        else:
            # If self.defaultTransitions is not None, it is a map of
            # allowed transitions from each state.  That is, each key
            # of the map is the current state name; for that key, the
            # value is a list of allowed transitions from the
            # indicated state.
            if request in self.defaultTransitions.get(self.state, []):
                # This transition is listed in the defaultTransitions map;
                # accept it.
                return (request,) + args

            elif '*' in self.defaultTransitions.get(self.state, []):
                # Whenever we have a '*' as our to transition, we allow
                # to transit to any other state
                return (request,) + args

            elif request in self.defaultTransitions.get('*', []):
                # If the requested state is in the default transitions
                # from any state list, we also alow to transit to the
                # new state
                return (request,) + args

            elif '*' in self.defaultTransitions.get('*', []):
                # This is like we had set the defaultTransitions to None.
                # Any state can transit to any other state
                return (request,) + args

            # If self.defaultTransitions is not None, it is an error
            # to request a direct state transition (capital letter
            # request) not listed in defaultTransitions and not
            # handled by an earlier filter.
            if request[0].isupper():
                raise RequestDenied("%s (from state: %s)" % (request, self.state))

        # In either case, we quietly ignore unhandled command
        # (lowercase) requests.
        assert self.notify.debug("%s ignoring request %s from state %s." % (self._name, request, self.state))
        return None

    def find(self, searchString):
        return Actor.find(self, searchString)

    def hide(self):
        Actor.hide(self)
        if self.getConfig("use_simple_shadow"):
            self.shadow.hide()

    def show(self):
        Actor.show(self)
        if self.getConfig("use_simple_shadow"):
            self.shadow.show()

    def catchCursor(self):
        # center the mouse in the middle of the window
        base.win.movePointer(0, self.getConfig("win_width_half"), self.getConfig("win_height_half"))
        # Set mouse mode to relative which should work best for our purpose
        wp = WindowProperties()
        # As the M_relative mouse mode breaks the mouse handling code,
        # we simply keep the absolute mode for that.
        if base.pipe.getInterfaceName() != "TinyPanda":
            wp.setMouseMode(WindowProperties.M_relative)
        else:
            wp.setMouseMode(WindowProperties.M_absolute)
        base.win.requestProperties(wp)

    def freeCursor(self):
        # free the cursor
        wp = WindowProperties()
        wp.setMouseMode(WindowProperties.M_absolute)
        base.win.requestProperties(wp)

    def changeCameraSystem(self, mode, initMode=False):
        active_anim = None
        if not initMode:
            self.camera_handler.centerCamera()
            self.camera_handler.stopCamera()
            active_anim = self.getCurrentAnim()
            active_anim_frame = self.getCurrentFrame(active_anim)
        if mode == "firstperson":
            self.setConfig("first_pserson_mode", True)
            logging.info("INIT FIRST PERSON CAMERA...")
            self.cam_near_clip = self.getConfig("cam_near_clip_default_firstperson")
            self.cam_fov = self.getConfig("cam_fov_default_firstperson")
            self.mouse_speed_x = self.getConfig("mouse_speed_x_default_firsrperson")
            self.mouse_speed_y = self.getConfig("mouse_speed_y_default_firsrperson")
            self.keyboard_cam_speed_x = self.getConfig("keyboard_cam_speed_x_default_firsrperson")
            self.keyboard_cam_speed_y = self.getConfig("keyboard_cam_speed_y_default_firsrperson")
            self.camera_handler = CameraFirstPerson(
                self,
                self.cam_near_clip,
                self.getConfig("cam_far_clip"),
                self.cam_fov)
            self.loadAnims({
                self.IDLE: self.getConfig("anim_idle_fp"),
                self.WALK: self.getConfig("anim_walk_fp"),
                self.RUN: self.getConfig("anim_run_fp"),
                self.SPRINT: self.getConfig("anim_sprint_fp"),
                self.JUMP_START: self.getConfig("anim_jumpstart_fp"),
                self.JUMP_LAND: self.getConfig("anim_jumpland_fp"),
                self.FALL: self.getConfig("anim_falling_fp"),
                self.CROUCH: self.getConfig("anim_crouch_move_fp"),
                self.CROUCH_IDLE: self.getConfig("anim_crouch_idle_fp"),
                self.CRAWL: self.getConfig("anim_crawl_move_fp"),
                self.CRAWL_IDLE: self.getConfig("anim_crawl_idle_fp"),
                self.ROLL: self.getConfig("anim_roll_fp"),})

        elif mode == "thirdperson":
            self.setConfig("first_pserson_mode", False)
            logging.info("INIT THIRD PERSON CAMERA...")
            self.cam_near_clip = self.getConfig("cam_near_clip_default_thirdperson")
            self.cam_fov = self.getConfig("cam_fov_default_thirdperson")
            self.mouse_speed_x = self.getConfig("mouse_speed_x_default_thirdperson")
            self.mouse_speed_y = self.getConfig("mouse_speed_y_default_thirdperson")
            self.keyboard_cam_speed_x = self.getConfig("keyboard_cam_speed_x_default_thirdperson")
            self.keyboard_cam_speed_y = self.getConfig("keyboard_cam_speed_y_default_thirdperson")
            self.camera_handler = CameraThirdPerson(
                self,
                self.cam_near_clip,
                self.getConfig("cam_far_clip"),
                self.cam_fov)
            self.loadAnims({
                self.IDLE: self.getConfig("anim_idle"),
                self.WALK: self.getConfig("anim_walk"),
                self.RUN: self.getConfig("anim_run"),
                self.SPRINT: self.getConfig("anim_sprint"),
                self.JUMP_START: self.getConfig("anim_jumpstart"),
                self.JUMP_LAND: self.getConfig("anim_jumpland"),
                self.FALL: self.getConfig("anim_falling"),
                self.CROUCH: self.getConfig("anim_crouch_move"),
                self.CROUCH_IDLE: self.getConfig("anim_crouch_idle"),
                self.CRAWL: self.getConfig("anim_crawl_move"),
                self.CRAWL_IDLE: self.getConfig("anim_crawl_idle"),
                self.ROLL: self.getConfig("anim_roll"),})
        else:
            logging.error("Unknown camera mode!")
        # "preload" all animations of the character
        self.bindAllAnims()
        if not initMode:
            # reset the anim after we swapped animations
            self.loop(active_anim, restart = active_anim_frame)
            self.camera_handler.startCamera()
            self.camera_handler.centerCamera()

    def startPlayer(self):
        logging.debug("start player...")
        self.show()
        self.request(self.STATE_IDLE)
        logging.debug("...start physics...")
        self.startPhysics()
        logging.debug("...start control...")
        self.startControl()
        logging.debug("...start camera...")
        self.camera_handler.startCamera()
        self.camera_handler.centerCamera()
        logging.debug("...player started")
        self.catchCursor()

    def stopPlayer(self):
        logging.debug("stop player...")
        logging.debug("...stop control...")
        self.stopControl()
        logging.debug("...stop camera...")
        self.camera_handler.stopCamera()
        logging.debug("...stop base...")
        self.freeCursor()
        # remove the simple shadow
        self.shadow.removeNode()
        Animator.cleanup(self)
        # remove the actor
        Actor.cleanup(self)
        self.removeNode()
        logging.debug("...player stop")

    def pausePlayer(self):
        self.pauseControl()
        self.pauseAnimator()
        self.camera_handler.pauseCamera()
        self.freeCursor()

    def resumePlayer(self):
        self.catchCursor()
        self.startControl()
        self.resumeAnimator()
        self.camera_handler.resumeCamera()
        self.doStep()

    def plugin_registerState(self, state, toTransitionStates=[], fromTransitionStates=[], isOnGround=False, isFlying=False, isIgnoreInput=False, fromAnyState=False, isPreventRotation=False, isPreventJump=False):
        if state in self.defaultTransitions:
            self.defaultTransitions[state].append(toTransitionStates)
        else:
            self.defaultTransitions[state] = toTransitionStates

        for fromState in fromTransitionStates:
            self.defaultTransitions[fromState] + toTransitionStates

        if fromAnyState:
            self.defaultTransitions["*"].append(state)

        if isOnGround:
            self.on_ground_states.append(state)

        if isFlying:
            self.ignore_step_states.append(state)

        if isIgnoreInput:
            self.ignore_input_states.append(state)

        if isPreventRotation:
            self.prevent_rotation_states.append(state)

        if isPreventJump:
            self.prevent_jump_states.append(state)

    def plugin_addStateTransition(self, state, transitions):
        self.defaultTransitions[state] += transitions

    def plugin_setCurrentAnimationPlayRate(self,rate):
        self.setCurrentAnimsPlayRate(rate)

    def plugin_requestNewState(self, state):
        if self.state != state:
            self.plugin_defined_character_state = state
            max_cam_shake_force = self.getConfig("cam_shake_max_landing_force")
            if state is self.STATE_LAND:
                shake = max(self.landing_force.getZ(), -max_cam_shake_force)
                shake = shake / max_cam_shake_force
                shake = shake * self.getConfig("cam_shake_max_strenght")
                self.camera_handler.camShakeNod(shake)

    def plugin_getRequestedNewState(self):
        return self.plugin_defined_character_state

    def enterNewState(self):
        self.prev_state = self.state
        if self.plugin_defined_character_state is not None:
            self.request(self.plugin_defined_character_state)
        self.plugin_defined_character_state = None

    def plugin_setPos(self, pos):
        self.main_node.setPos(pos)
        if self.getConfig("use_simple_shadow"):
            self.shadow.setPos(pos)
        self.updatePhysics()

    def plugin_getPos(self, relTo=None):
        if relTo is not None:
            return self.main_node.getPos(relTo)
        return self.main_node.getPos()

    def plugin_getMoveDirection(self):
        return self.movementVec

    def plugin_setMoveDirection(self, direction):
        self.movementVec = direction

    def calcMoveDirection(self):
        maxVec = Vec3()
        for plugin in self.inputPlugins:
            if plugin.active:
                plugVec = plugin.getMovementVec()
                if abs(plugVec.getX()) > abs(maxVec.getX()):
                    maxVec.setX(plugVec.getX())

                if abs(plugVec.getY()) > abs(maxVec.getY()):
                    maxVec.setY(plugVec.getY())

                if abs(plugVec.getZ()) > abs(maxVec.getZ()):
                    maxVec.setZ(plugVec.getZ())

        self.plugin_setMoveDirection(maxVec)

    def plugin_getHpr(self):
        return self.main_node.getHpr()

    def plugin_setHpr(self, hpr):
        self.main_node.setHpr(hpr)

    def plugin_requestFly(self):
        self.request_fly_mode = True

    def plugin_getFallForce(self):
        return self.getFallForce()

    def plugin_registerCharacterRayCheck(self, ray_id, pos_a, pos_b, ignore_ray_cycles=False):
        self.registerRayCheck(ray_id, pos_a, pos_b, self.main_node, ignore_ray_cycles)

    def plugin_isFirstPersonMode(self):
        return self.getConfig("first_pserson_mode")

    def setStartPos(self, startPos):
        self.plugin_setPos(startPos)

    def setStartHpr(self, startHpr):
        self.plugin_setHpr(startHpr)

