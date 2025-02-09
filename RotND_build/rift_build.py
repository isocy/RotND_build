from Global import *

from Analyze import *
from Simulate import *

from bisect import bisect_right, bisect_left
import itertools
from math import floor, isclose
import numpy as np


map = Map(LANES, ROWS)

enemy_db = EnemyDB.json_to_dict(ENEMY_DB_PATH)
EnemyDB.init_objs(enemy_db)

input_ratings_def = InputRatingsDef.load_json(INPUT_RATINGS_DEF_PATH)
perf_range = input_ratings_def.perf_range - 5
great_range = input_ratings_def.great_range - 5
hit_range = input_ratings_def.hit_range - 5
perf_score = input_ratings_def.perf_score
great_score = input_ratings_def.great_score
perf_bonus = input_ratings_def.perf_bonus
true_perf_bonus = input_ratings_def.true_perf_bonus

raw_beatmap = RawBeatmap.load_json(RAW_BEATMAP_PATH, enemy_db)
base_bpm = raw_beatmap.bpm
beat_divs = raw_beatmap.beat_divs
beat_timings = raw_beatmap.beat_timings
(nodes, chain_cnts) = Node.obj_events_to_nodes(
    raw_beatmap.obj_events, raw_beatmap.vibe_events, enemy_db
)
nodes_len = len(nodes)

# These beats indicate the moment a vibe power is charged
vibe_beats: list[float] = []
chain_idx = 0

