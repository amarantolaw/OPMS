from django.shortcuts import render_to_response
from django.http import  HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_unicode
from ffm.models import *
from opms import settings
import time
from os import path
from django.core.mail import send_mail


# Default FFM module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:FFM Homepage.")
    return render_to_response('ffm/base.html', {})


def summary_feeds(request):
    "List the Feedgroups and their associated feeds"
    summary_data = FeedGroup.objects.all().order_by('title')
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



@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        upload = request.FILES['Filedata']
#        print request.POST
#        print request.POST.get('description')
        description = smart_unicode(request.POST.get('description'), strings_only=True)
        print description
        file_path = settings.MEDIA_ROOT + 'podcastingNAS/'
        if path.ismount(file_path):
            # Adding timestamp as a way to avoid issue with existing filenames, and to give an easy sort option
            file_name = str(int(time.time()*1000)) + '-' + upload.name
            try:
#                print 'Attempting to write to:' + file_path + file_name
                dest = open(file_path + file_name, "wb+")
#                print 'Beginning write process'
                for block in upload.chunks():
                    dest.write(block)
                dest.close()
#                print 'Finished write process'

                # Send a notification email
                mail_text = 'The following file has been added to the UPLOADS folder on the Podcasting NAS: ' +\
                            file_name + '.\n It is described as: ' + description
#                print mail_text
                send_mail('[OPMS] File Upload Notification',
                          mail_text,
                          'opms@ives.oucs.ox.ac.uk',
                          ['carl.marshall@oucs.ox.ac.uk'],
                          fail_silently=False)
            except IOError:
                msg = 'IOError has been raised for ' + upload.name
                print msg
                return HttpResponseServerError(content=msg)
        else:
            msg = 'File upload failed for ' + upload.name + ' due to storage problems on the server'
            print msg
            return HttpResponseServerError(content=msg)

    response = HttpResponse()
    response.write("%s\r\n" % upload.name)
    return response