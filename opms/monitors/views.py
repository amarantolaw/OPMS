import random
from datetime import timedelta
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_safe
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum, Count
from django_tables2 import RequestConfig
import opms.settings as settings
from opms.monitors.models import URLMonitorURL, URLMonitorScan
from feedback.models import Metric, Traffic, Category, Comment, Event, Tag
from feedback.views import create_metric_textfiles
from monitors.models import ItuCollectionChartScan, ItuCollectionHistorical, ItuCollection, ItuItemChartScan, ItuItemHistorical, ItuItem, ItuScanLog, ItuGenre, ItuInstitution, ItuRating, ItuComment
from monitors.models import InstitutionalCollectionTable
#import pylab
#import numpy as np
#import matplotlib
#import matplotlib.dates
#import matplotlib.ticker as ticker
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure

# Default Monitors module homepage
#@require_safe(request)
@login_required
def index(request):
    """The Monitoring home page."""
    return render_to_response('monitors/base.html', {}, context_instance=RequestContext(request))


######
# URL Monitoring Subviews
######

@login_required
def urlmonitoring_summary(request):
    """Show the results for a url monitoring"""
    # List the URLS and the number of scans for that URL
    summary_listing = []

    urls = URLMonitorURL.objects.all().order_by('-active', 'url')

    return render_to_response('monitors/url_summary.html', {'urls': urls, },
        context_instance=RequestContext(request))


@login_required
def urlmonitoring_task(request, task_id):
    """Show the results for a url monitoring of a specific task"""
    scan_data = URLMonitorScan.objects.filter(task__id__exact=task_id).select_related().order_by('-url__url',
        'iteration')
    return render_to_response('monitors/url_summary.html', {'scan_data': scan_data, 'task_id': task_id},
        context_instance=RequestContext(request))


@login_required
def urlmonitoring_url(request, url_id):
    """Show the results for a url monitoring of specific url"""
    # Limit to the last 3 days' worth of scans (10 scans * 4 times an hour * 24 hours * 3 days)
    scan_data = URLMonitorScan.objects.filter(url__id__exact=url_id).select_related().order_by('-time_of_request')[
                :2880]
    return render_to_response('monitors/url_summary.html', {'scan_data': scan_data, 'url_id': url_id},
        context_instance=RequestContext(request))


######
# =================================================================================
# =============================  GRAPHS AND IMAGES  ===============================
# =================================================================================
######

#def graph_urlmonitoring_url(request, url_id = 0):
#    "Generate a plot of request times over a series of scans. Allow for a high resolution version to be produced"
#    try:
#        resolution = int(request.GET.get('dpi', 100))
#    except ValueError:
#        resolution = 100
#    if resolution > 600:
#        resolution = 600
#    elif resolution < 100:
#        resolution = 100
#
#    fig = Figure(figsize=(9,5), dpi=resolution, facecolor='white', edgecolor='white')
#    ax1 = fig.add_subplot(1,1,1)
#    #    ax2 = ax1.twinx()
#
#    # Limit to the last 3 days' worth of scans (10 scans * 4 times an hour * 24 hours * 3 days)
#    s = URLMonitorScan.objects.filter(url__id__exact=url_id).select_related().order_by('-time_of_request')[:2880]
#    x = []
#    x_dates = []
#    ttfb = []
#    ttlb = []
#    ttfb_cols = []
#    ttlb_cols = []
#
#    url = str(s[0].url.url)
#    if len(url) > 55:
#        title = u"Data for " + str(s[0].url.url)[:55] + "..."
#    else:
#        title = u"Data for " + str(s[0].url.url)
#    ax1.set_title(title)
#
#    #    xticks = matplotlib.numpy.arange(1,len(x),10) # Only show the date every 10 values
#    # Note that the resultset is in reverse order, so will have to build the lists in reverse order, hence insert over append
#    for count, item in enumerate(s):
#        if item.time_of_request == None:
#            continue # Skip data where we failed to write a time of request...
#        x.insert(0,item.time_of_request)
#        try:
#            ttfb.insert(0,float(item.ttfb))
#        except (ValueError, TypeError):
#            ttfb.insert(0,float(0.0))
#        try:
#            ttlb.insert(0,float(item.ttlb))
#        except (ValueError, TypeError):
#            ttlb.insert(0,float(0.0))
#        if item.iteration == 1:
#            ttfb_cols.insert(0,'#0000FF')
#            ttlb_cols.insert(0,'#FF0000')
#        else:
#            ttfb_cols.insert(0,'#000066')
#            ttlb_cols.insert(0,'#660000')
#        #        if count % 10 == 0:
#        #            x_dates.append(item.time_of_request)
#
#    # Generate the x axis manually.
#    N = len(x)
#    xind = np.arange(N)
#
#    def format_date(xin, pos=None):
#        thisind = np.clip(int(xin+0.5), 0, N-1)
#        return x[thisind].strftime("%Y-%m-%d")
#
#    ax1.scatter(xind, ttfb, marker='o', color=ttfb_cols)
#    ax1.set_ylabel("Time in Seconds", color='blue', size='small')
#    ax1.set_yscale('log')
#    for tl in ax1.get_yticklabels():
#        tl.set_color('b')
#
#    ax1.scatter(xind, ttlb, marker='+', color=ttlb_cols)
#    #    ax2.set_ylabel("TTLB in Seconds", color='red', size='small')
#    #    ax2.set_yscale('log')
#    #    for tl in ax2.get_yticklabels():
#    #        tl.set_color('r')
#
#    ax1.set_xticklabels(xind, rotation=300, size=5, ha='center', va='top')
#    #    ax1.set_autoscalex_on(False)
#    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
#    ax1.set_xlabel("Time of Request")
#    fig.autofmt_xdate()
#
#    canvas = FigureCanvas(fig)
#    response = HttpResponse(content_type='image/png')
#    canvas.print_png(response)
#    return response