beats: list[Beat] = []
wyrm_body_cnt = 0
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
                if isclose(enemy_node.cooltime, min_cooltime):
                    target_nodes.append(enemy_node)
                elif enemy_node.cooltime < min_cooltime:
                    min_cooltime = enemy_node.cooltime
                    target_nodes = [enemy_node]
            trap_node = map.grids[i][j].trap
            if trap_node != None:
                if isclose(trap_node.cooltime, min_cooltime):
                    target_nodes.append(trap_node)
                elif trap_node.cooltime < min_cooltime:
                    min_cooltime = trap_node.cooltime
                    target_nodes = [trap_node]

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
    nodes_done: list[Node] = []

    # introduce new nodes
    #
    # Let a trap spawn at t=0 and at some grid.
    # If an enemy reaches that grid at the same time t=0,
    # Then enemy should be affected by the trap
    # That's why this code block is ahead of below
    if node_idx < nodes_len:
        next_node.cooltime = round(next_node.cooltime - min_cooltime, NDIGITS)

        while isclose(next_node.cooltime, 0):
            obj: Object = next_node.obj
            next_node.cooltime = obj.get_cooltime()
            if isinstance(obj, Enemy):
                if obj.flying:
                    map.grids[obj.appear_lane - 1][Enemy.appear_row].enemies.append(
                        next_node
                    )

                    # insert new wyrm body into 'nodes'
                    if (
                        isinstance(obj, WyrmHead)
                        or isinstance(obj, Wyrm)
                        and obj.len_left > ONBEAT_THRESHOLD
                    ):
                        new_obj = WyrmBody(
                            obj.appear_lane, obj.chained, obj.len_left - 1
                        )
                        new_node = Node(
                            new_obj,
                            round(
                                cur_beat + min_cooltime + new_obj.get_cooltime(),
                                NDIGITS,
                            ),
                        )

                        insert_idx = node_idx + 1
                        while (
                            insert_idx < nodes_len
                            and new_node.cooltime > nodes[insert_idx].cooltime
                        ):
                            insert_idx += 1
                        nodes.insert(insert_idx, new_node)
                        nodes_len += 1
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
            # removal of 'grid_enemy' may cause impairment on the iteration of 'grid_enemies'
            # so remove those enemies at the end
            enemies_removed = []
            for grid_enemy in grid_enemies:
                if grid_enemy in nodes_done:
                    continue

                # Update 'target_nodes'
                # For enemies previously shielded (j is 0), do not move
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
                            i, j - dist, nodes_done, grid_enemy
                        )
                        if is_blocked and j == 1:
                            grid_enemy.cooltime = 0
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
                else:
                    grid_enemy.cooltime = round(
                        grid_enemy.cooltime - min_cooltime, NDIGITS
                    )
                nodes_done.append(grid_enemy)

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
                                map.is_left_open(i, j, grid_enemy, nodes_done)
                                if i != 0
                                else False
                            )

                            if is_left_open:
                                (new_i, new_j) = map.step_trap(
                                    i - 1, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.RIGHT
                                is_right_open = (
                                    map.is_right_open(i, j, grid_enemy, nodes_done)
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
                                map.is_right_open(i, j, grid_enemy, nodes_done)
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
                                    map.is_left_open(i, j, grid_enemy, nodes_done)
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
                                            not isinstance(enemy.obj, Harpy)
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
                                            not isinstance(enemy.obj, Harpy)
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
                            is_left_open = map.is_left_open(
                                i, j, grid_enemy, nodes_done
                            )

                            if is_left_open:
                                (new_i, new_j) = map.step_trap(
                                    i - 1, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.RIGHT
                                is_right_open = map.is_right_open(
                                    i, j, grid_enemy, nodes_done
                                )

                                if is_right_open:
                                    (new_i, new_j) = map.step_trap(
                                        (i + 1) % map.lanes, j - dist, grid_enemy
                                    )
                                else:
                                    (new_i, new_j) = map.step_trap(
                                        i, j - dist, grid_enemy
                                    )
                        else:
                            is_right_open = map.is_right_open(
                                i, j, grid_enemy, nodes_done
                            )

                            if is_right_open:
                                (new_i, new_j) = map.step_trap(
                                    (i + 1) % map.lanes, j - dist, grid_enemy
                                )
                            else:
                                obj.facing = Facing.LEFT
                                is_left_open = map.is_left_open(
                                    i, j, grid_enemy, nodes_done
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
                                is_left_open = True
                                for enemy in map.grids[new_i - 1][new_j].enemies:
                                    if (
                                        not isinstance(enemy.obj, Harpy)
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
                                        not isinstance(enemy.obj, Harpy)
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
    # if 221 < cur_beat < 235:
    #     print(cur_beat)
    #     print(map)

    # hit notes
    for i in range(map.lanes):
        # It becomes a problem when a wyrm body and other enemies collide at j = 0
        wyrm_node = None
        is_other_enemy = False
        is_wyrm_head = False
        for enemy_node in map.grids[i][0].enemies:
            if isinstance(enemy_node.obj, WyrmBody):
                wyrm_node = enemy_node
            else:
                is_other_enemy = True
                if isinstance(enemy_node.obj, WyrmHead):
                    is_wyrm_head = True
        if is_other_enemy:
            # collision possibly at wyrm tail
            if wyrm_node != None:
                assert not wyrm_node.obj.chained
                map.grids[i][0].enemies.remove(wyrm_node)

            if not is_wyrm_head:
                target_j = 1
                while target_j < map.rows:
                    wyrm_node: Node[WyrmBody] = next(
                        (
                            enemy_node
                            for enemy_node in iter(map.grids[i][target_j].enemies)
                            if isinstance(enemy_node.obj, WyrmBody)
                        ),
                        None,
                    )
                    if wyrm_node != None:
                        assert not wyrm_node.obj.chained
                        map.grids[i][target_j].enemies.remove(wyrm_node)
                        if wyrm_node.obj.len_left < 1:
                            break
                        target_j += 1
                    else:
                        break

                if target_j == map.rows:
                    wyrm_node = next(
                        node
                        for node in nodes[node_idx:]
                        if isinstance(node.obj, WyrmBody)
                    )
                    nodes.remove(wyrm_node)
                    nodes_len -= 1

        # Now a wyrm cannot be with other enemies
        for enemy_node in map.grids[i][0].enemies:
            if enemy_node.cooltime != 0:
                continue

            map.grids[i][0].enemies.remove(enemy_node)

            enemy = enemy_node.obj
            enemy.on_fire = False

            if isinstance(enemy, WyrmBody):
                # There is no enemy in the grid other than a wyrm body
                wyrm_body_cnt += 1
                if enemy.len_left < 1 and enemy.chained:
                    chain_cnts[chain_idx] -= 1

                    if chain_cnts[chain_idx] == 0:
                        vibe_beats.append(cur_beat)
                        chain_idx += 1
                # is not counted as a beat
                break

            beats.append(Beat(i, cur_beat))

            if enemy.shield > 0:
                enemy.shield -= 1
                if isinstance(enemy, ShieldedBaseSkeleton):
                    new_node: Node[Enemy] = Node(
                        BaseSkeleton(i + 1, enemy.chained), enemy.get_cooltime() / 2
                    )
                    map.grids[i][0].enemies.append(new_node)
                elif isinstance(enemy, DoubleShieldedBaseSkeleton):
                    new_node = Node(
                        ShieldedBaseSkeleton(i + 1, enemy.chained),
                        enemy.get_cooltime() / 2,
                    )
                    map.grids[i][0].enemies.append(new_node)
                elif isinstance(enemy, BlueArmadillo) or isinstance(
                    enemy, YellowArmadillo
                ):
                    enemy_node.cooltime = enemy.get_cooltime() / 3
                    map.grids[i][0].enemies.append(enemy_node)
                elif isinstance(enemy, RedArmadillo):
                    enemy_node.cooltime = enemy.get_cooltime() * 2 / 3
                    map.grids[i][0].enemies.append(enemy_node)
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
                continue
            elif enemy.health > 1:
                enemy.health -= 1
                enemy_node.cooltime = enemy.get_cooltime()
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
                elif isinstance(enemy, WyrmHead):
                    if enemy.chained:
                        chain_cnts[chain_idx] -= 1

                        if chain_cnts[chain_idx] == 0:
                            vibe_beats.append(cur_beat)
                            chain_idx += 1
                elif isinstance(enemy, RedSkull):
                    if enemy.facing == Facing.LEFT:
                        map.step_trap(i - 1, 1, enemy_node)
                    else:
                        map.step_trap((i + 1) % 3, 1, enemy_node)
                else:
                    map.step_trap(i, 1, enemy_node)
                continue
            elif isinstance(enemy, Skull):
                new_obj = BaseSkeleton(i + 1, enemy.chained)
                new_node = Node(new_obj, new_obj.get_cooltime())
                map.grids[i][1].enemies.append(new_node)

                if enemy.facing == Facing.LEFT:
                    new_obj = BaseSkeleton(i + 2, enemy.chained)
                    new_node = Node(new_obj, new_obj.get_cooltime())
                    map.grids[(i + 1) % 3][1].enemies.append(new_node)
                else:
                    new_obj = BaseSkeleton(i, enemy.chained)
                    new_node = Node(new_obj, new_obj.get_cooltime())
                    map.grids[i - 1][1].enemies.append(new_node)

            if enemy.chained:
                chain_cnts[chain_idx] -= 1

                if chain_cnts[chain_idx] == 0:
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


def get_max_end_beat(target_beat, stack, time_discount=0):
    """Given the vibe stacks, return the maximum beat that could be reached from 'target_beat'"""
    if beat_timings == []:
        max_time_until_vibe_ends = (
            2 * perf_range + FRAME_IN_MSEC * (300 * stack + 2) - time_discount
        )
        max_time_until_vibe_ends = max_time_until_vibe_ends + 1000 * (1 / beat_divs) * (
            60 / base_bpm
        )
        max_beat_until_vibe_ends = max_time_until_vibe_ends * base_bpm / 60000
        target_end_beat = target_beat + max_beat_until_vibe_ends
    else:
        # round due to int()
        target_beat_num = round(target_beat - BEAT_OFFSET, NDIGITS)
        start_beat_num = int(target_beat_num)
        start_beat_progress = target_beat_num % 1
        beat_len = (
            beat_timings[start_beat_num + 1] - beat_timings[start_beat_num]
        ) * 1000
        target_time = (
            beat_timings[start_beat_num] * 1000 + start_beat_progress * beat_len
        )

        target_end_time = (
            target_time + perf_range + FRAME_IN_MSEC * (300 * stack + 1) - time_discount
        )
        end_beat_num = bisect_right(beat_timings, target_end_time / 1000) - 1
        beat_len = (
            (beat_timings[end_beat_num + 1] - beat_timings[end_beat_num]) * 1000
            if end_beat_num + 1 < len(beat_timings)
            else (beat_timings[end_beat_num] - beat_timings[end_beat_num - 1]) * 1000
        )
        end_time_progress = target_end_time - beat_timings[end_beat_num] * 1000
        end_beat_progress = end_time_progress / beat_len
        target_end_beat = end_beat_num + end_beat_progress
        vibe_limit = (end_time_progress + hit_range) / beat_len
        beat_div_cnt = 0
        while vibe_limit + beat_div_cnt / beat_divs < target_end_beat:
            beat_div_cnt += 1
        vibe_limit += beat_div_cnt / beat_divs
        while target_end_beat < vibe_limit:
            target_end_beat += FRAME_IN_MSEC / beat_len
        target_end_beat += perf_range / beat_len + BEAT_OFFSET

    return target_end_beat


def get_min_end_beat(target_beat, stack):
    """Given the vibe stacks, return the minimum beat that could be reached from 'target_beat'"""
    if beat_timings == []:
        min_time_until_vibe_ends = -2 * perf_range + FRAME_IN_MSEC * (300 * stack + 1)
        min_beat_until_vibe_ends = min_time_until_vibe_ends * base_bpm / 60000
        target_end_beat = target_beat + min_beat_until_vibe_ends
    else:
        target_beat_num = round(target_beat - BEAT_OFFSET, NDIGITS)
        start_beat_num = int(target_beat_num)
        start_beat_progress = target_beat_num % 1
        beat_len = (
            beat_timings[start_beat_num + 1] - beat_timings[start_beat_num]
        ) * 1000
        target_time = (
            beat_timings[start_beat_num] * 1000 + start_beat_progress * beat_len
        )

        target_end_time = target_time - perf_range + FRAME_IN_MSEC * 300 * stack
        end_beat_num = bisect_right(beat_timings, target_end_time / 1000) - 1
        beat_len = (
            (beat_timings[end_beat_num + 1] - beat_timings[end_beat_num]) * 1000
            if end_beat_num + 1 < len(beat_timings)
            else (beat_timings[end_beat_num] - beat_timings[end_beat_num - 1]) * 1000
        )
        end_time_progress = target_end_time - beat_timings[end_beat_num] * 1000
        end_beat_progress = end_time_progress / beat_len
        target_end_beat = end_beat_num + end_beat_progress
        vibe_limit = (end_time_progress + hit_range) / beat_len
        beat_div_cnt = 0
        while vibe_limit + beat_div_cnt / beat_divs < target_end_beat:
            beat_div_cnt += 1
        vibe_limit += beat_div_cnt / beat_divs
        while target_end_beat < vibe_limit:
            target_end_beat += FRAME_IN_MSEC / beat_len
        target_end_beat += -perf_range / beat_len + BEAT_OFFSET

    return target_end_beat


raw_beats = [beat.beat for beat in beats]
raw_beats_len = len(raw_beats)
vibe_beats_len = len(vibe_beats)

# Let the user be cautious about four or more vibe activation in once
vibe_idx = 0
# Assume 3 consecutive vibe power activation is possible
vibe_in_row = 3
while vibe_idx < vibe_beats_len - 3:
    # one vibe is used for ignitition
    target_end_beat = get_max_end_beat(vibe_beats[vibe_idx + 2], vibe_in_row - 1)

    if (
        not vibe_idx + vibe_in_row < vibe_beats_len
        or target_end_beat < vibe_beats[vibe_idx + vibe_in_row]
    ):
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
        target_end_beat = get_max_end_beat(target_beat, 1)

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
                    target_end_beat = get_min_end_beat(vibe_beats[vibe_idx], 1)

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
        target_end_beat = get_max_end_beat(target_beat, 2)

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
                    target_end_beat = get_min_end_beat(vibe_beats[vibe_idx + 1], 1)

                    if target_end_beat >= vibe_beats[vibe_idx + 2]:
                        break

                    # case 2
                    target_end_beat = get_min_end_beat(vibe_beats[vibe_idx], 2)

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
        target_end_beat = get_max_end_beat(target_beat, 1)

        # if branch: no vibe power loss
        if target_end_beat < vibe_beats[vibe_idx + 2]:
            target_end_beat = get_max_end_beat(target_beat, 3)

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
                        target_end_beat = get_min_end_beat(vibe_beats[vibe_idx + 2], 1)

                        if target_end_beat >= vibe_beats[vibe_idx + 3]:
                            break

                        # case 2
                        target_end_beat = get_min_end_beat(vibe_beats[vibe_idx + 1], 2)

                        if target_end_beat >= vibe_beats[vibe_idx + 3]:
                            break

                        # case 3
                        target_end_beat = get_min_end_beat(vibe_beats[vibe_idx], 3)

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
        # else branch: possible vibe power loss
        else:
            if beat_timings == []:
                loss_beat = target_end_beat - vibe_beats[vibe_idx + 2]
                loss_time = 1000 * loss_beat * (60 / base_bpm)
            else:
                # loss_time calculation should be based on 'beat_timings' if it exists
                target_beat_num = round(target_end_beat - BEAT_OFFSET, NDIGITS)
                beat_num = int(target_beat_num)
                beat_progress = target_beat_num % 1
                beat_len = (beat_timings[beat_num + 1] - beat_timings[beat_num]) * 1000
                target_time = beat_timings[beat_num] * 1000 + beat_progress * beat_len
                vibe_beat_num = round(vibe_beats[vibe_idx + 2], NDIGITS)
                beat_num = int(vibe_beat_num)
                beat_progress = vibe_beat_num % 1
                beat_len = (beat_timings[beat_num + 1] - beat_timings[beat_num]) * 1000
                vibe_time = beat_timings[beat_num] * 1000 + beat_progress * beat_len
                loss_time = target_time - vibe_time

            # no vibe power loss but extendable only with one vibe -> 'time_discount' > 0
            time_discount = 0
            if loss_time < 2 * perf_range:
                time_discount = 2 * perf_range - loss_time

            if vibe_idx < vibe_beats_len - 3:
                next_beat_idxs.append(beat_idx)

                # case 1
                target_end_beat = get_min_end_beat(vibe_beats[vibe_idx + 2], 2)

                if target_end_beat >= vibe_beats[vibe_idx + 3]:
                    break

                # case 3
                target_end_beat = get_min_end_beat(vibe_beats[vibe_idx], 3)

                if target_end_beat >= vibe_beats[vibe_idx + 3]:
                    break

                target_end_beat = get_max_end_beat(
                    vibe_beats[vibe_idx + 2], 2, time_discount
                )

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
                target_end_beat = get_max_end_beat(
                    vibe_beats[vibe_idx + 2], 2, time_discount
                )

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
    cand_beatcnts = [
        beatcnt
        for beatcnt in beatcnts
        if not close_to_any(beatcnt.start_beat, ONE_VIBE_START_BEATS_EXCEPT)
    ]

    for beatcnt in cand_beatcnts:
        start_beat = beatcnt.start_beat
        if start_beat in target_start_beats:
            loose_idx = target_start_beats.index(start_beat)
            loose_cnt = ONE_VIBE_START_BEATS_LOOSE[loose_idx][1]

            if loose_cnt > 0:
                end_beat = round(start_beat + beatcnt.beat_diff, NDIGITS)

                beat_idx = bisect_left(raw_beats, start_beat)
                target_end_beat_idx = bisect_right(raw_beats, end_beat)

                target_end_beat_idx -= loose_cnt
                if target_end_beat_idx - 1 < beat_idx:
                    target_end_beat_idx = beat_idx + 1

                beatcnt.beat_diff = round(
                    raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
                )
                beatcnt.cnt = target_end_beat_idx - beat_idx

    max_beatcnt = max(cand_beatcnts)
    max_one_vibe_beatcnts.append(max_beatcnt)
max_two_vibes_beatcnts = []
target_start_beats = [start_beat for (start_beat, _) in TWO_VIBES_START_BEATS_LOOSE]
for beatcnts in two_vibes_beatcnts:
    cand_beatcnts = [
        beatcnt
        for beatcnt in beatcnts
        if not close_to_any(beatcnt.start_beat, TWO_VIBES_START_BEATS_EXCEPT)
    ]

    for beatcnt in cand_beatcnts:
        start_beat = beatcnt.start_beat
        if start_beat in target_start_beats:
            loose_idx = target_start_beats.index(start_beat)
            loose_cnt = TWO_VIBES_START_BEATS_LOOSE[loose_idx][1]

            if loose_cnt > 0:
                end_beat = round(start_beat + beatcnt.beat_diff, NDIGITS)

                beat_idx = bisect_left(raw_beats, start_beat)
                target_end_beat_idx = bisect_right(raw_beats, end_beat)

                while (
                    loose_cnt > 0
                    and raw_beats[target_end_beat_idx - 1] not in vibe_beats
                    and target_end_beat_idx - 1 > beat_idx
                ):
                    loose_cnt -= 1
                    target_end_beat_idx -= 1

                beatcnt.beat_diff = round(
                    raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
                )
                beatcnt.cnt = target_end_beat_idx - beat_idx

    max_beatcnt = max(cand_beatcnts)
    max_two_vibes_beatcnts.append(max_beatcnt)
max_three_vibes_beatcnts = []
target_start_beats = [start_beat for (start_beat, _) in THREE_VIBES_START_BEATS_LOOSE]
for beatcnts in three_vibes_beatcnts:
    cand_beatcnts = [
        beatcnt
        for beatcnt in beatcnts
        if not close_to_any(beatcnt.start_beat, THREE_VIBES_START_BEATS_EXCEPT)
    ]

    for beatcnt in cand_beatcnts:
        start_beat = beatcnt.start_beat
        if start_beat in target_start_beats:
            loose_idx = target_start_beats.index(start_beat)
            loose_cnt = THREE_VIBES_START_BEATS_LOOSE[loose_idx][1]

            if loose_cnt > 0:
                end_beat = round(start_beat + beatcnt.beat_diff, NDIGITS)

                beat_idx = bisect_left(raw_beats, start_beat)
                target_end_beat_idx = bisect_right(raw_beats, end_beat)

                while (
                    loose_cnt > 0
                    and raw_beats[target_end_beat_idx - 1] not in vibe_beats
                ):
                    loose_cnt -= 1
                    target_end_beat_idx -= 1

                beatcnt.beat_diff = round(
                    raw_beats[target_end_beat_idx - 1] - start_beat, NDIGITS
                )
                beatcnt.cnt = target_end_beat_idx - beat_idx

    max_beatcnt = max(cand_beatcnts)
    max_three_vibes_beatcnts.append(max_beatcnt)

print("\nBeatmap Path:")
print(RAW_BEATMAP_PATH)

practice_start_nums = [
    floor(vibe_event.start_beat + ROWS - 1) for vibe_event in raw_beatmap.vibe_events
]
print("\nPractice Start Numbers:")
print(practice_start_nums, end="\n\n")

score_base = (
    (
        min(10, raw_beats_len) * perf_score
        + max(0, min(10, raw_beats_len - 10)) * perf_score * 2
        + max(0, min(10, raw_beats_len - 20)) * perf_score * 3
        + max(0, raw_beats_len - 30) * perf_score * 4
    )
    + raw_beats_len * perf_bonus * PERF_BONUS_SCORE_MULT
    + raw_beats_len * true_perf_bonus * TRUE_PERF_BONUS_SCORE_MULT
    + wyrm_body_cnt * WYRM_BODY_SCORE
)
great_add_score = 2 * great_score - perf_score

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
        elif num == 3:
            max_beatcnts.append(max_three_vibes_beatcnts[vibe_idx])
            vibe_idx += 3
        else:
            break

    score_add = 0
    for max_beatcnt in max_beatcnts:
        beat_idx = bisect_left(raw_beats, max_beatcnt.start_beat)
        end_idx = beat_idx + max_beatcnt.cnt

        # There may be different 'max_beatcnt's with the same start_beat in different partition
        # parition should be specified to eliminate interference
        if partition == TARGET_PARTITION:
            start_beat = raw_beats[beat_idx]
            for great_info in great_infos:
                (great_start_beat, great_cnt) = great_info
                if start_beat == great_start_beat:
                    while great_cnt > 0:
                        if beat_idx >= 30:
                            score_add += great_add_score * 4
                        elif beat_idx >= 20:
                            score_add += great_add_score * 3
                        elif beat_idx >= 10:
                            score_add += great_add_score * 2
                        else:
                            score_add += great_add_score
                        beat_idx += 1
                        great_cnt -= 1
                    break

        while beat_idx < end_idx:
            if beat_idx >= 30:
                score_add += (end_idx - beat_idx) * perf_score * 4
                break
            elif beat_idx >= 20:
                score_add += perf_score * 3
            elif beat_idx >= 10:
                score_add += perf_score * 2
            else:
                score_add += perf_score
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
    print(build)
