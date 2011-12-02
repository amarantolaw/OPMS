from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import *
import ffm.models as ffm_models
import pylab
import numpy as np
import matplotlib
import matplotlib.dates
import matplotlib.ticker as ticker
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

    return render_to_response('stats/reports/feed.html',{
        'listing':listing, 'ref':partial_guid, 'summary':summary
        })



def summary_items(request):
    #listing = TrackCount.merged.psuedo_feeds()
    #return render_to_response('stats/reports/items.html',{'listing':listing})
    "Show the results for all items"
    return HttpResponse("Hello World. You're at the ITEMS LISTING page.")



def item_detail(request, item_id):
    "Show the results for a given item"
    return HttpResponse("Hello World. You're at the ITEM DETAIL page.")





def summary_authors(request):
    "Show a list of all people with a 25.16 role, and the Feed GUIDs associated with them"
    # return HttpResponse("Hello from the Summary Authors Page")
    authors = ffm_models.Person.objects.all().order_by('last_name').order_by('first_name')
    listing = []
    for author in authors:
        guids = []
        items = author.item_set.all() # Shortcut because we know all roles are 25.16
        for item in items:
            files = item.file_set.all()
            for file in files:
                fifs = file.fileinfeed_set.all()
                for fif in fifs:
                    guids.append(fif.guid)
        listing.append({
            'titles': author.titles,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'guids' : guids
        })
    return render_to_response('stats/reports/authors_summary.html',{'listing':listing})




def summary_urlmonitoring(request):
    "Show the results for a url monitoring"
    # List the URLS and the number of scans for that URL
    summary_listing = []

    urls = URLMonitorTarget.objects.all().order_by('url')
    for url in urls:
        summary_listing.append(
            '<a href="/stats/report/urlmonitoring/url/' + str(url.id) + '">' + str(url.url) + '</a> (' +\
            str(url.urlmonitorscan_set.count()) + ')'
        )
    return render_to_response('stats/reports/url_summary.html', {'summary_listing': summary_listing,})




    # Create a pivot table for Tasks vs URLs
    # Orientation 0 is tasks on x, urls on y. Anything else is urls on x, tasks on y.
#    try:
#        orientation = int(request.GET.get('orientation', 0))
#    except ValueError:
#        orientation = 0
#
#    tasks = URLMonitorTask.objects.all().order_by('id').select_related('urlmonitorscan_set')
#    urls = URLMonitorTarget.objects.all().order_by('url')
#
#
#    summary_data = []
#    if orientation == 0:
#        for url in urls:
#            row_data = []
#            for task in tasks:
#                scan_count = int(
#                    # This is SLOW!!!
#                    task.urlmonitorscan_set.filter(url__exact=url.id).count()
#                )
##                if scan_count > 0:
##                    row_data.append('<a href="">' + str(scan_count) + '</a>')
##                else:
#                row_data.append(str(scan_count))
#            summary_data.append({
#                'url':'<a href="/stats/report/urlmonitoring/url/' + str(url.id) + '">' + str(url.url) + '</a>',
#                'data':row_data,
#                })
#
#
#    # Put column headers and totals into listing array - values, then headings
#    row_data = []
#    for task in tasks:
#        row_data.append('<a href="/stats/report/urlmonitoring/task/' + str(task.id) + '">' + str(task.comment) + '</a>')
#    summary_data.insert(0,{'url':'', 'data':row_data,})
#
#    return render_to_response('stats/reports/url_summary.html', {'summary_data': summary_data,})



def urlmonitoring_task(request, task_id):
    "Show the results for a url monitoring of a specific task"
    scan_data = URLMonitorScan.objects.filter(task__id__exact=task_id).select_related().order_by('-url__url', 'iteration')
    return render_to_response('stats/reports/url_summary.html', {'scan_data': scan_data,})


