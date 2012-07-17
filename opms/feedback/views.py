from django.shortcuts import render_to_response, get_object_or_404
from feedback.models import Metric, Traffic, Category, Comment, Event
from stats.models import AppleWeeklySummary
from django.db.models import Max, Min
from django.template import RequestContext
import settings
import datetime, time
from dateutil.parser import parse
import imaplib
from email import message_from_string
from email.parser import Parser

def index(request, error='', message=''):
    metrics_to_plot = Metric.objects.all()
    categories_to_plot = Category.objects.all()
    traffic_to_plot = list(Traffic.objects.all())

    try:
        #Import Apple weekly summary metrics, but just for one-time use - don't save in db.
        appleweekly_metrics = []
        for m in metrics_to_plot:
            if m.source == 'appleweekly':
                appleweekly_metrics.append(m)

        append = traffic_to_plot.append #Avoid re-calling the .append function in the middle of all those loops.
        for w in AppleWeeklySummary.merged.all():
            for d in range(0,7,1):
                dat = w.week_beginning + datetime.timedelta(d)
                for m in appleweekly_metrics:
                    for field in AppleWeeklySummary._meta._fields():        #This grabs a list of field objects from the model specified as part of the stats app
                        if field.verbose_name == m.description:             #Verbose name is specified as ("verbose_name") in stats/models/apple_summary.py
                            append(Traffic(date=dat, count=w.__dict__[field.name], metric=m))
    except:
        print('WARNING: Can\'t find any Apple summary data. Have you imported it?')

    if traffic_to_plot:
        start = traffic_to_plot[0].date
        stop = start
        for t in traffic_to_plot:
            d = t.date
            if d < start:
                start = d
            if d > stop:
                stop = d

        x = start
        date_range = [start]
        while x != stop:
            x += datetime.timedelta(days=1)
            date_range.append(x)
    else:
        date_range = []
        print('WARNING: No traffic to plot. Did you put any in the database?')

    #Timeplot is designed to take in CSV text files, so build a string containing one:
    metrics_textfile = ""
    for d in date_range:
        metrics_textfile += str(d)
        for m in metrics_to_plot:
            t_exists = False    #Will become true IFF we have a traffic datum for this d and this m.
            for t in traffic_to_plot:
                if t.date == d:
                    if t.metric == m:
                        metrics_textfile += ',' + str(t.count)
                        t_exists = True
            if t_exists == False:
                metrics_textfile += ',0' #Replace missing values with '0' for the sake of the chart.
        metrics_textfile += '\\n'

    #NOTE: We do not need to handle the temporal range of comments and events since this is done automatically by Timeplot.

    return render_to_response('feedback/index.html', {
        'metrics_to_plot': metrics_to_plot,
        'metrics_textfile': metrics_textfile,
        'categories_to_plot': categories_to_plot,
        'comments': Comment.objects.all(),
        'error': error,
        'message': message,
        'events': Event.objects.all()
    }, context_instance=RequestContext(request))

def comment_add(request,comment=None, error='', message=''):
    "Adds a new comment to the database. Optionally, it may replace the comment instead."
    categories = Category.objects.all()
    default_comment = Comment(date=datetime.date.today(), time=datetime.datetime.now().time, source='', detail='', category=Category.objects.filter(description='Default')[0])

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    if added == True:
        try:
            new_date = parse(request.POST['date'], dayfirst=True)
            new_time = parse(request.POST['time'])
        except:
            error += ' Datetime invalid or not specified.'

        try:
            new_detail = request.POST['detail']
            if new_detail == '':
                error += ' Comment text is blank.'
        except:
            error += ' No comment text provided.'

        try:
            new_source = request.POST['source']
            if new_source == '':
                error += ' Source is blank.'
        except:
            error += ' No comment source provided.'

        try:
            new_category = Category.objects.filter(pk=int(request.POST['category_id']))[0] #The [0] is OK since the fact that category_id is a primary key ensures that the array has only length 1.
        except:
            error += ' Category invalid or nonexistent.'

        if error == '':
            try:
                new_comment = Comment(date=new_date, time=new_time, source=new_source, detail=new_detail, category=new_category)
                new_comment.save()
                message += 'Your comment was added to the database.'
                default_comment = new_comment
            except:
                error += ' Failed to act on the database.'
    try:
        action = request.POST['action']
    except:
        action = 'add'

    if action == 'saveandaddanother' or action == 'add':
        return render_to_response('feedback/comment_add.html',
            {'categories': categories,
            'error': error,
            'message': message,
            'added': added,
            'comment': default_comment},
            context_instance=RequestContext(request))
    elif action == 'save':
        return index(request, error=error, message=message)
    else:
        error += 'Invalid submit action requested.'
        return render_to_response('feedback/comment_add.html',
                {'categories': categories,
                 'error': error,
                 'comment': comment,
                 'added': added,
                 'message': message,
                 'comment': default_comment},
            context_instance=RequestContext(request))

