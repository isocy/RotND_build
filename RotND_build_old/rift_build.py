from Shared.RhythmEngine import StageScoringDefinition, InputRatingsBpmMapping, Beatmap

from RhythmRift import (
    RRBeatmapPlayer,
    RRStageController,
    RREnemyDatabase,
    RREnemyController,
)
from UnityEngine import Time

FPS = 60

BEATMAP_PATH = "exports/unity3d/beatmaps/rhythmrift/RhythmRift_Overthinker_Expert"
SCORING_DEF_PATH = "exports/bundles/Assets/Shared/ScriptableObjects/RatingsDefinitions/DefaultStageScoringDefinition.json"
RATINGS_BPM_MAP_PATH = "exports/bundles/RR_InputRatingsBpmMapping.json"
RATINGS_BPM_PAIR_PATHS = [
    "exports/bundles/Assets/Shared/Prefabs/ScoreResults/RhythmRift_InputRatingsDefinition.json"
]
ENEMY_DB_PATH = "exports/bundles/RREnemyDatabase.json"

Time.deltaTime = 1 / FPS

scoring_def = StageScoringDefinition.LoadFromJson(SCORING_DEF_PATH)
ratings_bpm_map = InputRatingsBpmMapping.LoadFromJson(
    RATINGS_BPM_MAP_PATH, RATINGS_BPM_PAIR_PATHS
)

beatmap = Beatmap.LoadFromJson(BEATMAP_PATH)
beatmap_player = RRBeatmapPlayer()
stage_controller = RRStageController()

enemy_db = RREnemyDatabase.LoadFromJson(ENEMY_DB_PATH)
enemy_controller = RREnemyController(enemy_db)

cur_frame = 0

while beatmap_player._activeBeatmap:
    beatmap_player.Update(cur_frame)

    cur_frame += 1
