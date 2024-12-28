from global_def import *
from object import *
from event import *

from bisect import bisect_right
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


class InputRatingsDef:
    def __init__(self, perf_range: float, great_range: float):
        self.perf_range = perf_range
        self.great_range = great_range

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            input_ratings_def = json.load(f)

        hit_window = input_ratings_def["_beforeBeatHitWindow"] * 1000
        ratings = input_ratings_def["_ratings"]

        perf_range = (100 - ratings[-1]["minimumValue"]) * hit_window / 100
        great_range = (100 - ratings[-2]["minimumValue"]) * hit_window / 100

        return InputRatingsDef(perf_range, great_range)


class Beat:
    def __init__(self, lane, beat):
        self.lane = lane
        self.beat = beat

    def __lt__(self, other):
        if isinstance(other, Beat):
            return self.beat < other.beat
        else:
            return self.beat < other

    def __repr__(self):
        return f"{self.beat} {self.lane}"


class BeatCnt:
    def __init__(self, beat: float, cnt: int):
        self.beat = beat
        self.cnt = cnt

    def __lt__(self, other: Self):
        return self.cnt < other.cnt

    def __repr__(self):
        return f"{self.beat} {self.cnt}"


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
                grid_enemies = grid.enemies
                for grid_enemy in grid_enemies:
                    if grid_enemy in target_nodes:
                        obj = grid_enemy.obj
                        grid_enemy.cooltime = obj.get_cooltime()
                        grid_enemies.remove(grid_enemy)
                        if (
                            isinstance(obj, Slime)
                            or isinstance(obj, BlueBat)
                            or isinstance(obj, Skeleton)
                            or isinstance(obj, Food)
                        ):
                            map.grids[i][j - 1].enemies.append(grid_enemy)
                        # TODO
                        else:
                            pass
                        target_nodes.remove(grid_enemy)
                    else:
                        grid_enemy.cooltime -= min_cooltime
                trap_nodes = grid.traps
                for trap_node in trap_nodes:
                    if trap_node in target_nodes:
                        trap_nodes.remove(trap_node)
                        target_nodes.remove(trap_node)
                    else:
                        trap_node.cooltime -= min_cooltime

        return min_cooltime


class RawBeatmap:
    def __init__(self, bpm, beat_divs, enemy_events, vibe_events):
        self.bpm = bpm
        self.beat_divs = beat_divs
        self.enemy_events: list[EnemyEvent] = enemy_events
        self.vibe_events: list[VibeEvent] = vibe_events

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            raw_beatmap = json.load(f)

        # TODO
        enemy_events = []
        vibe_events = []
        for event in raw_beatmap["events"]:
            if event["type"] == "SpawnEnemy":
                enemy_events.append(event)
            elif event["type"] == "StartVibeChain":
                vibe_events.append(event)

        return RawBeatmap(
            raw_beatmap["bpm"],
            raw_beatmap["beatDivisions"],
            [EnemyEvent.load_dict(event) for event in enemy_events],
            [VibeEvent.load_dict(vibe_event) for vibe_event in vibe_events],
        )


class Node[T: Object]:
    def __init__(self, obj: T, appear_beat):
        """Initialize a node which will be present at some grids for a period of time"""
        self.obj = obj
        self.cooltime = appear_beat

    def __eq__(self, other: Self):
        return self.obj == other.obj

    def __repr__(self):
        return f"{self.obj} {self.cooltime}"

    @classmethod
    def enemy_events_to_nodes(
        cls,
        enemy_events: list[EnemyEvent],
        vibe_events: list[VibeEvent],
        enemy_db: EnemyDB,
    ) -> tuple[list[Self], list[int]]:
        nodes: list[Node] = []

        vibe_events_len = len(vibe_events)
        chain_cnts = []
        chain_cnt = 0

        for enemy_event in enemy_events:
            lane = enemy_event.lane
            appear_beat = enemy_event.appear_beat

            enemy_id = enemy_event.enemy_id
            enemy_def: dict = enemy_db[enemy_id]
            name = enemy_def["name"]

            chained = False
            while len(chain_cnts) < vibe_events_len:
                cur_vibe_event = vibe_events[len(chain_cnts)]
                if appear_beat < cur_vibe_event.start_beat:
                    break
                elif appear_beat < cur_vibe_event.end_beat:
                    chain_cnt += 1
                    chained = True
                    break
                else:
                    chain_cnts.append(chain_cnt)
                    chain_cnt = 0

            # TODO
            if name == GREEN_SLIME:
                nodes.append(Node(GreenSlime(lane, chained), appear_beat))
            elif name == BLUE_SLIME:
                nodes.append(Node(BlueSlime(lane, chained), appear_beat))
            elif name == BLUE_BAT:
                nodes.append(
                    Node(BlueBat(lane, enemy_event.facing, chained), appear_beat)
                )
            elif name == BASE_SKELETON:
                nodes.append(Node(BaseSkeleton(lane, chained), appear_beat))
            elif name == APPLE:
                nodes.append(Node(Apple(lane, chained), appear_beat))

        return (nodes, chain_cnts)


