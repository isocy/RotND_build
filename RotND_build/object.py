from global_def import ROWS

from abc import abstractmethod
from enum import Enum, auto


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
    dist_for_move: int
    appear_row = ROWS - 1

    def __init__(self, appear_lane):
        super(Enemy, self).__init__(appear_lane)
        self.health = 0

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_cooltime(self):
        pass


class Slime(Enemy):
    dist_for_move = 1

    def __init__(self, appear_lane):
        super(Slime, self).__init__(appear_lane)

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(GreenSlime, "beat_for_move")


class GreenSlime(Slime):
    def __init__(self, appear_lane):
        super(GreenSlime, self).__init__(appear_lane)
        self.health = getattr(GreenSlime, "max_health")
        self.shield = getattr(GreenSlime, "max_shield")

    def __repr__(self):
        return "GS"


class BlueSlime(Slime):
    def __init__(self, appear_lane):
        super(BlueSlime, self).__init__(appear_lane)
        self.health = getattr(BlueSlime, "max_health")
        self.shield = getattr(BlueSlime, "max_shield")

    def __repr__(self):
        return "BS"


class Skeleton(Enemy):
    dist_for_move = 1

    def __init__(self, appear_lane):
        super(Skeleton, self).__init__(appear_lane)

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(BaseSkeleton, "beat_for_move")


class BaseSkeleton(Skeleton):
    def __init__(self, appear_lane):
        super(BaseSkeleton, self).__init__(appear_lane)
        self.health = getattr(BaseSkeleton, "max_health")
        self.shield = getattr(BaseSkeleton, "max_shield")

    def __repr__(self):
        return "BSk"


class Food(Enemy):
    dist_for_move = 1

    def __init__(self, appear_lane):
        super(Food, self).__init__(appear_lane)

    @abstractmethod
    def __repr__(self):
        pass

    def get_cooltime(self):
        return getattr(Apple, "beat_for_move")


class Apple(Food):
    def __init__(self, appear_lane):
        super(Apple, self).__init__(appear_lane)
        self.health = getattr(Apple, "max_health")
        self.shield = getattr(Apple, "max_shield")

    def __repr__(self):
        return "Ap"


class Trap(Object):
    pass
