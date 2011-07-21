from django import template

register = template.Library()

@register.filter
def pubstatus(obj, value):
    if obj is None:
        return
    if int(obj) == 1: # POAU
        return self._format("[P]", value)
    elif int(obj) == 2: # POAU-beta
        return self._format("[b]", value)
    elif int(obj) == 3: # iTunes U
        return self._format("[i]", value)
    elif int(obj) == 4: # m.ox
        return self._format("[m]", value)
    else:
        return self._format("[?]", value)


def _format(icon, withhold):
    if withhold == 0:
        return '<span style="color:#0f0;">' + str(icon) + '</span>'
    elif withhold == 1000:
        return '<span style="color:#bbb;">' + str(icon) + '</span>'
    else:
        return '<span style="color:#f00;">' + str(icon) + '</span>'