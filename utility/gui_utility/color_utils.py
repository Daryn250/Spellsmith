def get_temperature_color(temp, material_range):
    """
    Returns a color from white to red depending on how far 'temp' is from material's ideal range.
    """
    tmin = material_range["min"]
    tmax = material_range["max"]
    mid = (tmin + tmax) / 2

    if temp < tmin:
        return (255, 255, 255)  # too cold = white
    elif temp < mid:
        # White → Yellow (255,255,255) → (255,255,0)
        factor = (temp - tmin) / (mid - tmin)
        return (
            255,
            255,
            int(255 * (1 - factor))
        )
    elif temp < tmax:
        # Yellow → Red (255,255,0) → (255,0,0)
        factor = (temp - mid) / (tmax - mid)
        return (
            255,
            int(255 * (1 - factor)),
            0
        )
    else:
        return (255, 0, 0)  # too hot = red
