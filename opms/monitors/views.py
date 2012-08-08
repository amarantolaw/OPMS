import random
from datetime import timedelta
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_safe
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.db.models import Q, F, Sum
import settings
from opms.monitors.models import URLMonitorURL, URLMonitorScan
from feedback.models import Metric, Traffic, Category, Comment, Event
from feedback.views import create_metric_textfiles
from monitors.models import ItuCollectionChartScan, ItuCollectionHistorical, ItuCollection, ItuItemChartScan, ItuItemHistorical, ItuItem, ItuScanLog, ItuGenre, ItuInstitution, ItuRating, ItuComment
#import pylab
#import numpy as np
#import matplotlib
#import matplotlib.dates
#import matplotlib.ticker as ticker
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure


# Default Monitors module homepage
#@require_safe(request)
def index(request):
#    t = loader.get_template('monitors/base.html')
#    return HttpResponse(t.render())
    # return HttpResponse("Hello World. You're at the OPMS:Monitors Homepage.")
    return render_to_response('monitors/base.html', {}, context_instance=RequestContext(request))

######
# URL Monitoring Subviews
######

def urlmonitoring_summary(request):
    "Show the results for a url monitoring"
    # List the URLS and the number of scans for that URL
    summary_listing = []

    urls = URLMonitorURL.objects.all().order_by('-active', 'url')
    # TODO: Take out the hard coded HTML from here and put that in the template where it belongs!
    for url in urls:
        if url.active:
            summary_listing.append(
                '<a href="./url-' + str(url.id) + '">' + str(url.url) + '</a> (' +\
                str(url.urlmonitorscan_set.count()) + ')'
            )
        else:
            summary_listing.append(
                '<strong>[INACTIVE]</strong> <a href="./url-' + str(url.id) + '">' + str(url.url) + '</a> (' +\
                str(url.urlmonitorscan_set.count()) + ')'
            )
    return render_to_response('monitors/url_summary.html', {'summary_listing': summary_listing, },
        context_instance=RequestContext(request))


def urlmonitoring_task(request, task_id):
    "Show the results for a url monitoring of a specific task"
    scan_data = URLMonitorScan.objects.filter(task__id__exact=task_id).select_related().order_by('-url__url',
        'iteration')
    return render_to_response('monitors/url_summary.html', {'scan_data': scan_data, 'task_id': task_id},
        context_instance=RequestContext(request))


def urlmonitoring_url(request, url_id):
    "Show the results for a url monitoring of specific url"
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

def itu_home(request):
    """The iTunes U Monitoring home page."""
    message = ''
    error = ''
    this_institution = ItuInstitution.objects.get(name=settings.YOUR_INSTITUTION)
    return render_to_response('monitors/itu_home.html',
            {'error': error, 'message': message, 'this_institution': this_institution},
        context_instance=RequestContext(request))


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
    chartrows = ItuCollectionChartScan.objects.filter(scanlog=chartscan)
    return render_to_response('monitors/itu_top_collections.html',
            {'error': error, 'message': message, 'chartrows': chartrows, 'scanlog': chartscan},
        context_instance=RequestContext(request))


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


def itu_collections(request):
    """Show a clickable list of all collections."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_collections.html', {'error': error, 'message': message},
        context_instance=RequestContext(request))


def itu_items(request):
    """Show a clickable list of all items."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_items.html', {'error': error, 'message': message},
        context_instance=RequestContext(request))


def itu_institutions(request, institutions=[]):
    """Show a clickable list of all institutions."""
    message = ''
    error = ''
    if not institutions:
        try:
            institutions = ItuInstitution.objects.all()
        except:
            error += 'Failed to query the database for institutions.'
    if not institutions:
        error += 'Couldn\'t find any institutions. Perhaps you haven\'t run scan_itunes --mode 4 yet?'
    return render_to_response('monitors/itu_institutions.html',
            {'error': error, 'message': message, 'institutions': institutions},
        context_instance=RequestContext(request))


def itu_genres(request):
    """Show a clickable list of all genres."""
    message = ''
    error = ''
    try:
        genres = ItuGenre.objects.all()
    except:
        error += 'Failed to query the database for genres.'
    if not genres:
        error += 'Couldn\'t find any genres. Perhaps you haven\'t run scan_itunes yet?'
    return render_to_response('monitors/itu_genres.html', {'error': error, 'message': message, 'genres': genres},
        context_instance=RequestContext(request))


