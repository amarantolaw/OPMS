from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import *

import array
import pylab
import matplotlib
import matplotlib.dates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


# Default Stats module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:Stats Homepage.")
    return render_to_response('stats/base.html', {})


def summary_index(request):
    "Show the Apple 'Summary' User Action results"
    # return HttpResponse("Summary Report")
    summary_data = Summary.merged.all()
    return render_to_response('stats/reports/summary.html', {'summary_data': summary_data,})


def summary_weekof(request):
    "Show the results for a given week"
    return HttpResponse("Hello World. You're at the  Week of Results page.")


def summary_feeds(request):
    listing = TrackCount.merged.psuedo_feeds()
    return render_to_response('stats/reports/feeds.html',{'listing':listing})


def feed_detail(request, partial_guid):
    # Construct pivot table of data.
    # Orientation 0 is items on x, time on y. Anything else is time on x, items on y.
    try:
        orientation = int(request.GET.get('orientation', 0))
    except ValueError:
        orientation = 0

    i = TrackCount.merged.feed_items(partial_guid)
    w = TrackCount.merged.feed_weeks(partial_guid)
    c = TrackCount.merged.feed_counts(partial_guid, orientation)

    column_totals = {}
    for item in i:
        column_totals[item] = 0

    listing = []
    count = c.pop(0)
    if orientation == 0:
        for week in w:
            row_data = []
            row_total = 0
            for item in i:
                if count != None and count.get("week_ending") == week and count.get("guid") == item:
                    row_data.append(int(count.get("count")))
                    row_total += int(count.get("count"))
                    column_totals[item] += int(count.get("count"))
                    try:
                        count = c.pop(0)
                    except IndexError:
                        count = None
                else:
                    row_data.append(None)
            listing.append({'column_a':week, 'data':row_data, 'total':row_total})

        # Put column headers and totals into listing array - values, then headings
        row_data = []
        for item in i:
            row_data.append(column_totals.get(item))
        listing.insert(0,{'column_a':'Item Total', 'data':row_data, 'total':''})
        row_data = []
        for item in i:
            row_data.append(str(item)[29:50])
        listing.insert(0,{'column_a':'Week Commencing', 'data':row_data, 'total':'Week Total'})
    else:
        for item in i:
            row_data = []
            row_total = 0
            for week in w:
                if count != None and count.get("week_ending") == week and count.get("guid") == item:
                    row_data.append(int(count.get("count")))
                    row_total += int(count.get("count"))
                    column_totals[week] += int(count.get("count"))
                    try:
                        count = c.pop(0)
                    except IndexError:
                        count = None
                else:
                    row_data.append(None)
            listing.append({'column_a':item, 'data':row_data, 'total':row_total})

        # Put column headers and totals into listing array - values, then headings
        row_data = []
        for week in w:
            row_data.append(column_totals.get(week))
        listing.insert(0,{'column_a':'Week Total', 'data':row_data, 'total':''})
        row_data = []
        for week in w:
            row_data.append(str(week))
        listing.insert(0,{'column_a':'Item', 'data':row_data, 'total':'Item Total'})

    summary = {}
    summary['count'] = len(i)
    summary['total'] = 0
    summary['max']   = 0
    for k, v in column_totals.items():
        summary['total'] += v
        if v > summary.get('max'):
            summary['max'] = v
            summary['max_guid'] = k
    try:
        summary['avg'] = summary.get('total') // summary.get('count')
    except ZeroDivisionError:
        summary['avg'] = summary.get('total')

    return render_to_response('stats/reports/feed.html',{
        'listing':listing, 'ref':partial_guid, 'summary':summary
        })


def item_detail(request, guid):
    pass



def graph_apple_summary_totals(request):
    "Generate the Apple summary chart. Allow for a high resolution version to be produced"
    try:
        resolution = int(request.GET.get('dpi', 100))
    except ValueError:
        resolution = 100
    if resolution > 600:
        resolution = 600
    elif resolution < 100:
        resolution = 100

    fig = Figure(figsize=(9,5), dpi=resolution, facecolor='white', edgecolor='white')
    ax1 = fig.add_subplot(1,1,1)
    ax1.set_xmargin(0.4)
    ax2 = ax1.twinx()

    title = u"Apple Weekly Downloads and Cumulative Total"
    ax1.set_title(title)

    s = Summary.merged.all()
    x = matplotlib.numpy.arange(1,len(s))

    tracks = []
    cumulative = []
    dates = []
    xticks = matplotlib.numpy.arange(1,len(s),4) # Only show the date every four weeks
    running_total = 0
    count = 0
    latest_date = ''
    for item in s:
        running_total += int(item.total_track_downloads)
        cumulative.append(running_total)
        tracks.append(int(item.total_track_downloads))
        if count == 0 or (count % 4) == 0:
            dates.append(str(item.week_ending))
        count += 1
        latest_date = str(item.week_ending)

    ind = matplotlib.numpy.arange(len(s)) # the x locations for the groups

    cols = ['blue']*len(ind)
    ax1.bar(ind, tracks, color=cols, linewidth=0, edgecolor='w')
    ax1.set_ylabel("Weekly Downloads", color='blue', size='small')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    # ax1.yaxis.major.formatter.set_powerlimits((-3,3))

    # Add some manual annotations, but check that there is data there already for them!
    if len(s) > 107:
        ax1.annotate('iTU PSM launch', xy=(107,370000), xytext=(70,450000),
                     arrowprops=dict(facecolor='black', linewidth=0, shrink=0.05),)
    if len(s) > 53:
        ax1.annotate('iTunes 9.0 released', xy=(53,80000), xytext=(40,150000),
                     arrowprops=dict(facecolor='black', linewidth=0, shrink=0.05),)
    if len(s) > 11:
        ax1.annotate('Oxford on iTunes U launch', xy=(4,80000), xytext=(10,200000),
                     arrowprops=dict(facecolor='black', linewidth=0, shrink=0.05),)


    ax2.plot(ind, cumulative, 'r-')
    ax2.set_ylabel("Cumulative Downloads", color='red', size='small')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    # ax2.yaxis.major.formatter.set_powerlimits((-3,6))

    ax2.annotate('Cumulative Downloads for\n' + latest_date + ': ' + str(running_total),
                 color = 'black', ha = 'right', size = 'small',
                 xy = (len(s),running_total),
                 xytext = (len(s),int(running_total*0.7)),
                 arrowprops = dict(facecolor = 'red', linewidth=0, shrink = 0.05),)

    ax1.set_xticks(xticks - 0.6)
    ax1.set_xticklabels(dates, rotation=270, size=5, ha='center', va='top')
    ax1.set_xlabel("Week Commencing")

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response