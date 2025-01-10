from enum import Enum

BEAT_OFFSET = 1.5
FRAME_IN_MSEC = 16 + 2 / 3
ONBEAT_THRESHOLD = 0.95
# number of significant digits after decimal point when round()
NDIGITS = 12

ROWS = 9
LANES = 3

WYRM_BODY_SCORE = 333
PERF_BONUS_SCORE_MULT = 0.72
TRUE_PERF_BONUS_SCORE_MULT = 0.18

GREEN_SLIME = "Green Slime"
BLUE_SLIME = "Blue Slime"
YELLOW_SLIME = "Yellow Slime"
BLUE_BAT = "Blue Bat"
YELLOW_BAT = "Yellow Bat"
RED_BAT = "Red Bat"
GREEN_ZOMBIE = "Green Zombie"
BLUE_ZOMBIE = "Blue Zombie"
RED_ZOMBIE = "Red Zombie"
BASE_SKELETON = "Base Skeleton"
SHIELDED_BASE_SKELETON = "Shielded Base Skeleton"
TRIPLE_SHIELD_BASE_SKELETON = "Triple Shield Base Skeleton"
BLUE_ARMADILLO = "Blue Armadillo"
RED_ARMADILLO = "Red Armadillo"
YELLOW_ARMADILLO = "Yellow Armadillo"
YELLOW_SKELETON = "Yellow Skeleton"
SHIELDED_YELLOW_SKELETON = "Shielded Yellow Skeleton"
BLACK_SKELETON = "Black Skeleton"
SHIELDED_BLACK_SKELETON = "Shielded Black Skeleton"
BASE_WYRM = "Base Wyrm"
BASE_HARPY = "Base Harpy"
RED_HARPY = "Red Harpy"
BLUE_HARPY = "Blue Harpy"
APPLE = "Apple"
CHEESE = "Cheese"
DRUMSTICK = "Drumstick"
HAM = "Ham"
BASE_BLADEMASTER = "Base Blademaster"
STRONG_BLADEMASTER = "Strong Blademaster"
YELLOW_BLADEMASTER = "Yellow Blademaster"
BASE_SKULL = "Base Skull"
BLUE_SKULL = "Blue Skull"
RED_SKULL = "Red Skull"

BOUNCE = "Bounce"
PORTAL = "PortalIn"
COALS = "Coals"


class Facing(Enum):
    LEFT = 0
    RIGHT = 1


class TrapDir(Enum):
    UP = 0
    RIGHT = 1
    LEFT = 2
    DOWN = 3
    UPLEFT = 4
    UPRIGHT = 5
    DOWNLEFT = 6
    DOWNRIGHT = 7
