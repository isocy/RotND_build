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

    def __init__(self, appear_lane, chained=False):
        super(Enemy, self).__init__(appear_lane)
        self.health = 0
        self.shield = 0
        # with respect to the lane axis
        self.dist_per_move = 0
        self.facing = Facing.LEFT
        self.flying = False
        self.chained = chained

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class Slime(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Slime, self).__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class GreenSlime(Slime):
    def __init__(self, appear_lane, chained=False):
        super(GreenSlime, self).__init__(appear_lane, chained)
        self.health = getattr(GreenSlime, "max_health")
        self.shield = getattr(GreenSlime, "max_shield")

    def __repr__(self):
        return "GS"

    def get_cooltime(self):
        return getattr(GreenSlime, "beat_for_move")


class BlueSlime(Slime):
    def __init__(self, appear_lane, chained=False):
        super(BlueSlime, self).__init__(appear_lane, chained)
        self.health = getattr(BlueSlime, "max_health")
        self.shield = getattr(BlueSlime, "max_shield")

    def __repr__(self):
        return "BS"

    def get_cooltime(self):
        return getattr(BlueSlime, "beat_for_move")


# TODO: add classes whose super class is Enemy


class Bat(Enemy):
    def __init__(self, appear_lane, facing, chained=False):
        super(Bat, self).__init__(appear_lane, chained)
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
    def __init__(self, appear_lane, facing, chained=False):
        super(BlueBat, self).__init__(appear_lane, facing, chained)
        self.health = getattr(BlueBat, "max_health")
        self.shield = getattr(BlueBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "BB" + facing

    def get_cooltime(self):
        return getattr(BlueBat, "beat_for_move")


class YellowBat(Bat):
    def __init__(self, appear_lane, facing, chained=False):
        super(YellowBat, self).__init__(appear_lane, facing, chained)
        self.health = getattr(YellowBat, "max_health")
        self.shield = getattr(YellowBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "YB" + facing

    def get_cooltime(self):
        return getattr(YellowBat, "beat_for_move")


class Zombie(Enemy):
    def __init__(self, appear_lane, facing, chained=False):
        super(Zombie, self).__init__(appear_lane, chained)
        self.dist_per_move = 1
        self.facing = facing

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class GreenZombie(Zombie):
    def __init__(self, appear_lane, facing, chained=False):
        super(GreenZombie, self).__init__(appear_lane, facing, chained)
        self.health = getattr(GreenZombie, "max_health")
        self.shield = getattr(GreenZombie, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "GZ" + facing

    def get_cooltime(self):
        return getattr(GreenZombie, "beat_for_move")


class RedZombie(Zombie):
    def __init__(self, appear_lane, facing, chained=False):
        super(RedZombie, self).__init__(appear_lane, facing, chained)
        self.health = getattr(RedZombie, "max_health")
        self.shield = getattr(RedZombie, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "RZ" + facing

    def get_cooltime(self):
        return getattr(RedZombie, "beat_for_move")


class Skeleton(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Skeleton, self).__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained=False):
        super(BaseSkeleton, self).__init__(appear_lane, chained)
        self.health = getattr(BaseSkeleton, "max_health")
        self.shield = getattr(BaseSkeleton, "max_shield")

    def __repr__(self):
        return "Sk"

    def get_cooltime(self):
        return getattr(BaseSkeleton, "beat_for_move")


class ShieldedBaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained=False):
        super(ShieldedBaseSkeleton, self).__init__(appear_lane, chained)
        self.health = getattr(ShieldedBaseSkeleton, "max_health")
        self.shield = getattr(ShieldedBaseSkeleton, "max_shield")

    def __repr__(self):
        return "SSk"

    def get_cooltime(self):
        return getattr(ShieldedBaseSkeleton, "beat_for_move")


class Harpy(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Harpy, self).__init__(appear_lane, chained)
        self.dist_per_move = 2
        self.flying = True

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class BaseHarpy(Harpy):
    def __init__(self, appear_lane, chained=False):
        super(BaseHarpy, self).__init__(appear_lane, chained)
        self.health = getattr(BaseHarpy, "max_health")
        self.shield = getattr(BaseHarpy, "max_shield")

    def __repr__(self):
        return "H"

    def get_cooltime(self):
        return getattr(BaseHarpy, "beat_for_move")


class BlueHarpy(Harpy):
    def __init__(self, appear_lane, chained=False):
        super(BlueHarpy, self).__init__(appear_lane, chained)
        self.health = getattr(BlueHarpy, "max_health")
        self.shield = getattr(BlueHarpy, "max_shield")

    def __repr__(self):
        return "BH"

    def get_cooltime(self):
        return getattr(BlueHarpy, "beat_for_move")


class Food(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Food, self).__init__(appear_lane, chained)
        self.dist_per_move = 1

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(Apple, "beat_for_move")


class Apple(Food):
    def __init__(self, appear_lane, chained=False):
        super(Apple, self).__init__(appear_lane, chained)
        self.health = getattr(Apple, "max_health")
        self.shield = getattr(Apple, "max_shield")

    def __repr__(self):
        return "Ap"


class Cheese(Food):
    def __init__(self, appear_lane, chained=False):
        super(Cheese, self).__init__(appear_lane, chained)
        self.health = getattr(Cheese, "max_health")
        self.shield = getattr(Cheese, "max_shield")

    def __repr__(self):
        return "Ch"


class Trap(Object):
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class Bounce(Trap):
    def __init__(
        self, appear_lane: int, appear_row: int, duration: float, dir: TrapDir
    ):
        super(Bounce, self).__init__()
        self.appear_lane = appear_lane
        self.appear_row = appear_row
        self.duration = duration
        self.dir = dir

    def __repr__(self):
        if dir == TrapDir.LEFT:
            return "BL"
        else:
            return "B"

    def get_cooltime(self):
        return self.duration
