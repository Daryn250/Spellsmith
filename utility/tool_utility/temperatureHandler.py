# defines temperature ranges depending on material

def get_temp_range(material):
    if material == "copper":
        return {"min":250, "max":1085}
    if material == "iron":
        return {"min":450, "max":2800}
    if material == "lead":
        return {"min":500, "max":621}
    if material == "lomium":
        return {"min":800, "max":900}
    if material == "silver":
        return {"min":900, "max":961}
    if material == "thanium":
        return {"min":1200, "max":1250}
    if material == "titanium":
        return {"min":2995, "max":3034}
    