from Global.const_def import (
    BEAT_OFFSET,
    Facing,
    TrapDir,
    BASE_BLADEMASTER,
    BASE_WYRM,
    BOUNCE,
    PORTAL,
)

from abc import abstractmethod


class Event:
    pass


class ObjectEvent(Event):
    @classmethod
    def load_dict(cls, event, enemy_db):
        """Construct Event with given dictionary"""
        if event["type"] == "SpawnEnemy":
            return EnemyEvent.load_dict(event, enemy_db)
        elif event["type"] == "SpawnTrap":
            return TrapEvent.load_dict(event)


class EnemyEvent(ObjectEvent):
    def __init__(self, lane, appear_beat, enemy_id, facing=Facing.LEFT):
        self.lane = lane
        self.appear_beat = appear_beat
        self.enemy_id = enemy_id
        self.facing = facing

    @classmethod
    def load_dict(cls, event, enemy_db):
        lane = event["track"]
        appear_beat = BEAT_OFFSET + event["startBeatNumber"]
        enemy_id = next(
            int(pair["_eventDataValue"])
            for pair in iter(event["dataPairs"])
            if pair["_eventDataKey"] == "EnemyId"
        )
        name = enemy_db[enemy_id]["name"]

        if name == BASE_BLADEMASTER:
            attack_row = next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "BlademasterAttackRow"
            )
            return BlademasterEvent(lane, appear_beat, enemy_id, attack_row)
        elif name == BASE_WYRM:
            len_left = event["endBeatNumber"] - event["startBeatNumber"] - 1
            return WyrmEvent(lane, appear_beat, enemy_id, len_left)

        facing = next(
            (
                (
                    Facing.RIGHT
                    if pair["_eventDataValue"] == "True"
                    or pair["_eventDataValue"] == "true"
                    else Facing.LEFT
                )
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "ShouldStartFacingRight"
            ),
            Facing.LEFT,
        )
        return EnemyEvent(lane, appear_beat, enemy_id, facing)


class WyrmEvent(EnemyEvent):
    def __init__(self, lane, appear_beat, enemy_id, len_left):
        self.lane = lane
        self.appear_beat = appear_beat
        self.enemy_id = enemy_id
        self.len_left = len_left


class BlademasterEvent(EnemyEvent):
    def __init__(self, lane, appear_beat, enemy_id, attack_row):
        self.lane = lane
        self.appear_beat = appear_beat
        self.enemy_id = enemy_id
        self.attack_row = attack_row


class TrapEvent(ObjectEvent):
    def __init__(
        self,
        lane: int,
        row: int,
        appear_beat: float,
        duration: float,
        trap_type: str,
    ):
        self.lane = lane
        self.row = row
        self.appear_beat = appear_beat
        self.duration = duration
        self.trap_type = trap_type

    @classmethod
    def load_dict(cls, event):
        trap_type = next(
            pair["_eventDataValue"]
            for pair in iter(event["dataPairs"])
            if pair["_eventDataKey"] == "TrapTypeToSpawn"
        )
        if trap_type == BOUNCE:
            return BounceEvent.load_dict(event)
        elif trap_type == PORTAL:
            return PortalEvent.load_dict(event)


class BounceEvent(TrapEvent):
    def __init__(
        self,
        lane: int,
        row: int,
        appear_beat: float,
        duration: float,
        trap_type: str,
        dir: TrapDir,
    ):
        super().__init__(lane, row, appear_beat, duration, trap_type)
        self.dir = dir

    @classmethod
    def load_dict(cls, event):
        dir_num = next(
            int(pair["_eventDataValue"])
            for pair in iter(event["dataPairs"])
            if pair["_eventDataKey"] == "TrapDirection"
        )
        if dir_num == 0:
            dir = TrapDir.UP
        elif dir_num == 1:
            dir = TrapDir.RIGHT
        elif dir_num == 2:
            dir = TrapDir.LEFT
        elif dir_num == 3:
            dir = TrapDir.DOWN
        elif dir_num == 4:
            dir = TrapDir.UPLEFT
        elif dir_num == 5:
            dir = TrapDir.UPRIGHT
        elif dir_num == 6:
            dir = TrapDir.DOWNLEFT
        elif dir_num == 7:
            dir = TrapDir.DOWNRIGHT

        return BounceEvent(
            event["track"],
            next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapDropRow"
            ),
            BEAT_OFFSET + event["startBeatNumber"],
            next(
                float(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapHealthInBeats"
            ),
            BOUNCE,
            dir,
        )


class PortalEvent(TrapEvent):
    def __init__(
        self,
        lane: int,
        row: int,
        appear_beat: float,
        duration: float,
        trap_type: str,
        child_lane: int,
        child_row: int,
    ):
        super().__init__(lane, row, appear_beat, duration, trap_type)
        self.child_lane = child_lane
        self.child_row = child_row

    @classmethod
    def load_dict(cls, event):
        return PortalEvent(
            event["track"],
            next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapDropRow"
            ),
            BEAT_OFFSET + event["startBeatNumber"],
            next(
                float(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapHealthInBeats"
            ),
            PORTAL,
            next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapChildSpawnLane"
            ),
            next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapChildSpawnRow"
            ),
        )


class VibeEvent(Event):
    def __init__(self, start_beat, end_beat):
        self.start_beat = start_beat
        self.end_beat = end_beat

    def __repr__(self):
        return f"{self.start_beat} {self.end_beat}"

    @classmethod
    def load_dict(cls, event):
        return VibeEvent(
            BEAT_OFFSET + event["startBeatNumber"], BEAT_OFFSET + event["endBeatNumber"]
        )
