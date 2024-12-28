from Global.const_def import ROWS, Facing

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

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(GreenSlime, "beat_for_move")


class GreenSlime(Slime):
    def __init__(self, appear_lane, chained=False):
        super(GreenSlime, self).__init__(appear_lane, chained)
        self.health = getattr(GreenSlime, "max_health")
        self.shield = getattr(GreenSlime, "max_shield")

    def __repr__(self):
        return "GS"


class BlueSlime(Slime):
    def __init__(self, appear_lane, chained=False):
        super(BlueSlime, self).__init__(appear_lane, chained)
        self.health = getattr(BlueSlime, "max_health")
        self.shield = getattr(BlueSlime, "max_shield")

    def __repr__(self):
        return "BS"


class Skeleton(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Skeleton, self).__init__(appear_lane, chained)

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(BaseSkeleton, "beat_for_move")


class BaseSkeleton(Skeleton):
    def __init__(self, appear_lane, chained=False):
        super(BaseSkeleton, self).__init__(appear_lane, chained)
        self.health = getattr(BaseSkeleton, "max_health")
        self.shield = getattr(BaseSkeleton, "max_shield")

    def __repr__(self):
        return "BSk"


class Bat(Enemy):
    def __init__(self, appear_lane, facing=Facing.LEFT, chained=False):
        super(Bat, self).__init__(appear_lane, chained)
        self.facing = facing

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(BlueBat, "beat_for_move")


class BlueBat(Bat):
    def __init__(self, appear_lane, facing=Facing.LEFT, chained=False):
        super(BlueBat, self).__init__(appear_lane, facing, chained)
        self.health = getattr(BlueBat, "max_health")
        self.shield = getattr(BlueBat, "max_shield")

    def __repr__(self):
        facing = "L" if self.facing == Facing.LEFT else "R"
        return "BB" + facing


class Food(Enemy):
    def __init__(self, appear_lane, chained=False):
        super(Food, self).__init__(appear_lane, chained)

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


class Trap(Object):
    pass