@login_required
def itu_home(request):
    """The iTunes U Monitoring home page."""
    message = ''
    error = ''
    try:
        this_institution = ItuInstitution.objects.get(name=settings.YOUR_INSTITUTION)
    except:
        this_institution = None
        error += 'Institution in settings file does not match an institution in the database. Perhaps you need to run scan_itunes first?'
    return render_to_response('monitors/itu_home.html',
            {'error': error, 'message': message, 'this_institution': this_institution},
        context_instance=RequestContext(request))


@login_required
def itu_top_collections(request, chartscan=None):
    """Show a top collections chart, defaulting to the most recent completed scan."""
    message = ''
    error = ''
    if not chartscan:
        try:
            chartscan = ItuScanLog.objects.filter(mode=2, complete=True).order_by('-time')[0]
        except:
            error += 'Couldn\'t find latest top collections scan. You probably need to run one first.'
            return render_to_response('monitors/itu_top_collections.html',
                    {'error': error, 'message': message, 'chartrows': [], 'scanlog': None},
                context_instance=RequestContext(request))
        #    try:
        #        next_chartscan = ItuScanLog.objects.filter(mode=2, complete=True, time__gt=chartscan.time).order_by('time')[0]
        #    except:
        #        next_chartscan = None
        #    try:
        #        previous_chartscan = ItuScanLog.objects.filter(mode=2, complete=True, time__lt=chartscan.time).order_by('-time')[0]
        #    except:
        #        previous_chartscan = None
    chartrows = ItuCollectionChartScan.objects.filter(scanlog=chartscan)
    return render_to_response('monitors/itu_top_collections.html',
            {'error': error, 'message': message, 'chartrows': chartrows, 'scanlog': chartscan},
        context_instance=RequestContext(request))


@login_required
def itu_top_items(request, chartscan=None):
    """Show a top items chart, defaulting to the most recent completed scan."""
    message = ''
    error = ''
    if not chartscan:
        try:
            chartscan = ItuScanLog.objects.filter(mode=3, complete=True).order_by('-time')[0]
        except:
            error += 'Couldn\'t find latest top items scan. You probably need to run one first.'
            return render_to_response('monitors/itu_top_items.html',
                    {'error': error, 'message': message, 'chartrows': [], 'scanlog': None},
                context_instance=RequestContext(request))
    chartrows = ItuItemChartScan.objects.filter(scanlog=chartscan)
    return render_to_response('monitors/itu_top_items.html',
            {'error': error, 'message': message, 'chartrows': chartrows, 'scanlog': chartscan},
        context_instance=RequestContext(request))


@login_required
def itu_collections(request):
    """Show a clickable list of all collections."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_collections.html', {'error': error, 'message': message},
        context_instance=RequestContext(request))


@login_required
def itu_items(request):
    """Show a clickable list of all items."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_items.html', {'error': error, 'message': message},
        context_instance=RequestContext(request))


