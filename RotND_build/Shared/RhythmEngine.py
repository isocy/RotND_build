from __future__ import annotations

from Shared import InputRating
from UnityEngine import *

from abc import ABC, abstractmethod
from enum import Enum
import json


class Beatmap:
    def __init__(self, bpm, events, beatDivisions=2, beatTimings=None):
        self.bpm = bpm
        self.beatDivisions = beatDivisions
        self.events: list[BeatmapEvent] = events
        self.beatTimings = beatTimings

        self.endBeatNumberBacking = -1.0
        self.beatmapEventsBacking: list[BeatmapEvent] = {}

    def EndBeatNumber(self):
        if self.endBeatNumberBacking >= 0.0:
            return self.endBeatNumberBacking

        num = 0.0
        for event in self.events:
            if event.endBeatNumber >= num:
                num = event.endBeatNumber

        self.endBeatNumberBacking = num
        return self.endBeatNumberBacking

    def BeatLengthInSeconds(self):
        return 60.0 / self.bpm

    def OriginalDuration(self):
        if self.beatTimings:
            return self.beatTimings[len(self.beatTimings) - 1]
        return self.EndBeatNumber() * self.BeatLengthInSeconds()

    def DurationInBeats(self):
        if self.beatTimings:
            return len(self.beatTimings)
        return self.OriginalDuration() / self.BeatLengthInSeconds()

    def NumBeatmapEvents(self):
        return len(self.beatmapEventsBacking)

    def BeatmapEvents(self):
        return self.beatmapEventsBacking

    @classmethod
    def LoadFromJson(cls, path) -> Beatmap:
        with open(path) as f:
            beatmap: dict = json.load(f)
        beatmap: Beatmap = Beatmap(
            beatmap["bpm"],
            [
                BeatmapEvent(
                    event["track"],
                    event["startBeatNumber"],
                    event["endBeatNumber"],
                    event["type"],
                    [BeatmapEventDataPair(**pair) for pair in event["dataPairs"]],
                )
                for event in beatmap["events"]
            ],
            beatmap["beatDivisions"],
            beatmap["BeatTimings"],
        )

        for event_idx in range(len(beatmap.events)):
            event = beatmap.events[event_idx]
            event.InitializeEventDataDictionary()
            beatmap.events[event_idx] = event

        beatmap.beatmapEventsBacking = beatmap.events
        return beatmap


class BeatmapEvent:
    def __init__(self, track, startBeatNumber, endBeatNumber, type, dataPairs):
        self.track = track
        self.startBeatNumber = startBeatNumber
        self.endBeatNumber = endBeatNumber
        self.type = type
        self.dataPairs: list[BeatmapEventDataPair] = dataPairs

        self._data: dict[str, list[str]] = None

    def GetFirstEventDataAsString(self, dataKey):
        if self._data and dataKey in self._data:
            return next((dataVal for dataVal in self._data[dataKey] if dataVal), "")
        return ""

    def GetFirstEventDataAsInt(self, dataKey):
        eventDataAsString = self.GetFirstEventDataAsString(dataKey)
        try:
            result = int(eventDataAsString)
            return result
        except (TypeError, ValueError):
            return None

    def GetFirstEventDataAsBool(self, dataKey):
        eventDataAsString = self.GetFirstEventDataAsString(dataKey)
        try:
            result = bool(eventDataAsString)
            return result
        except (TypeError, ValueError):
            return None

    def AddEventData(self, dataKey, dataValue):
        if not self._data:
            self._data = {}
        if dataKey in self._data:
            self._data[dataKey].append(dataValue)
        else:
            self._data[dataKey] = [dataValue]

    def InitializeEventDataDictionary(self):
        self._data = {}
        for dataPair in self.dataPairs:
            if dataPair.EventDataKey() and dataPair.EventDataValue():
                self.AddEventData(dataPair.EventDataKey(), dataPair.EventDataValue())


class BeatmapEventDataPair:
    def __init__(self, _eventDataKey, _eventDataValue):
        self._eventDataKey = _eventDataKey
        self._eventDataValue = _eventDataValue

    def EventDataKey(self):
        return self._eventDataKey

    def EventDataValue(self):
        return self._eventDataValue


