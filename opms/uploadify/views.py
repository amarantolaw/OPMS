from django.http import HttpResponse
import django.dispatch

upload_received = django.dispatch.Signal(providing_args=['data'])

def upload(request, *args, **kwargs):
    if request.method == 'POST':
        if request.FILES:
            upload_received.send(sender='uploadify', data=request.FILES['Filedata'])
    return HttpResponse('True')


def upload_received_handler(sender, data, **kwargs):
     if file:
          # process the received file here
          print data.file

upload_recieved.connect(upload_received_handler, dispatch_uid='opms.uploadify.upload_received')