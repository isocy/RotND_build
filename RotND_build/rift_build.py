from Global import *
from object import *
from enemy_db import EnemyDB
from event import *

from bisect import bisect_right, bisect_left
import itertools
import json
from math import floor
import numpy as np
from typing import Self


class InputRatingsDef:
    def __init__(
        self,
        perf_range: float,
        great_range: float,
        perf_score: int,
        great_score: int,
        perf_bonus: int,
        true_perf_bonus: int,
    ):
        self.perf_range = perf_range
        self.great_range = great_range
        self.perf_score = perf_score
        self.great_score = great_score
        self.perf_bonus = perf_bonus
        self.true_perf_bonus = true_perf_bonus

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            input_ratings_def = json.load(f)

        hit_window = input_ratings_def["_beforeBeatHitWindow"] * 1000
        ratings = input_ratings_def["_ratings"]

        perf_range = (100 - ratings[-1]["minimumValue"]) * hit_window / 100
        great_range = (100 - ratings[-2]["minimumValue"]) * hit_window / 100

        perf_score = ratings[-1]["score"]
        great_score = ratings[-2]["score"]
        perf_bonus = input_ratings_def["_perfectBonusScore"]
        true_perf_bonus = input_ratings_def["_truePerfectBonusScore"]

        return InputRatingsDef(
            perf_range,
            great_range,
            perf_score,
            great_score,
            perf_bonus,
            true_perf_bonus,
        )


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


class Build:
    def __init__(
        self,
        partition: tuple[int, ...],
        cnt_sum: int,
        beatcnts: list[BeatCnt],
        expected_score: int,
    ):
        self.partition = partition
        self.cnt_sum = cnt_sum
        self.beatcnts = beatcnts
        self.expected_score = expected_score

    def __lt__(self, other: Self):
        if self.cnt_sum == other.cnt_sum:
            self_len = len(self.partition)
            other_len = len(other.partition)
            if self_len == other_len:
                return self.partition > self.partition
            return self_len > other_len
        return self.cnt_sum < other.cnt_sum

    def __repr__(self):
        return "{}, {}\n{}, {}".format(
            str(self.partition),
            str(self.cnt_sum),
            self.beatcnts,
            str(self.expected_score),
        )


