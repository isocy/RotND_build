from Shared import *
from RhythmRift import *

SAMPLE_RATE = 60

BEATMAP_PATH = "RotND_build/rhythmrift/RhythmRift_Overthinker_Expert.json"

beatmap = Beatmap.LoadFromJson(BEATMAP_PATH)
beatmap_player = RRBeatmapPlayer(beatmap, SAMPLE_RATE)
stage_controller = RRStageController(beatmap_player)

cur_frame = 0

while beatmap_player._activeBeatmap:
    beatmap_player.Update(cur_frame)

    cur_frame += 1
