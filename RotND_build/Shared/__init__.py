from Shared.RhythmEngine import *

from enum import Enum


class InputRating(Enum):
    Miss = -1
    Ok = 0
    Good = 1
    Great = 2
    Perfect = 3


class StageController[T: BeatmapPlayer]:
    def __init__(self, _beatmapPlayer: T, _stageScoringDefinition):
        self._beatmapPlayer = _beatmapPlayer
        self._stageScoringDefinition = _stageScoringDefinition
        # TODO

    def Awake(self):
        # TODO
        # self._stageInputRecord = StageInputRecord(self._stageScoringDefinition, self.BeatmapPlayer().)
        pass

    def BeatmapPlayer(self):
        return self._beatmapPlayer

    def OnEnable(self):
        if self._beatmapPlayer:
            # TODO
            pass
