from django import template
from django.utils.safestring import mark_safe

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
        return mark_safe(u'<span style="color:#0f0;">' + str(icon) + '</span>')
    elif withhold == 1000:
        return mark_safe(u'<span style="color:#bbb;">' + str(icon) + '</span>')
    else:
        return mark_safe(u'<span style="color:#f00;">' + str(icon) + '</span>')


@register.simple_tag
def submenu(current_section=0):
    menu_html = u'''<h3>Sub sections for Files and Feeds</h3>
    <ul class="level-2">'''
    if int(current_section) == 1:
        menu_html += '<li><span class="youarehere">Feeds</span></li>\n'
    else:
        menu_html += '<li><a href="/ffm/feeds/">Feeds</a></li>\n'
    if int(current_section) == 2:
        menu_html += '<li><span class="youarehere">Items</span></li>\n'
    else:
        menu_html += '<li><a href="/ffm/items/">Items</a></li>\n'
    if int(current_section) == 3:
        menu_html += '<li><span class="youarehere">People</span></li>\n'
    else:
        menu_html += '<li><a href="/ffm/people/">People</a></li>\n'
    menu_html += '</ul>'
    return mark_safe(menu_html)