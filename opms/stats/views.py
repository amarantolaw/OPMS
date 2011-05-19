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
    fig = Figure()
    
    ax=fig.add_subplot(1,1,1)
    s = Summary.merged.all()
    
    x = matplotlib.numpy.arange(1,len(s))
    
    tracks = [int(item.total_track_downloads) for item in s]
    dates = [item.week_ending for item in s]
    
    
    numTests = len(s)
    ind = matplotlib.numpy.arange(numTests) # the x locations for the groups
    
    cols = ['red','orange','yellow','green','blue','purple','indigo']*10
    
    cols = cols[0:len(ind)]
    ax.bar(ind, tracks,color=cols)
    
    
    ax.set_xticks(ind + 0.5)
    ax.set_xticklabels(dates)
    
    
    ax.set_xlabel("Week")
    ax.set_ylabel("Downloads")
    
    #ax.set_xticklabels(names)
    
    title = u"Dynamically Generated Results Plot for Summary"
    ax.set_title(title)
    
    
    #ax.grid(True)
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    
    canvas.print_png(response)
    return response