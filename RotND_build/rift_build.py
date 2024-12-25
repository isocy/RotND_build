from global_def import *
from object import *
from event import *

import json
from typing import Self


class EnemyDB:
    @classmethod
    def json_to_dict(self, path) -> dict:
        """Construct dictionary as enemy database with given json file"""
        with open(path) as f:
            enemy_defs: list[dict] = json.load(f)["_enemyDefinitions"]

        enemy_db = {}
        for enemy_def in enemy_defs:
            id = enemy_def.pop("_id")

            # keys of enemy_def:
            #   name, health, total_hits, beat_for_move, priority,
            #   properties, shield, enemy_on_death_id
            enemy_def["name"] = enemy_def["_displayName"]
            enemy_def["health"] = enemy_def["_maxHealth"]
            enemy_def["total_hits"] = enemy_def["_totalHitsAddedToStage"]
            del enemy_def["_totalEnemiesGenerated"]
            del enemy_def["_playerDamage"]
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


class Beat:
    def __init__(self, lane, beat):
        self.lane = lane
        self.beat = beat

    def __repr__(self):
        return f"{self.beat} {self.lane}"


class Grid:
    def __init__(self):
        self.enemies: list[Node[Enemy]] = []
        self.traps: list[Node[Trap]] = []

    def __repr__(self):
        return (self.enemies + self.traps).__repr__()

    def is_empty(self):
        return not self.enemies and not self.traps


class Map:
    def __init__(self, lanes, rows):
        self.lanes = lanes
        self.rows = rows
        self.grids: list[list[Grid]] = [
            [Grid() for j in range(rows)] for i in range(lanes)
        ]

    def __repr__(self):
        str = ""
        for j in reversed(range(self.rows)):
            for i in range(self.lanes):
                str += "{:<15}".format(map.grids[i][j].__repr__())
            str += "\n"
        return str

    def is_clean(self):
        for i in range(self.lanes):
            for j in range(self.rows):
                if not self.grids[i][j].is_empty():
                    return False
        return True

    def step(self, init_cooltime=float("inf")) -> float:
        # Update map for one step
        # return: elapsed beat for the update
        min_cooltime = init_cooltime
        target_nodes = []
        for i in range(map.lanes):
            for j in range(map.rows):
                for enemy_node in map.grids[i][j].enemies:
                    if enemy_node.cooltime < min_cooltime:
                        min_cooltime = enemy_node.cooltime
                        target_nodes = [enemy_node]
                    elif enemy_node.cooltime == min_cooltime:
                        target_nodes.append(enemy_node)
                for trap_node in map.grids[i][j].traps:
                    if trap_node.cooltime < min_cooltime:
                        min_cooltime = trap_node.cooltime
                        target_nodes = [trap_node]
                    elif trap_node.cooltime == min_cooltime:
                        target_nodes.append(trap_node)

        for i in range(map.lanes):
            for j in range(map.rows):
                grid = map.grids[i][j]
                enemy_nodes = grid.enemies
                for enemy_node in enemy_nodes:
                    if enemy_node in target_nodes:
                        enemy_node.cooltime = enemy_node.object.get_cooltime()
                        enemy_nodes.remove(enemy_node)
                        map.grids[i][
                            j - enemy_node.object.dist_for_move
                        ].enemies.append(enemy_node)
                        target_nodes.remove(enemy_node)
                    else:
                        enemy_node.cooltime -= min_cooltime
                trap_nodes = grid.traps
                for trap_node in trap_nodes:
                    if trap_node in target_nodes:
                        trap_nodes.remove(trap_node)
                        target_nodes.remove(trap_node)
                    else:
                        trap_node.cooltime -= min_cooltime

        return min_cooltime

    def hit_notes(self, beatmap: list[Beat]):
        """Process nodes at the bottom row and update 'beatmap'"""
        for i in range(map.lanes):
            for enemy_node in map.grids[i][0].enemies:
                beatmap.append(Beat(i, cur_beat))
                enemy = enemy_node.object
                if enemy.health > 1:
                    enemy.health -= 1
                    enemy_node.cooltime = enemy.get_cooltime()
                    map.grids[i][0].enemies.remove(enemy_node)
                    map.grids[i][1].enemies.append(enemy_node)

            map.grids[i][0].enemies.clear()


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


