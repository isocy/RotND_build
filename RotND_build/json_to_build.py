import json

with open("RotND_build/rhythmrift/RhythmRift_Overthinker_Expert.json") as f:
    beatmap: dict = json.load(f)

bpm = beatmap["bpm"]
beatDivisions = beatmap["beatDivisions"]
events: list = beatmap["events"]
has_beatTimings: bool = beatmap["BeatTimings"]


A_THIRD = 0.33333333333
TWO_THIRDS = 0.66666666667

GREEN_SLIME = 1722
BLUE_SLIME = 4355
YELLOW_SLIME = 9189
BLUE_BAT = 8675309
YELLOW_BAT = 717
RED_BAT = 911
GREEN_ZOMBIE = 1234
RED_ZOMBIE = 1236
BASE_SKELETON = 2202
SHIELDED_BASE_SKELETON = 1911
TRIPLE_SHIELD_BASE_SKELETON = 6471
BLUE_ARMADILLO = 7831
RED_ARMADILLO = 1707
YELLOW_ARMADILLO = 6311
YELLOW_SKELETON = 6803
HEADLESS_SKELETON = 6804
SHIELDED_YELLOW_SKELETON = 4871
BLACK_SKELETON = 2716
SHIELDED_BLACK_SKELETON = 3307
BASE_WYRM = 7794
BASE_HARPY = 8519
RED_HARPY = 3826
BLUE_HARPY = 8156
APPLE = 7358
CHEESE = 2054
DRUMSTICK = 1817
HAM = 3211
BASE_BLADEMASTER = 929
# STRONG_BLADEMASTER = 3685
# YELLOW_BLADEMASTER = 7288
BASE_SKULL = 4601
BLUE_SKULL = 3543
RED_SKULL = 7685


class Note:
    def __init__(self, start: float):
        self.start = start
        self.end = start

    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.start} {self.end}"


headless_skeletons = [None, None, None]
beatmap: list = []
for event in events:
    if event["type"] != "SpawnEnemy":
        continue

    for pair in event["dataPairs"]:
        if pair["_eventDataKey"] == "EnemyId":
            id = int(pair["_eventDataValue"])
            break
    track = event["track"]
    start = event["startBeatNumber"]
    end = event["endBeatNumber"]

    headless_skeleton = headless_skeletons[track - 1]
    if headless_skeleton:
        if start > headless_skeleton + 2.0:
            beatmap.append(Note(start - 1.0))
        else:
            beatmap.append(Note(headless_skeleton + 1.0))
        headless_skeletons[track - 1] = None

    beatmap.append(Note(start, end))
    if id in [BLUE_SLIME, BLUE_BAT]:
        beatmap.append(Note(start + 1.0))
    elif id in [YELLOW_SLIME, YELLOW_BAT, RED_BAT]:
        beatmap.append(Note(start + 1.0))
        beatmap.append(Note(start + 2.0))
    elif id in [SHIELDED_BASE_SKELETON]:
        beatmap.append(Note(start + 0.5))
    elif id in [TRIPLE_SHIELD_BASE_SKELETON]:
        beatmap.append(Note(start + 0.5))
        beatmap.append(Note(start + 1.0))
    elif id in [BLUE_ARMADILLO]:
        beatmap.append(Note(start + A_THIRD))
    elif id in [RED_ARMADILLO]:
        beatmap.append(Note(start + TWO_THIRDS))
    elif id in [YELLOW_ARMADILLO]:
        beatmap.append(Note(start + A_THIRD))
        beatmap.append(Note(start + TWO_THIRDS))
    elif id in [YELLOW_SKELETON]:
        headless_skeletons[track - 1] = start
beatmap.sort(key=lambda note: note.start)

# vibe_chain = []
# for event in events:
#     if event['type'] == 'StartVibeChain':
#         event['dataPairs']

if has_beatTimings:
    pass
else:
    pass