map = Map(LANES, ROWS)

enemy_db = EnemyDB.json_to_dict(ENEMY_DB_PATH)

for enemy_def in enemy_db.values():
    name = enemy_def["name"]
    # TODO
    if name == GREEN_SLIME:
        setattr(GreenSlime, "beat_for_move", enemy_def["beat_for_move"])
        setattr(GreenSlime, "max_health", enemy_def["health"])
        setattr(GreenSlime, "max_shield", enemy_def["shield"])
    elif name == BLUE_SLIME:
        setattr(BlueSlime, "beat_for_move", enemy_def["beat_for_move"])
        setattr(BlueSlime, "max_health", enemy_def["health"])
        setattr(BlueSlime, "max_shield", enemy_def["shield"])
    elif name == BLUE_BAT:
        setattr(BlueBat, "beat_for_move", enemy_def["beat_for_move"])
        setattr(BlueBat, "max_health", enemy_def["health"])
        setattr(BlueBat, "max_shield", enemy_def["shield"])
    elif name == BASE_SKELETON:
        setattr(BaseSkeleton, "beat_for_move", enemy_def["beat_for_move"])
        setattr(BaseSkeleton, "max_health", enemy_def["health"])
        setattr(BaseSkeleton, "max_shield", enemy_def["shield"])
    elif name == APPLE:
        setattr(Apple, "beat_for_move", enemy_def["beat_for_move"])
        setattr(Apple, "max_health", enemy_def["health"])
        setattr(Apple, "max_shield", enemy_def["shield"])

input_ratings_def = InputRatingsDef.load_json(INPUT_RATINGS_DEF_PATH)
perf_range = input_ratings_def.perf_range
great_range = input_ratings_def.great_range

raw_beatmap_path = DISCO_DISASTER_EASY_PATH
raw_beatmap = RawBeatmap.load_json(raw_beatmap_path)
(enemy_nodes, chain_cnts) = Node.enemy_events_to_nodes(
    raw_beatmap.enemy_events, raw_beatmap.vibe_events, enemy_db
)
enemy_nodes_len = len(enemy_nodes)

# These beats indicate the moment a vibe power is charged
vibe_beats: list[float] = []
chain_idx = 0

beats: list[Beat] = []
node_idx = 0
cur_beat = 0
next_node = enemy_nodes[node_idx]
# cooltime changes of nodes in 'enemy_nodes' for each iteration of the outmost loop cost a lot,
# so the cooltime corrections occur for each node when the node is 'next_node'.
next_node.cooltime -= cur_beat
while node_idx < enemy_nodes_len or not map.is_clean():
    min_cooltime = map.step(next_node.cooltime)

    if node_idx < enemy_nodes_len:
        next_node.cooltime -= min_cooltime

        while next_node.cooltime == 0:
            obj: Object = next_node.obj
            next_node.cooltime = obj.get_cooltime()
            # TODO: traps
            if isinstance(obj, Enemy):
                map.grids[obj.appear_lane - 1][Enemy.appear_row].enemies.append(
                    next_node
                )

            node_idx += 1
            if node_idx >= enemy_nodes_len:
                break
            next_node = enemy_nodes[node_idx]
            next_node.cooltime -= cur_beat + min_cooltime

    cur_beat += min_cooltime

    # TODO: trap

    # hit_notes()
    for i in range(map.lanes):
        for enemy_node in map.grids[i][0].enemies:
            beats.append(Beat(i, cur_beat))
            enemy = enemy_node.obj
            if enemy.health > 1:
                enemy.health -= 1
                enemy_node.cooltime = enemy.get_cooltime()
                map.grids[i][0].enemies.remove(enemy_node)
                # TODO: different 'dist_for_move' for different enemies
                if isinstance(enemy, BlueBat):
                    if enemy.facing == Facing.LEFT:
                        map.grids[i - 1][1].enemies.append(enemy_node)
                    else:
                        map.grids[(i + 1) % 3][1].enemies.append(enemy_node)
                else:
                    map.grids[i][1].enemies.append(enemy_node)
            elif enemy.chained:
                chain_cnts[chain_idx] -= 1

                if chain_cnts[chain_idx] == 0:
                    # TODO: special case for wyrms
                    vibe_beats.append(cur_beat)
                    chain_idx += 1

        map.grids[i][0].enemies.clear()


