from abc import ABC, abstractmethod
from enum import Enum
import json

BEAT_OFFSET = 1.5
ROWS = 9
LANES = 3

ENEMY_DB_PATH = "exports/bundles/RREnemyDatabase.json"

DISCO_DISASTER_EASY_PATH = (
    "exports/unity3d/beatmaps/rhythmrift/RhythmRift_DiscoDisaster_Easy"
)


class EnemyDB:
    @classmethod
    def load_dict(self, path):
        with open(path) as f:
            enemy_defs: list[dict] = json.load(f)["_enemyDefinitions"]

        enemy_db = {}
        for enemy_def in enemy_defs:
            id = enemy_def.pop("_id")

            # keys of enemy_def:
            # name, health, total_hits, player_dmg, beat_for_move,
            # priority, properties, shield, enemy_on_death_id
            enemy_def["name"] = enemy_def["_displayName"]
            enemy_def["health"] = enemy_def["_maxHealth"]
            enemy_def["total_hits"] = enemy_def["_totalHitsAddedToStage"]
            del enemy_def["_totalEnemiesGenerated"]
            enemy_def["player_dmg"] = enemy_def["_playerDamage"]
            del enemy_def["_hpAwardedOnDeath"]
            enemy_def["beat_for_move"] = enemy_def["_updateTempoInBeats"]
            enemy_def["priority"] = enemy_def["_collisionPriority"]
            enemy_def["properties"] = enemy_def["_specialProperties"]
            enemy_def["shield"] = enemy_def["_shieldHealth"]
            del enemy_def["_prefabAssetReference"]
            del enemy_def["_heldPrefabAssetReference"]
            del enemy_def["_bodyEnemyId"]
            del enemy_def["_tailEnemyId"]
            enemy_def["enemy_on_death_id"] = enemy_def["_enemySpawnedOnDeathId"]

            enemy_db[id] = enemy_def

        return enemy_db


class Object:
    pass


class Enemy(Object, ABC):
    @property
    @abstractmethod
    def BeatForMove(self):
        """The number of beats for an enemy to move once"""
        return 1

    @property
    @abstractmethod
    def DistForMove(self):
        """The number of grids an enemy takes to move"""
        return 1

    @property
    @abstractmethod
    def Health(self):
        return 1

    @property
    @abstractmethod
    def Shield(self):
        return 0


class Slime(Enemy):
    pass


class GreenSlime(Slime):
    pass


class Grid:
    def __init__(self):
        self.enemies: list[Node] = []
        self.traps: list[Node] = []

    def is_empty(self):
        return not self.enemies and not self.traps


class Map:
    def __init__(self, lanes, rows):
        self.lanes = lanes
        self.rows = rows
        self.grids = [[Grid() for j in range(rows)] for i in range(lanes)]

    def is_clean(self):
        for i in range(self.lanes):
            for j in range(self.rows):
                if not self.grids[i][j].is_empty():
                    return False
        return True


class EventType(Enum):
    ENEMY = 0


class Event:
    def __init__(self):
        self.type = EventType.ENEMY

        self.row_idx = ROWS - 1

    @classmethod
    @abstractmethod
    def load_dict(cls, event: dict):
        if event["type"] == "SpawnEnemy":
            return EnemyEvent.load_dict(event)


class EnemyEvent(Event):
    def __init__(self, lane, beat_appear, enemy_id):
        super(EnemyEvent, self).__init__()
        self.lane = lane
        self.beat_appear = beat_appear
        self.enemy_id = enemy_id

    @classmethod
    def load_dict(cls, event):
        """Construct EnemyEvent with given dictionary"""
        return EnemyEvent(
            event["track"],
            event["startBeatNumber"],
            next(
                pair["_eventDataValue"]
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "EnemyId"
            ),
        )


class RawBeatmap:
    def __init__(self, bpm, beat_divs, events):
        self.bpm = bpm
        self.beat_divs = beat_divs
        self.events: list[Event] = events

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            beatmap = json.load(f)

        return RawBeatmap(
            beatmap["bpm"],
            beatmap["beatDivisions"],
            [Event.load_dict(event) for event in beatmap["events"]],
        )


class Node:
    def __init__(self, object: Object, update_period):
        """Initialize a node which will be present at some grids for a period of time"""
        self.object = object
        self.period = update_period
        self.lifetime = self.period

    @classmethod
    def events_to_nodes(cls, events: list[Event], enemy_db: EnemyDB):
        nodes: list[Node] = []
        for event in events:
            if event.type == EventType.ENEMY:
                event: EnemyEvent = event
                enemy_id = event.enemy_id
                enemy_def: dict = enemy_db[enemy_id]

                if enemy_id == 1722:
                    nodes.append(Node(GreenSlime(), enemy_def["beat_for_move"]))


class Beat:
    def __init__(self, lane, beat):
        self.lane = lane
        self.beat = beat


map = Map(LANES, ROWS)

enemy_db = EnemyDB.load_dict(ENEMY_DB_PATH)

raw_beatmap_path = DISCO_DISASTER_EASY_PATH
raw_beatmap = RawBeatmap.load_json(raw_beatmap_path)
events = raw_beatmap.events
events_len = len(events)

event_idx = 0
while event_idx < events_len or not map.is_clean():
    pass