def urlmonitoring_url(request, url_id):
    "Show the results for a url monitoring of specific url"
    # Limit to the last 7 days' worth of scans (10 scans * 4 times an hour * 24 hours * 7 days)
    scan_data = URLMonitorScan.objects.filter(url__id__exact=url_id).select_related().order_by('-time_of_request')[:6720]
    return render_to_response('stats/reports/url_summary.html', {'scan_data': scan_data,'url_id':url_id})


# TEMP FUNCTIONS
def summary_feeds_cc(request):
    listing = TrackCount.merged.psuedo_feeds_cc()
    return render_to_response('stats/reports/feeds-cc.html',{'listing':listing})

def feed_detail_cc(request):
    return HttpResponse("Hello, world. You're at the feed_detail_cc view.")

######
# =================================================================================
# =============================  GRAPHS AND IMAGES  ===============================
# =================================================================================
######

def graph_urlmonitoring_url(request, url_id = 0):
    "Generate a plot of request times over a series of scans. Allow for a high resolution version to be produced"
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
#    ax2 = ax1.twinx()

    # Limit to the last 7 days' worth of scans (10 scans * 4 times an hour * 24 hours * 7 days)
    s = URLMonitorScan.objects.filter(url__id__exact=url_id).select_related().order_by('-time_of_request')[:6720]
    x = []
    x_dates = []
    ttfb = []
    ttlb = []
    ttfb_cols = []
    ttlb_cols = []

    url = str(s[0].url.url)
    if len(url) > 55:
        title = u"Data for " + str(s[0].url.url)[:55] + "..."
    else:
        title = u"Data for " + str(s[0].url.url)
    ax1.set_title(title)

#    xticks = matplotlib.numpy.arange(1,len(x),10) # Only show the date every 10 values
    # Note that the resultset is in reverse order, so will have to build the lists in reverse order, hence insert over append
    for count, item in enumerate(s):
        if item.time_of_request == None:
            continue # Skip data where we failed to write a time of request...
        x.insert(0,item.time_of_request)
        try:
            ttfb.insert(0,float(item.ttfb))
        except (ValueError, TypeError):
            ttfb.insert(0,float(0.0))
        try:
            ttlb.insert(0,float(item.ttlb))
        except (ValueError, TypeError):
            ttlb.insert(0,float(0.0))
        if item.iteration == 1:
            ttfb_cols.insert(0,'#0000FF')
            ttlb_cols.insert(0,'#FF0000')
        else:
            ttfb_cols.insert(0,'#000066')
            ttlb_cols.insert(0,'#660000')
#        if count % 10 == 0:
#            x_dates.append(item.time_of_request)

    # Generate the x axis manually.
    N = len(x)
    xind = np.arange(N)

    def format_date(xin, pos=None):
        thisind = np.clip(int(xin+0.5), 0, N-1)
        return x[thisind].strftime("%Y-%m-%d")

    ax1.scatter(xind, ttfb, marker='o', color=ttfb_cols)
    ax1.set_ylabel("Time in Seconds", color='blue', size='small')
    ax1.set_yscale('log')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax1.scatter(xind, ttlb, marker='+', color=ttlb_cols)
#    ax2.set_ylabel("TTLB in Seconds", color='red', size='small')
#    ax2.set_yscale('log')
#    for tl in ax2.get_yticklabels():
#        tl.set_color('r')

    ax1.set_xticklabels(xind, rotation=300, size=5, ha='center', va='top')
#    ax1.set_autoscalex_on(False)
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax1.set_xlabel("Time of Request")
    fig.autofmt_xdate()

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response





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

        #Create a colour scale
        if int(row.get("count")) > 10000000:
            cols.append('#ff0000')
        elif int(row.get("count")) > 1000000:
            cols.append('#cc0000')
        elif int(row.get("count")) > 100000:
            cols.append('#990000')
        elif int(row.get("count")) > 10000:
            cols.append('#660000')
        elif int(row.get("count")) > 1000:
            cols.append('#330033')
        elif int(row.get("count")) > 100:
            cols.append('#000066')
        elif int(row.get("count")) > 10:
            cols.append('#000099')
        else:
            cols.append('#0000cc')

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