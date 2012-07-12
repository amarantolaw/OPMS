from django.shortcuts import render_to_response, get_object_or_404
from feedback.models import Metric, Traffic, Category, Comment, Event
from stats.models import AppleWeeklySummary
from django.db.models import Max, Min
from django.template import RequestContext
import datetime, time

DAYS = range(1,32,1)
MONTHS = ('January','February','March','April','May','June','July','August','September','October','November','December')
YEARS = range(2000,datetime.date.today().year + 1,1)
HOURS = range(0,24,1)
MINUTES = range(0,60,1)
SECONDS = range(0,60,1)

def index(request):
    metrics_to_plot = Metric.objects.all()
    categories_to_plot = Category.objects.all()
    traffic_to_plot = list(Traffic.objects.all())

    try:
        #Import Apple's download metric, but just for one-time use - don't save in db.
        ttd_metric = Metric.objects.filter(description="Total track downloads")[0] #Force the metrics to be queried outside the for loops below: vital to save about 5s of CPU time.
        browse_metric = Metric.objects.filter(description="Browse")[0]
        for w in AppleWeeklySummary.merged.all():
            for d in range(0,7,1):
                traffic_to_plot.append(Traffic(date=w.week_beginning + datetime.timedelta(d), count=w.total_track_downloads, metric=ttd_metric))
                traffic_to_plot.append(Traffic(date=w.week_beginning + datetime.timedelta(d), count=w.browse, metric=browse_metric))
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
        'events': Event.objects.all()
    }, context_instance=RequestContext(request))

def comment_add(request,edit=False,comment=None):
    "Adds a new comment to the database. Optionally, it may replace the comment instead."
    categories = Category.objects.all()
    error = ''
    if edit:
        default_comment = comment
    else:
        default_comment = Comment(date=datetime.date.today(), time=datetime.datetime.now().time, source='', detail='', category=Category.objects.filter(pk=1)[0])

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    if added == True:
        try:
            new_date = datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
            new_time = datetime.time(int(request.POST['hour']), int(request.POST['minute']), int(request.POST['second']))
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
                if edit == True:
                    new_comment = comment
                    new_comment.date,new_comment.time,new_comment.source,new_comment.detail,new_comment.category = new_date,new_time,new_source,new_detail,new_category
                else:
                    new_comment = Comment(date=new_date, time=new_time, source=new_source, detail=new_detail, category=new_category)
                new_comment.save()
                default_comment = new_comment
            except:
                error += ' Failed to act on the database.'

    return render_to_response('feedback/comment_add.html',
            {'categories': categories,
            'DAYS': DAYS,
            'MONTHS': MONTHS,
            'YEARS': YEARS,
            'HOURS': HOURS,
            'MINUTES': MINUTES,
            'SECONDS': SECONDS,
            'error': error,
            'added': added,
            'edit': edit,
            'comment': default_comment},
        context_instance=RequestContext(request))

def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, pk=int(comment_id)) #Find the appropriate comment object from comment_id.
    return render_to_response('feedback/comment_detail.html', {'comment': comment}, context_instance=RequestContext(request))

def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=int(comment_id)) #Find the appropriate comment object from comment_id.
    return comment_add(request,True,comment)

def comment_delete(request, comment_id):
    error = ''
    comment = get_object_or_404(Comment, pk=int(comment_id)) #Find the appropriate comment object from comment_id.
    try:
        comment.delete()
    except:
        error += 'Could not delete comment.'
    return render_to_response('feedback/comment_delete.html', {'error': error}, context_instance=RequestContext(request))

def event_add(request,edit=False,event=None):
    "Adds a new event to the database. Optionally, it may replace the event instead."
    categories = Category.objects.all()
    error = ''
    if edit:
        default_event = event
    else:
        default_event = Event(date=datetime.date.today(), title='', detail='', category=Category.objects.filter(pk=1)[0])

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    if added == True:
        try:
            new_date = datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
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
#            try:
                if edit == True:
                    new_event = event
                    new_event.date,new_event.title,new_event.detail,new_event.category = new_date,new_title,new_detail,new_category
                else:
                    new_event = Event(date=new_date, title=new_title, detail=new_detail, category=new_category)
                new_event.save()
                default_event = new_event
#            except:
#                error += ' Failed to act on the database.'

    return render_to_response('feedback/event_add.html',
            {'categories': categories,
             'DAYS': DAYS,
             'MONTHS': MONTHS,
             'YEARS': YEARS,
             'error': error,
             'added': added,
             'edit': edit,
             'event': default_event},
        context_instance=RequestContext(request))

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=int(event_id)) #Find the appropriate event object from event_id.
    return render_to_response('feedback/event_detail.html', {'event': event}, context_instance=RequestContext(request))

def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=int(event_id)) #Find the appropriate event object from event_id.
    return event_add(request,True,event)

def event_delete(request, event_id):
    error = ''
    event = get_object_or_404(Event, pk=int(event_id)) #Find the appropriate event object from event_id.
    try:
        event.delete()
    except:
        error += 'Could not delete event.'
    return render_to_response('feedback/event_delete.html', {'error': error}, context_instance=RequestContext(request))