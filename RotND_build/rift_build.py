from Shared import *
from RhythmRift import *

beatmap = Beatmap.LoadFromJson(
    "RotND_build/rhythmrift/RhythmRift_Overthinker_Expert.json"
)
beatmap_player = RRBeatmapPlayer(beatmap, 60)
stage_controller = RRStageController(beatmap_player)

cur_frame = 0

while beatmap_player._activeBeatmap:
    beatmap_player.Update(cur_frame)

    cur_frame += 1
