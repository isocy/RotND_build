import Shared.RhythmEngine


class StageController[T: Shared.RhythmEngine.BeatmapPlayer]:
    def __init__(self, _beatmapPlayer: T):
        self._beatmapPlayer = _beatmapPlayer

    def BeatmapPlayer(self):
        return self._beatmapPlayer
