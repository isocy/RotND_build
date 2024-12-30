from Global import *
from object import *
from enemy_db import EnemyDB
from event import *

from bisect import bisect_right
import itertools
import json
from typing import Self


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
    def __init__(self, start_beat: float, cnt: int, beat_diff: float):
        self.start_beat = start_beat
        self.cnt = cnt
        self.beat_diff = beat_diff

    def __lt__(self, other: Self):
        if self.cnt < other.cnt:
            return True
        elif self.cnt == other.cnt:
            return self.beat_diff > other.beat_diff
        return False

    def __repr__(self):
        return f"{self.start_beat} {self.cnt} {self.beat_diff}"


class Grid:
    def __init__(self):
        self.enemies: list[Node[Enemy]] = []
        self.traps: list[Node[Trap]] = []

    def __repr__(self):
        return (self.enemies + self.traps).__repr__()

    def is_empty(self):
        return not self.enemies and not self.traps


class Map:
    def __init__(self, lanes: int, rows: int):
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
        """Update map for one step
        return: elapsed beat for the update"""
        min_cooltime = init_cooltime
        target_nodes = []
        for i in range(self.lanes):
            for j in range(self.rows):
                for enemy_node in self.grids[i][j].enemies:
                    if enemy_node.cooltime < min_cooltime:
                        min_cooltime = enemy_node.cooltime
                        target_nodes = [enemy_node]
                    elif enemy_node.cooltime == min_cooltime:
                        target_nodes.append(enemy_node)
                for trap_node in self.grids[i][j].traps:
                    if trap_node.cooltime < min_cooltime:
                        min_cooltime = trap_node.cooltime
                        target_nodes = [trap_node]
                    elif trap_node.cooltime == min_cooltime:
                        target_nodes.append(trap_node)

        # subset of 'target_nodes'
        nodes_done = []
        for i in range(self.lanes):
            for j in range(self.rows):
                grid = self.grids[i][j]
                grid_enemies = grid.enemies
                for grid_enemy in grid_enemies:
                    if grid_enemy in nodes_done:
                        continue

                    # Update 'target_nodes'
                    # For enemies previously shielded, do not move
                    if grid_enemy in target_nodes and j != 0:
                        obj = grid_enemy.obj
                        grid_enemy.cooltime = obj.get_cooltime() if j != 1 else 0
                        grid_enemies.remove(grid_enemy)
                        if isinstance(obj, GreenZombie):
                            if i == 0:
                                self.grids[1][j - 1].enemies.append(grid_enemy)
                            elif i == self.lanes - 1:
                                self.grids[self.lanes - 2][j - 1].enemies.append(
                                    grid_enemy
                                )
                            else:
                                if obj.facing == Facing.LEFT:
                                    self.grids[i - 1][j - 1].enemies.append(grid_enemy)
                                    obj.facing = Facing.RIGHT
                                else:
                                    self.grids[i + 1][j - 1].enemies.append(grid_enemy)
                                    obj.facing = Facing.LEFT
                        # TODO
                        elif False:
                            pass
                        else:
                            self.grids[i][j - 1].enemies.append(grid_enemy)
                        nodes_done.append(grid_enemy)
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
    def __init__(self, obj: T, cooltime):
        """Initialize a node which will be present at some grids for a period of time"""
        self.obj = obj
        self.cooltime = cooltime

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

            if name == GREEN_SLIME:
                nodes.append(Node(GreenSlime(lane, chained), appear_beat))
            elif name == BLUE_SLIME:
                nodes.append(Node(BlueSlime(lane, chained), appear_beat))
            # TODO
            elif name == BLUE_BAT:
                nodes.append(
                    Node(BlueBat(lane, enemy_event.facing, chained), appear_beat)
                )
            elif name == YELLOW_BAT:
                nodes.append(
                    Node(YellowBat(lane, enemy_event.facing, chained), appear_beat)
                )
            elif name == GREEN_ZOMBIE:
                nodes.append(
                    Node(GreenZombie(lane, enemy_event.facing, chained), appear_beat)
                )
            elif name == BASE_SKELETON:
                nodes.append(Node(BaseSkeleton(lane, chained), appear_beat))
            elif name == SHIELDED_BASE_SKELETON:
                nodes.append(Node(ShieldedBaseSkeleton(lane, chained), appear_beat))
            elif name == APPLE:
                nodes.append(Node(Apple(lane, chained), appear_beat))
            elif name == CHEESE:
                nodes.append(Node(Cheese(lane, chained), appear_beat))

        return (nodes, chain_cnts)


map = Map(LANES, ROWS)

enemy_db = EnemyDB.json_to_dict(ENEMY_DB_PATH)
EnemyDB.init_objs(enemy_db)

input_ratings_def = InputRatingsDef.load_json(INPUT_RATINGS_DEF_PATH)
perf_range = input_ratings_def.perf_range - 5
great_range = input_ratings_def.great_range - 5

