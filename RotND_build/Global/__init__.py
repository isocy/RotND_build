from Global.Path import *
from Global.const_def import *
from Global.input_ratings_def import *

RAW_BEATMAP_PATH = VISUALIZE_YOURSELF_HARD_PATH

ONE_VIBE_START_BEATS_EXCEPT: list[float] = []
TWO_VIBES_START_BEATS_EXCEPT: list[float] = []
THREE_VIBES_START_BEATS_EXCEPT: list[float] = []

ONE_VIBE_START_BEATS_LOOSE: list[tuple[float, int]] = [
    (229.5, 1),
    (230.5, 1),
    (231.5, 1),
    (232.5, 1),
    (237.5, 1),
    (238.5, 1),
    (239.5, 1),
    (240.5, 1),
    (245.5, 1),
    (246.5, 1),
    (247.5, 1),
    (248.5, 1),
]
TWO_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = [
    (253.5, 1),
    (254.5, 1),
    (255.5, 1),
    (256.5, 1),
    (257.5, 1),
    (258.5, 1),
    (259.5, 1),
    (260.5, 1),
    (261.5, 1),
]
THREE_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = []

TARGET_PARTITION: tuple[int, ...] = ()
GREAT_START_BEATS: list[tuple[float, int]] = []