def comment_detail(request, comment_id, error='', message=''):
    comment = get_object_or_404(Comment, pk=int(comment_id)) #Find the appropriate comment object from comment_id.
    return render_to_response('feedback/comment_detail.html', {'comment': comment, 'error': error, 'message': message}, context_instance=RequestContext(request))

def event_add(request,event=None, error='', message=''):
    "Adds a new event to the database. Optionally, it may replace the event instead."
    categories = Category.objects.all()

    try:
        widget = bool(request.POST['widget'])
    except:
        widget = False
    if widget == True:
        url = request.POST['url']
        detail = request.POST['description']
        title = request.POST['title']
        try:
            timestamp = request.POST['timestamp']
            datetimestamp = parse(timestamp)
        except:
            datetimestamp = datetime.datetime.now()
            print('WARNING: Widget returned datetime we couldn\'t process. Defaulting to today.')
        print('Autocompleting form from widget... ' + url + str(timestamp) + title)
        default_event = Event(date=datetimestamp.date(), title=title, detail=detail, category=Category.objects.filter(description='Found on the internet')[0])
    else:
        default_event = Event(date=datetime.date.today(), title='', detail='', category=Category.objects.filter(description='Default')[0])

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    if added == True:
        try:
            new_date = parse(request.POST['date'], dayfirst=True)
        except:
            error += ' Date invalid or not specified.'

        try:
            new_detail = request.POST['detail']
            if new_detail == '':
                error += ' Event text is blank.'
        except:
            error += ' No event text provided.'

        try:
            new_title = request.POST['title']
            if new_title == '':
                error += ' Title is blank.'
        except:
            error += ' No event title provided.'

        try:
            new_category = Category.objects.filter(pk=int(request.POST['category_id']))[0] #The [0] is OK since the fact that category_id is a primary key ensures that the array has only length 1.
        except:
            error += ' Category invalid or nonexistent.'

        if error == '':
            try:
                new_event = Event(date=new_date, title=new_title, detail=new_detail, category=new_category)
                new_event.save()
                message += 'Your event was added to the database.'
                default_event = new_event
            except:
                error += 'Failed to act on the database.'
    try:
        action = request.POST['action']
    except:
        action = 'add'

    if action == 'saveandaddanother' or action == 'add':
        return render_to_response('feedback/event_add.html',
            {'categories': categories,
             'error': error,
             'added': added,
             'message': message,
             'event': default_event},
            context_instance=RequestContext(request))
    elif action == 'save':
        return index(request, error=error, message=message)
    else:
        error += 'Invalid submit action requested.'
        return render_to_response('feedback/event_add.html',
                {'categories': categories,
                 'error': error,
                 'added': added,
                 'message': message,
                 'event': default_event},
            context_instance=RequestContext(request))

def event_detail(request, event_id, error='', message=''):
    event = get_object_or_404(Event, pk=int(event_id)) #Find the appropriate event object from event_id.
    return render_to_response('feedback/event_detail.html', {'event': event, 'error': error, 'message': message}, context_instance=RequestContext(request))

def email(request, error='', message=''):
    output = ''
    try:
        host = settings.EMAIL_HOST
        imap = settings.EMAIL_IMAP
        eddress = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        port = settings.EMAIL_PORT
        prefix = settings.EMAIL_SUBJECT_PREFIX
    except:
        error += 'ERROR: You haven\'t configured e-mail in settings.py.'
    if error == '':
        mail = imaplib.IMAP4_SSL(imap)
        mail.login(eddress, password)
        mail.select("inbox")
        result, data = mail.uid('search', None, "ALL")
        uids = data[0].split()
        emails = []
        for u in uids:
            result, data = mail.uid('fetch', u, '(RFC822)')
            raw_email = data[0][1]
            email_message = message_from_string(raw_email)
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    output += 'PART: ' + str(part.get_payload()) + '\n'
    return render_to_response('feedback/email.html', {'error': error, 'message': message, 'output': output}, context_instance=RequestContext(request))