raw_beatmap = RawBeatmap.load_json(RAW_BEATMAP_PATH)
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
            if enemy_node.cooltime != 0:
                continue

            beats.append(Beat(i, cur_beat))
            map.grids[i][0].enemies.remove(enemy_node)

            enemy = enemy_node.obj
            if enemy.shield > 0:
                # no decrement of shield required due to the node exchange
                if isinstance(enemy, ShieldedBaseSkeleton):
                    new_node = Node(
                        BaseSkeleton(i + 1, enemy.chained), enemy.get_cooltime() / 2
                    )
                    map.grids[i][0].enemies.append(new_node)
                # TODO: other shielded enemies
                else:
                    pass
            elif enemy.health > 1:
                enemy.health -= 1
                enemy_node.cooltime = enemy.get_cooltime()
                # TODO: different 'dist_for_move' for different enemies
                if isinstance(enemy, BlueBat) or isinstance(enemy, YellowBat):
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


# Debug: beats
# for beat in beats:
#     print(beat)


# All elements of 'vibe_beats' is included in 'raw_beats'
raw_beats = [beat.beat for beat in beats]
raw_beats_len = len(raw_beats)
vibe_beats_len = len(vibe_beats)

# Let the user be cautious about four or more vibe activation in once
vibe_idx = 0
# Assume 3 consecutive vibe power activation is possible
vibe_in_row = 3
while vibe_idx < vibe_beats_len - 3:
    # one vibe is used for ignitition
    max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * (
        (vibe_in_row - 1) * 300 + 2
    )
    # TODO: consider bpm change
    max_time_until_vibe_ends = (
        max_time_until_vibe_ends
        + (1 / raw_beatmap.beat_divs) * (60 / raw_beatmap.bpm) * 1000
    )
    max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
    target_end_beat = vibe_beats[vibe_idx + 2] + max_beat_until_vibe_ends

    if target_end_beat < vibe_beats[vibe_idx + vibe_in_row]:
        vibe_idx += 1
        vibe_in_row = 3
    else:
        vibe_in_row += 1
        print(
            (
                f"[Caution] As with the first vibe charge of 'vibe_idx' {vibe_idx}, "
                + f"vibe power is extendable up to {vibe_in_row}. "
                + "Check it for the better vibe build."
            )
        )


one_vibe_beatcnts: list[list[BeatCnt]] = []
next_beat_idxs: list[int] = []
# 'vibe_idx' indicates which vibe_beat is the first one
# which contributes to the current vibe activation
for vibe_idx in range(vibe_beats_len):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = bisect_right(raw_beats, vibe_beats[vibe_idx])
    beat_idx = start_idx
    extra_beatcnts_cnt = 1
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
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
                    )
                )
                beat_idx += 1
            else:
                next_beat_idxs.append(beat_idx)

                # very extreme case
                if beat_idx == start_idx:
                    # case 1
                    min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * 301
                    min_beat_until_vibe_ends = (
                        min_time_until_vibe_ends * raw_beatmap.bpm / 60000
                    )
                    target_end_beat = vibe_beats[vibe_idx] + min_beat_until_vibe_ends

                    if target_end_beat >= vibe_beats[vibe_idx + 1]:
                        break

                # Even if 'target_end_beat' >= 'vibe_beats[vibe_idx + 1]',
                # vibe power may be activated earlier in order not to extend vibe
                target_end_beat_idx = (
                    bisect_right(raw_beats, vibe_beats[vibe_idx + 1]) - 1
                )
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
                    )
                )
                break
        else:
            if target_end_beat < raw_beats[-1]:
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        raw_beats_len - beat_idx,
                        raw_beats[-1] - target_beat,
                    )
                )
                if extra_beatcnts_cnt == 0:
                    break
                else:
                    extra_beatcnts_cnt -= 1
                    beat_idx += 1
    one_vibe_beatcnts.append(vibe_beatcnts)

two_vibes_beatcnts: list[list[BeatCnt]] = []
for vibe_idx in range(vibe_beats_len - 1):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = next_beat_idxs.pop(0)
    beat_idx = start_idx
    extra_beatcnts_cnt = 1
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
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
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

                target_end_beat_idx = (
                    bisect_right(raw_beats, vibe_beats[vibe_idx + 2]) - 1
                )
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
                    )
                )
                break
        else:
            if target_end_beat < raw_beats[-1]:
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        raw_beats[target_end_beat_idx - 1] - target_beat,
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        raw_beats_len - beat_idx,
                        raw_beats[-1] - target_beat,
                    )
                )
                if extra_beatcnts_cnt == 0:
                    break
                else:
                    extra_beatcnts_cnt -= 1
                    beat_idx += 1
    two_vibes_beatcnts.append(vibe_beatcnts)

