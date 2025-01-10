from event import *

import json


class RawBeatmap:
    def __init__(
        self, bpm, beat_divs, beat_timings, obj_events, vibe_events, bpm_events
    ):
        self.bpm = bpm
        self.beat_divs = beat_divs
        self.beat_timings = beat_timings
        self.obj_events: list[ObjectEvent] = obj_events
        self.vibe_events: list[VibeEvent] = vibe_events
        self.bpm_events: list[BpmEvent] = bpm_events

    @classmethod
    def load_json(cls, path, enemy_db):
        with open(path) as f:
            raw_beatmap = json.load(f)

        obj_events = []
        vibe_events = []
        bpm_events = []
        for event in raw_beatmap["events"]:
            if event["type"] == "SpawnEnemy" or event["type"] == "SpawnTrap":
                obj_events.append(event)
            elif event["type"] == "StartVibeChain":
                vibe_events.append(event)
            elif event["type"] == "AdjustBPM":
                bpm_events.append(event)

        return RawBeatmap(
            raw_beatmap["bpm"],
            raw_beatmap["beatDivisions"],
            raw_beatmap["BeatTimings"] if "BeatTimings" in raw_beatmap else [],
            [ObjectEvent.load_dict(event, enemy_db) for event in obj_events],
            [VibeEvent.load_dict(vibe_event) for vibe_event in vibe_events],
            [BpmEvent.load_dict(bpm_event) for bpm_event in bpm_events],
        )