class BeatmapPlayer(MonoBehaviour):
    SingleInstance = None

    def __init__(self, _inputRatingsBpmMapping):
        self._currentBpm = -1
        self._activeBeatDivisions = 2

        self._previousFmodTime = 0
        self._activeBeatmapBeatTimingIndex = 0

        self._inputRatingsBpmMapping: InputRatingsBpmMapping = _inputRatingsBpmMapping

        self.Awake()

    def ActiveInputRatingsDefinition(self):
        return self._inputRatingsBpmMapping.GetInputRatingsDefinitionForBpm(
            self._currentBpm
        )

    def Awake(self):
        if BeatmapPlayer.SingleInstance == None:
            BeatmapPlayer.SingleInstance = self

    def CalculateCurrentTrueBeatNumber(self, currentTime):
        beatmap = self._activeBeatmap
        activeBeatTimings = beatmap.beatTimings
        timing_cnt = len(activeBeatTimings)
        if activeBeatTimings:
            last_beatDiff = (
                activeBeatTimings[timing_cnt - 1] - activeBeatTimings[timing_cnt - 2]
            )
            if self._activeBeatmapBeatTimingIndex >= timing_cnt:
                excessed_idx = self._activeBeatmapBeatTimingIndex - (timing_cnt - 1)
                cur_extendedBeatTiming = (
                    activeBeatTimings[timing_cnt - 1] + excessed_idx * last_beatDiff
                )
                next_extendedBeatTiming = cur_extendedBeatTiming + last_beatDiff

                if currentTime >= next_extendedBeatTiming:
                    self._activeBeatmapBeatTimingIndex += 1
                    currentTrueBeatNumber = (
                        1.0
                        + self._activeBeatmapBeatTimingIndex
                        + (currentTime - next_extendedBeatTiming) / last_beatDiff
                    )
                else:
                    currentTrueBeatNumber = (
                        1.0
                        + self._activeBeatmapBeatTimingIndex
                        + (currentTime - cur_extendedBeatTiming) / last_beatDiff
                    )
            else:
                cur_beatTiming = activeBeatTimings[self._activeBeatmapBeatTimingIndex]
                if self._activeBeatmapBeatTimingIndex == timing_cnt - 1:
                    next_beatTiming = cur_beatTiming + last_beatDiff
                else:
                    next_beatTiming = activeBeatTimings[
                        self._activeBeatmapBeatTimingIndex + 1
                    ]

                if currentTime >= next_beatTiming:
                    self._activeBeatmapBeatTimingIndex += 1
                    if self._activeBeatmapBeatTimingIndex >= timing_cnt - 1:
                        cur_beatDiff = next_beatTiming - cur_beatTiming
                        cur_beatTiming = next_beatTiming
                        next_beatTiming += cur_beatDiff
                    else:
                        cur_beatTiming = next_beatTiming
                        next_beatTiming = activeBeatTimings[
                            self._activeBeatmapBeatTimingIndex + 1
                        ]

                cur_beatDiff = next_beatTiming - cur_beatTiming
                currentTrueBeatNumber = (
                    1.0
                    + self._activeBeatmapBeatTimingIndex
                    + (currentTime - cur_beatTiming) / cur_beatDiff
                )
        else:
            currentTrueBeatNumber = 1.0 + currentTime * beatmap.bpm / 60.0
        return currentTrueBeatNumber

    @property
    def CurrentBeatmapStartBeatNum(self):
        return 1

    def GetCurrentBeatLengthInSeconds(self, currentBeatNumber: int):
        beatTimings = self._activeBeatmap.beatTimings
        if beatTimings and currentBeatNumber < len(beatTimings):
            return beatTimings[currentBeatNumber] - beatTimings[currentBeatNumber - 1]
        return 60.0 / self._activeBeatmap.bpm

    def HasActiveBeatmap(self):
        return self._activeBeatmap != None

    @classmethod
    def LoadFromJson(cls, map_path, map_paths) -> BeatmapPlayer:
        return BeatmapPlayer(InputRatingsBpmMapping.LoadFromJson(map_path, map_paths))

    def ProcessBeatEvents(self, currentTime):
        activeBeatmap = self._activeBeatmap
        cur_beat = self.FmodTimeCapsule.TrueBeatNumber - 1
        while self._beatEventIndex < activeBeatmap.NumBeatmapEvents():
            beatmapEvent: BeatmapEvent = activeBeatmap.BeatmapEvents()[
                self._beatEventIndex
            ]
            if beatmapEvent.startBeatNumber <= cur_beat:
                if cur_beat <= beatmapEvent.endBeatNumber:
                    pass

    def Update(self, cur_frame):
        cur_time = cur_frame * Time.deltaTime
        currentTrueBeatNumber = self.CalculateCurrentTrueBeatNumber(cur_time)
        self.FmodTimeCapsule = FmodTimeCapsule(
            cur_time,
            cur_time - self._previousFmodTime,
            self.GetCurrentBeatLengthInSeconds(int(currentTrueBeatNumber)),
            currentTrueBeatNumber,
            self._activeBeatDivisions,
        )
        self._previousFmodTime = cur_time
        if (
            currentTrueBeatNumber - self.CurrentBeatmapStartBeatNum
            > self._activeBeatmap.DurationInBeats()
        ):
            self._activeBeatmap = None
            return
        if self.HasActiveBeatmap():
            self.ProcessBeatEvents(cur_time)
            # TODO