three_vibes_beatcnts: list[list[BeatCnt]] = []
for vibe_idx in range(vibe_beats_len - 2):
    vibe_beatcnts: list[BeatCnt] = []
    start_idx = next_beat_idxs.pop(0)
    beat_idx = start_idx
    extra_beatcnts_cnt = 1
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
                    target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            target_end_beat_idx - beat_idx,
                            raw_beats[target_end_beat_idx - 1] - target_beat,
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

                    target_end_beat_idx = (
                        bisect_right(raw_beats, vibe_beats[vibe_idx + 2]) - 1
                    )
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            target_end_beat_idx - beat_idx,
                            raw_beats[target_end_beat_idx - 1] - target_beat,
                        )
                    )
                    break
            else:
                if target_end_beat < raw_beats[-1]:
                    target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            target_end_beat_idx - beat_idx,
                            raw_beats[target_end_beat_idx - 1] - target_beat,
                        )
                    )
                    beat_idx += 1
                else:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            raw_beats_len - beat_idx,
                            raw_beats[-1] - target_beat,
                        )
                    )
                    if extra_beatcnts_cnt == 0:
                        break
                    else:
                        extra_beatcnts_cnt -= 1
                        beat_idx += 1
        # else branch: vibe power loss
        else:
            loss_beat = target_end_beat - vibe_beats[vibe_idx + 2]
            loss_time = loss_beat * (60 / raw_beatmap.bpm) * 1000
            time_discount = 0
            if loss_time < 2 * perf_range:
                time_discount = 2 * perf_range - loss_time

            if vibe_idx < vibe_beats_len - 3:
                next_beat_idxs.append(beat_idx)

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
                    target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            target_end_beat_idx - beat_idx,
                            raw_beats[target_end_beat_idx - 1] - target_beat,
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
                    target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            target_end_beat_idx - beat_idx,
                            raw_beats[target_end_beat_idx - 1] - target_beat,
                        )
                    )
                    break
                else:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            raw_beats_len - beat_idx,
                            raw_beats[-1] - target_beat,
                        )
                    )
                    if extra_beatcnts_cnt == 0:
                        break
                    else:
                        extra_beatcnts_cnt -= 1
                        beat_idx += 1
    three_vibes_beatcnts.append(vibe_beatcnts)

# For Debug
# for vibe_beatcnts in one_vibe_beatcnts:
#     for beatcnt in vibe_beatcnts:
#         print(beatcnt)
#     print()
#     print(max(vibe_beatcnts))
#     print()
# print()
# for vibe_beatcnts in two_vibes_beatcnts:
#     for beatcnt in vibe_beatcnts:
#         print(beatcnt)
#     print()
#     print(max(vibe_beatcnts))
#     print()
# print()
# for vibe_beatcnts in three_vibes_beatcnts:
#     for beatcnt in vibe_beatcnts:
#         print(beatcnt)
#     print()
#     print(max(vibe_beatcnts))
#     print()
# print()


# originated from efficient integer partitioning code from
# https://stackoverflow.com/questions/10035752/elegant-python-code-for-integer-partitioning
def get_partitions(n):
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2 * x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            if [element for element in a[: k + 2] if element > 3] == []:
                yield a[: k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        if [element for element in a[: k + 1] if element > 3] == []:
            yield a[: k + 1]


partitions = [
    *itertools.chain.from_iterable(
        set(itertools.permutations(p)) for p in get_partitions(vibe_beats_len)
    )
]

max_one_vibe_beatcnts = []
max_two_vibes_beatcnts = []
max_three_vibes_beatcnts = []
for beatcnts in one_vibe_beatcnts:
    max_one_vibe_beatcnts.append(
        max(
            [
                beatcnt
                for beatcnt in beatcnts
                if beatcnt.beat_diff < ONE_VIBE_MAX_BEAT_DIFF
                and beatcnt.start_beat not in ONE_VIBE_START_BEATS_EXCEPT
            ]
        )
    )
for beatcnts in two_vibes_beatcnts:
    max_two_vibes_beatcnts.append(
        max(
            [
                beatcnt
                for beatcnt in beatcnts
                if beatcnt.beat_diff < TWO_VIBES_MAX_BEAT_DIFF
                and beatcnt.start_beat not in TWO_VIBES_START_BEATS_EXCEPT
            ]
        )
    )
for beatcnts in three_vibes_beatcnts:
    max_three_vibes_beatcnts.append(
        max(
            [
                beatcnt
                for beatcnt in beatcnts
                if beatcnt.beat_diff < THREE_VIBES_MAX_BEAT_DIFF
                and beatcnt.start_beat not in THREE_VIBES_START_BEATS_EXCEPT
            ]
        )
    )

practice_start_nums = [
    vibe_event.start_beat + ROWS - 1 for vibe_event in raw_beatmap.vibe_events
]
print("\nPractice Start Numbers:")
print(practice_start_nums, end="\n\n")

for partition in partitions:
    max_beatcnts: list[BeatCnt] = []
    vibe_idx = 0
    for num in partition:
        if num == 1:
            max_beatcnts.append(max_one_vibe_beatcnts[vibe_idx])
            vibe_idx += 1
        elif num == 2:
            max_beatcnts.append(max_two_vibes_beatcnts[vibe_idx])
            vibe_idx += 2
        else:
            max_beatcnts.append(max_three_vibes_beatcnts[vibe_idx])
            vibe_idx += 3
    print(
        str(partition)
        + ", "
        + str(sum(max_beatcnt.cnt for max_beatcnt in max_beatcnts))
    )
    print(max_beatcnts)
