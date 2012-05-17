from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Sum
from stats.models import *
from chartit import PivotDataPool, PivotChart, DataPool, Chart


# Default Stats module homepage
def index(request):
    return render_to_response('stats/base.html', {}, context_instance=RequestContext(request))

def apple_index(request):
    return render_to_response('stats/apple/base.html', {}, context_instance=RequestContext(request))


#####
# APPLE/iTU Subviews
#####
def summary_index(request):
    "Show the Apple 'Summary' User Action results"
    summary_data = AppleWeeklySummary.merged.all()

    # Create a Datapool object for Chartit
    cdata = PivotDataPool(
        series=[{
            'options':{
                'source': AppleWeeklySummary.objects.all(),
                'categories': [
                    'week_beginning'
                ],
            },
            'terms':{
                'weekly_total': Sum('total_track_downloads')
            }
        }]
    )
    # Create a Chart object for Chartit
    pivcht = PivotChart(
        datasource = cdata,
        series_options = [{
            'options':{
                'type':'column',
                'stacking':False,
                'yAxis': 0
            },
            'terms':[
                'weekly_total',
            ]
        }],
        chart_options = {
            'title':{'text':'Number of downloads per week for iTunes U'},
            'xAxis':{
                'title': {
                    'text':'Week Beginning'
                },
                'labels':{
                    'rotation': '0',
                    'step': '8',
                    'staggerLines':'2'
                }
            },
            'yAxis':[{
                'title': {
                    'text':'Download Count',
                    'rotation': '90'
                },
                'min':0
            }]
        }
    )

    return render_to_response('stats/apple/apple_summary.html', {
            'summary_data': summary_data,
            'cht':pivcht
        }, context_instance=RequestContext(request)
    )


#####
# FEEDS Subviews
#####
def summary_feeds(request):
    listing = AppleWeeklyTrackCount.merged.psuedo_feeds()
    return render_to_response('stats/apple/feeds.html',{
            'listing':listing
        }, context_instance=RequestContext(request))


def feed_detail(request, partial_guid):
    # Construct pivot table of data.
    # Orientation 0 is items on x, time on y. Anything else is time on x, items on y.
    try:
        orientation = int(request.GET.get('orientation', 1))
    except ValueError:
        orientation = 1

    i = AppleWeeklyTrackCount.merged.feed_items(partial_guid)
    w = AppleWeeklyTrackCount.merged.feed_weeks(partial_guid)
    c = AppleWeeklyTrackCount.merged.feed_counts(partial_guid, orientation)

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
                if count != None and count.get("week_beginning") == week and count.get("guid") == item:
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
            row_data.append(str(item)[23:52])
        listing.insert(0,{'column_a':'Week Commencing', 'data':row_data, 'total':'Week Total'})
    else:
        for week in w:
            column_totals[week] = 0

        for item in i:
            row_data = []
            row_total = 0
            for week in w:
                if count != None and count.get("week_beginning") == week and count.get("guid") == item:
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

    # Create a Datapool object for Chartit
    cdata = PivotDataPool(
        series=[{
            'options':{
                'source': AppleWeeklyTrackCount.objects.filter(guid__guid__contains = partial_guid),
                'categories': [
                    'summary__week_beginning'
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
                    'rotation': '0',
                    'step': '4',
                    'staggerLines':'2'
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

    return render_to_response('stats/apple/feed.html',{
            'listing':listing,
            'ref':partial_guid,
            'summary':summary,
            'cht':pivcht,
            'chart_height':int(40+summary.get('count')),
            'orientation':orientation
        }, context_instance=RequestContext(request))


def guid_detail(request, target_guid):

    listing = AppleWeeklyTrackCount.objects.filter(guid__guid__exact=target_guid).order_by("summary__week_beginning")

    # Generate summary data
    summary = {}
    summary['count'] = len(listing)
    summary['total'] = 0
    summary['max_value']   = 0
    summary['max_week'] = ""
    for row in listing:
        summary['total'] += int(row.count)
        if int(row.count) > summary.get('max_value'):
            summary['max_value'] = int(row.count)
            summary['max_week'] = row.summary.week_beginning
    try:
        summary['avg'] = summary.get('total') // summary.get('count')
    except ZeroDivisionError:
        summary['avg'] = summary.get('total')

    # Create a Datapool object for Chartit
    cdata = PivotDataPool(
        series=[{
            'options':{
                'source': AppleWeeklyTrackCount.objects.filter(guid__guid__exact=target_guid),
                'categories': [
                    'summary__week_beginning'
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
            'title':{'text':'Number of downloads per week for this item'},
            'xAxis':{
                'title': {
                    'text':'Week Beginning'
                },
                'labels':{
                    'rotation': '0',
                    'step': '4',
                    'staggerLines':'2'
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

    return render_to_response('stats/apple/guid.html',{
        'listing':listing,
        'ref':target_guid,
        'summary':summary,
        'cht':pivcht
    }, context_instance=RequestContext(request))


