from Shared.RhythmEngine import *
from Shared import *
from UnityEngine import Time
from UnityEngine.AddressableAssets import AssetReference

from enum import Enum, auto


class VibeChainStartData:
    def __init__(self, vibeChainEventId, vibeChainStartBeat, vibeChainEndBeat):
        self.vibeChainEventId = vibeChainEventId
        self.vibeChainStartBeat = vibeChainStartBeat
        self.vibeChainEndBeat = vibeChainEndBeat


class RRBeatmapPlayer(BeatmapPlayer):
    def __init__(self):
        super(RRBeatmapPlayer, self).__init__(None)

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


class RREnemyController(MonoBehaviourFmodSystem):
    def __init__(self, _enemyDatabase):
        self._enemyDatabase = _enemyDatabase

    def UpdateSystem(self, fmodTimeCapsule):
        pass


class RREnemyDatabase(ScriptableObject):
    def __init__(self, _enemyDefinitions):
        self._enemyDefinitions = _enemyDefinitions

    @classmethod
    def LoadFromJson(self, path):
        with open(path) as f:
            _enemyDefinitions: dict = json.load(f)["_enemyDefinitions"]

        enemy_defs = []
        for enemy_def in _enemyDefinitions:
            prefab_ref = enemy_def["_prefabAssetReference"]
            held_prefab_ref = enemy_def["_heldPrefabAssetReference"]
            enemy_def = RREnemyDefinition(
                enemy_def["_id"],
                enemy_def["_displayName"],
                max(1, enemy_def["_maxHealth"]),
                max(0, enemy_def["_totalHitsAddedToStage"]),
                max(0, enemy_def["_totalEnemiesGenerated"]),
                max(0, enemy_def["_playerDamage"]),
                enemy_def["_hpAwardedOnDeath"],
                max(0, enemy_def["_updateTempoInBeats"]),
                max(1, enemy_def["_collisionPriority"]),
                enemy_def["_specialProperties"],
                enemy_def["_shieldHealth"],
                AssetReference(
                    prefab_ref["m_SubObjectName"],
                    prefab_ref["m_SubObjectType"],
                    prefab_ref["m_AssetGUID"],
                ),
                AssetReference(
                    held_prefab_ref["m_SubObjectName"],
                    held_prefab_ref["m_SubObjectType"],
                    held_prefab_ref["m_AssetGUID"],
                ),
                enemy_def["_bodyEnemyId"],
                enemy_def["_tailEnemyId"],
                enemy_def["_enemySpawnedOnDeathId"],
            )
            enemy_defs.append(enemy_def)

        return RREnemyDatabase(enemy_defs)


class RREnemyDefinition:
    def __init__(
        self,
        _id,
        _displayName,
        _maxHealth,
        _totalHitsAddedToStage,
        _totalEnemiesGenerated,
        _playerDamage,
        _hpAwardedOnDeath,
        _updateTempoInBeats,
        _collisionPriority,
        _specialProperties,
        _shieldHealth,
        _prefabAssetReference,
        _heldPrefabAssetReference,
        _bodyEnemyId,
        _tailEnemyId,
        _enemySpawnedOnDeathId,
    ):
        # TODO
        pass


class RRStageController(StageController[RRBeatmapPlayer]):
    def __init__(self):
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
        fmodTimeCapsule = self.BeatmapPlayer.FmodTimeCapsule

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
                    Time.deltaTime * self._calculatedVibePowerDecayPerSecond
                )
                if self._currentVibePower < 0.0:
                    self._currentVibePower = 0.0
                if self._currentVibePower == 0.0:
                    num1 = 1 / fmodTimeCapsule.BeatDivisions
                    pass
        # TODO


class RRTrapType(Enum):
    Coals = auto()
    PortalIn = auto()
    PortalOut = auto()
    Bounce = auto()
    Wind = auto()
    Freeze = auto()