class BeatTrackLaneDesignation(Enum):
    Left = 1
    Mid = 2
    Right = 3


class FmodTimeCapsule:
    def __init__(
        self, Time, DeltaTime, BeatLengthInSeconds, TrueBeatNumber, BeatDivisions
    ):
        self.Time = Time
        self.DeltaTime = DeltaTime
        self.BeatLengthInSeconds = BeatLengthInSeconds
        self.TrueBeatNumber = TrueBeatNumber
        self.BeatDivisions = BeatDivisions


class IFmodTimeSystem(ABC):
    @abstractmethod
    def UpdateSystem(self, fmodTimeCapsule):
        pass


class InputRatingsDefinition:
    class Rating:
        def __init__(self, inputRating, minimumValue, score):
            self.inputRating = inputRating
            self.minimumValue = max(0, min(100, minimumValue))
            self.score = score

    def __init__(
        self,
        _ratings,
        _beforeBeatHitWindow=0.5,
        _afterBeatHitWindow=0.5,
        _onBeatMinimumValue=90,
        _truePerfectBonusMinimumValue=90,
        _perfectBonusScore=1,
        _truePerfectBonusScore=2,
    ):
        self._beforeBeatHitWindow = max(0, min(1, _beforeBeatHitWindow))
        self._afterBeatHitWindow = max(0, min(1, _afterBeatHitWindow))
        self._ratings: list[InputRatingsDefinition.Rating] = _ratings
        self._onBeatMinimumValue = _onBeatMinimumValue
        self._truePerfectBonusMinimumValue = _truePerfectBonusMinimumValue
        self._perfectBonusScore = _perfectBonusScore
        self._truePerfectBonusScore = _truePerfectBonusScore

        self._precalcRatings = {}
        self.PrecalculateRatings()

        self.OnValidate()

    def OnValidate(self):
        assert self._beforeBeatHitWindow + self._afterBeatHitWindow <= 1.001

    def PrecalculateRatings(self):
        self._precalcRatings = {}
        for inputRating in InputRating:
            present_rating = next(
                (
                    rating
                    for rating in self._ratings
                    if rating.inputRating == inputRating
                ),
                None,
            )
            if present_rating != None:
                self._precalcRatings[inputRating] = present_rating

    @classmethod
    def LoadFromJson(cls, path) -> InputRatingsDefinition:
        with open(path) as f:
            input_ratings_definition: dict = json.load(f)
        return InputRatingsDefinition(
            [cls.Rating(**rating) for rating in input_ratings_definition["_ratings"]],
            input_ratings_definition["_beforeBeatHitWindow"],
            input_ratings_definition["_afterBeatHitWindow"],
            input_ratings_definition["_onBeatMinimumValue"],
            input_ratings_definition["_truePerfectBonusMinimumValue"],
            input_ratings_definition["_perfectBonusScore"],
            input_ratings_definition["_truePerfectBonusScore"],
        )


