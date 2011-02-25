from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from stats.models import Track, Summary


# Default Stats module homepage
def index(request):
    return HttpResponse("Hello World. You're at the OPMS:Stats Homepage.")


def summary_index(request):
    # return HttpResponse("Summary Report")
    latest_summary_data = Summary.objects.all().order_by('-week_ending')
    return render_to_response('stats/reports/summary.html', {'latest_summary_data': latest_summary_data,})



def pr_report1(request, sort_by=''):
    # return HttpResponse("PR Report 1")
    if sort_by == 'count':
        listing = Track.objects.grouped_by_feed('1 DESC')
    else:
        listing = Track.objects.grouped_by_feed('2 ASC')

    return render_to_response('stats/reports/pr1.html',{'listing':listing})



def pr_report2(request, partial_guid):
    # return HttpResponse("PR Report 2 for '%s'." % partial_guid)
    listing = Track.objects.items_by_feed(partial_guid)
    summary = {}
    summary['count'] = len(listing)
    summary['total'] = 0
    summary['max']   = 0
    for row in listing:
        summary['total'] += row.count
        if row.count > summary.get('max'): 
            summary['max'] = row.count
    summary['avg'] = summary.get('total') // summary.get('count')

    return render_to_response('stats/reports/pr2.html',{'listing':listing, 'ref':partial_guid, 'summary':summary})



def pr_report3(request, guid):
    # return HttpResponse("PR Report 3 for '%s'." % guid)
    listing = Track.objects.all().filter(guid=guid).order_by('week_ending')
    return render_to_response('stats/reports/pr3.html',{'listing':listing, 'ref':guid})

