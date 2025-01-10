from Global.const_def import *

from Simulate.event import *
from Simulate.object import *

from typing import Self


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
                    elif appear_beat <= cur_vibe_event.end_beat:
                        chain_cnt += enemy_def["total_enemies"]
                        chained = True
                        break
                    else:
                        chain_cnts.append(chain_cnt)
                        chain_cnt = 0

                if name == GREEN_SLIME:
                    nodes.append(Node(GreenSlime(lane, chained), appear_beat))
                elif name == BLUE_SLIME:
                    nodes.append(Node(BlueSlime(lane, chained), appear_beat))
                elif name == YELLOW_SLIME:
                    nodes.append(Node(YellowSlime(lane, chained), appear_beat))
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
                elif name == TRIPLE_SHIELD_BASE_SKELETON:
                    nodes.append(
                        Node(DoubleShieldedBaseSkeleton(lane, chained), appear_beat)
                    )
                elif name == BLUE_ARMADILLO:
                    nodes.append(Node(BlueArmadillo(lane, chained), appear_beat))
                elif name == RED_ARMADILLO:
                    nodes.append(Node(RedArmadillo(lane, chained), appear_beat))
                elif name == YELLOW_ARMADILLO:
                    nodes.append(Node(YellowArmadillo(lane, chained), appear_beat))
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
                elif name == BASE_WYRM:
                    assert isinstance(obj_event, WyrmEvent)
                    nodes.append(
                        Node(
                            WyrmHead(lane, chained, obj_event.len_left),
                            appear_beat,
                        )
                    )
                elif name == BASE_HARPY:
                    nodes.append(Node(BaseHarpy(lane, chained), appear_beat))
                elif name == RED_HARPY:
                    nodes.append(Node(RedHarpy(lane, chained), appear_beat))
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
                elif name == BASE_SKULL:
                    nodes.append(
                        Node(BaseSkull(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == BLUE_SKULL:
                    nodes.append(
                        Node(BlueSkull(lane, obj_event.facing, chained), appear_beat)
                    )
                elif name == RED_SKULL:
                    nodes.append(
                        Node(RedSkull(lane, obj_event.facing, chained), appear_beat)
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
            elif isinstance(obj_event, CoalsEvent):
                lane = obj_event.lane
                row = obj_event.row
                appear_beat = obj_event.appear_beat
                duration = obj_event.duration

                nodes.append(Node(Coals(lane, row, duration), appear_beat))

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

    def is_node_blocked(
        self,
        i: int,
        j: int,
        nodes_done: list[Node],
        target_enemy: Node[HeadlessSkeleton],
    ):
        """Determine if the headless skeleton node is blocked at the current timestep.
        (i, j): target position of the node"""
        is_blocked = False
        will_be_blocked = False
        for upper_enemy in self.grids[i][j].enemies:
            if (
                upper_enemy in nodes_done
                and upper_enemy.cooltime < ONBEAT_THRESHOLD
                or upper_enemy not in nodes_done
                and upper_enemy.cooltime - target_enemy.cooltime < ONBEAT_THRESHOLD
            ):
                is_blocked = True
                break
            else:
                will_be_blocked = True

        # Enemies on (i, j) may be above a trap if it was blocked to move
        # Once that case is dealt with, the headless skeleton is possible to step into the trap
        upper_trap = self.grids[i][j].trap
        if (
            not is_blocked
            and not will_be_blocked
            and upper_trap != None
            and (
                isinstance(upper_trap.obj, Bounce) or isinstance(upper_trap.obj, Portal)
            )
        ):
            return (False, False)

        for upper_enemy in self.grids[i][j + 1].enemies:
            if (
                upper_enemy in nodes_done
                and upper_enemy.cooltime < ONBEAT_THRESHOLD
                or upper_enemy not in nodes_done
                and upper_enemy.cooltime - target_enemy.cooltime < ONBEAT_THRESHOLD
            ):
                will_be_blocked = True
                break

        return (is_blocked, will_be_blocked)

    def is_node_blocked_imm(self, i: int):
        """Determine if the newly created headless skeleton node is blocked immediately."""
        is_blocked = False
        for upper_enemy in self.grids[i][1].enemies + self.grids[i][2].enemies:
            is_blocked = True
            break

        return is_blocked

    def is_left_open(
        self, i: int, j: int, target_enemy: Node[Enemy], nodes_done: list[Node]
    ):
        """Determine if the zombie at position (i, j) can go to the left"""
        is_left_open = True
        for enemy in self.grids[i - 1][j - 1].enemies:
            is_zombie = isinstance(enemy.obj, Zombie)
            if not (isinstance(enemy.obj, Harpy) and enemy in nodes_done) and (
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
                    not isinstance(enemy.obj, Harpy)
                    and not isinstance(enemy.obj, Zombie)
                    and enemy.cooltime < ONBEAT_THRESHOLD
                ):
                    is_left_open = False
                    break

        return is_left_open

    def is_right_open(
        self, i: int, j: int, target_enemy: Node[Enemy], nodes_done: list[Node]
    ):
        """Determine if the zombie at position (i, j) can go to the right"""
        is_right_open = True
        for enemy in self.grids[(i + 1) % self.lanes][j - 1].enemies:
            is_zombie = isinstance(enemy.obj, Zombie)
            if not (isinstance(enemy.obj, Harpy) and enemy in nodes_done) and (
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
                    not isinstance(enemy.obj, Harpy)
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
                if dir == TrapDir.UP:
                    init_j += 1
                elif dir == TrapDir.RIGHT:
                    init_i += 1
                elif dir == TrapDir.LEFT:
                    init_i -= 1
                elif dir == TrapDir.DOWN:
                    init_j -= 1
                elif dir == TrapDir.UPLEFT:
                    init_i -= 1
                    init_j += 1
                elif dir == TrapDir.UPRIGHT:
                    init_i += 1
                    init_j += 1
                elif dir == TrapDir.DOWNLEFT:
                    init_i -= 1
                    init_j -= 1
                elif dir == TrapDir.DOWNRIGHT:
                    init_i += 1
                    init_j -= 1

                init_i %= self.lanes
            elif isinstance(trap, Portal):
                init_i = trap.child_lane - 1
                init_j = trap.child_row
            elif isinstance(trap, Coals):
                enemy_node.obj.on_fire = True
        self.grids[init_i][init_j].enemies.append(enemy_node)

        return init_i, init_j
