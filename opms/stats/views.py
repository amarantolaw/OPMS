from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.db.models import Sum, Max
from stats.models import *
import ffm.models as ffm_models
import pylab
import numpy as np
import matplotlib
import matplotlib.dates
import matplotlib.ticker as ticker
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from chartit import PivotDataPool, PivotChart, DataPool, Chart


# Default Stats module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:Stats Homepage.")
    return render_to_response('stats/base.html', {}, context_instance=RequestContext(request))


#####
# APPLE/iTU Subviews
#####
def summary_index(request):
    "Show the Apple 'Summary' User Action results"
    # return HttpResponse("Summary Report")
    summary_data = Summary.merged.all()
    return render_to_response('stats/apple/summary.html', {'summary_data': summary_data,}, context_instance=RequestContext(request))


#####
# FEEDS Subviews
#####
def summary_feeds(request):
    listing = TrackCount.merged.psuedo_feeds()
    return render_to_response('stats/apple/feeds.html',{'listing':listing}, context_instance=RequestContext(request))


def feed_detail(request, partial_guid):
    # Construct pivot table of data.
    # Orientation 0 is items on x, time on y. Anything else is time on x, items on y.
    try:
        orientation = int(request.GET.get('orientation', 0))
    except ValueError:
        orientation = 0

    # Create a Datapool object for Chartit
    cdata = PivotDataPool(
        series=[{
            'options':{
                'source': TrackCount.objects.filter(guid__guid__contains = partial_guid),
                'categories': [
                    'summary__week_ending'
                ],
                'legend_by': 'guid__guid'
            },
            'terms':{
                'feed_total': Sum('count')
            }
        }]
    )
    # Create a Chart object for Chartit
    pivcht = PivotChart(
        datasource = cdata,
        series_options = [{
            'options':{
                'type':'column',
                'stacking':True,
                'xAxis': 0,
                'yAxis': 0
            },
            'terms':['feed_total']
        }],
        chart_options = {
            'title':{'text':'Number of downloads per week for whole feed'},
            'xAxis':{
                'title': {
                    'text':'Week Beginning'
                },
                'labels':{
                    'rotation': '90',
                    'textAlign': 'right',
                    'step': '3'
                }
            },
            'yAxis':{
                'title': {
                    'text':'Download Count',
                    'rotation': '90'
                },
                'stackLabels': {
                    'enabled': True,
                    'rotation': '90',
                    'textAlign': 'right'
                }
            }
        }
    )


    i = TrackCount.merged.feed_items(partial_guid)
    w = TrackCount.merged.feed_weeks(partial_guid)
    c = TrackCount.merged.feed_counts(partial_guid, orientation)

    listing = []
    column_totals = {}
    count = c.pop(0)
    if orientation == 0:
        for item in i:
            column_totals[item] = 0

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
        for week in w:
            column_totals[week] = 0

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
    summary['max_value']   = 0
    if orientation == 0:
        summary['max_term'] = "item"
    else:
        summary['max_term'] = "week"
    for k, v in column_totals.items():
        summary['total'] += v
        if v > summary.get('max_value'):
            summary['max_value'] = int(v)
            summary['max_name'] = k
    try:
        summary['avg'] = summary.get('total') // summary.get('count')
    except ZeroDivisionError:
        summary['avg'] = summary.get('total')

    return render_to_response('stats/apple/feed.html',{
            'listing':listing,
            'ref':partial_guid,
            'summary':summary,
            'cht':pivcht,
            'chart_height':int(40+summary.get('count'))
        }, context_instance=RequestContext(request))

#####
# CONTRIBUTORS Subviews  -- DOES NOT WORK. REPLACE!!!
#####

