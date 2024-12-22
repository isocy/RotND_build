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
