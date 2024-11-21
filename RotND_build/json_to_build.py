import json
from typing import Self


class FmodTimeCapsule:
    def __init__(self, Time, DeltaTime, BeatLengthInSeconds, TrueBeatNumber):
        self.Time = Time
        self.DeltaTime = DeltaTime
        self.BeatLengthInSeconds = BeatLengthInSeconds
        self.TrueBeatNumber = TrueBeatNumber


class BeatmapEventDataPair:
    def __init__(self, eventDataKey, eventDataValue):
        self._eventDataKey = eventDataKey
        self._eventDataValue = eventDataValue

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


class BeatmapAnalyzer:
    def __init__(self, beatmap, _sampleRate):
        self._activeBeatmap: Beatmap = beatmap
        self.SampleRate = _sampleRate

        self._previousFmodTime = 0
        self._beatEventIndex = 0

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

    def ProcessBeatEvent(currentTime, beatEvent: BeatmapEvent, isAddedEvent=False):
        if beatEvent.type == "SpawnEnemy":
            pass

    def ProcessBeatEvents(self, currentTime):
        activeBeatmap = self._activeBeatmap
        cur_beat = self.FmodTimeCapsule.TrueBeatNumber - 1.0
        while self._beatEventIndex < activeBeatmap.NumBeatmapEvents:
            beatmapEvent: BeatmapEvent = activeBeatmap.BeatmapEvents[
                self._beatEventIndex
            ]
            if beatmapEvent.startBeatNumber <= cur_beat:
                if cur_beat <= beatmapEvent.endBeatNumber:
                    pass

    def analyze(self):
        cur_frame = 0
        self._activeBeatmapBeatTimingIndex = 0

        while True:
            cur_time = cur_frame * (1 / self.SampleRate)
            currentTrueBeatNumber = self.CalculateCurrentTrueBeatNumber(cur_time)
            self.FmodTimeCapsule = FmodTimeCapsule(
                cur_time,
                cur_time - self._previousFmodTime,
                self.GetCurrentBeatLengthInSeconds(int(currentTrueBeatNumber)),
                currentTrueBeatNumber,
            )
            if currentTrueBeatNumber - 1.0 > self._activeBeatmap.DurationInBeats():
                break
            self.ProcessBeatEvents(cur_time)
            # TODO

            cur_frame += 1


class Beatmap:
    def __init__(self, bpm, events, beatDivision=2, beatTimings=None):
        self.bpm = bpm
        self.beatDivision = beatDivision
        self.events: list[dict] = events
        self.beatTimings = beatTimings

        self.endBeatNumberBacking = -1.0
        self.beatmapEventsBacking: list = {}

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
            # TODO
            beatmap["events"],
            beatmap["beatDivisions"],
            beatmap["BeatTimings"],
        )

        for event_idx in range(len(beatmap.events)):
            event = beatmap.events[event_idx]
            beatmapEvent = BeatmapEvent(
                event["track"],
                event["startBeatNumber"],
                event["endBeatNumber"],
                event["type"],
                list(
                    map(
                        lambda dict: BeatmapEventDataPair(
                            dict["_eventDataKey"], dict["_eventDataValue"]
                        ),
                        event["dataPairs"],
                    )
                ),
            )
            beatmapEvent.InitializeEventDataDictionary()
            beatmap.events[event_idx] = beatmapEvent

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


beatmap = Beatmap.LoadFromJson(
    "RotND_build/rhythmrift/RhythmRift_Overthinker_Expert.json"
)
print(beatmap.DurationInBeats())


# bpm = beatmap["bpm"]
# beatDivisions = beatmap["beatDivisions"]
# events: list = beatmap["events"]
# has_beatTimings: bool = beatmap["BeatTimings"]


# A_THIRD = 0.33333333333
# TWO_THIRDS = 0.66666666667

# GREEN_SLIME = 1722
# BLUE_SLIME = 4355
# YELLOW_SLIME = 9189
# BLUE_BAT = 8675309
# YELLOW_BAT = 717
# RED_BAT = 911
# GREEN_ZOMBIE = 1234
# RED_ZOMBIE = 1236
# BASE_SKELETON = 2202
# SHIELDED_BASE_SKELETON = 1911
# TRIPLE_SHIELD_BASE_SKELETON = 6471
# BLUE_ARMADILLO = 7831
# RED_ARMADILLO = 1707
# YELLOW_ARMADILLO = 6311
# YELLOW_SKELETON = 6803
# HEADLESS_SKELETON = 6804
# SHIELDED_YELLOW_SKELETON = 4871
# BLACK_SKELETON = 2716
# SHIELDED_BLACK_SKELETON = 3307
# BASE_WYRM = 7794
# BASE_HARPY = 8519
# RED_HARPY = 3826
# BLUE_HARPY = 8156
# APPLE = 7358
# CHEESE = 2054
# DRUMSTICK = 1817
# HAM = 3211
# BASE_BLADEMASTER = 929
# # STRONG_BLADEMASTER = 3685
# # YELLOW_BLADEMASTER = 7288
# BASE_SKULL = 4601
# BLUE_SKULL = 3543
# RED_SKULL = 7685


