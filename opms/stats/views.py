from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import Summary

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg


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
    plt.plot([1,2,3,4])
    plt.ylabel('some numbers')

    canvas = FigureCanvasAgg(plt.show())    
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close()
    
    return response