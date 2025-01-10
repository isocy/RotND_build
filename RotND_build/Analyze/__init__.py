from typing import Self


class BeatCnt:
    def __init__(self, start_beat: float, cnt: int, beat_diff: float):
        self.start_beat = start_beat
        self.cnt = cnt
        self.beat_diff = beat_diff

    def __lt__(self, other: Self):
        if self.cnt < other.cnt:
            return True
        elif self.cnt == other.cnt:
            return self.beat_diff > other.beat_diff
        return False

    def __repr__(self):
        return f"{self.start_beat} {self.cnt} {self.beat_diff}"


class Build:
    def __init__(
        self,
        partition: tuple[int, ...],
        cnt_sum: int,
        beatcnts: list[BeatCnt],
        expected_score: int,
    ):
        self.partition = partition
        self.cnt_sum = cnt_sum
        self.beatcnts = beatcnts
        self.expected_score = expected_score

    def __lt__(self, other: Self):
        if self.cnt_sum == other.cnt_sum:
            self_len = len(self.partition)
            other_len = len(other.partition)
            if self_len == other_len:
                return self.partition > self.partition
            return self_len > other_len
        return self.cnt_sum < other.cnt_sum

    def __repr__(self):
        return "{}, {}\n{}, {}".format(
            str(self.partition),
            str(self.cnt_sum),
            self.beatcnts,
            str(self.expected_score),
        )
