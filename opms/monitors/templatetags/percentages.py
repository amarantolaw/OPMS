from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(fraction, population):
    if not population:
        return 'n/a %'
    try:
        return "%.2f%%" % ((float(fraction) / float(population)) * 100)
    except TypeError:
        try:
            return "%.2f%%" % ((float(fraction.total_seconds()) / float(population.total_seconds())) * 100) #cope with timedeltas
        except:
            return 'TypeError'
    except ValueError:
        return ''