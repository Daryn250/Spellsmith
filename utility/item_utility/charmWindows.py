from utility.gui_utility.InfoWindow import InfoWindow
def returnCharmWindow(charm):
    if charm.charmType == 'moon_charm':
        moonNumber = 1 # will be changed in the future to allow for different moon cycles
        return InfoWindow(
            charm, "Moon Charm", 
            "The moon charm allows you to tell the moon phase tonight.",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height()),
            image_path=f"assets/gui/charm_board/moon_charm/gui/gui{moonNumber}.png"
        )
    if charm.charmType == 'mana_charm':
        mana_level = 1
        return InfoWindow(
            charm, "Mana Charm", 
            "The mana charm can sense mana density in this part of the sea!",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height()),
            image_path=f"assets/gui/charm_board/mana_charm/gui/mana_charm{mana_level}.png"
        )
    if charm.charmType == 'rain_charm':
        weather_event = 1
        return InfoWindow(
            charm, "Rain Charm", 
            "The sun charm can tell the weather tomorrow.",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height()),
            image_path=f"assets/gui/charm_board/rain_charm/gui/rain_charm{weather_event}.png"
        )
    elif hasattr(charm, "charmType"):
        return InfoWindow(
            charm, "Unknown Charm",
            "This charm has not been discovered yet. This is probably a bug. Here's a picture of a cat:",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height()),
            image_path="assets/very_important/cat.png"
        )