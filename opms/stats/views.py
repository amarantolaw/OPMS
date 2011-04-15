from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import Summary


# Default Stats module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:Stats Homepage.")
    return render_to_response('base.html', {})


def summary_index(request):
    # return HttpResponse("Summary Report")
    latest_summary_data = Summary.objects.all().order_by('-week_ending')
    return render_to_response('stats/reports/summary.html', {'latest_summary_data': latest_summary_data,})