@login_required
def itu_institutions(request, institutions=[]):
    """Show a clickable list of all institutions."""
    message = ''
    error = ''
    if not institutions:
        try:
            institutions = ItuInstitution.objects.annotate(number_of_collections=Count('itucollection')).filter(
                number_of_collections__gt=0)
        except:
            error += 'Failed to query the database for institutions.'
    if not institutions:
        error += 'Couldn\'t find any institutions. Perhaps you haven\'t run scan_itunes --mode 4 yet?'
    return render_to_response('monitors/itu_institutions.html',
            {'error': error, 'message': message, 'institutions': institutions},
        context_instance=RequestContext(request))


@login_required
def itu_genres(request):
    """Show a clickable list of all genres."""
    message = ''
    error = ''
    try:
        genres = ItuGenre.objects.all()
    except:
        genres = []
        error += 'Failed to query the database for genres.'
    if not genres:
        error += 'Couldn\'t find any genres. Perhaps you haven\'t run scan_itunes yet?'
    return render_to_response('monitors/itu_genres.html', {'error': error, 'message': message, 'genres': genres},
        context_instance=RequestContext(request))


@login_required
def itu_scanlogs(request, all=False):
    """Show a clickable list of all scanlogs."""
    message = ''
    error = ''
    if not all:
        try:
            scanlogs = ItuScanLog.objects.all().order_by('-time')[:100]
        except KeyError: #ie. when there aren't 100 scanlogs yet.
            scanlogs = ItuScanLog.objects.all()
    else:
        scanlogs = ItuScanLog.objects.all()
    if not scanlogs:
        error += 'Can\'t find any scanlogs. Perhaps you haven\'t run scan_itunes yet?'
    return render_to_response('monitors/itu_scanlogs.html', {'error': error, 'message': message, 'scanlogs': scanlogs, 'all': all},
        context_instance=RequestContext(request))


