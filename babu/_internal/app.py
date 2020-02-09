from importlib import import_module
from typings import Set
from babu.db import Model

class App:
    import_path: str

    def __init__(self, import_path):
        self.import_path = import_path

    def load_models(self) -> Set[Model]:
        # TODO: replace this with a metaclass registry mechanism
        model_path = f'{self.import_path}.models'
        models_mod = import_module(model_path)
        models_items = models_mod.__dict__.items()
        return {n: o for n, o in models_items if issubclass(o, Model) and o is not Model}
