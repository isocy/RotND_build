from global_def import BEAT_OFFSET

from enum import Enum, auto


class Event:
    @classmethod
    def load_dict(cls, event: dict):
        """Construct Event with given dictionary"""
        if event["type"] == "SpawnEnemy":
            return EnemyEvent.load_dict(event)
        elif event["type"] == "StartVibeChain":
            return VibeEvent.load_dict(event)


class EnemyEvent(Event):
    def __init__(self, lane, appear_beat, enemy_id):
        self.lane = lane
        self.appear_beat = appear_beat
        self.enemy_id = enemy_id

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
        )


class VibeEvent(Event):
    def __init__(self, start_beat, end_beat):
        self.start_beat = start_beat
        self.end_beat = end_beat

    @classmethod
    def load_dict(cls, event):
        return VibeEvent(
            event["startBeatNumber"],
            event["endBeatNumber"],
        )
