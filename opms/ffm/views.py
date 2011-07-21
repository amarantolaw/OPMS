from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from ffm.models import *


# Default FFM module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:FFM Homepage.")
    return render_to_response('ffm/base.html', {})


def summary_feeds(request):
    "List the Feedgroups and their associated feeds"
    summary_data = FeedGroup.objects.all().order_by('title')[:50]
    return render_to_response('ffm/feedgroups.html', {'summary_data': summary_data,})


def feed_detail(request, feed_id):
    "Show the results for a given feed"
    return HttpResponse("Hello World. You're at the FEED (" + str(feed_id) + ") DETAIL page.")


def summary_items(request):
    "List the Items and their associated files"
    summary_data = []
    return render_to_response('ffm/items.html', {'summary_data': summary_data,})


def item_detail(request, item_id):
    "Show the results for a given item"
    return HttpResponse("Hello World. You're at the ITEM (" + str(item_id) + ") DETAIL page.")


def summary_people(request):
    "List the People and their associated Feeds and Items"
    summary_data = []
    return render_to_response('ffm/people.html', {'summary_data': summary_data,})


def person_detail(request, person_id):
    "Show the results for a given person"
    return HttpResponse("Hello World. You're at the PERSON (" + str(person_id) + ") DETAIL page.")