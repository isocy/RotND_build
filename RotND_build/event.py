from global_def import BEAT_OFFSET, Facing


class Event:
    @classmethod
    def load_dict(cls, event: dict):
        """Construct Event with given dictionary"""
        # TODO
        if event["type"] == "SpawnEnemy":
            return EnemyEvent.load_dict(event)
        elif event["type"] == "StartVibeChain":
            return VibeEvent.load_dict(event)


class EnemyEvent(Event):
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
