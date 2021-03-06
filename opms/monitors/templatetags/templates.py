from django import template
from datetime import timedelta

register = template.Library()

@register.filter(name='percentage')
def percentage(fraction, population):
    if not population:
        return 'n/a %'
    try:
        return "%.2f%%" % ((float(fraction) / float(population)) * 100)
    except TypeError:
        try:
            if total_seconds(population):
                return "%.2f%%" % ((float(total_seconds(fraction)) / float(total_seconds(population))) * 100) #cope with timedeltas
            else:
                return "0 %"
        except:
            return 'Error: ' + str(fraction) + ' / ' + str(population) + '%'
    except ValueError:
        return ''

@register.filter(name='chop')
def chop(text, length=10):
    """Ensure that a string text is shorter than length, adding ... if appropriate."""
    if len(text) > length:
        return text[:length] + '...'
    else:
        return text

@register.filter(name='mean')
def mean(total, n):
    """Finds the mean from a total of values and the number of values."""
    if n and total:
        try:
            return round((float(total) / float(n)),2)
        except TypeError:
            try:
                return timedelta(seconds=int(float(total_seconds(total)) / float(n)))
            except:
                return "(Error: " + str(total) + ' / ' + str(n) + ')'
    else:
        return 0

def total_seconds(td):
    """The same as td.total_seconds() in Python 2.7."""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6