# All elements of 'vibe_beats' is included in 'raw_beats'
raw_beats = [beat.beat for beat in beats]
raw_beats_len = len(raw_beats)
vibe_beats_len = len(vibe_beats)

one_vibe_beatcnts: list[list[BeatCnt]] = []
next_beat_idxs: list[int] = []
for vibe_idx in range(vibe_beats_len):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = bisect_right(raw_beats, vibe_beats[vibe_idx])
    beat_idx = start_idx
    # condition for when 'vibe_idx' is equal to 'len(vibe_beats) - 1'
    while beat_idx < raw_beats_len:
        target_beat = raw_beats[beat_idx]
        if vibe_idx < vibe_beats_len - 1 and target_beat >= vibe_beats[vibe_idx + 1]:
            next_beat_idxs.append(beat_idx)
            break
        max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * 302
        # TODO: consider bpm change
        max_time_until_vibe_ends = (
            max_time_until_vibe_ends
            + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
        )
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        if vibe_idx < vibe_beats_len - 1:
            if target_end_beat < vibe_beats[vibe_idx + 1]:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat, bisect_right(raw_beats, target_end_beat) - beat_idx
                    )
                )
                beat_idx += 1
            else:
                next_beat_idxs.append(beat_idx)

                # very extreme case
                if beat_idx == start_idx:
                    min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 301
                    min_beat_until_vibe_ends = (
                        min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                    )
                    target_end_beat = vibe_beats[vibe_idx] + min_beat_until_vibe_ends

                    if target_end_beat >= vibe_beats[vibe_idx + 1]:
                        break

                # Even if 'target_end_beat' >= 'vibe_beats[vibe_idx + 1]',
                # vibe power may be activated earlier in order not to extend vibe
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        (bisect_right(raw_beats, vibe_beats[vibe_idx + 1]) - 1)
                        - beat_idx,
                    )
                )
                break
        else:
            if target_end_beat < raw_beats[-1]:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat, bisect_right(raw_beats, target_end_beat) - beat_idx
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(BeatCnt(target_beat, raw_beats_len - beat_idx))
                break
    one_vibe_beatcnts.append(vibe_beatcnts)

two_vibes_beatcnts: list[list[BeatCnt]] = []
for vibe_idx in range(vibe_beats_len - 1):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = next_beat_idxs.pop(0)
    beat_idx = start_idx
    while True:
        target_beat = raw_beats[beat_idx]
        max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * 602
        # TODO: consider bpm change
        max_time_until_vibe_ends = (
            max_time_until_vibe_ends
            + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
        )
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        if vibe_idx < vibe_beats_len - 2:
            if target_end_beat < vibe_beats[vibe_idx + 2]:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat, bisect_right(raw_beats, target_end_beat) - beat_idx
                    )
                )
                beat_idx += 1
            else:
                next_beat_idxs.append(beat_idx)

                # very extreme cases
                if beat_idx == start_idx:
                    # case 1
                    min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 301
                    min_beat_until_vibe_ends = (
                        min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                    )
                    target_end_beat = (
                        vibe_beats[vibe_idx + 1] + min_beat_until_vibe_ends
                    )

                    if target_end_beat >= vibe_beats[vibe_idx + 2]:
                        break

                    # case 2
                    min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 601
                    min_beat_until_vibe_ends = (
                        min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                    )
                    target_end_beat = vibe_beats[vibe_idx] + min_beat_until_vibe_ends

                    if target_end_beat >= vibe_beats[vibe_idx + 2]:
                        break

                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        (bisect_right(raw_beats, vibe_beats[vibe_idx + 2]) - 1)
                        - beat_idx,
                    )
                )
                break
        else:
            if target_end_beat < raw_beats[-1]:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat, bisect_right(raw_beats, target_end_beat) - beat_idx
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(BeatCnt(target_beat, raw_beats_len - beat_idx))
                break
    two_vibes_beatcnts.append(vibe_beatcnts)