# class Note:
#     def __init__(self, start: float):
#         self.start = start
#         self.end = start

#     def __init__(self, start: float, end: float):
#         self.start = start
#         self.end = end

#     def __str__(self):
#         return f"{self.start} {self.end}"


# beatmap: list = []
# for event in events:
#     if event["type"] != "SpawnEnemy":
#         continue

#     for pair in event["dataPairs"]:
#         if pair["_eventDataKey"] == "EnemyId":
#             id = int(pair["_eventDataValue"])
#             break
#     track = event["track"]
#     start = event["startBeatNumber"]
#     end = event["endBeatNumber"]

#     headless_skeleton = headless_skeletons[track - 1]
#     if headless_skeleton:
#         if start > headless_skeleton + 2.0:
#             beatmap.append(Note(start - 1.0))
#         else:
#             beatmap.append(Note(headless_skeleton + 1.0))
#         headless_skeletons[track - 1] = None

#     beatmap.append(Note(start, end))
#     if id in [BLUE_SLIME, BLUE_BAT]:
#         beatmap.append(Note(start + 1.0))
#     elif id in [YELLOW_SLIME, YELLOW_BAT, RED_BAT]:
#         beatmap.append(Note(start + 1.0))
#         beatmap.append(Note(start + 2.0))
#     elif id in [SHIELDED_BASE_SKELETON]:
#         beatmap.append(Note(start + 0.5))
#     elif id in [TRIPLE_SHIELD_BASE_SKELETON]:
#         beatmap.append(Note(start + 0.5))
#         beatmap.append(Note(start + 1.0))
#     elif id in [BLUE_ARMADILLO]:
#         beatmap.append(Note(start + A_THIRD))
#     elif id in [RED_ARMADILLO]:
#         beatmap.append(Note(start + TWO_THIRDS))
#     elif id in [YELLOW_ARMADILLO]:
#         beatmap.append(Note(start + A_THIRD))
#         beatmap.append(Note(start + TWO_THIRDS))
#     elif id in [YELLOW_SKELETON]:
#         headless_skeletons[track - 1] = start
# event_idx = 0
# while event_idx < len(events):
#     event = events[event_idx]

#     if event["type"] != "SpawnEnemy":
#         continue

#     for pair in event["dataPairs"]:
#         if pair["_eventDataKey"] == "EnemyId":
#             id = int(pair["_eventDataValue"])
#             break
#     track = event["track"]
#     start = event["startBeatNumber"]
#     end = event["endBeatNumber"]

#     beatmap.append(Note(start, end))
#     if id in [BLUE_SLIME, BLUE_BAT]:
#         beatmap.append(Note(start + 1.0))
#     elif id in [YELLOW_SLIME, YELLOW_BAT, RED_BAT]:
#         beatmap.append(Note(start + 1.0))
#         beatmap.append(Note(start + 2.0))
#     elif id in [SHIELDED_BASE_SKELETON]:
#         beatmap.append(Note(start + 0.5))
#     elif id in [TRIPLE_SHIELD_BASE_SKELETON]:
#         beatmap.append(Note(start + 0.5))
#         beatmap.append(Note(start + 1.0))
#     elif id in [BLUE_ARMADILLO]:
#         beatmap.append(Note(start + A_THIRD))
#     elif id in [RED_ARMADILLO]:
#         beatmap.append(Note(start + TWO_THIRDS))
#     elif id in [YELLOW_ARMADILLO]:
#         beatmap.append(Note(start + A_THIRD))
#         beatmap.append(Note(start + TWO_THIRDS))
#     elif id in [YELLOW_SKELETON]:
#         wall_idx = event_idx + 1
#         while (
#             events[wall_idx]["type"] != "SpawnEnemy"
#             or events[wall_idx]["track"] != track
#         ):
#             wall_idx += 1

#         wall_event = events[wall_idx]
#         if wall_event["startBeatNumber"] > start + 2.0:
#             pass
#     event_idx += 1
# beatmap.sort(key=lambda note: note.start)

# vibe_chain = []
# for event in events:
#     if event['type'] == 'StartVibeChain':
#         event['dataPairs']

# if has_beatTimings:
#     pass
# else:
#     pass
