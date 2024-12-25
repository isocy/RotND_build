from typing import Self
from enum import Enum

BEAT_OFFSET = 1.5
ROWS = 9
LANES = 3

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

ENEMY_DB_PATH = "exports/bundles/RREnemyDatabase.json"

DISCO_DISASTER_EASY_PATH = (
    "exports/unity3d/beatmaps/rhythmrift/RhythmRift_DiscoDisaster_Easy"
)


class Facing(Enum):
    LEFT = 0
    RIGHT = 1
