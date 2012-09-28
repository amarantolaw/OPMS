from datetime import timedelta
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Sum, Count, Max, Min, Q
from stats.models import *
from monitors.models import ItuCollectionHistorical
from chartit import PivotDataPool, PivotChart, DataPool, Chart


# Default Stats module homepage
def index(request):
    return render_to_response('stats/base.html', {}, context_instance=RequestContext(request))


def apple_index(request):
    return render_to_response('stats/apple/base.html', {}, context_instance=RequestContext(request))


#####
# APPLE/iTU Subviews
#####
@login_required
def summary_index(request):
    "Show the Apple 'Summary' User Action results"

    # Do a check to see if the latest Apple Raw Daily summaries have been cloned into the equivalent WeeklySummary
#    latest_raw = AppleRawLogEntry.objects.order_by('-timestamp').all()[0]
    summary_temp = []
    raw_daily = AppleRawLogDailySummary.objects.order_by('-date').all()
    try:
        latest_weekly = AppleWeeklySummary.objects.filter(service_name__exact='itu-raw').order_by('-week_beginning')[0]

        if (raw_daily[0].date - latest_weekly.week_beginning).days >= 7:
            pass #TODO calculate some weekly summaries

    except IndexError:
        pass #TODO No weekly summaries exist for itu-raw, start from the beginning

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


#######
# Apple Raw Log Display
#######
def apple_raw_summary(request):
    daily_summary_list = AppleRawLogDailySummary.objects.all().order_by('date')
    total_d = int(daily_summary_list.aggregate(Sum('download')).get("download__sum"))
    total_da = int(daily_summary_list.aggregate(Sum('download_all')).get("download_all__sum"))
    total_ad = int(daily_summary_list.aggregate(Sum('auto_download')).get("auto_download__sum"))
    total_se = int(daily_summary_list.aggregate(Sum('subscription_enclosure')).get("subscription_enclosure__sum"))
    total_downloads =  total_d + total_da + total_ad + total_se
    latest_date = daily_summary_list.aggregate(Max('date')).get("date__max")
    average_downloads_per_day = int(total_downloads / daily_summary_list.count())
    return render_to_response('stats/apple/raw/index.html',
        {
            'summary_list':daily_summary_list,
            'total_downloads':total_downloads,
            'latest_date':latest_date,
            'average_downloads_per_day':average_downloads_per_day,
        },
        context_instance=RequestContext(request)
    )


def apple_raw_collection_list(request):
    """
    @param request:
    @return:

    Display all collections belonging to an institution.
    """
#    message = ''
#    error = ''
#    institution = ItuInstitution.objects.get(id=int(institution_id))
#    collections = ItuCollection.objects.filter(institution=institution).order_by('-latest__last_modified')
#    collection_table = InstitutionalCollectionTable(collections, order_by=('-last_modified'))
#    RequestConfig(request, paginate={'per_page': 100}).configure(collection_table)
#    return render_to_response('monitors/itu_institution_collections.html',
#            {'error': error, 'message': message, 'institution': institution,
#             'collections': collections, 'collection_table': collection_table,
#             'chart': False}, context_instance=RequestContext(request))
#    )
    pass


#Pretty representation of the previous day's raw traffic
def apple_raw_animation(request):
    download_raw_log_entries = AppleRawLogEntry.objects.filter(~Q(action_type='Browse'),Q(itunes_id__gte=0))
    date = download_raw_log_entries.aggregate(Max('timestamp'))['timestamp__max'].date() - timedelta(1)
    raw_log_entries = download_raw_log_entries.filter(timestamp__contains=date)
    #    raw_log_entries = download_raw_log_entries #Cheat and merge all the days together.
    browses = AppleRawLogEntry.objects.filter(Q(action_type='Browse'),Q(itunes_id__gte=0),Q(timestamp__contains=date))
    itu_ids = raw_log_entries.values('itunes_id').distinct()
    historical_collection_records = []
    for itu_id in itu_ids:
        try:
            historical_collection_record = ItuCollectionHistorical.objects.filter(itu_id=int(itu_id['itunes_id'])).order_by('-version')[0]
            historical_collection_records.append(historical_collection_record)
        except IndexError:
            pass
    return render_to_response('stats/apple/raw/animation.html', {'historical_collection_records': historical_collection_records, 'raw_log_entries': raw_log_entries, 'browses': browses}, context_instance=RequestContext(request))