def itu_scanlogs(request):
    """Show a clickable list of all scanlogs."""
    message = ''
    error = ''
    scanlogs = ItuScanLog.objects.all()
    if not scanlogs:
        error += 'Can\'t find any scanlogs. Perhaps you haven\'t run scan_itunes yet?'
    return render_to_response('monitors/itu_scanlogs.html', {'error': error, 'message': message, 'scanlogs': scanlogs},
        context_instance=RequestContext(request))


def itu_collection(request, collection_id):
    """Display an absolute record of a collection."""
    message = ''
    error = ''
    collection = ItuCollection.objects.get(id=int(collection_id))
    chartrecords = ItuCollectionChartScan.objects.filter(itucollection=collection).order_by('date')
    items = ItuItem.objects.filter(latest__series__itucollection=collection)
    total_duration = timedelta(microseconds = int(items.aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
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
                fillcolor='#FFFFFF', mouseover=True, defaultvisibility=True, source='itunes-chart')
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
             'comments': comments, 'items': items, 'total_duration': total_duration, 'ratings': ratings, 'average_rating': average_rating,
             'comments_to_plot': comments_to_plot,
             'metrics_to_plot': metrics_to_plot,
             'metric_textfiles': create_metric_textfiles(traffic_to_plot, metrics_to_plot),
             'categories_to_plot': categories_to_plot,
             'events': [],
             'chart': True}, context_instance=RequestContext(request), )


def itu_item(request, item_id):
    """Display an absolute record of an item."""
    message = ''
    error = ''
    item = ItuItem.objects.get(id=int(item_id))
    chartrecords = ItuItemChartScan.objects.filter(ituitem=item)

    metrics_to_plot = []
    traffic_to_plot = []
    categories_to_plot = []
    comments_to_plot = []
    if chartrecords:
        #Get or create a suitable Metric
        metrics = Metric.objects.filter(description=item.latest.name)
        if len(metrics) == 0:
            random_colour = '#' + str(random.randint(222222, 999999))
            top_items_position = Metric(description=item.latest.name, linecolor=random_colour, fillcolor='#FFFFFF',
                mouseover=True, defaultvisibility=True, source='itunes-chart')
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
             'chart': True},
        context_instance=RequestContext(request))


def itu_institution(request, institution_id):
    """Display an institution."""
    message = ''
    error = ''
    institution = ItuInstitution.objects.get(id=int(institution_id))
    comments = ItuComment.objects.filter(ituinstitution=institution)
    collections = ItuCollection.objects.filter(institution=institution)

    total_duration = timedelta(microseconds = int(ItuItem.objects.filter(institution=institution).aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)

    metrics_to_plot = []
    traffic_to_plot = []
    categories_to_plot = []
    comments_to_plot = []
    for collection in collections:
        chartrecords = ItuCollectionChartScan.objects.filter(itucollection=collection).order_by('date')
        if chartrecords:
            #Get or create a suitable Metric
            try:
                top_collections_position = Metric.objects.get(description=collection.latest.name)
                metrics_to_plot.append(top_collections_position)
            except:
                random_colour = '#' + str(random.randint(222222, 999999))
                top_collections_position = Metric(description=collection.latest.name, linecolor=random_colour,
                    fillcolor='#FFFFFF', mouseover=True, defaultvisibility=True, source='itunes-chart')
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
                traffic_to_plot.append(Traffic(date=date, count=(-1 * chartrecords_day[0].position), metric=top_collections_position))

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
            {'error': error, 'message': message, 'institution': institution, 'comments': comments, 'total_duration': total_duration,
             'collections': collections,
             'comments_to_plot': comments_to_plot,
             'metrics_to_plot': metrics_to_plot,
             'metric_textfiles': create_metric_textfiles(traffic_to_plot, metrics_to_plot),
             'categories_to_plot': categories_to_plot,
             'events': [],
             'chart': True}, context_instance=RequestContext(request))


def itu_genre(request, genre_id):
    """Display a genre."""
    message = ''
    error = ''
    genre = ItuGenre.objects.get(id=int(genre_id))
    comments = ItuComment.objects.filter(itucollectionhistorical__genre=genre)
    collections = ItuCollection.objects.filter(latest__genre=genre)
    total_duration = timedelta(microseconds = int(ItuItem.objects.filter(latest__genre=genre).aggregate(Sum('latest__duration'))['latest__duration__sum']) * 1000)
    return render_to_response('monitors/itu_genre.html',
            {'error': error, 'message': message, 'genre': genre, 'comments': comments, 'collections': collections, 'total_duration': total_duration},
            context_instance=RequestContext(request))


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