class Node[T: Object]:
    def __init__(self, obj: T, cooltime: float):
        """Initialize a node which will be present at some grids for a period of time"""
        self.obj = obj
        self.cooltime = cooltime

    def __eq__(self, other: Self):
        if self is None or other is None:
            return False
        return self.obj == other.obj

    def __repr__(self):
        return f"{self.obj} {self.cooltime}"

    @classmethod
    def obj_events_to_nodes(
        cls,
        obj_events: list[ObjectEvent],
        # Used to determine whether a node of enemy is vibe-chained
        vibe_events: list[VibeEvent],
        enemy_db: dict,
    ) -> tuple[list["Node"], list[int]]:
        """Convert events into nodes
        Returns the list of nodes and the list of vibe chain counts"""
        nodes: list[Node] = []

        vibe_events_len = len(vibe_events)
        chain_cnts = []
        chain_cnt = 0

        for obj_event in obj_events:
            if isinstance(obj_event, EnemyEvent):
                lane = obj_event.lane
                appear_beat = obj_event.appear_beat

                enemy_id = obj_event.enemy_id
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
                # TODO: enemies
                elif name == BLUE_BAT:
                    nodes.append(
                        Node(BlueBat(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == YELLOW_BAT:
                    nodes.append(
                        Node(YellowBat(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == RED_BAT:
                    nodes.append(
                        Node(RedBat(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == GREEN_ZOMBIE:
                    nodes.append(
                        Node(GreenZombie(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == RED_ZOMBIE:
                    nodes.append(
                        Node(RedZombie(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == BASE_SKELETON:
                    nodes.append(Node(BaseSkeleton(lane, chained), appear_beat))
                elif name == SHIELDED_BASE_SKELETON:
                    nodes.append(Node(ShieldedBaseSkeleton(lane, chained), appear_beat))
                elif name == YELLOW_SKELETON:
                    nodes.append(Node(YellowSkeleton(lane, chained), appear_beat))
                elif name == SHIELDED_YELLOW_SKELETON:
                    nodes.append(
                        Node(ShieldedYellowSkeleton(lane, chained), appear_beat)
                    )
                elif name == BLACK_SKELETON:
                    nodes.append(Node(BlackSkeleton(lane, chained), appear_beat))
                elif name == SHIELDED_BLACK_SKELETON:
                    nodes.append(
                        Node(ShieldedBlackSkeleton(lane, chained), appear_beat)
                    )
                elif name == BASE_HARPY:
                    nodes.append(Node(BaseHarpy(lane, chained), appear_beat))
                elif name == BLUE_HARPY:
                    nodes.append(Node(BlueHarpy(lane, chained), appear_beat))
                elif name == APPLE:
                    nodes.append(Node(Apple(lane, chained), appear_beat))
                elif name == CHEESE:
                    nodes.append(Node(Cheese(lane, chained), appear_beat))
                elif name == DRUMSTICK:
                    nodes.append(Node(Drumstick(lane, chained), appear_beat))
                elif name == HAM:
                    nodes.append(Node(Ham(lane, chained), appear_beat))
                elif name == BASE_BLADEMASTER:
                    assert isinstance(obj_event, BlademasterEvent)
                    nodes.append(
                        Node(
                            Blademaster(lane, chained, obj_event.attack_row),
                            appear_beat,
                        )
                    )
            elif isinstance(obj_event, BounceEvent):
                lane = obj_event.lane
                row = obj_event.row
                appear_beat = obj_event.appear_beat
                duration = obj_event.duration
                dir = obj_event.dir

                nodes.append(Node(Bounce(lane, row, duration, dir), appear_beat))
            elif isinstance(obj_event, PortalEvent):
                lane = obj_event.lane
                row = obj_event.row
                appear_beat = obj_event.appear_beat
                duration = obj_event.duration
                child_lane = obj_event.child_lane
                child_row = obj_event.child_row

                nodes.append(
                    Node(
                        Portal(lane, row, child_lane, child_row, duration), appear_beat
                    )
                )
            # TODO: traps
            elif False:
                pass

        return (nodes, chain_cnts)


class Grid:
    def __init__(self):
        self.enemies: list[Node[Enemy]] = []
        self.trap: Node[Trap] | None = None

    def __repr__(self):
        return (self.enemies + [self.trap]).__repr__()

    def is_empty(self):
        return not self.enemies and self.trap == None


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
                str += "{:<30}".format(map.grids[i][j].__repr__())
            str += "\n"
        return str

    def is_clean(self):
        for i in range(self.lanes):
            for j in range(self.rows):
                if not self.grids[i][j].is_empty():
                    return False
        return True

    def is_node_blocked(self, i: int, j: int, target_nodes: list[Node[Enemy]]):
        """Determine if the headless skeleton node is blocked at the current timestep."""
        is_blocked = False
        will_be_blocked = False
        for upper_enemy in self.grids[i][j].enemies:
            if not isinstance(upper_enemy, Harpy):
                if (
                    upper_enemy in target_nodes
                    or upper_enemy.cooltime < ONBEAT_THRESHOLD
                ):
                    is_blocked = True
                    break
                else:
                    will_be_blocked = True

        upper_trap = self.grids[i][j].trap
        if not is_blocked and upper_trap != None and isinstance(upper_trap.obj, Bounce):
            return (False, False)

        for upper_enemy in self.grids[i][j + 1].enemies:
            if not isinstance(upper_enemy, Harpy):
                will_be_blocked = True
                break

        return (is_blocked, will_be_blocked)

    def is_node_blocked_imm(self, i: int):
        """Determine if the newly created headless skeleton node is blocked immediately."""
        is_blocked = False
        for upper_enemy in self.grids[i][1].enemies + self.grids[i][2].enemies:
            if not upper_enemy.obj.flying:
                is_blocked = True
                break

        return is_blocked

    def is_left_open(self, i: int, j: int, target_enemy: Node[Enemy]):
        """Determine if the zombie at position (i, j) can go to left"""
        is_left_open = True
        for enemy in self.grids[i - 1][j - 1].enemies:
            if not enemy.obj.flying:
                is_zombie = isinstance(enemy.obj, Zombie)
                if (
                    is_zombie
                    and enemy.cooltime - target_enemy.cooltime > 1 - ONBEAT_THRESHOLD
                    or not is_zombie
                    and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                ):
                    is_left_open = False
                    break
        if is_left_open:
            for enemy in self.grids[i - 1][j].enemies:
                if (
                    not enemy.obj.flying
                    and not isinstance(enemy.obj, Zombie)
                    and enemy.cooltime < ONBEAT_THRESHOLD
                ):
                    is_left_open = False
                    break

        return is_left_open

    def is_right_open(self, i: int, j: int, target_enemy: Node[Enemy]):
        """Determine if the zombie at position (i, j) can go to right"""
        is_right_open = True
        for enemy in self.grids[(i + 1) % self.lanes][j - 1].enemies:
            if not enemy.obj.flying:
                is_zombie = isinstance(enemy.obj, Zombie)
                if (
                    is_zombie
                    and enemy.cooltime - target_enemy.cooltime > 1 - ONBEAT_THRESHOLD
                    or not is_zombie
                    and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                ):
                    is_right_open = False
                    break
        if is_right_open:
            for enemy in self.grids[(i + 1) % self.lanes][j].enemies:
                if (
                    not enemy.obj.flying
                    and not isinstance(enemy.obj, Zombie)
                    and enemy.cooltime < ONBEAT_THRESHOLD
                ):
                    is_right_open = False
                    break

        return is_right_open

    def step_trap(
        self, init_i: int, init_j: int, enemy_node: Node[Enemy]
    ) -> tuple[int, int]:
        """Move 'enemy_node' to the appropriate position
        if there is a trap at (init_i, init_j)."""
        trap_node = self.grids[init_i][init_j].trap
        if trap_node != None:
            trap = trap_node.obj
            if isinstance(trap, Bounce):
                dir = trap.dir
                # TODO: other directions
                if dir == TrapDir.UP:
                    init_j += 1
                elif dir == TrapDir.RIGHT:
                    init_i += 1
                elif dir == TrapDir.LEFT:
                    init_i -= 1
                elif dir == TrapDir.DOWNLEFT:
                    init_i -= 1
                    init_j -= 1
                elif dir == TrapDir.DOWNRIGHT:
                    init_i += 1
                    init_j -= 1
                else:
                    pass

                self.grids[init_i % self.lanes][init_j].enemies.append(enemy_node)
            elif isinstance(trap, Portal):
                init_i = trap.child_lane - 1
                init_j = trap.child_row

                self.grids[init_i][init_j].enemies.append(enemy_node)
            # TODO: other traps
            elif False:
                pass
        else:
            self.grids[init_i][init_j].enemies.append(enemy_node)

        return init_i, init_j


class RawBeatmap:
    def __init__(self, bpm, beat_divs, obj_events, vibe_events):
        self.bpm = bpm
        self.beat_divs = beat_divs
        self.obj_events: list[ObjectEvent] = obj_events
        self.vibe_events: list[VibeEvent] = vibe_events

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            raw_beatmap = json.load(f)

        obj_events = []
        vibe_events = []
        for event in raw_beatmap["events"]:
            if event["type"] == "SpawnEnemy" or event["type"] == "SpawnTrap":
                obj_events.append(event)
            elif event["type"] == "StartVibeChain":
                vibe_events.append(event)

        return RawBeatmap(
            raw_beatmap["bpm"],
            raw_beatmap["beatDivisions"],
            [ObjectEvent.load_dict(event) for event in obj_events],
            [VibeEvent.load_dict(vibe_event) for vibe_event in vibe_events],
        )


map = Map(LANES, ROWS)

enemy_db = EnemyDB.json_to_dict(ENEMY_DB_PATH)
EnemyDB.init_objs(enemy_db)

input_ratings_def = InputRatingsDef.load_json(INPUT_RATINGS_DEF_PATH)
perf_range = input_ratings_def.perf_range - 5
great_range = input_ratings_def.great_range - 5
perf_score = input_ratings_def.perf_score
great_score = input_ratings_def.great_score
perf_bonus = input_ratings_def.perf_bonus
true_perf_bonus = input_ratings_def.true_perf_bonus

raw_beatmap = RawBeatmap.load_json(RAW_BEATMAP_PATH)
(nodes, chain_cnts) = Node.obj_events_to_nodes(
    raw_beatmap.obj_events, raw_beatmap.vibe_events, enemy_db
)
nodes_len = len(nodes)

# These beats indicate the moment a vibe power is charged
vibe_beats: list[float] = []
chain_idx = 0

beats: list[Beat] = []
node_idx = 0
cur_beat = 0
next_node = nodes[node_idx]
# cooltime changes of nodes for each iteration of the outmost loop cost a lot,
# so the cooltime corrections occur for each node when the node is 'next_node'.
while node_idx < nodes_len or not map.is_clean():
    # derive 'min_cooltime'
    min_cooltime = next_node.cooltime
    target_nodes: list = []
    for i in range(map.lanes):
        for j in range(map.rows):
            for enemy_node in map.grids[i][j].enemies:
                if enemy_node.cooltime < min_cooltime:
                    min_cooltime = enemy_node.cooltime
                    target_nodes = [enemy_node]
                elif enemy_node.cooltime == min_cooltime:
                    target_nodes.append(enemy_node)
            trap_node = map.grids[i][j].trap
            if trap_node != None:
                if trap_node.cooltime < min_cooltime:
                    min_cooltime = trap_node.cooltime
                    target_nodes = [trap_node]
                elif trap_node.cooltime == min_cooltime:
                    target_nodes.append(trap_node)

    # decrement lifetime of traps
    #
    # Let a trap despawn at t=0.
    # If an enemy reaches the grid where the trap was at the same time t=0,
    # Then enemy should NOT be affected by the trap
    # That's why this code block is ahead of all below
    for i in range(map.lanes):
        for j in range(map.rows):
            grid = map.grids[i][j]
            trap_node = grid.trap

            if trap_node in target_nodes:
                grid.trap = None
                target_nodes.remove(trap_node)
            elif trap_node != None:
                trap_node.cooltime = round(trap_node.cooltime - min_cooltime, NDIGITS)

    # now 'target_nodes' only contains enemy nodes

    # exclusion of 'target_nodes'
    nodes_done = []

    # introduce new nodes
    #
    # Let a trap spawn at t=0 and at some grid.
    # If an enemy reaches that grid at the same time t=0,
    # Then enemy should be affected by the trap
    # That's why this code block is ahead of below
    if node_idx < nodes_len:
        next_node.cooltime = round(next_node.cooltime - min_cooltime, NDIGITS)

        while next_node.cooltime == 0:
            obj: Object = next_node.obj
            next_node.cooltime = obj.get_cooltime()
            if isinstance(obj, Enemy):
                if obj.flying:
                    map.grids[obj.appear_lane - 1][Enemy.appear_row].enemies.append(
                        next_node
                    )
                else:
                    map.step_trap(obj.appear_lane - 1, Enemy.appear_row, next_node)
            elif isinstance(obj, Trap):
                map.grids[obj.appear_lane - 1][obj.appear_row].trap = next_node
            nodes_done.append(next_node)

            node_idx += 1
            if node_idx >= nodes_len:
                break
            next_node = nodes[node_idx]
            next_node.cooltime = round(
                next_node.cooltime - (cur_beat + min_cooltime), NDIGITS
            )

    # let the time pass by for enemies
    for i in range(map.lanes):
        for j in range(map.rows):
            grid = map.grids[i][j]
            grid_enemies = grid.enemies
            enemies_removed = []
            for grid_enemy in grid_enemies:
                if grid_enemy in nodes_done:
                    continue

                # Update 'target_nodes'
                # For enemies previously shielded, do not move
                if grid_enemy in target_nodes and j != 0:
                    obj = grid_enemy.obj
                    dist = obj.dist_per_move
                    grid_enemy.cooltime = obj.get_cooltime() if j != dist else 0
                    if obj.flying:
                        map.grids[i][j - dist].enemies.append(grid_enemy)
                    # zombies later
                    elif isinstance(obj, Zombie):
                        continue
                    elif isinstance(obj, HeadlessSkeleton) and dist == -1:
                        (is_blocked, will_be_blocked) = map.is_node_blocked(
                            i, j - dist, target_nodes
                        )
                        if is_blocked or will_be_blocked:
                            obj.dist_per_move = 1
                            dist = 1

                        if is_blocked or not will_be_blocked:
                            map.step_trap(i, j - dist, grid_enemy)
                        else:
                            map.grids[i][j].enemies.append(grid_enemy)
                    elif isinstance(obj, Blademaster):
                        if obj.is_ready:
                            grid_enemy.cooltime = 0
                            map.grids[i][0].enemies.append(grid_enemy)
                        elif obj.attack_row == j:
                            obj.is_ready = True
                            grid_enemy.cooltime = obj.get_cooltime()
                            map.grids[i][j].enemies.append(grid_enemy)
                        else:
                            map.step_trap(i, j - dist, grid_enemy)
                    else:
                        map.step_trap(i, j - dist, grid_enemy)
                    enemies_removed.append(grid_enemy)
                    nodes_done.append(grid_enemy)
                else:
                    grid_enemy.cooltime = round(
                        grid_enemy.cooltime - min_cooltime, NDIGITS
                    )

            for enemy_removed in enemies_removed:
                grid_enemies.remove(enemy_removed)

    # resolve collisions for zombies
    for i in range(map.lanes):
        for j in range(map.rows):
            grid = map.grids[i][j]
            grid_enemies = grid.enemies
            enemies_removed = []

            for grid_enemy in grid_enemies:
                if grid_enemy in nodes_done:
                    continue

                if grid_enemy in target_nodes and j != 0:
                    obj = grid_enemy.obj
                    assert isinstance(obj, Zombie)
                    dist = obj.dist_per_move
                    grid_enemy.cooltime = obj.get_cooltime() if j != dist else 0
                    if isinstance(obj, GreenZombie):
                        if obj.facing == Facing.LEFT:
                            is_left_open = (
                                map.is_left_open(i, j, grid_enemy) if i != 0 else False
                            )

                            if is_left_open:
                                (new_i, new_j) = map.step_trap(
                                    i - 1, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.RIGHT
                                is_right_open = (
                                    map.is_right_open(i, j, grid_enemy)
                                    if i != map.lanes - 1
                                    else False
                                )

                                if is_right_open:
                                    (new_i, new_j) = map.step_trap(
                                        i + 1, j - dist, grid_enemy
                                    )
                                else:
                                    (new_i, new_j) = map.step_trap(
                                        i, j - dist, grid_enemy
                                    )
                        else:
                            is_right_open = (
                                map.is_right_open(i, j, grid_enemy)
                                if i != map.lanes - 1
                                else False
                            )

                            if is_right_open:
                                (new_i, new_j) = map.step_trap(
                                    i + 1, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.LEFT
                                is_left_open = (
                                    map.is_left_open(i, j, grid_enemy)
                                    if i != 0
                                    else False
                                )

                                if is_left_open:
                                    (new_i, new_j) = map.step_trap(
                                        i - 1, j - dist, grid_enemy
                                    )
                                else:
                                    (new_i, new_j) = map.step_trap(
                                        i, j - dist, grid_enemy
                                    )

                        if new_j == 1:
                            if obj.facing == Facing.LEFT:
                                is_left_open = True if new_i != 0 else False
                                if is_left_open:
                                    for enemy in map.grids[new_i - 1][new_j].enemies:
                                        if (
                                            not enemy.obj.flying
                                            and not isinstance(enemy.obj, Zombie)
                                            and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                                        ):
                                            is_left_open = False
                                            break
                                if is_left_open:
                                    for enemy in map.grids[new_i - 2][new_j].enemies:
                                        if (
                                            enemy.obj.facing == Facing.RIGHT
                                            and enemy.cooltime > ONBEAT_THRESHOLD
                                            and (
                                                isinstance(enemy.obj, GreenZombie)
                                                and new_i != 1
                                                or isinstance(enemy.obj, RedZombie)
                                            )
                                        ):
                                            is_left_open = False
                                            break
                                if not is_left_open:
                                    obj.facing = Facing.RIGHT
                            else:
                                is_right_open = (
                                    True if new_i != map.lanes - 1 else False
                                )
                                if is_right_open:
                                    for enemy in map.grids[new_i + 1][new_j].enemies:
                                        if (
                                            not enemy.obj.flying
                                            and not isinstance(enemy.obj, Zombie)
                                            and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                                        ):
                                            is_right_open = False
                                            break
                                if is_right_open:
                                    for enemy in map.grids[(new_i + 2) % map.lanes][
                                        new_j
                                    ].enemies:
                                        if (
                                            enemy.obj.facing == Facing.LEFT
                                            and enemy.cooltime > ONBEAT_THRESHOLD
                                            and (
                                                isinstance(enemy.obj, GreenZombie)
                                                and new_i != map.lanes - 2
                                                or isinstance(enemy.obj, RedZombie)
                                            )
                                        ):
                                            is_right_open = False
                                            break
                                if not is_right_open:
                                    obj.facing = Facing.LEFT
                    elif isinstance(obj, RedZombie):
                        if obj.facing == Facing.LEFT:
                            is_left_open = map.is_left_open(i, j, grid_enemy)

                            if is_left_open:
                                (new_i, new_j) = map.step_trap(
                                    i - 1, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.RIGHT
                                is_right_open = map.is_right_open(i, j, grid_enemy)

                                if is_right_open:
                                    (new_i, new_j) = map.step_trap(
                                        (i + 1) % map.lanes, j - dist, grid_enemy
                                    )
                                else:
                                    (new_i, new_j) = map.step_trap(
                                        i, j - dist, grid_enemy
                                    )
                        else:
                            is_right_open = map.is_right_open(i, j, grid_enemy)

                            if is_right_open:
                                (new_i, new_j) = map.step_trap(
                                    (i + 1) % map.lanes, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.LEFT
                                is_left_open = map.is_left_open(i, j, grid_enemy)

                                if is_left_open:
                                    (new_i, new_j) = map.step_trap(
                                        i - 1, j - dist, grid_enemy
                                    )
                                else:
                                    (new_i, new_j) = map.step_trap(
                                        i, j - dist, grid_enemy
                                    )

                        if new_j == 1:
                            if obj.facing == Facing.LEFT:
                                is_left_open = True
                                for enemy in map.grids[new_i - 1][new_j].enemies:
                                    if (
                                        not enemy.obj.flying
                                        and not isinstance(enemy.obj, Zombie)
                                        and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                                    ):
                                        is_left_open = False
                                        break
                                if is_left_open:
                                    for enemy in map.grids[new_i - 2][new_j].enemies:
                                        if (
                                            enemy.obj.facing == Facing.RIGHT
                                            and enemy.cooltime > ONBEAT_THRESHOLD
                                            and (
                                                isinstance(enemy.obj, GreenZombie)
                                                and new_i != 1
                                                or isinstance(enemy.obj, RedZombie)
                                            )
                                        ):
                                            is_left_open = False
                                            break
                                if not is_left_open:
                                    obj.facing = Facing.RIGHT
                            else:
                                is_right_open = True
                                for enemy in map.grids[(new_i + 1) % map.lanes][
                                    new_j
                                ].enemies:
                                    if (
                                        not enemy.obj.flying
                                        and not isinstance(enemy.obj, Zombie)
                                        and enemy.cooltime > 1 - ONBEAT_THRESHOLD
                                    ):
                                        is_right_open = False
                                        break
                                if is_right_open:
                                    for enemy in map.grids[(new_i + 2) % map.lanes][
                                        new_j
                                    ].enemies:
                                        if (
                                            enemy.obj.facing == Facing.LEFT
                                            and enemy.cooltime > ONBEAT_THRESHOLD
                                            and (
                                                isinstance(enemy.obj, GreenZombie)
                                                and new_i != map.lanes - 2
                                                or isinstance(enemy.obj, RedZombie)
                                            )
                                        ):
                                            is_right_open = False
                                            break
                                if not is_right_open:
                                    obj.facing = Facing.LEFT
                    enemies_removed.append(grid_enemy)
                    nodes_done.append(grid_enemy)

            for enemy_removed in enemies_removed:
                grid_enemies.remove(enemy_removed)

    cur_beat = round(cur_beat + min_cooltime, NDIGITS)

    # Debug: map
    # if 398 < cur_beat < 440:
    #     print(cur_beat)
    #     print(map)

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
                    new_node: Node[Enemy] = Node(
                        BaseSkeleton(i + 1, enemy.chained), enemy.get_cooltime() / 2
                    )
                    map.grids[i][0].enemies.append(new_node)
                elif isinstance(enemy, ShieldedYellowSkeleton):
                    new_node = Node(
                        YellowSkeleton(i + 1, enemy.chained), enemy.get_cooltime() / 2
                    )
                    map.grids[i][0].enemies.append(new_node)
                elif isinstance(enemy, ShieldedBlackSkeleton):
                    new_node = Node(
                        BlackSkeleton(i + 1, enemy.chained), enemy.get_cooltime() / 2
                    )
                    map.grids[i][0].enemies.append(new_node)
                # TODO: other shielded enemies
                elif False:
                    pass
            elif enemy.health > 1:
                enemy.health -= 1
                enemy_node.cooltime = enemy.get_cooltime()
                # TODO: health > 1 enemies
                if isinstance(enemy, BlueBat) or isinstance(enemy, YellowBat):
                    if enemy.facing == Facing.LEFT:
                        map.grids[i - 1][1].enemies.append(enemy_node)
                    else:
                        map.grids[(i + 1) % 3][1].enemies.append(enemy_node)
                elif isinstance(enemy, RedBat):
                    if enemy.facing == Facing.LEFT:
                        map.grids[i - 1][1].enemies.append(enemy_node)
                        enemy.facing = Facing.RIGHT
                    else:
                        map.grids[(i + 1) % 3][1].enemies.append(enemy_node)
                        enemy.facing = Facing.LEFT
                elif isinstance(enemy, BlueHarpy):
                    map.grids[i][2].enemies.append(enemy_node)
                elif isinstance(enemy, YellowSkeleton):
                    dist_per_move = -1
                    is_blocked = map.is_node_blocked_imm(i)
                    if is_blocked:
                        dist_per_move = 1

                    new_node = Node(
                        HeadlessYellowSkeleton(i + 1, enemy.chained, dist_per_move),
                        enemy.get_cooltime(),
                    )
                    map.step_trap(i, 1, new_node)
                elif isinstance(enemy, BlackSkeleton) and enemy.health == 1:
                    dist_per_move = -1
                    is_blocked = map.is_node_blocked_imm(i)
                    if is_blocked:
                        dist_per_move = 1

                    new_node = Node(
                        HeadlessBlackSkeleton(i + 1, enemy.chained, dist_per_move),
                        enemy.get_cooltime(),
                    )
                    map.step_trap(i, 1, new_node)
                else:
                    map.step_trap(i, 1, enemy_node)
            elif enemy.chained:
                chain_cnts[chain_idx] -= 1

                if chain_cnts[chain_idx] == 0:
                    # TODO: special case for wyrms
                    vibe_beats.append(cur_beat)
                    chain_idx += 1


# Debug: beats
# same_beats = [beats[0]]
# for beat in beats[1:]:
#     if same_beats[0].beat == beat.beat:
#         same_beats.append(beat)
#     else:
#         print(same_beats)
#         same_beats = [beat]
# print(same_beats)


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
    max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
        1 / raw_beatmap.beat_divs
    ) * (60 / raw_beatmap.bpm)
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
        max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
            1 / raw_beatmap.beat_divs
        ) * (60 / raw_beatmap.bpm)
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        if vibe_idx < vibe_beats_len - 1:
            if target_end_beat < vibe_beats[vibe_idx + 1]:
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
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
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
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
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        raw_beats_len - beat_idx,
                        round(raw_beats[-1] - target_beat, NDIGITS),
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
        max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
            1 / raw_beatmap.beat_divs
        ) * (60 / raw_beatmap.bpm)
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        if vibe_idx < vibe_beats_len - 2:
            if target_end_beat < vibe_beats[vibe_idx + 2]:
                target_end_beat_idx = bisect_right(raw_beats, target_end_beat)
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        target_end_beat_idx - beat_idx,
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
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
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
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
                        round(
                            raw_beats[target_end_beat_idx - 1] - target_beat, NDIGITS
                        ),
                    )
                )
                beat_idx += 1
            else:
                vibe_beatcnts.append(
                    BeatCnt(
                        target_beat,
                        raw_beats_len - beat_idx,
                        round(raw_beats[-1] - target_beat, NDIGITS),
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
        max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
            1 / raw_beatmap.beat_divs
        ) * (60 / raw_beatmap.bpm)
        max_beat_until_vibe_ends = max_time_until_vibe_ends * raw_beatmap.bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends

        # if branch: no vibe power loss
        if target_end_beat < vibe_beats[vibe_idx + 2]:
            max_time_until_vibe_ends = 2 * perf_range + FRAME_IN_MSEC * 902
            # TODO: consider bpm change
            max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
                1 / raw_beatmap.beat_divs
            ) * (60 / raw_beatmap.bpm)
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
                            round(
                                raw_beats[target_end_beat_idx - 1] - target_beat,
                                NDIGITS,
                            ),
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
                            round(
                                raw_beats[target_end_beat_idx - 1] - target_beat,
                                NDIGITS,
                            ),
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
                            round(
                                raw_beats[target_end_beat_idx - 1] - target_beat,
                                NDIGITS,
                            ),
                        )
                    )
                    beat_idx += 1
                else:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            raw_beats_len - beat_idx,
                            round(raw_beats[-1] - target_beat, NDIGITS),
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
            loss_time = 1000 * loss_beat * (60 / raw_beatmap.bpm)
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
                max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
                    1 / raw_beatmap.beat_divs
                ) * (60 / raw_beatmap.bpm)
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
                            round(
                                raw_beats[target_end_beat_idx - 1] - target_beat,
                                NDIGITS,
                            ),
                        )
                    )
                break
            else:
                max_time_until_vibe_ends = (
                    2 * perf_range + FRAME_IN_MSEC * 603 - time_discount
                )
                # TODO: consider bpm change
                max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (
                    1 / raw_beatmap.beat_divs
                ) * (60 / raw_beatmap.bpm)
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
                            round(
                                raw_beats[target_end_beat_idx - 1] - target_beat,
                                NDIGITS,
                            ),
                        )
                    )
                    break
                else:
                    vibe_beatcnts.append(
                        BeatCnt(
                            target_beat,
                            raw_beats_len - beat_idx,
                            round(raw_beats[-1] - target_beat, NDIGITS),
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


# check if a float value is in the list
# https://stackoverflow.com/questions/55239065/checking-if-a-specific-float-value-is-in-list-array-in-python-numpy
def close_to_any(a, floats, **kwargs):
    return np.any(np.isclose(a, floats, **kwargs))


max_one_vibe_beatcnts = []
target_start_beats = [start_beat for (start_beat, _) in ONE_VIBE_START_BEATS_LOOSE]
for beatcnts in one_vibe_beatcnts:
    max_beatcnt = max(
        [
            beatcnt
            for beatcnt in beatcnts
            if not close_to_any(beatcnt.start_beat, ONE_VIBE_START_BEATS_EXCEPT)
        ]
    )
    start_beat = max_beatcnt.start_beat

    if start_beat in target_start_beats:
        loose_idx = target_start_beats.index(start_beat)
        loose_cnt = ONE_VIBE_START_BEATS_LOOSE[loose_idx][1]

        if loose_cnt > 0:
            end_beat = round(start_beat + max_beatcnt.beat_diff, NDIGITS)

            beat_idx = bisect_left(raw_beats, start_beat)
            target_end_beat_idx = bisect_right(raw_beats, end_beat)

            target_end_beat_idx -= loose_cnt
            if target_end_beat_idx - 1 < beat_idx:
                target_end_beat_idx = beat_idx + 1

            max_beatcnt.beat_diff = round(
                raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
            )
            max_beatcnt.cnt = target_end_beat_idx - beat_idx

    max_one_vibe_beatcnts.append(max_beatcnt)
max_two_vibes_beatcnts = []
target_start_beats = [start_beat for (start_beat, _) in TWO_VIBES_START_BEATS_LOOSE]
for beatcnts in two_vibes_beatcnts:
    max_beatcnt = max(
        [
            beatcnt
            for beatcnt in beatcnts
            if not close_to_any(beatcnt.start_beat, TWO_VIBES_START_BEATS_EXCEPT)
        ]
    )
    start_beat = max_beatcnt.start_beat

    if start_beat in target_start_beats:
        loose_idx = target_start_beats.index(start_beat)
        loose_cnt = TWO_VIBES_START_BEATS_LOOSE[loose_idx][1]

        if loose_cnt > 0:
            end_beat = round(start_beat + max_beatcnt.beat_diff, NDIGITS)

            beat_idx = bisect_left(raw_beats, start_beat)
            target_end_beat_idx = bisect_right(raw_beats, end_beat)

            while (
                loose_cnt > 0
                and raw_beats[target_end_beat_idx - 1] not in vibe_beats
                and target_end_beat_idx - 1 > beat_idx
            ):
                loose_cnt -= 1
                target_end_beat_idx -= 1

            max_beatcnt.beat_diff = round(
                raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
            )
            max_beatcnt.cnt = target_end_beat_idx - beat_idx

    max_two_vibes_beatcnts.append(max_beatcnt)
max_three_vibes_beatcnts = []
target_start_beats = [start_beat for (start_beat, _) in THREE_VIBES_START_BEATS_LOOSE]
for beatcnts in three_vibes_beatcnts:
    max_beatcnt = max(
        [
            beatcnt
            for beatcnt in beatcnts
            if not close_to_any(beatcnt.start_beat, THREE_VIBES_START_BEATS_EXCEPT)
        ]
    )
    start_beat = max_beatcnt.start_beat

    if start_beat in target_start_beats:
        loose_idx = target_start_beats.index(start_beat)
        loose_cnt = THREE_VIBES_START_BEATS_LOOSE[loose_idx][1]

        if loose_cnt > 0:
            end_beat = round(start_beat + max_beatcnt.beat_diff, NDIGITS)

            beat_idx = bisect_left(raw_beats, start_beat)
            target_end_beat_idx = bisect_right(raw_beats, end_beat)

            while (
                loose_cnt > 0 and raw_beats[target_end_beat_idx - 1] not in vibe_beats
            ):
                loose_cnt -= 1
                target_end_beat_idx -= 1

            max_beatcnt.beat_diff = round(
                raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
            )
            max_beatcnt.cnt = target_end_beat_idx - beat_idx

    max_three_vibes_beatcnts.append(max_beatcnt)

print("\nBeatmap Path:")
print(RAW_BEATMAP_PATH)

practice_start_nums = [
    floor(vibe_event.start_beat + ROWS - 1) for vibe_event in raw_beatmap.vibe_events
]
print("\nPractice Start Numbers:")
print(practice_start_nums, end="\n\n")

note_score_avg = (
    perf_score
    + perf_bonus * PERF_BONUS_SCORE_MULT
    + true_perf_bonus * TRUE_PERF_BONUS_SCORE_MULT
)
score_base = (
    min(9, raw_beats_len) * note_score_avg
    + max(0, min(10, raw_beats_len - 9)) * note_score_avg * 2
    + max(0, min(10, raw_beats_len - 19)) * note_score_avg * 3
    + max(0, raw_beats_len - 29) * note_score_avg * 4
)
great_add_score = 2 * 333 - perf_score

great_infos = GREAT_START_BEATS
builds: list[Build] = []
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

    score_add = 0
    for max_beatcnt in max_beatcnts:
        beat_idx = bisect_left(raw_beats, max_beatcnt.start_beat)
        end_idx = beat_idx + max_beatcnt.cnt

        if partition == TARGET_PARTITION:
            for great_info in great_infos:
                if raw_beats[beat_idx] == great_info[0] and great_info[1] > 0:
                    if beat_idx >= 29:
                        score_add += great_add_score * 4
                    elif beat_idx >= 19:
                        score_add += great_add_score * 3
                    elif beat_idx >= 9:
                        score_add += great_add_score * 2
                    else:
                        score_add += great_add_score
                    beat_idx += 1
                    great_info = (great_info[0], great_info[1] - 1)

        while beat_idx < end_idx:
            if beat_idx >= 29:
                score_add += (end_idx - beat_idx) * note_score_avg * 4
                break
            elif beat_idx >= 19:
                score_add += note_score_avg * 3
            elif beat_idx >= 9:
                score_add += note_score_avg * 2
            else:
                score_add += note_score_avg
            beat_idx += 1

    build = Build(
        partition,
        sum(max_beatcnt.cnt for max_beatcnt in max_beatcnts),
        max_beatcnts,
        floor(score_base + score_add),
    )
    builds.append(build)

builds.sort(reverse=True)
for build in builds:
    if build.partition == TARGET_PARTITION:
        builds.remove(build)
        builds.insert(0, build)
for build in builds:
    print(build)
