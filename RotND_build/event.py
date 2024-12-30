from Global.const_def import BEAT_OFFSET, Facing, TrapDir


class Event:
    @classmethod
    def load_dict(cls, event: dict):
        pass


class ObjectEvent(Event):
    @classmethod
    def load_dict(cls, event):
        """Construct Event with given dictionary"""
        if event["type"] == "SpawnEnemy":
            return EnemyEvent.load_dict(event)
        elif event["type"] == "SpawnTrap":
            return TrapEvent.load_dict(event)


class EnemyEvent(ObjectEvent):
    def __init__(self, lane, appear_beat, enemy_id, facing=Facing.LEFT):
        self.lane = lane
        self.appear_beat = appear_beat
        self.enemy_id = enemy_id
        self.facing = facing

    @classmethod
    def load_dict(cls, event):
        return EnemyEvent(
            event["track"],
            BEAT_OFFSET + event["startBeatNumber"],
            next(
                int(pair["_eventDataValue"])
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "EnemyId"
            ),
            next(
                (
                    Facing.RIGHT if pair["_eventDataValue"] == "true" else Facing.LEFT
                    for pair in iter(event["dataPairs"])
                    if pair["_eventDataKey"] == "ShouldStartFacingRight"
                ),
                Facing.LEFT,
            ),
        )


class TrapEvent(ObjectEvent):
    def __init__(
        self,
        lane: int,
        row: int,
        appear_beat: float,
        duration: float,
        trap_type: str,
        dir: TrapDir,
    ):
        self.lane = lane
        self.row = row
        self.appear_beat = appear_beat
        self.duration = duration
        self.trap_type = trap_type
        self.dir = dir

    @classmethod
    def load_dict(cls, event):
        dir_num = next(
            int(pair["_eventDataValue"])
            for pair in iter(event["dataPairs"])
            if pair["_eventDataKey"] == "TrapDirection"
        )
        if dir_num == 1:
            dir = TrapDir.RIGHT
        elif dir_num == 2:
            dir = TrapDir.LEFT
        # TODO: other directions
        else:
            dir = TrapDir.RIGHT

        return TrapEvent(
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
            next(
                pair["_eventDataValue"]
                for pair in iter(event["dataPairs"])
                if pair["_eventDataKey"] == "TrapTypeToSpawn"
            ),
            dir,
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