class InputRatingsBpmMapping:
    class InputRatingBpmPair:
        def __init__(self, MinimumBpm, InputRatingsDefinition):
            self.MinimumBpm = MinimumBpm
            self.InputRatingsDefinition = InputRatingsDefinition

    def __init__(
        self, _inputRatingBpmPairs: list[InputRatingsBpmMapping.InputRatingBpmPair]
    ):
        self._inputRatingBpmPairs = _inputRatingBpmPairs

    def GetInputRatingsDefinitionForBpm(self, bpm):
        if len(self._inputRatingBpmPairs) < 1:
            return None

        index = 0
        while (
            index < len(self._inputRatingBpmPairs)
            and self._inputRatingBpmPairs[index].MinimumBpm <= bpm
        ):
            index += 1
        index -= 1

        return self._inputRatingBpmPairs[index].InputRatingsDefinition

    @classmethod
    def LoadFromJson(cls, path, map_paths) -> InputRatingsBpmMapping:
        with open(path) as f:
            input_ratings_bpm_pairs: dict = json.load(f)["_inputRatingBpmPairs"]

        _inputRatingBpmPairs = []
        for pair_idx in range(len(input_ratings_bpm_pairs)):
            input_rating_bpm_pair = input_ratings_bpm_pairs[pair_idx]
            MinimumBpm = input_rating_bpm_pair["MinimumBpm"]
            input_ratings_def = InputRatingsDefinition.LoadFromJson(map_paths[pair_idx])
            _inputRatingBpmPairs.append(
                cls.InputRatingBpmPair(MinimumBpm, input_ratings_def)
            )

        return InputRatingsBpmMapping(_inputRatingBpmPairs)


class MonoBehaviourFmodSystem(MonoBehaviour, IFmodTimeSystem, ABC):
    @abstractmethod
    def UpdateSystem(self, fmodTimeCapsule):
        pass


class Object:
    pass


class ScriptableObject(Object):
    pass


class SpawnEnemyData:
    def __init__(
        self,
        EnemyId,
        LaneDesignation,
        SpawnTrueBeatNumber,
        ItemToDropOnDeathId,
        ShouldSpawnAsVibeChain,
        BlademasterAttackRow,
    ):
        self.EnemyId = EnemyId
        self.LaneDesignation = LaneDesignation
        self.SpawnTrueBeatNumber = SpawnTrueBeatNumber
        self.ItemToDropOnDeathId = ItemToDropOnDeathId
        self.ShouldSpawnAsVibeChain = ShouldSpawnAsVibeChain
        self.BlademasterAttackRow = BlademasterAttackRow


class StageInputRecord:
    def __init__(self, stageScoringDefinition, inputRatingsDefinition):
        self._stageScoringDefinition = stageScoringDefinition
        self._inputRatingsDefinition = inputRatingsDefinition


class StageScoringDefinition:
    def __init__(
        self,
        _consecutiveHitsForComboStart,
        _consecutiveHitsForComboMultiplierIncrease,
        _maximumComboMultiplier,
        _holdNotePerBeatHeldBonus,
        _vibePowerScoreMultiplier,
    ):
        self._consecutiveHitsForComboStart = _consecutiveHitsForComboStart
        self._consecutiveHitsForComboMultiplierIncrease = (
            _consecutiveHitsForComboMultiplierIncrease
        )
        self._maximumComboMultiplier = _maximumComboMultiplier
        self._holdNotePerBeatHeldBonus = _holdNotePerBeatHeldBonus
        self._vibePowerScoreMultiplier = _vibePowerScoreMultiplier

    @classmethod
    def LoadFromJson(cls, path) -> StageScoringDefinition:
        with open(path) as f:
            stage_scoring_def = json.load(f)
        return StageScoringDefinition(
            stage_scoring_def["_consecutiveHitsForComboStart"],
            stage_scoring_def["_consecutiveHitsForComboMultiplierIncrease"],
            stage_scoring_def["_maximumComboMultiplier"],
            stage_scoring_def["_holdNotePerBeatHeldBonus"],
            stage_scoring_def["_vibePowerScoreMultiplier"],
        )
