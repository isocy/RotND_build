from Shared.RhythmEngine import *
from RhythmRift import *

SAMPLE_RATE = 60

BEATMAP_PATH = "C:/Users/mschoi/Saved Games/Rift of the NecroDancer/Rift of the NecroDancer Demo 2/builds/exports/unity3d/beatmaps/rhythmrift/RhythmRift_Overthinker_Expert"
SCORING_DEF_PATH = "exports/bundles/Assets/Shared/ScriptableObjects/RatingsDefinitions/DefaultStageScoringDefinition.json"
RATINGS_BPM_MAP_PATH = "exports/bundles/RR_InputRatingsBpmMapping.json"

scoring_def = StageScoringDefinition.LoadFromJson(SCORING_DEF_PATH)
ratings_bpm_map = InputRatingsBpmMapping.LoadFromJson(RATINGS_BPM_MAP_PATH)

beatmap = Beatmap.LoadFromJson(BEATMAP_PATH)
beatmap_player = RRBeatmapPlayer(beatmap, SAMPLE_RATE)
stage_controller = RRStageController(beatmap_player, scoring_def)

cur_frame = 0

while beatmap_player._activeBeatmap:
    beatmap_player.Update(cur_frame)

    cur_frame += 1