@login_required
def itu_collection(request, collection_id):
    """Display an absolute record of a collection."""
    message = ''
    error = ''
    tags = Tag.objects.all()
    collection = ItuCollection.objects.get(id=int(collection_id))
    chartrecords = ItuCollectionChartScan.objects.filter(itucollection=collection).order_by('date')
    items = ItuItem.objects.filter(latest__series__itucollection=collection, latest__missing=None)
    try:
        total_duration = timedelta(
            microseconds=int(items.aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
    except:
        total_duration = timedelta(microseconds=0)
        message += 'WARNING: Couldn\'t calculate the total duration properly.'
    comments = ItuComment.objects.filter(itucollectionhistorical__itucollection=collection)
    ratings = ItuRating.objects.filter(itucollectionhistorical=collection.latest)
    average_rating = collection.latest.average_rating()
    metrics_to_plot = []
    traffic_to_plot = []
    categories_to_plot = []
    comments_to_plot = []
    if chartrecords:
        #Get or create a suitable Metric
        try:
            top_collections_position = Metric.objects.get(description=collection.latest.name)
            metrics_to_plot.append(top_collections_position)
        except:
            random_colour = '#' + str(random.randint(222222, 999999))
            top_collections_position = Metric(description=collection.latest.name, linecolor=random_colour,
                fillcolor='#FFFFFF', mouseover=True, defaultvisibility=True, source='itu-collection-chart', itucollection=collection)
            top_collections_position.save()
            metrics_to_plot.append(top_collections_position)

        #Add the first chartrecord of the day to traffic_to_plot
        dates = []
        for chartrecord in chartrecords:
            if chartrecord.date.date() not in dates:
                dates.append(chartrecord.date.date())
        for date in dates:
            chartrecords_day = []
            for chartrecord in chartrecords:
                if chartrecord.date.date() == date:
                    chartrecords_day.append(chartrecord)
            traffic_to_plot.append(
                Traffic(date=date, count=(-1 * chartrecords_day[0].position), metric=top_collections_position))

        if comments:
            from_itunes_u = Category.objects.get(description='From iTunes U')
            from_itunes_u.defaultvisibility = False
            categories_to_plot.append(from_itunes_u)
            for comment in comments:
                comment_to_plot = Comment(date=comment.date,
                    source=(comment.itucollectionhistorical.name + ' - comment by ' + comment.source),
                    detail=comment.detail, user_email='scan_itunes@manage.py', category=from_itunes_u)
                comments_to_plot.append(comment_to_plot)

    return render_to_response('monitors/itu_collection.html',
            {'error': error, 'message': message, 'collection': collection, 'chartrecords': chartrecords,
             'comments': comments, 'items': items, 'total_duration': total_duration, 'ratings': ratings,
             'average_rating': average_rating,
             'comments_to_plot': comments_to_plot,
             'metrics_to_plot': metrics_to_plot,
             'metric_textfiles': create_metric_textfiles(traffic_to_plot, metrics_to_plot),
             'categories_to_plot': categories_to_plot,
             'events': [],
             'chart': True,
             'tags': tags}, context_instance=RequestContext(request), )


@login_required
def itu_item(request, item_id):
    """Display an absolute record of an item."""
    message = ''
    error = ''
    tags = Tag.objects.all()
    item = ItuItem.objects.get(id=int(item_id))
    chartrecords = ItuItemChartScan.objects.filter(ituitem=item)

    metrics_to_plot = []
    traffic_to_plot = []
    categories_to_plot = []
    if chartrecords:
        #Get or create a suitable Metric
        metrics = Metric.objects.filter(description=item.latest.name)
        if not metrics:
            random_colour = '#' + str(random.randint(222222, 999999))
            top_items_position = Metric(description=item.latest.name, linecolor=random_colour, fillcolor='#FFFFFF',
                mouseover=True, defaultvisibility=True, source='itu-item-chart', ituitem=item)
            top_items_position.save()
            metrics_to_plot.append(top_items_position)
        else:
            metrics_to_plot.append(metrics[0])

        #Add the first chartrecord of the day to traffic_to_plot
        dates = []
        for chartrecord in chartrecords:
            if chartrecord.date.date() not in dates:
                dates.append(chartrecord.date.date())
        for date in dates:
            chartrecords_day = []
            for chartrecord in chartrecords:
                if chartrecord.date.date() == date:
                    chartrecords_day.append(chartrecord)
            traffic_to_plot.append(
                Traffic(date=date, count=(-1 * chartrecords_day[0].position), metric=metrics_to_plot[0]))

    return render_to_response('monitors/itu_item.html',
            {'error': error, 'message': message, 'item': item, 'chartrecords': chartrecords,
             'comments_to_plot': [],
             'metrics_to_plot': metrics_to_plot,
             'metric_textfiles': create_metric_textfiles(traffic_to_plot, metrics_to_plot),
             'categories_to_plot': categories_to_plot,
             'events': [],
             'chart': True, 'tags': tags}, context_instance=RequestContext(request))


@login_required
def itu_institution(request, institution_id):
    """Display an institution."""
    message = ''
    error = ''
    tags = Tag.objects.all()
    latest_tc_scanlog = ItuScanLog.objects.filter(mode=2).order_by('-time')[0]
    latest_ti_scanlog = ItuScanLog.objects.filter(mode=3).order_by('-time')[0]
    institution = ItuInstitution.objects.get(id=int(institution_id))
    comments = ItuComment.objects.filter(ituinstitution=institution).order_by('-date')
    collections = ItuCollection.objects.filter(institution=institution).order_by('-latest__last_modified')
    current_collection_chartscans = ItuCollectionChartScan.objects.filter(itucollection__institution=institution,scanlog=latest_tc_scanlog).order_by('position')
    current_item_chartscans = ItuItemChartScan.objects.filter(ituitem__institution=institution,scanlog=latest_ti_scanlog)
    if current_collection_chartscans.count() > 5:
        top_five_tc_scanlogs = current_collection_chartscans[0:5]
    else:
        top_five_tc_scanlogs = current_collection_chartscans
    if collections.filter(latest__last_modified__isnull=False).count() > 5:
        recently_updated_collections = collections.filter(latest__last_modified__isnull=False)[0:5]
    else:
        recently_updated_collections = collections.filter(latest__last_modified__isnull=False)
    try:
        audio_items = ItuItem.objects.filter(Q(institution=institution) & Q(latest__missing=None) & (
        Q(latest__file_extension='mp3') | Q(latest__file_extension='m4a') | Q(latest__file_extension='aac') | Q(
            latest__file_extension='aif') | Q(latest__file_extension='aiff') | Q(latest__file_extension='aifc') | Q(
            latest__file_extension='wav')))
        audio_duration = timedelta(
            microseconds=int(audio_items.aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
        audio_number = audio_items.count()
    except:
        audio_duration = timedelta(microseconds=0)
        audio_number = 0
        message += 'WARNING: Couldn\'t calculate the total audio duration/number properly. '
    try:
        video_items = ItuItem.objects.filter(Q(institution=institution) & Q(latest__missing=None) & (
        Q(latest__file_extension='mp4') | Q(latest__file_extension='m4v') | Q(latest__file_extension='mov')))
        video_duration = timedelta(
            microseconds=int(video_items.aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
        video_number = video_items.count()
    except:
        video_duration = timedelta(microseconds=0)
        video_number = 0
        message += 'WARNING: Couldn\'t calculate the total video duration/number properly. '
    try:
        total_duration = timedelta(microseconds=int(ItuItem.objects.filter(Q(institution=institution) & Q(latest__missing=None)).aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
    except:
        total_duration = timedelta(microseconds=0)
        message += 'WARNING: Couldn\'t calculate total duration properly. '
    unknown_duration = total_duration - (audio_duration + video_duration)
    try:
        total_number = ItuItem.objects.filter(latest__missing=None, latest__institution=institution).count()
    except:
        total_number = 0
        message += 'WARNING: Couldn\'t calculate the total number of items properly. '
    other_number = total_number - (audio_number + video_number)
    collections_number = collections.count()
    collections_containing_movies_number = collections.filter(latest__contains_movies=True).count()
    collections_not_containing_movies_number = collections_number - collections_containing_movies_number

    metrics_to_plot = []
    traffic_to_plot = []
    categories_to_plot = []
    comments_to_plot = []

    try:
        top_collections_count = Metric.objects.get(description='# of collections in the top 200')
        metrics_to_plot.append(top_collections_count)
    except:
        random_colour = '#' + str(random.randint(222222, 999999))
        top_collections_count = Metric(description='# of collections in the top 200', linecolor=random_colour,
            fillcolor='#FFFFFF', mouseover=True, defaultvisibility=True, source='itu-#tc', ituinstitution=institution)
        top_collections_count.save()
        metrics_to_plot.append(top_collections_count)
    try:
        top_items_count = Metric.objects.get(description='# of items in the top 200')
        metrics_to_plot.append(top_items_count)
    except:
        random_colour = '#' + str(random.randint(222222, 999999))
        top_items_count = Metric(description='# of items in the top 200', linecolor=random_colour,
            fillcolor='#FFFFFF', mouseover=True, defaultvisibility=True, source='itu-#ti', ituinstitution=institution)
        top_items_count.save()
        metrics_to_plot.append(top_items_count)

    dates_processed = []
    for tc_scan in ItuScanLog.objects.filter(mode=2).order_by('time'):
        date = tc_scan.time.date()
        if date not in dates_processed:
            dates_processed.append(date)
            tc_count = ItuCollectionChartScan.objects.filter(scanlog=tc_scan,
                itucollection__institution=institution).count()
            traffic_to_plot.append(Traffic(date=date, count=tc_count, metric=top_collections_count))
    dates_processed = []
    for ti_scan in ItuScanLog.objects.filter(mode=3).order_by('time'):
        date = ti_scan.time.date()
        if date not in dates_processed:
            dates_processed.append(date)
            ti_count = ItuItemChartScan.objects.filter(scanlog=ti_scan, ituitem__institution=institution).count()
            traffic_to_plot.append(Traffic(date=date, count=ti_count, metric=top_items_count))

    if comments:
        from_itunes_u = Category.objects.get(description='From iTunes U')
        from_itunes_u.defaultvisibility = False
        categories_to_plot.append(from_itunes_u)
        for comment in comments:
            comment_to_plot = Comment(date=comment.date,
                source=(comment.itucollectionhistorical.name + ' - comment by ' + comment.source), detail=comment.detail
                , user_email='scan_itunes@manage.py', category=from_itunes_u)
            comments_to_plot.append(comment_to_plot)

    return render_to_response('monitors/itu_institution.html',
            {'error': error, 'message': message, 'institution': institution, 'comments': comments,
             'total_duration': total_duration, 'audio_duration': audio_duration, 'video_duration': video_duration, 'unknown_duration': unknown_duration,
             'audio_number': audio_number, 'video_number': video_number, 'total_number': total_number, 'other_number': other_number,
             'collections_number': collections_number,
             'collections_containing_movies_number': collections_containing_movies_number,
             'collections_not_containing_movies_number': collections_not_containing_movies_number,
             'collections': collections, 'current_collection_chartscans': current_collection_chartscans, 'current_item_chartscans': current_item_chartscans, 'top_five_tc_scanlogs': top_five_tc_scanlogs, 'recently_updated_collections': recently_updated_collections,
             'comments_to_plot': comments_to_plot,
             'metrics_to_plot': metrics_to_plot,
             'metric_textfiles': create_metric_textfiles(traffic_to_plot, metrics_to_plot),
             'categories_to_plot': categories_to_plot,
             'events': [],
             'chart': False,
             'tags': tags}, context_instance=RequestContext(request))


@login_required
def itu_institution_collections(request, institution_id):
    """Display all collections belonging to an institution."""
    message = ''
    error = ''
    institution = ItuInstitution.objects.get(id=int(institution_id))
    collections = ItuCollection.objects.filter(institution=institution).order_by('-latest__last_modified')
    collection_table = InstitutionalCollectionTable(collections, order_by=('-last_modified'))
    RequestConfig(request, paginate={'per_page': 100}).configure(collection_table)
    return render_to_response('monitors/itu_institution_collections.html',
            {'error': error, 'message': message, 'institution': institution,
             'collections': collections, 'collection_table': collection_table,
             'chart': False}, context_instance=RequestContext(request))


@login_required
def itu_genre(request, genre_id):
    """Display a genre."""
    message = ''
    error = ''
    genre = ItuGenre.objects.get(id=int(genre_id))
    comments = ItuComment.objects.filter(itucollectionhistorical__genre=genre)
    collections = ItuCollection.objects.filter(latest__genre=genre)
    try:
        total_duration = timedelta(microseconds=int(
            ItuItem.objects.filter(latest__genre=genre, latest__missing=None).aggregate(Sum('latest__duration'))[
            'latest__duration__sum']) * 1000)
    except:
        total_duration = timedelta(microseconds=0)
        message += 'WARNING: Couldn\'t calculate the total duration properly.'
    return render_to_response('monitors/itu_genre.html',
            {'error': error, 'message': message, 'genre': genre, 'comments': comments, 'collections': collections,
             'total_duration': total_duration},
        context_instance=RequestContext(request))


@login_required
def itu_scanlog(request, scanlog_id):
    """Display a scanlog, along with details of any relevant charts, modified items or modified collections."""
    message = ''
    error = ''
    scanlog = ItuScanLog.objects.get(id=int(scanlog_id))
    if scanlog.mode == 2: #Top collections scan
        return itu_top_collections(request, chartscan=scanlog)
    elif scanlog.mode == 3: #Top items scan
        return itu_top_items(request, chartscan=scanlog)
    elif scanlog.mode == 4: #Scan of institution lists
        error += 'No information is stored in the database about the results of scans of the lists of institutions. Perhaps try looking at the logfile scan_itunes.log?'
        return render_to_response('monitors/itu_scanlog.html', {'error': error, 'message': message, 'scanlog': scanlog},
            context_instance=RequestContext(request))
    elif scanlog.mode == 1: #Institutional scan
        new_collections = ItuCollection.objects.filter(latest__scanlog=scanlog, latest__version=1)
        updated_collections = ItuCollection.objects.filter(latest__scanlog=scanlog, latest__version__gt=1)
        missing_collections = ItuCollection.objects.filter(latest__missing=scanlog)
        new_items = ItuItem.objects.filter(latest__scanlog=scanlog, latest__version=1)
        updated_items = ItuItem.objects.filter(latest__scanlog=scanlog, latest__version__gt=1)
        missing_items = ItuItem.objects.filter(latest__missing=scanlog)

        return render_to_response('monitors/itu_scanlog.html',
                {'error': error, 'message': message, 'scanlog': scanlog, 'new_collections': new_collections,
                 'updated_collections': updated_collections, 'missing_collections': missing_collections,
                 'new_items': new_items, 'updated_items': updated_items, 'missing_items': missing_items},
            context_instance=RequestContext(request))
    else:
        error += 'Invalid scanlog mode. This is a bug, so please report it!'
        return render_to_response('monitors/itu_scanlog.html', {'error': error, 'message': message, 'scanlog': scanlog},
            context_instance=RequestContext(request))
