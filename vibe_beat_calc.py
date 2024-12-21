import math

AFTER_WINDOW_IN_MSEC = 175
PERFECT_BEFORE_WINDOW_IN_MSEC = 35
PERFECT_AFTER_WINDOW_IN_MSEC = 35
GREAT_AFTER_WINDOW_IN_MSEC = 87.5
FRAME_DIFF_IN_MSEC = 16 + 2 / 3

bpm = float(input("bpm: "))
beat_divisions = int(input("beatDivisions: "))
multiplier = int(input("multiplier: "))

beat_len_in_msec = 60000 / bpm

vibe_time_max = 5016.6 + FRAME_DIFF_IN_MSEC * math.ceil(
    (AFTER_WINDOW_IN_MSEC % (beat_len_in_msec / beat_divisions)) / FRAME_DIFF_IN_MSEC
)

perf_vibe_window_max = [
    vibe_time_max + PERFECT_AFTER_WINDOW_IN_MSEC + PERFECT_BEFORE_WINDOW_IN_MSEC
]
perf_vibe_window_max.append(perf_vibe_window_max[0] + 5000)
perf_vibe_window_max.append(perf_vibe_window_max[0] + 10000)

great_vibe_window_max = [
    vibe_time_max + GREAT_AFTER_WINDOW_IN_MSEC + PERFECT_BEFORE_WINDOW_IN_MSEC
]
great_vibe_window_max.append(great_vibe_window_max[0] + 5000)
great_vibe_window_max.append(great_vibe_window_max[0] + 10000)

vibe_rows = list(
    map(
        lambda x: x / beat_len_in_msec * multiplier,
        perf_vibe_window_max,
    )
)
print(vibe_rows[0], end=",")
print(vibe_rows[1], end=",")
print(vibe_rows[2])
