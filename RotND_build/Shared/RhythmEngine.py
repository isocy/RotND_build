import json
from typing import Self
from enum import Enum


class FmodTimeCapsule:
    def __init__(self, Time, DeltaTime, BeatLengthInSeconds, TrueBeatNumber):
        self.Time = Time
        self.DeltaTime = DeltaTime
        self.BeatLengthInSeconds = BeatLengthInSeconds
        self.TrueBeatNumber = TrueBeatNumber


class BeatTrackLaneDesignation(Enum):
    Left = 1
    Mid = 2
    Right = 3


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


class BeatmapEventDataPair:
    def __init__(self, _eventDataKey, _eventDataValue):
        self._eventDataKey = _eventDataKey
        self._eventDataValue = _eventDataValue

    def EventDataKey(self):
        return self._eventDataKey

    def EventDataValue(self):
        return self._eventDataValue


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


class BeatmapPlayer:
    def __init__(self, beatmap, _sampleRate):
        self._activeBeatmap: Beatmap = beatmap
        self.SampleRate = _sampleRate

        self._previousFmodTime = 0
        self._beatEventIndex = 0
        self._activeBeatmapBeatTimingIndex = 0

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

    def GetCurrentBeatLengthInSeconds(self, currentBeatNumber: int):
        beatTimings = self._activeBeatmap.beatTimings
        if beatTimings and currentBeatNumber < len(beatTimings):
            return beatTimings[currentBeatNumber] - beatTimings[currentBeatNumber - 1]
        return 60.0 / self._activeBeatmap.bpm

    def ProcessBeatEvents(self, currentTime):
        activeBeatmap = self._activeBeatmap
        cur_beat = self.FmodTimeCapsule.TrueBeatNumber - 1.0
        while self._beatEventIndex < activeBeatmap.NumBeatmapEvents():
            beatmapEvent: BeatmapEvent = activeBeatmap.BeatmapEvents()[
                self._beatEventIndex
            ]
            if beatmapEvent.startBeatNumber <= cur_beat:
                if cur_beat <= beatmapEvent.endBeatNumber:
                    pass

    def Update(self, cur_frame):
        cur_time = cur_frame * (1 / self.SampleRate)
        currentTrueBeatNumber = self.CalculateCurrentTrueBeatNumber(cur_time)
        self.FmodTimeCapsule = FmodTimeCapsule(
            cur_time,
            cur_time - self._previousFmodTime,
            self.GetCurrentBeatLengthInSeconds(int(currentTrueBeatNumber)),
            currentTrueBeatNumber,
        )
        if currentTrueBeatNumber - 1.0 > self._activeBeatmap.DurationInBeats():
            self._activeBeatmap = None
            return
        self.ProcessBeatEvents(cur_time)
        # TODO


class Beatmap:
    def __init__(self, bpm, events, beatDivision=2, beatTimings=None):
        self.bpm = bpm
        self.beatDivision = beatDivision
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
    def LoadFromJson(cls, path) -> Self:
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


class InputRatingsDefinition:
    def __init__(
        self,
        _beforeBeatHitWindow,
        _afterBeatHitWindow,
        _ratings,
        _onBeatMinimumValue,
        _truePerfectBonusMinimumValue,
        _perfectBonusScore,
        _truePerfectBonusScore,
    ):
        self.BeforeBeatHitWindow = _beforeBeatHitWindow
        self.AfterBeatHitWindow = _afterBeatHitWindow
        self._ratings = _ratings
        self._onBeatMinimumValue = _onBeatMinimumValue
        self._truePerfectBonusMinimumValue = _truePerfectBonusMinimumValue
        self._perfectBonusScore = _perfectBonusScore
        self._truePerfectBonusScore = _truePerfectBonusScore
