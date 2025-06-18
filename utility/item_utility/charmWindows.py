from utility.gui_utility.InfoWindow import InfoWindow
def returnCharmWindow(charm):
    if charm.charmType == 'moon_charm':
        moonNumber = 1 # will be changed in the future to allow for different moon cycles
        return InfoWindow(
            charm, charm.charmType, 
            "The moon charm allows you to tell the moon phase tonight.",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height()),
            image_path=f"assets/gui/charm_board/moon_charm/gui/gui{moonNumber}.png"
        )
    if charm.charmType == 'sun_charm':
        return InfoWindow(
            charm, charm.charmType, 
            "The sun charm can tell the weather tomorrow.",
            (charm.pos[0] + charm.image.get_width(), charm.pos[1] + charm.image.get_height(), )
        )