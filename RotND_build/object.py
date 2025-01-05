from Global.const_def import ROWS, Facing, TrapDir

from abc import abstractmethod


class Object:
    def __init__(self, appear_lane: int):
        self.appear_lane = appear_lane

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self) -> float:
        pass


class Enemy(Object):
    appear_row = ROWS - 1

    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane)
        self.health = 0
        self.shield = 0
        # with respect to the lane axis
        self.dist_per_move = 0
        self.facing = Facing.LEFT
        self.flying = False
        self.on_fire = False
        self.chained = chained

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self) -> float:
        pass


class Slime(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class GreenSlime(Slime):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(GreenSlime, "max_health")
        self.shield = getattr(GreenSlime, "max_shield")

    def __repr__(self):
        return "GS"

    def get_cooltime(self):
        return (
            getattr(GreenSlime, "beat_for_move")
            if not self.on_fire
            else getattr(GreenSlime, "beat_for_move") / 2
        )


class BlueSlime(Slime):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(BlueSlime, "max_health")
        self.shield = getattr(BlueSlime, "max_shield")

    def __repr__(self):
        return "BS" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(BlueSlime, "beat_for_move")
            if not self.on_fire
            else getattr(BlueSlime, "beat_for_move") / 2
        )


class YellowSlime(Slime):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(YellowSlime, "max_health")
        self.shield = getattr(YellowSlime, "max_shield")

    def __repr__(self):
        return "YS" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(YellowSlime, "beat_for_move")
            if not self.on_fire
            else getattr(YellowSlime, "beat_for_move") / 2
        )


class Bat(Enemy):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1
        self.facing = facing
        self.flying = True

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BlueBat(Bat):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, facing, chained)
        self.health = getattr(BlueBat, "max_health")
        self.shield = getattr(BlueBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "BB" + facing + str(self.health)

    def get_cooltime(self):
        return getattr(BlueBat, "beat_for_move")


class YellowBat(Bat):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, facing, chained)
        self.health = getattr(YellowBat, "max_health")
        self.shield = getattr(YellowBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "YB" + facing + str(self.health)

    def get_cooltime(self):
        return getattr(YellowBat, "beat_for_move")


class RedBat(Bat):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, facing, chained)
        self.health = getattr(RedBat, "max_health")
        self.shield = getattr(RedBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "RB" + facing + str(self.health)

    def get_cooltime(self):
        return getattr(RedBat, "beat_for_move")


class Zombie(Enemy):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1
        self.facing = facing

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self) -> float:
        pass


