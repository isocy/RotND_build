from Shared.RhythmEngine import *
from System import Guid
from Unity.Mathematics import int2

from abc import ABC, abstractmethod
from typing import Self


class RRTrapController(MonoBehaviourFmodSystem):
    def __init__(self):
        self._activeTrapInstances: list[RRTrapController.TrapInstance] = []
        self._trapInstancesByGridPosition: dict[int2, RRTrapController.TrapInstance] = (
            {}
        )
        self._trapInstancesById: dict[Guid, RRTrapController.TrapInstance] = {}

    class ITrapInstanceAccessor(ABC):
        @property
        @abstractmethod
        def TrapId(self):
            pass

        @property
        @abstractmethod
        def GridPosition(self):
            pass

        @property
        @abstractmethod
        def TrapType(self):
            pass

        @property
        @abstractmethod
        def CurrentHealth(self):
            pass

        @property
        @abstractmethod
        def StartingHealth(self):
            pass

        @property
        @abstractmethod
        def TrueBeatNumberOfLastUpdate(self):
            pass

        @property
        @abstractmethod
        def TrapOrientation(self):
            pass

        @property
        @abstractmethod
        def ActiveTrapView(self):
            pass

        @property
        @abstractmethod
        def ChildTrapId(self):
            pass

    class TrapInstance(Self.ITrapInstanceAccessor):
        def __init__(
            self,
            trapId,
            gridPosition,
            trapType,
            startingHealth,
            trueBeatNumberOfLastUpdate,
            activeTrapView,
            trapOrientation,
        ):
            self._trapId = trapId
            self._gridPosition = gridPosition
            self._trapType = trapType
            self._startingHealth = startingHealth
            self._currentHealth = startingHealth
            self._trueBeatNumberOfLastUpdate = trueBeatNumberOfLastUpdate
            self._activeTrapView = activeTrapView
            self._trapOrientation = trapOrientation

        @property
        def ActiveTrapView(self):
            return self._activeTrapView

        @property
        def ChildTrapId(self):
            return self._childTrapId

        @property
        def CurrentHealth(self):
            return self._currentHealth

        @property
        def CurrentHealthPercentage(self):
            return self.CurrentHealth / self.StartingHealth

        @property
        def GridPosition(self):
            return self._gridPosition

        @property
        def StartingHealth(self):
            return self._startingHealth

        @property
        def TrapId(self):
            return self._trapId

        @property
        def TrapType(self):
            return self._trapType

        @property
        def TrueBeatNumberOfLastUpdate(self):
            return self._trueBeatNumberOfLastUpdate

        @property
        def TrapOrientation(self):
            return self._trapOrientation

        def TickTrapHealth(self):
            self._currentHealth -= 1
            self._trueBeatNumberOfLastUpdate += 1.0

    def UpdateSystem(self, fmodTimeCapsule: FmodTimeCapsule):
        for idx in range(len(self._activeTrapInstances) - 1, -1, -1):
            trapInstance = self._activeTrapInstances[idx]
            activeTrapView = trapInstance.ActiveTrapView
            if activeTrapView == None:
                self._activeTrapInstances.pop(idx)
                self._trapInstancesByGridPosition.pop(trapInstance.GridPosition)
                self._trapInstancesById.pop(trapInstance.TrapId)
            else:
                if (
                    fmodTimeCapsule.TrueBeatNumber
                    >= trapInstance.TrueBeatNumberOfLastUpdate + 1.0
                ):
                    trapInstance.TickTrapHealth()
                    if trapInstance.CurrentHealth <= 0:
                        trapInstance._activeTrapView = None
                        self._activeTrapInstances.pop(idx)
                        self._trapInstancesByGridPosition.pop(trapInstance.GridPosition)
                        self._trapInstancesById.pop(trapInstance.TrapId)


class RRTrapView:
    pass
