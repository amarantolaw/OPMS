from django.http import Http404, HttpResponse
from django.views.decorators.http import require_safe
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from opms.monitors.models import URLMonitorURL, URLMonitorScan
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
    return render_to_response('monitors/url_summary.html', {'summary_listing': summary_listing,}, context_instance=RequestContext(request))


def urlmonitoring_task(request, task_id):
    "Show the results for a url monitoring of a specific task"
    scan_data = URLMonitorScan.objects.filter(task__id__exact=task_id).select_related().order_by('-url__url', 'iteration')
    return render_to_response('monitors/url_summary.html', {'scan_data': scan_data,'task_id':task_id}, context_instance=RequestContext(request))


def urlmonitoring_url(request, url_id):
    "Show the results for a url monitoring of specific url"
    # Limit to the last 3 days' worth of scans (10 scans * 4 times an hour * 24 hours * 3 days)
    scan_data = URLMonitorScan.objects.filter(url__id__exact=url_id).select_related().order_by('-time_of_request')[:2880]
    return render_to_response('monitors/url_summary.html', {'scan_data': scan_data,'url_id':url_id}, context_instance=RequestContext(request))



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
    """Show a mock version of the iTunes U home page."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_home.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_top_collections(request):
    """Show the most recent top collections chart."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_top_collections.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_top_items(request):
    """Show the most recent top items chart."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_top_items.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_collections(request):
    """Show a clickable list of all collections."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_collections.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_items(request):
    """Show a clickable list of all items."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_items.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_institutions(request):
    """Show a clickable list of all institutions."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_institutions.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_genres(request):
    """Show a clickable list of all genres."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_genres.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_scanlogs(request):
    """Show a clickable list of all scanlogs."""
    message = ''
    error = ''
    return render_to_response('monitors/itu_scanlogs.html', {'error': error,'message':message}, context_instance=RequestContext(request))

def itu_collection(request, collection_id):
    """Display an absolute record of a collection."""
    message = ''
    error = ''
    collection = ItuCollection.objects.get(id=int(collection_id))
    return render_to_response('monitors/itu_collection.html', {'error': error,'message':message,'collection':collection}, context_instance=RequestContext(request))

def itu_item(request, item_id):
    """Display an absolute record of an item."""
    message = ''
    error = ''
    item = ItuItem.objects.get(id=int(item_id))
    return render_to_response('monitors/itu_item.html', {'error': error,'message':message,'item':item}, context_instance=RequestContext(request))

def itu_institution(request, institution_id):
    """Display an institution."""
    message = ''
    error = ''
    institution = ItuInstitution.objects.get(id=int(institution_id))
    return render_to_response('monitors/itu_institution.html', {'error': error,'message':message,'institution':institution}, context_instance=RequestContext(request))

def itu_genre(request, genre_id):
    """Display a genre."""
    message = ''
    error = ''
    genre = ItuGenre.objects.get(id=int(genre_id))
    return render_to_response('monitors/itu_genre.html', {'error': error,'message':message,'genre':genre}, context_instance=RequestContext(request))

def itu_scanlog(request, scanlog_id):
    """Display a scanlog, along with details of any relevant charts, modified items or modified collections."""
    message = ''
    error = ''
    scanlog = ItuScanLog.objects.get(id=int(scanlog_id))
    return render_to_response('monitors/itu_scanlog.html', {'error': error,'message':message,'scanlog':scanlog}, context_instance=RequestContext(request))