from Global.Path import *
from Global.const_def import *

RAW_BEATMAP_PATH = OVERTHINKER_IMPOSSIBLE_PATH

ONE_VIBE_START_BEATS_EXCEPT: list[float] = [
    239.5,
    240.5,
    241.5,
    242.5,
    243.5,
    244.5,
    275,
    283,
    291,
]  # remove 243.5 or 244.5 for tougher build (+444)
TWO_VIBES_START_BEATS_EXCEPT: list[float] = []
THREE_VIBES_START_BEATS_EXCEPT: list[float] = []

ONE_VIBE_START_BEATS_LOOSE: list[tuple[float, int]] = [(415.5, 1)]
TWO_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = []
THREE_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = []

TARGET_PARTITION: tuple[int, ...] = (2, 1, 1, 1)
GREAT_START_BEATS: list[tuple[float, int]] = [(243.5, 1), (244.5, 1)]
