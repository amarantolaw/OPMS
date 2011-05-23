from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import Summary

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter


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



def graph_apple_summary_totals(request):
    fig = Figure(figsize=(10,7.5), dpi=100, facecolor='white', edgecolor='white')
    ax = fig.add_subplot(1,1,1)
    
    s = Summary.merged.all()
    x = matplotlib.numpy.arange(1,len(s))
    
    tracks = [int(item.total_track_downloads) for item in s]
    dates = [item.week_number for item in s]
    
    numTests = len(s)
    ind = matplotlib.numpy.arange(numTests/2) # the x locations for the groups
    
    cols = ['blue','blue','blue']*100
    
    cols = cols[0:len(ind)]
    ax.bar(ind, tracks,color=cols)
    
    ax.set_xticks(ind + 0.5)
    ax.set_xticklabels(dates, rotation=270, size='x-small', lod=True)
    
    ax.set_xlabel("Week Number")
    ax.set_ylabel("Downloads")
    
    title = u"Apple Weekly Downloads and Cumulative Total"
    ax.set_title(title)
    
    # ax.grid(True)
    ax.annotate('iTU PSM launch', xy=(105,400000), xytext=(70,450000), arrowprops=dict(facecolor='black', shrink=0.05),)
    ax.annotate('iTunes 9.0 released', xy=(53,80000), xytext=(40,150000), arrowprops=dict(facecolor='black', shrink=0.05),)
    ax.annotate('Oxford on iTunes U launch', xy=(4,80000), xytext=(20,250000), arrowprops=dict(facecolor='black', shrink=0.05),)
    
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response