class Node[T: Object]:
    def __init__(self, object: T, appear_beat):
        """Initialize a node which will be present at some grids for a period of time"""
        self.object = object
        self.cooltime = appear_beat

    def __eq__(self, other: Self):
        return self.object == other.object

    def __repr__(self):
        return f"{self.object} {self.cooltime}"

    @classmethod
    def events_to_nodes(cls, events: list[Event], enemy_db: EnemyDB) -> list[Self]:
        nodes: list[Node] = []
        for event in events:
            if event.type == EventType.ENEMY:
                event: EnemyEvent = event
                enemy_id = event.enemy_id
                enemy_def: dict = enemy_db[enemy_id]
                name = enemy_def["name"]

                if name == GREEN_SLIME:
                    nodes.append(Node(GreenSlime(event.lane), event.appear_beat))
                elif name == BLUE_SLIME:
                    nodes.append(Node(BlueSlime(event.lane), event.appear_beat))
                elif name == BASE_SKELETON:
                    nodes.append(Node(BaseSkeleton(event.lane), event.appear_beat))
                elif name == APPLE:
                    nodes.append(Node(Apple(event.lane), event.appear_beat))

        return nodes


map = Map(LANES, ROWS)

enemy_db = EnemyDB.json_to_dict(ENEMY_DB_PATH)

for enemy_def in enemy_db.values():
    name = enemy_def["name"]
    if name == GREEN_SLIME:
        setattr(GreenSlime, "beat_for_move", enemy_def["beat_for_move"])
        setattr(GreenSlime, "max_health", enemy_def["health"])
        setattr(GreenSlime, "max_shield", enemy_def["shield"])
    elif name == BLUE_SLIME:
        setattr(BlueSlime, "beat_for_move", enemy_def["beat_for_move"])
        setattr(BlueSlime, "max_health", enemy_def["health"])
        setattr(BlueSlime, "max_shield", enemy_def["shield"])
    elif name == BASE_SKELETON:
        setattr(BaseSkeleton, "beat_for_move", enemy_def["beat_for_move"])
        setattr(BaseSkeleton, "max_health", enemy_def["health"])
        setattr(BaseSkeleton, "max_shield", enemy_def["shield"])
    elif name == APPLE:
        setattr(Apple, "beat_for_move", enemy_def["beat_for_move"])
        setattr(Apple, "max_health", enemy_def["health"])
        setattr(Apple, "max_shield", enemy_def["shield"])

raw_beatmap_path = DISCO_DISASTER_EASY_PATH
raw_beatmap = RawBeatmap.load_json(raw_beatmap_path)
events = Node.events_to_nodes(raw_beatmap.events, enemy_db)
events_len = len(events)

beatmap: list[Beat] = []
event_idx = 0
cur_beat = 0
next_node = events[event_idx]
# cooltime changes of nodes in 'events' for each iteration of the outmost loop cost a lot,
# so the cooltime corrections occur for each node when the node is 'next_node'.
next_node.cooltime -= cur_beat
while event_idx < events_len:
    min_cooltime = map.step(next_node.cooltime)
    next_node.cooltime -= min_cooltime

    while next_node.cooltime == 0:
        object: Object = next_node.object
        next_node.cooltime = object.get_cooltime()
        if object.type == ObjectType.ENEMY:
            map.grids[object.appear_lane - 1][Enemy.appear_row].enemies.append(
                next_node
            )

        event_idx += 1
        if event_idx >= events_len:
            break
        next_node = events[event_idx]
        next_node.cooltime -= cur_beat + min_cooltime

    cur_beat += min_cooltime

    # TODO

    map.hit_notes(beatmap)

# This while loop is almost same as the above one
# Here is no 'next_node' to appear
while not map.is_clean():
    min_cooltime = map.step()
    cur_beat += min_cooltime

    # TODO

    map.hit_notes(beatmap)

for beat in beatmap:
    print(beat)
