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
    screen_funcs = {}  # maps internal_name -> screen function
    for filename in os.listdir(SCREENS_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            screen_name = filename[:-3]
            try:
                screen_func = get_screen_function(screen_name)
                screen_funcs[screen_name] = screen_func
            except ValueError:
                continue  # skip invalid screen modules
    return screen_funcs

def get_formatted_screen_name(name):
    try:
        module = importlib.import_module(f"{SCREENS_DIR}.{name}")
        return getattr(module, "formattedScreenName", lambda: name)()
    except ModuleNotFoundError:
        return name  # fallback if module doesn't exist
