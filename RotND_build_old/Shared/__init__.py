from __future__ import annotations

from RhythmRift import RREnemyController
from RhythmRift.Traps import RRTrapController

from enum import Enum
import json


class InputRating(Enum):
    Miss = -1
    Ok = 0
    Good = 1
    Great = 2
    Perfect = 3


class StageController[T: BeatmapPlayer]:
    def __init__(
        self, _beatmapPlayer: T, _fmodSystemsToUpdate, _stageScoringDefinition
    ):
        self._beatmapPlayer = _beatmapPlayer
        self._fmodSystemsToUpdate = _fmodSystemsToUpdate
        self._stageScoringDefinition = _stageScoringDefinition
        # TODO

    def Awake(self):
        self._stageInputRecord = StageInputRecord(
            self._stageScoringDefinition,
            self.BeatmapPlayer.ActiveInputRatingsDefinition(),
        )

    @property
    def BeatmapPlayer(self):
        return self._beatmapPlayer

    @classmethod
    def LoadFromJson(cls, path) -> StageController:
        with open(path) as f:
            stage_controller: dict = json.load(f)

        # TODO
        _fmodSystemsToUpdate = [RRTrapController(), RREnemyController()]

    def OnEnable(self):
        if self._beatmapPlayer:
            # TODO
            pass
