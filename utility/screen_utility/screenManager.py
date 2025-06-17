def get_screen_function(name):
    if name == "main_menu":
        from screens.main_menu import main_screen
        return main_screen
    elif name == "table":
        from screens.table import table
        return table
    elif name == "testing":
        from screens.testing import testScreen
        return testScreen
    else:
        raise ValueError(f"Unknown screen function: {name}")


def get_all_screen_functions():
    screen_names = ["main_menu", "table", "testScreen"]
    return {
        name: get_screen_function(name) for name in screen_names
    }