three_vibes_beatcnts: list[list[BeatCnt]] = []
for vibe_idx in range(vibe_beats_len - 2):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = next_beat_idxs.pop(0)
    beat_idx = start_idx
    while True:
        target_beat = raw_beats[beat_idx]

        max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * 302
        # TODO: consider bpm change
        max_time_until_vibe_ends = (
            max_time_until_vibe_ends
            + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
        )
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        # if branch: no vibe power loss
        if target_end_beat < vibe_beats[vibe_idx + 2]:
            max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * 902
            # TODO: consider bpm change
            max_time_until_vibe_ends = (
                max_time_until_vibe_ends
                + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
            )
            max_beat_until_vibe_ends = (
                max_time_until_vibe_ends * raw_beatmap.bpm / 60000
            )
            target_end_beat = target_beat + max_beat_until_vibe_ends

            if vibe_idx < vibe_beats_len - 3:
                if target_end_beat < vibe_beats[vibe_idx + 3]:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            bisect_right(raw_beats, target_end_beat) - beat_idx,
                        )
                    )
                    beat_idx += 1
                else:
                    next_beat_idxs.append(beat_idx)

                    # very extreme cases
                    if beat_idx == start_idx:
                        # case 1
                        min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 301
                        min_beat_until_vibe_ends = (
                            min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                        )
                        target_end_beat = (
                            vibe_beats[vibe_idx + 2] + min_beat_until_vibe_ends
                        )

                        if target_end_beat >= vibe_beats[vibe_idx + 3]:
                            break

                        # case 2
                        min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 601
                        min_beat_until_vibe_ends = (
                            min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                        )
                        target_end_beat = (
                            vibe_beats[vibe_idx + 1] + min_beat_until_vibe_ends
                        )

                        if target_end_beat >= vibe_beats[vibe_idx + 3]:
                            break

                        # case 3
                        min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 901
                        min_beat_until_vibe_ends = (
                            min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                        )
                        target_end_beat = (
                            vibe_beats[vibe_idx] + min_beat_until_vibe_ends
                        )

                        if target_end_beat >= vibe_beats[vibe_idx + 3]:
                            break

                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            (bisect_right(raw_beats, vibe_beats[vibe_idx + 2]) - 1)
                            - beat_idx,
                        )
                    )
                    break
            else:
                if target_end_beat < raw_beats[-1]:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            bisect_right(raw_beats, target_end_beat) - beat_idx,
                        )
                    )
                    beat_idx += 1
                else:
                    vibe_beatcnts.append(BeatCnt(target_beat, raw_beats_len - beat_idx))
                    break
        # else branch: vibe power loss
        else:
            next_beat_idxs.append(beat_idx)

            loss_beat = target_end_beat - vibe_beats[vibe_idx + 2]
            loss_time = loss_beat * (60 / raw_beatmap.bpm) * 1000
            time_discount = 0
            if loss_time < 2 * perf_range:
                time_discount = 2 * perf_range - loss_time

            if vibe_idx < vibe_beats_len - 3:
                # case 1
                min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 601
                min_beat_until_vibe_ends = (
                    min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                )
                target_end_beat = vibe_beats[vibe_idx + 2] + min_beat_until_vibe_ends

                if target_end_beat >= vibe_beats[vibe_idx + 3]:
                    break

                # case 3
                min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 901
                min_beat_until_vibe_ends = (
                    min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                )
                target_end_beat = vibe_beats[vibe_idx] + min_beat_until_vibe_ends

                if target_end_beat >= vibe_beats[vibe_idx + 3]:
                    break

                # caution: slightly different calculation
                max_time_until_vibe_ends = (
                    2 * perf_range + FRAME_IN_MSEC * 602 - time_discount
                )
                # TODO: consider bpm change
                max_time_until_vibe_ends = (
                    max_time_until_vibe_ends
                    + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
                )
                max_beat_until_vibe_ends = (
                    max_time_until_vibe_ends * raw_beatmap.bpm / 60000
                )
                target_end_beat = vibe_beats[vibe_idx + 2] + max_beat_until_vibe_ends

                if target_end_beat < vibe_beats[vibe_idx + 3]:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            bisect_right(raw_beats, target_end_beat) - beat_idx,
                        )
                    )
                break
            else:
                max_time_until_vibe_ends = (
                    2 * perf_range + FRAME_IN_MSEC * 603 - time_discount
                )
                # TODO: consider bpm change
                max_time_until_vibe_ends = (
                    max_time_until_vibe_ends
                    + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
                )
                max_beat_until_vibe_ends = (
                    max_time_until_vibe_ends * raw_beatmap.bpm / 60000
                )
                target_end_beat = vibe_beats[vibe_idx + 2] + max_beat_until_vibe_ends

                if target_end_beat < raw_beats[-1]:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            bisect_right(raw_beats, target_end_beat) - beat_idx,
                        )
                    )
                    break
                else:
                    vibe_beatcnts.append(BeatCnt(target_beat, raw_beats_len - beat_idx))
                    break
    three_vibes_beatcnts.append(vibe_beatcnts)

for vibe_beatcnts in one_vibe_beatcnts:
    for beatcnt in vibe_beatcnts:
        print(beatcnt)
    print()
    print(max(vibe_beatcnts))
    print()

for vibe_beatcnts in two_vibes_beatcnts:
    for beatcnt in vibe_beatcnts:
        print(beatcnt)
    print()
    print(max(vibe_beatcnts))
    print()

for vibe_beatcnts in three_vibes_beatcnts:
    for beatcnt in vibe_beatcnts:
        print(beatcnt)
    print()
    print(max(vibe_beatcnts))
    print()
