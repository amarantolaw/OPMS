from django import template

register = template.Library()

@register.filter
def pubstatus(obj, value):
    if obj is None:
        return
    if int(obj) == 1: # POAU
        return _format("[P]", value)
    elif int(obj) == 2: # POAU-beta
        return _format("[b]", value)
    elif int(obj) == 3: # iTunes U
        return _format("[i]", value)
    elif int(obj) == 4: # m.ox
        return _format("[m]", value)
    else:
        return _format("[?]", value)


def _format(icon, withhold):
    if withhold == 0:
        return '<span style="color:#0f0;">' + str(icon) + '</span>'
    elif withhold == 1000:
        return '<span style="color:#bbb;">' + str(icon) + '</span>'
    else:
        return '<span style="color:#f00;">' + str(icon) + '</span>'