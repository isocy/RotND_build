import json


class InputRatingsDef:
    def __init__(
        self,
        perf_range: float,
        great_range: float,
        hit_range: float,
        perf_score: int,
        great_score: int,
        perf_bonus: int,
        true_perf_bonus: int,
    ):
        self.perf_range = perf_range
        self.great_range = great_range
        self.hit_range = hit_range
        self.perf_score = perf_score
        self.great_score = great_score
        self.perf_bonus = perf_bonus
        self.true_perf_bonus = true_perf_bonus

    @classmethod
    def load_json(cls, path):
        with open(path) as f:
            input_ratings_def = json.load(f)

        hit_window = input_ratings_def["_afterBeatHitWindow"] * 1000
        ratings = input_ratings_def["_ratings"]

        perf_range = (100 - ratings[-1]["minimumValue"]) * hit_window / 100
        great_range = (100 - ratings[-2]["minimumValue"]) * hit_window / 100

        perf_score = ratings[-1]["score"]
        great_score = ratings[-2]["score"]
        perf_bonus = input_ratings_def["_perfectBonusScore"]
        true_perf_bonus = input_ratings_def["_truePerfectBonusScore"]

        return InputRatingsDef(
            perf_range,
            great_range,
            hit_window,
            perf_score,
            great_score,
            perf_bonus,
            true_perf_bonus,
        )
