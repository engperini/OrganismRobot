_runtime = {}

def register_runtime(**kwargs):
    _runtime.update(kwargs)

def get_runtime(name: str):
    return _runtime.get(name)
