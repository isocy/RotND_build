import json


class Action:
    def __init__(self):
        self._callbacks = []

    def __iadd__(self, callback):
        if callable(callback):
            self._callbacks.append(callback)
        else:
            raise ValueError("Only callable objects can be added")
        return self

    def __isub__(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
        return self

    def __call__(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class Guid:
    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h
        self.i = i
        self.j = j
        self.k = k

    def __eq__(self, other):
        return (
            self.a == other.a
            and self.b == other.b
            and self.c == other.c
            and self.d == other.d
            and self.e == other.e
            and self.f == other.f
            and self.g == other.g
            and self.h == other.h
            and self.i == other.i
            and self.j == other.j
            and self.k == other.k
        )

    @classmethod
    def LoadFromJson(cls, path):
        with open(path) as f:
            guid: dict = json.load(f)

        Data1 = guid["Data1"]
        Data2 = guid["Data2"]
        Data3 = guid["Data3"]
        Data4 = guid["Data4"]

        return Guid(
            Data1,
            Data2 >> 16 & 0xFFFF,
            Data2 & 0xFFFF,
            Data3 >> 24 & 0xFF,
            Data3 >> 16 & 0xFF,
            Data3 >> 8 & 0xFF,
            Data3 & 0xFF,
            Data4 >> 24 & 0xFF,
            Data4 >> 16 & 0xFF,
            Data4 >> 8 & 0xFF,
            Data4 & 0xFF,
        )
