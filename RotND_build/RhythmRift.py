from Shared.RhythmEngine import *
from Shared import *
from events import Events


class VibeChainStartData:
    def __init__(self, vibeChainEventId, vibeChainStartBeat, vibeChainEndBeat):
        self.vibeChainEventId = vibeChainEventId
        self.vibeChainStartBeat = vibeChainStartBeat
        self.vibeChainEndBeat = vibeChainEndBeat


class RRBeatmapPlayer(BeatmapPlayer):
    def __init__(self, beatmap, _sampleRate):
        super(RRBeatmapPlayer, self).__init__(beatmap, _sampleRate)

        self.currentVibeChains: list[VibeChainStartData] = []

    def ProcessBeatEvent(
        self, currentTime, beatEvent: BeatmapEvent, isAddedEvent=False
    ):
        if beatEvent.type == "SpawnEnemy":
            EnemyId = beatEvent.GetFirstEventDataAsInt("EnemyId")
            if not EnemyId:
                return
            track = beatEvent.track
            if track not in BeatTrackLaneDesignation:
                return
            ItemToDropOnDeathId = beatEvent.GetFirstEventDataAsInt(
                "ItemToDropOnDeathId"
            )
            ItemToDropOnDeathId = ItemToDropOnDeathId if ItemToDropOnDeathId else -1
            SpawnTrueBeatNumber = 1.0 + beatEvent.startBeatNumber
            BlademasterAttackRow = beatEvent.GetFirstEventDataAsInt(
                "BlademasterAttackRow"
            )
            if BlademasterAttackRow == None:
                BlademasterAttackRow = -1
            ShouldExcludeFromVibeChain = beatEvent.GetFirstEventDataAsBool(
                "ShouldExcludeFromVibeChain"
            )
            ShouldSpawnAsVibeChain = (
                self.IsPartOfActiveVibeChain(beatEvent)
                and not ShouldExcludeFromVibeChain
            )

            spawnEnemyData = SpawnEnemyData(
                EnemyId,
                BeatTrackLaneDesignation(track),
                SpawnTrueBeatNumber,
                ItemToDropOnDeathId,
                ShouldSpawnAsVibeChain,
                BlademasterAttackRow,
            )
            # TODO

    def IsPartOfActiveVibeChain(self, enemySpawnEvent: BeatmapEvent):
        for currentVibeChain in self.currentVibeChains:
            true_beatNum = 1.0 + enemySpawnEvent.startBeatNumber
            if (
                true_beatNum >= currentVibeChain.vibeChainStartBeat
                and true_beatNum <= currentVibeChain.vibeChainEndBeat
            ):
                return True
        return False


class RREnemyController:
    pass


class RRStageController(StageController[RRBeatmapPlayer]):
    def __init__(self, _beatmapPlayer):
        super(RRStageController, self).__init__(_beatmapPlayer)

        self._isVibeChainActive = False
        self._finalVibeChainBeat = 0

    def HandleEnemySpawnBeatEvent(self, spawnEnemyData):
        pass

    def DeactivateVibeChain(self):
        self._isVibeChainActive = False

    def Update(self, cur_frame):
        fmodTimeCapsule = self.BeatmapPlayer().FmodTimeCapsule

        if (
            self._isVibeChainActive
            and fmodTimeCapsule.TrueBeatNumber >= self._finalVibeChainBeat
        ):
            self.DeactivateVibeChain()
        # TODO
