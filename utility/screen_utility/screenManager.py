import os
import importlib

SCREENS_DIR = "screens"

def get_screen_function(name):
    try:
        module = importlib.import_module(f"{SCREENS_DIR}.{name}")
        return getattr(module, name)
    except (ModuleNotFoundError, AttributeError):
        raise ValueError(f"❌ Unknown or invalid screen: {name}")

def get_all_screen_functions():
    screen_funcs = {}
    for filename in os.listdir(SCREENS_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            screen_name = filename[:-3]
            try:
                screen_funcs[screen_name] = get_screen_function(screen_name)
            except ValueError:
                continue  # Skip if function isn't found
    return screen_funcs
