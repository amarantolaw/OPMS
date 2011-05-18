from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse


# Default FFM module homepage
def index(request):
    # return HttpResponse("Hello World. You're at the OPMS:FFM Homepage.")
    return render_to_response('ffm/base.html', {})
    #Comment test part 3
