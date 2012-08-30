from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Sum, Count, Max, Min
from stats.models import *
from monitors.models import ItuCollectionHistorical
from chartit import PivotDataPool, PivotChart, DataPool, Chart


# Default Stats module homepage
@login_required
def index(request):
    return render_to_response('stats/base.html', {}, context_instance=RequestContext(request))


@login_required
def apple_index(request):
    return render_to_response('stats/apple/base.html', {}, context_instance=RequestContext(request))

#Pretty representation of the previous day's raw traffic
@login_required
def apple_raw_animation(request):
    download_raw_log_entries = AppleRawLogEntry.objects.filter(action_type='Download',itunes_id__gte=0)
    date = download_raw_log_entries.aggregate(Max('timestamp'))['timestamp__max'].date()
    raw_log_entries = download_raw_log_entries.filter(timestamp__contains=date)
    itu_ids = raw_log_entries.values('itunes_id').annotate(Count('itunes_id')).order_by('-itunes_id__count')
    historical_collection_records = []
    for itu_id in itu_ids:
        historical_collection_record = ItuCollectionHistorical.objects.filter(itu_id=int(itu_id['itunes_id'])).order_by('-version')[0]
        historical_collection_records.append(historical_collection_record)
    return render_to_response('stats/apple/raw/animation.html', {'historical_collection_records': historical_collection_records}, context_instance=RequestContext(request))

#####
# APPLE/iTU Subviews
#####
@login_required
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
@login_required
def summary_feeds(request):
    listing = AppleWeeklyTrackCount.merged.psuedo_feeds()
    return render_to_response('stats/apple/feeds.html',{
            'listing':listing
        }, context_instance=RequestContext(request))


@login_required
def feed_detail(request, partial_guid):
    # Construct pivot table of data.
    # Orientation 0 is items on x, time on y. Anything else is time on x, items on y.
    try:
        orientation = int(request.GET.get('orientation', 1))
    except ValueError:
        orientation = 1

#    i = AppleWeeklyTrackCount.merged.feed_items(partial_guid)
    i = AppleTrackGUID.objects.filter(guid__contains=partial_guid).order_by("guid")
    w = AppleWeeklyTrackCount.merged.feed_weeks(partial_guid)
    c = AppleWeeklyTrackCount.merged.feed_counts(partial_guid, orientation)

    listing = []
    column_totals = {}
    count = c.pop(0)
    if orientation == 0: # Show items as columns, and weeks as rows
        for item in i:
            column_totals[item.guid] = 0

        for week in w:
            row_data = []
            row_total = 0
            for item in i:
                if count != None and count.get("week_beginning") == week and count.get("guid") == item.guid:
                    row_data.append(int(count.get("count")))
                    row_total += int(count.get("count"))
                    column_totals[item.guid] += int(count.get("count"))
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
            row_data.append(column_totals.get(item.guid))
        listing.insert(0,{'column_a':'Item Total', 'data':row_data, 'total':''})
        row_data = []
        for item in i:
            row_data.append(str(item.name))
        listing.insert(0,{'column_a':'Week Commencing', 'data':row_data, 'total':'Week Total'})
    else: # Show weeks as columns, and items as rows
        for week in w:
            column_totals[week] = 0

        for item in i:
            row_data = []
            row_total = 0
            for week in w:
                if count != None and count.get("week_beginning") == week and count.get("guid") == item.guid:
                    row_data.append(int(count.get("count")))
                    row_total += int(count.get("count"))
                    column_totals[week] += int(count.get("count"))
                    try:
                        count = c.pop(0)
                    except IndexError:
                        count = None
                else:
                    row_data.append(None)
            listing.append({'column_a':[item.id,item.name], 'data':row_data, 'total':row_total})

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

    try:
        # Create a Datapool object for Chartit
        # Chartit can't do unicode at present, so add a hack to do a separate legend when this fails
        cdata = PivotDataPool(
            series=[{
                'options':{
                    'source': AppleWeeklyTrackCount.objects.filter(guid__guid__contains = partial_guid),
                    'categories': [
                        'summary__week_beginning'
                    ],
                    'legend_by': 'guid__name'
                },
                'terms':{
                    'feed_total': Sum('count')
                }
            }]
        )
        trackguidlist = None
    except UnicodeEncodeError:
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
        trackguidlist = i


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
        'orientation':orientation,
        'trackguidlist': trackguidlist,
    }, context_instance=RequestContext(request))


@login_required
def guid_detail(request, trackguid_id):
    # TODO: This view needs some error checking to happen on the input value
    listing = AppleWeeklyTrackCount.objects.filter(guid__id__exact=trackguid_id).order_by("summary__week_beginning")
    guid = AppleTrackGUID.objects.get(id__exact=trackguid_id)
    partial_guid = guid.guid[51:] # Get the part after 52 characters to make up the partial guid.

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
                'source': AppleWeeklyTrackCount.objects.filter(guid__id__exact=trackguid_id),
                'categories': [
                    'summary__week_beginning'
                ],
                'legend_by': 'summary__service_name'
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
        'guid':guid,
        'listing':listing,
        'summary':summary,
        'cht':pivcht,
        'trackguid_id':trackguid_id, # Need this for the breadcrumb path via feeds
        'ref':partial_guid, # Need this for the breadcrumb path via feeds
    }, context_instance=RequestContext(request))


####
# TEST RAW OUTPUT
####
#def list_daily_raw(request):
#    raw_listing = AppleRawLogEntry.objects.raw(
#        """
#        SELECT date_trunc('day', timestamp) AS day, count(id) AS total, action_type
#        FROM stats_applerawlogentry
#        GROUP BY date_trunc('day', timestamp), action_type
#        ORDER BY day, action_type;
#        """
#    )
#    # Pivot this listing into a table on date vs action type, combining some actions to match the apple ones
#    # Date vs Browse, Subscribe, Download, Stream, Enclosure
#    listing = []
#    for row in raw_listing:
#
#
#
#    AppleWeeklyTrackCount.merged.psuedo_feeds()
#    return render_to_response('stats/apple/feeds.html',{
#        'listing':listing
#    }, context_instance=RequestContext(request))


#SELECT date_trunc('day', timestamp) AS day, count(id) AS total, action_type
#FROM stats_applerawlogentry
#WHERE date_trunc('day', timestamp) >= '2012-01-24'
#  AND date_trunc('day', timestamp) < '2012-01-25'
#GROUP BY date_trunc('day', timestamp), action_type
#ORDER BY day;