class GreenZombie(Zombie):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, facing, chained)
        self.health = getattr(GreenZombie, "max_health")
        self.shield = getattr(GreenZombie, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "GZ" + facing

    def get_cooltime(self):
        return (
            getattr(GreenZombie, "beat_for_move")
            if not self.on_fire
            else getattr(GreenZombie, "beat_for_move") / 2
        )


class RedZombie(Zombie):
    def __init__(self, appear_lane, facing, chained):
        super().__init__(appear_lane, facing, chained)
        self.health = getattr(RedZombie, "max_health")
        self.shield = getattr(RedZombie, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "RZ" + facing

    def get_cooltime(self):
        return (
            getattr(RedZombie, "beat_for_move")
            if not self.on_fire
            else getattr(RedZombie, "beat_for_move") / 2
        )


class Skeleton(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(BaseSkeleton, "max_health")
        self.shield = getattr(BaseSkeleton, "max_shield")

    def __repr__(self):
        return "Sk"

    def get_cooltime(self):
        return (
            getattr(BaseSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(BaseSkeleton, "beat_for_move") / 2
        )


class ShieldedBaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(ShieldedBaseSkeleton, "max_health")
        self.shield = getattr(ShieldedBaseSkeleton, "max_shield")

    def __repr__(self):
        return "ShSk"

    def get_cooltime(self):
        return (
            getattr(ShieldedBaseSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(ShieldedBaseSkeleton, "beat_for_move") / 2
        )


class DoubleShieldedBaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(DoubleShieldedBaseSkeleton, "max_health")
        self.shield = getattr(DoubleShieldedBaseSkeleton, "max_shield")

    def __repr__(self):
        return "DShSk"

    def get_cooltime(self):
        return (
            getattr(DoubleShieldedBaseSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(DoubleShieldedBaseSkeleton, "beat_for_move") / 2
        )


class Armadillo(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BlueArmadillo(Armadillo):
    def __init__(self, appear_lane, chained, shield=-1):
        super().__init__(appear_lane, chained)
        self.health = getattr(BlueArmadillo, "max_health")
        self.shield = getattr(BlueArmadillo, "max_shield") if shield == -1 else shield

    def __repr__(self):
        return "BA" + str(self.health + self.shield)

    def get_cooltime(self):
        return (
            getattr(BlueArmadillo, "beat_for_move")
            if not self.on_fire
            else getattr(BlueArmadillo, "beat_for_move") / 2
        )


class RedArmadillo(Armadillo):
    def __init__(self, appear_lane, chained, shield=-1):
        super().__init__(appear_lane, chained)
        self.health = getattr(RedArmadillo, "max_health")
        self.shield = getattr(RedArmadillo, "max_shield") if shield == -1 else shield

    def __repr__(self):
        return "RA" + str(self.health + self.shield)

    def get_cooltime(self):
        return (
            getattr(RedArmadillo, "beat_for_move")
            if not self.on_fire
            else getattr(RedArmadillo, "beat_for_move") / 2
        )


class YellowArmadillo(Armadillo):
    def __init__(self, appear_lane, chained, shield=-1):
        super().__init__(appear_lane, chained)
        self.health = getattr(YellowArmadillo, "max_health")
        self.shield = getattr(YellowArmadillo, "max_shield") if shield == -1 else shield

    def __repr__(self):
        return "YA" + str(self.health + self.shield)

    def get_cooltime(self):
        return (
            getattr(YellowArmadillo, "beat_for_move")
            if not self.on_fire
            else getattr(YellowArmadillo, "beat_for_move") / 2
        )


class HeadlessSkeleton(Enemy):
    beat_for_move = 1

    def __init__(self, appear_lane, chained, dist_per_move):
        super().__init__(appear_lane, chained)
        self.dist_per_move = dist_per_move
        self.health = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        return HeadlessSkeleton.beat_for_move


class YellowSkeleton(Skeleton):
    def __init__(self, appear_lane, chained=False):
        super().__init__(appear_lane, chained)
        self.health = getattr(YellowSkeleton, "max_health")
        self.shield = getattr(YellowSkeleton, "max_shield")

    def __repr__(self):
        return "YSk"

    def get_cooltime(self):
        return (
            getattr(YellowSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(YellowSkeleton, "beat_for_move") / 2
        )


class ShieldedYellowSkeleton(Skeleton):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(ShieldedYellowSkeleton, "max_health")
        self.shield = getattr(ShieldedYellowSkeleton, "max_shield")

    def __repr__(self):
        return "ShYSk"

    def get_cooltime(self):
        return (
            getattr(ShieldedYellowSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(ShieldedYellowSkeleton, "beat_for_move") / 2
        )


class HeadlessYellowSkeleton(HeadlessSkeleton):
    def __init__(self, appear_lane, chained, dist_per_move):
        super().__init__(appear_lane, chained, dist_per_move)

    def __repr__(self):
        return "HlYSk"


class BlackSkeleton(Skeleton):
    def __init__(self, appear_lane, chained=False):
        super().__init__(appear_lane, chained)
        self.health = getattr(BlackSkeleton, "max_health")
        self.shield = getattr(BlackSkeleton, "max_shield")

    def __repr__(self):
        return "BSk" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(BlackSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(BlackSkeleton, "beat_for_move") / 2
        )


class ShieldedBlackSkeleton(Skeleton):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(ShieldedBlackSkeleton, "max_health")
        self.shield = getattr(ShieldedBlackSkeleton, "max_shield")

    def __repr__(self):
        return "ShBSk"

    def get_cooltime(self):
        return (
            getattr(ShieldedBlackSkeleton, "beat_for_move")
            if not self.on_fire
            else getattr(ShieldedBlackSkeleton, "beat_for_move") / 2
        )


class HeadlessBlackSkeleton(HeadlessSkeleton):
    def __init__(self, appear_lane, chained, dist_per_move):
        super().__init__(appear_lane, chained, dist_per_move)

    def __repr__(self):
        return "HlBSk"


class Wyrm(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.flying = True
        self.dist_per_move = 1
        self.len_left = 0

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(WyrmHead, "beat_for_move")


class WyrmHead(Wyrm):
    def __init__(self, appear_lane, chained, len_left):
        super().__init__(appear_lane, chained)
        self.health = getattr(WyrmHead, "max_health")
        self.shield = getattr(WyrmHead, "max_shield")
        self.len_left = len_left

    def __repr__(self):
        return "WH"


class WyrmBody(Wyrm):
    def __init__(self, appear_lane, chained, len_left):
        super().__init__(appear_lane, chained)
        self.len_left = len_left

    def __repr__(self):
        return "WB"


class Harpy(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 2
        self.flying = True

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BaseHarpy(Harpy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(BaseHarpy, "max_health")
        self.shield = getattr(BaseHarpy, "max_shield")

    def __repr__(self):
        return "H"

    def get_cooltime(self):
        return getattr(BaseHarpy, "beat_for_move")


class BlueHarpy(Harpy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(BlueHarpy, "max_health")
        self.shield = getattr(BlueHarpy, "max_shield")

    def __repr__(self):
        return "BH" + str(self.health)

    def get_cooltime(self):
        return getattr(BlueHarpy, "beat_for_move")


class Food(Enemy):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class Apple(Food):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(Apple, "max_health")
        self.shield = getattr(Apple, "max_shield")

    def __repr__(self):
        return "Ap"

    def get_cooltime(self):
        return (
            getattr(Apple, "beat_for_move")
            if not self.on_fire
            else getattr(Apple, "beat_for_move") / 2
        )


class Cheese(Food):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(Cheese, "max_health")
        self.shield = getattr(Cheese, "max_shield")

    def __repr__(self):
        return "Ch" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(Cheese, "beat_for_move")
            if not self.on_fire
            else getattr(Cheese, "beat_for_move") / 2
        )


class Drumstick(Food):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(Drumstick, "max_health")
        self.shield = getattr(Drumstick, "max_shield")

    def __repr__(self):
        return "Dr" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(Drumstick, "beat_for_move")
            if not self.on_fire
            else getattr(Drumstick, "beat_for_move") / 2
        )


class Ham(Food):
    def __init__(self, appear_lane, chained):
        super().__init__(appear_lane, chained)
        self.health = getattr(Ham, "max_health")
        self.shield = getattr(Ham, "max_shield")

    def __repr__(self):
        return "Ha" + str(self.health)

    def get_cooltime(self):
        return (
            getattr(Ham, "beat_for_move")
            if not self.on_fire
            else getattr(Ham, "beat_for_move") / 2
        )


class Blademaster(Enemy):
    def __init__(self, appear_lane, chained, attack_row):
        super().__init__(appear_lane, chained)
        self.dist_per_move = 1
        self.health = getattr(Blademaster, "max_health")
        self.shield = getattr(Blademaster, "max_shield")
        self.attack_row = attack_row
        self.is_ready = False

    def __repr__(self):
        return "Bm" + ("R" if self.is_ready else "")

    def get_cooltime(self):
        return (
            getattr(Blademaster, "beat_for_move")
            if not self.on_fire
            else getattr(Blademaster, "beat_for_move") / 2
        )


class Trap(Object):
    def __init__(self, appear_lane: int, appear_row: int, duration: float):
        self.appear_lane = appear_lane
        self.appear_row = appear_row
        self.duration = duration

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return self.duration


class Bounce(Trap):
    def __init__(
        self, appear_lane: int, appear_row: int, duration: float, dir: TrapDir
    ):
        super().__init__(appear_lane, appear_row, duration)
        self.dir = dir

    def __repr__(self):
        if dir == TrapDir.UP:
            return "BU"
        elif dir == TrapDir.RIGHT:
            return "BR"
        elif dir == TrapDir.LEFT:
            return "BL"
        elif dir == TrapDir.DOWN:
            return "BD"
        elif dir == TrapDir.UPLEFT:
            return "BUL"
        elif dir == TrapDir.UPRIGHT:
            return "BUR"
        elif dir == TrapDir.DOWNLEFT:
            return "BDL"
        elif dir == TrapDir.DOWNRIGHT:
            return "BDR"


class Portal(Trap):
    def __init__(
        self,
        appear_lane: int,
        appear_row: int,
        child_lane: int,
        child_row: int,
        duration: float,
    ):
        super().__init__(appear_lane, appear_row, duration)
        self.child_lane = child_lane
        self.child_row = child_row

    def __repr__(self):
        return "P" + str((self.child_lane - 1) * (ROWS - 1) + self.child_row)

    def get_cooltime(self):
        return self.duration


class Coals(Trap):
    def __init__(self, appear_lane: int, appear_row: int, duration: float):
        super().__init__(appear_lane, appear_row, duration)

    def __repr__(self):
        return "C"
