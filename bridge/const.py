"""
Определение необходимых констант
"""

from enum import Enum


class State(Enum):
    """Класс с состояниями игры"""

    HALT = 0
    TIMEOUT = 1
    STOP = 2
    PREPARE_KICKOFF = 3
    BALL_PLACEMENT = 4
    PREPARE_PENALTY = 5
    KICKOFF = 6
    FREE_KICK = 7
    PENALTY = 8
    RUN = 9


class Color(Enum):
    """Класс с цветами"""

    ALL = 0
    BLUE = 1
    YELLOW = 2

    def reverse(self) -> "Color":
        """Returns another color"""
        if self == Color.BLUE:
            return Color.YELLOW
        if self == Color.YELLOW:
            return Color.BLUE
        return Color.ALL


class Div(Enum):
    """Класс с разными дивизионами"""

    A = 0  # XD
    B = 1
    C = 2


##################################################
# GAME SETTING CONSTS
DIV = Div.C
COLOR = Color.BLUE
POLARITY = 1  # -1 если ворота синих на +x; 1 если ворота синих на -x

IS_SIMULATOR_USED = True
SELF_PLAY = False

DEBUG_HALF = 0  # 1 = +x, -1 = -x, 0 = not debug

GK = 5
ENEMY_GK = 5

ROBOTS_MAX_COUNT: int = 32
TEAM_ROBOTS_MAX_COUNT: int = ROBOTS_MAX_COUNT // 2
GEOMETRY_PACKET_SIZE: int = 2

CONTROL_MAPPING: dict[int, int] = {
    # vision_id: control_id,
    # 0: 8,
    # 1: 9,
    # 2: 10,
    # 3: 11,
    # 4: 12,
    # 5: 13,
    # 6: 14,
    # 7: 15,
    # 8: 0,
    # 9: 1,
    # 10: 2,
    # 11: 3,
    # 12: 4,
    # 13: 5,
    # 14: 6,
    # 15: 7,
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
}
REVERSED_KICK: list[int] = []

for i in range(TEAM_ROBOTS_MAX_COUNT):
    try:
        CONTROL_MAPPING[i]
    except KeyError:
        CONTROL_MAPPING[i] = -1

CONTROL_TOPIC = "control-topic"
FIELD_TOPIC = "field-topic"
IMAGE_TOPIC = "image-topic"
##################################################

##################################################
# CONTROL CONST
Ts = 0.02  # s

# ROBOT SETTING CONSTS
MAX_SPEED = 2000 if not IS_SIMULATOR_USED else 1000
MAX_ACCELERATION = 5000
MAX_SPEED_R = 30
SOFT_MAX_SPEED = 500
SOFT_MAX_SPEED_R = 16

STOP_SPEED = 1000

INTERCEPT_SPEED = 50
##################################################
# GEOMETRY CONSTS

BALL_R = 22
ROBOT_R = 100
GRAVEYARD_POS_X = -10000

BALL_MAX_VISION_SPEED = 10000  # for filter random balls
ROBOT_MAX_VISION_SPEED = 10000  # for filter random robots
TIME_TO_BORN = 0.5  # time to add robot to field
TIME_TO_DIE = 0.5  # time to remove robot from field

match DIV:
    case Div.A:
        GOAL_DX = 1 / 0  # не дорос ещё

    case Div.B:
        GOAL_DX = 4500
        GOAL_DY = 1000
        GOAL_PEN_DX = 1000
        GOAL_PEN_DY = 2000

        PEN_DIST = 6000

        FIELD_DX = GOAL_DX
        FIELD_DY = 3000

        GK_FORW = 200 + ROBOT_R

    case Div.C:
        GOAL_DX = 2250
        GOAL_DY = 800
        GOAL_PEN_DX = 500
        GOAL_PEN_DY = 1350

        PEN_DIST = GOAL_DX

        FIELD_DX = GOAL_DX
        FIELD_DY = 1500

        GK_FORW = 100 + ROBOT_R


# ROUTE CONSTS
VIEW_DIST = 2500
KEEP_BALL_DIST = 300 + ROBOT_R

# is_ball_in
GRAB_ALIGN_DIST = 130
BALL_GRABBED_ANGLE = 0.8
BALL_GRABBED_DIST = 110
# is_kick_aligned
KICK_ALIGN_DIST_MULT = 1.5
KICK_ALIGN_ANGLE = 0.1
KICK_ALIGN_DIST = 150
KICK_ALIGN_OFFSET = 40

# for grabbing ball
GRAB_AREA = GRAB_ALIGN_DIST
# GRAB_DIST = 45  # 30 is good
GRAB_DIST = 70
GRAB_MULT = 5  # speed = dist * mult
GRAB_OFFSET_ANGLE = 0.55

if IS_SIMULATOR_USED:
    GRAB_ALIGN_DIST = 150
    BALL_GRABBED_DIST = 150
    GRAB_DIST = 85
    GRAB_MULT = 5
    GRAB_OFFSET_ANGLE = 0.35

# VOLTAGES
VOLTAGE_SHOOT = 15
VOLTAGE_UP = 15
VOLTAGE_ZERO = 12
