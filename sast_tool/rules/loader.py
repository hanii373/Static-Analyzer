import importlib
import pkgutil
import inspect

from sast_tool.rules.base import Rule


def load_rules():
    import sast_tool.rules

    rules = []
    package = sast_tool.rules

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Rule) and obj is not Rule:
                rules.append(obj())

    return rules