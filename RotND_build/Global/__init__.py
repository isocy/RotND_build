from Global.const_def import *

RAW_BEATMAP_PATH = RAVEVENGE_IMPOSSIBLE_PATH

ONE_VIBE_START_BEATS_EXCEPT: list[float] = [
    587.5,
    653.5,
    741.5,
    743.5,
]  # remove 587.5 for tougher build (+444)
TWO_VIBES_START_BEATS_EXCEPT: list[float] = [357.5, 359.5]
THREE_VIBES_START_BEATS_EXCEPT: list[float] = []

ONE_VIBE_START_BEATS_LOOSE: list[tuple[float, int]] = [(587, 3), (741.5, 1)]
TWO_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = [(358.5, 1)]
THREE_VIBES_START_BEATS_LOOSE: list[tuple[float, int]] = []

TARGET_PARTITION: tuple[int, ...] = (1, 2, 1, 1, 1)
GREAT_START_BEATS: list[tuple[float, int]] = [(93.5, 1), (587.5, 1)]