#def summary_authors(request):
#    """
#    Show a list of all people with a 25.16 role, the Feed GUIDs associated with them and a count of the iTU downloads.
#    Note: None means that no stats were found for this GUID, whereas 0 means stats found, but no downloads.
#    """
#    # Get a dictionary of GUIDS and their aggregated summed counts
#    track_counts = dict((x['guid__guid'], x['count__sum']) for x in TrackCount.objects.values('guid__guid').annotate(Sum('count')))
#    # Now get a list of dictionaries containing all the GUIDs in the FFM
#    authors = ffm_models.Person.extended.get_all_guids()
#    listing = []
#    previous_author = {}
#    author_track_count = None
#    guids = []
#    for author in authors:
#        count = None
#        if author.get("guid") is not None:
#            try:
#                count = int(track_counts.get(author.get("guid","")))
#            except TypeError:
#                pass
#            guids.append({
#                'name': author.get("title"),
#                'guid': author.get("guid"),
#                'count': count
#            })
#        if count is not None:
#            if author_track_count is None:
#                author_track_count = 0
#            author_track_count += count
#        if author.get('last_name') != previous_author.get('last_name','') or \
#            author.get('first_name') != previous_author.get('first_name',''): # move onto a clean slate
#            listing.append({
#                'titles': author.get("titles"),
#                'first_name': author.get("first_name"),
#                'last_name': author.get("last_name"),
#                'total_count': author_track_count,
#                'guids' : guids
#            })
#            previous_author = author
#            author_track_count = None
#            guids = []
#    return render_to_response('stats/reports/authors_summary.html',{'listing':listing})


######
# =================================================================================
# =============================  GRAPHS AND IMAGES  ===============================
# =================================================================================
######
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


def graph_apple_summary_feeds(request):
    "Generate the bar chart showing cumulative downloads for each feed. Allow for a high resolution version to be produced"
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

    title = u"Cumulative downloads of all feeds"
    ax1.set_title(title)

    s = TrackCount.merged.psuedo_feeds()
    x = matplotlib.numpy.arange(1,len(s))

    bars = []
    xvalues = []
    cols = []
    for counter, row in enumerate(s):
        bars.append(int(row.get("count")))
        if counter == 0 or (counter % 10) == 0:
            xvalues.append(str(row.get("feed")))

        colour_scale = ['#ff0000', '#ffff00', '#00ff00', '#00ffff', '#0000ff', '#000099', '#006666', '#000033']
        #Create a colour scale
        #if int(row.get("count")) > 10000000:
        #    cols.append(colour_scale[0])
        #el
        if int(row.get("count")) > 1000000:
            cols.append(colour_scale[0])
        elif int(row.get("count")) > 100000:
            cols.append(colour_scale[1])
        elif int(row.get("count")) > 10000:
            cols.append(colour_scale[2])
        elif int(row.get("count")) > 1000:
            cols.append(colour_scale[3])
        elif int(row.get("count")) > 100:
            cols.append(colour_scale[4])
        elif int(row.get("count")) > 10:
            cols.append(colour_scale[5])
        else:
            cols.append(colour_scale[6])

    ind = matplotlib.numpy.arange(len(bars)) # the x locations for the groups

    # cols = ['blue']*len(ind)
    ax1.bar(ind, bars, color=cols, linewidth=0, edgecolor='w', log=True)

    ax1.set_ylabel("Downloads", color='blue', size='small')
    ax1.set_yscale('log')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    xticks = matplotlib.numpy.arange(1,len(bars),10)
    ax1.set_xticks(xticks - 0.6)
    ax1.set_xticklabels(xvalues, rotation=270, size=5, ha='center', va='top')
    ax1.set_xlabel("Psudeo Feed")

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response



def graph_apple_feed_weeks(request, feed=''):
    "Generate a chart plotting weeks vs downloads for a given feed. Allow for a high resolution version to be produced"
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
    ax2 = ax1.twinx()

    title = u"Downloads per week for '" + str(feed) + "'"
    ax1.set_title(title)

    s = TrackCount.merged.feed_week_counts(feed)
    x = matplotlib.numpy.arange(1,len(s))

    bars = []
    lines = []
    xvalues = []
    for counter, row in enumerate(s):
        bars.append(int(row.get("count")))
        if counter == 0 or (counter % 4) == 0:
            xvalues.append(str(row.get("week_ending")))
        lines.append(int(row.get("item_count")))

    ind = matplotlib.numpy.arange(len(bars)) # the x locations for the groups
    cols = ['blue']*len(ind)
    ax1.bar(ind, bars, color=cols, linewidth=0, edgecolor='w')
    ax1.set_ylabel("Weekly Downloads", color='blue', size='small')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2.plot(ind, lines, 'r-')
    ax2.set_ylabel("Number of Items", color='red', size='small')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    xticks = matplotlib.numpy.arange(1,len(s),4) # Only show the date every four weeks
    ax1.set_xticks(xticks - 0.6)
    ax1.set_xticklabels(xvalues, rotation=270, size=5, ha='center', va='top')
    ax1.set_xlabel("Week Commencing")



    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response