import Shared.RhythmEngine

from enum import Enum


class InputRating(Enum):
    Miss = -1
    Ok = 0
    Good = 1
    Great = 2
    Perfect = 3


class StageController[T: Shared.RhythmEngine.BeatmapPlayer]:
    def __init__(self, _beatmapPlayer: T):
        self._beatmapPlayer = _beatmapPlayer

        # TODO

    def BeatmapPlayer(self):
        return self._beatmapPlayer
