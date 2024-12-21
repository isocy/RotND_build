from Shared.RhythmEngine import *
from Shared import *


class VibeChainStartData:
    def __init__(self, vibeChainEventId, vibeChainStartBeat, vibeChainEndBeat):
        self.vibeChainEventId = vibeChainEventId
        self.vibeChainStartBeat = vibeChainStartBeat
        self.vibeChainEndBeat = vibeChainEndBeat


class RRBeatmapPlayer(BeatmapPlayer):
    def __init__(self, beatmap, _sampleRate=60):
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
        self._haveVibeChainEnemiesReachedActionRow = False
        self._finalVibeChainBeat = 0.0
        self._numVibeChainEnemiesLeft = -1
        self._maxVibePower = 100
        self._currentVibePower = 0.0
        self._percentOfMaxVibePowerRequiredToActivate = 50
        self._percentOfMaxVibePowerLostPerSecond = 10

        self._minVibePowerToActivate = int(
            self._maxVibePower * (self._percentOfMaxVibePowerRequiredToActivate / 100.0)
        )
        self._calculatedVibePowerDecayPerSecond = self._maxVibePower * (
            self._percentOfMaxVibePowerLostPerSecond / 100.0
        )

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
        if (
            self._haveVibeChainEnemiesReachedActionRow
            and self._numVibeChainEnemiesLeft < 1
        ):
            self._haveVibeChainEnemiesReachedActionRow = False
        if self._isVibeChainActive:
            if self._currentVibePower > 0.0:
                self._currentVibePower -= (
                    1 / self._beatmapPlayer.SampleRate
                ) * self._calculatedVibePowerDecayPerSecond
                if self._currentVibePower < 0.0:
                    self._currentVibePower = 0.0
                if self._currentVibePower == 0.0:
                    num1 = 1 / fmodTimeCapsule.BeatDivisions
                    pass
        # TODO
