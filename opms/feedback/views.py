from django.shortcuts import render_to_response, get_object_or_404
from opms.utils import debug
from feedback.models import Tag, Metric, Traffic, Category, Comment, Event
from monitors.models import ItuCollectionChartScan, ItuCollectionHistorical, ItuCollection, ItuItemChartScan, ItuItemHistorical, ItuItem, ItuScanLog, ItuGenre, ItuInstitution, ItuRating, ItuComment
from stats.models import AppleWeeklySummary
from django.db.models import Max, Min
from django.template import RequestContext
from django.core.exceptions import ValidationError
import settings
import datetime, time
from dateutil.parser import parse
import imaplib
from email import message_from_string
from email.parser import Parser


def index(request, error='', message='', tag=None, tag_id=None, comment_id=None, event_id=None, metric_id=None):
    if tag:
        metrics_to_plot = Metric.objects.filter(tags=tag)
    else:
        metrics_to_plot = Metric.objects.filter(source='appleweekly')

    traffic_to_plot = []
    for metric in metrics_to_plot:
        metric_traffic = list(Traffic.objects.filter(metric=metric))
        if metric_traffic:
            traffic_to_plot.append(metric_traffic)

    try:
        #Import Apple weekly summary metrics, but just for one-time use - don't save in db.
        append = traffic_to_plot.append #Avoid re-calling the .append function in the middle of all those loops.
        for w in AppleWeeklySummary.merged.all():
            for m in metrics_to_plot:
                for field in AppleWeeklySummary._meta._fields():             #This grabs a list of field objects from the model specified as part of the stats app
                    if field.verbose_name == m.appleweeklyfield:             #Verbose name is specified as ("verbose_name") in stats/models/apple_summary.py
                        append(Traffic(date=w.week_beginning, count=w.__dict__[field.name], metric=m))
    except:
        debug.onscreen('WARNING: Can\'t find any Apple summary data. Have you imported it?')

    #NOTE: We do not need to handle the temporal range of comments and events since this is done automatically by Timeplot.

    categories_to_plot = Category.objects.all()
    from_itunes_u = categories_to_plot.get(description='From iTunes U')
    #Create comments in the feedback database if they don't already exist.
    for itu_comment in ItuComment.objects.filter(ituinstitution__name = 'Oxford University'):
        comment = Comment(
            date=itu_comment.date,
            time=datetime.time(0,0,0),
            source=itu_comment.itucollectionhistorical.name + ' - comment by ' + itu_comment.source,
            detail=itu_comment.detail,
            user_email='scan_itunes@manage.py',
            moderated=True,
            category=from_itunes_u,
            itu_source=itu_comment
        )
        if Comment.objects.filter(detail=itu_comment.detail).count() > 0:
            pass
        else:
            comment.save()
    if tag:
        comments_to_plot = Comment.objects.filter(moderated=True,tags=tag)
        events_to_plot = Event.objects.filter(moderated=True,tags=tag)
    else:
        comments_to_plot = Comment.objects.filter(moderated=True)
        events_to_plot = Event.objects.filter(moderated=True)

    return render_to_response('feedback/index.html', {
        'metrics_to_plot': metrics_to_plot,
        'metric_textfiles': create_metric_textfiles(traffic_to_plot,metrics_to_plot),
        'categories_to_plot': categories_to_plot,
        'comments_to_plot': comments_to_plot,
        'events': events_to_plot,
        'chart': True,
        'error': error,
        'message': message,
        'tag': tag, 'tag_id': tag_id, 'tags': Tag.objects.all(), 'comment_id': comment_id, 'event_id': event_id, 'metric_id': metric_id,
    }, context_instance=RequestContext(request))


def create_metric_textfiles(traffic_to_plot,metrics_to_plot):
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
        debug.onscreen('WARNING: No traffic to plot. Did you put any in the database?')

    #Timeplot is designed to take in CSV text files, so build one as a string for each metric:
    metric_textfiles = {}
    for m in metrics_to_plot:
        metric_textfile_strlist = []
        append = metric_textfile_strlist.append
        for d in date_range:
            sd = str(d)
            for t in traffic_to_plot:
                if t.date == d:
                    if t.metric == m:
                        append('%s%s%s' % (sd,',',str(t.count)))
        metric_textfiles[m.id] = '\\n'.join(metric_textfile_strlist)
    return metric_textfiles


def comment_add(request,comment=None, error='', message=''):
    "Adds a new comment to the database. Optionally, it may replace the comment instead."
    categories = Category.objects.all()
    error_fields=[]
    default_comment = Comment(date=datetime.date.today(), time=datetime.datetime.now().time, source='', detail='', category=Category.objects.filter(description='Events')[0], user_email='')

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    try:
        action = request.POST['action']
    except:
        action = 'add'

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

        try:
            new_user_email = request.POST['user_email']
            if new_user_email == '':
                error += ' You haven\'t provided your e-mail address.'
        except:
            error += ' No user e-mail address provided.'

        if error == '':
            try:
                new_comment = Comment(date=new_date, time=new_time, source=new_source, detail=new_detail, category=new_category, user_email=new_user_email)
                new_comment.full_clean()
                try:
                    new_comment.save()
                    message += 'Your comment was added to the database.'
                except:
                    error += 'Failed to access the database.'
            except ValidationError as ve:
                for k in ve.message_dict.keys():
                    error_fields.append(k)
                    for m in ve.message_dict[k]:
                        error += m + ' '
                default_comment = new_comment

    if action == 'saveandaddanother' or action == 'add' or error != '':
        return render_to_response('feedback/comment_add.html',
            {'categories': categories,
            'error': error,
            'error_fields': error_fields,
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
                 'error_fields': error_fields,
                 'added': added,
                 'message': message,
                 'comment': default_comment},
            context_instance=RequestContext(request))


def event_add(request,event=None, error='', message=''):
    "Adds a new event to the database. Optionally, it may replace the event instead."
    categories = Category.objects.all()
    error_fields=[]

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
            debug.onscreen('WARNING: Widget returned datetime we couldn\'t process. Defaulting to today.')
        debug.onscreen('Autocompleting form from widget... ' + url + str(timestamp) + title)
        default_event = Event(date=datetimestamp.date(), title=title, detail=detail, category=Category.objects.filter(description='Found on the internet')[0], user_email='')
    else:
        default_event = Event(date=datetime.date.today(), title='', detail='', category=Category.objects.filter(description='Events')[0], user_email='')

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    try:
        action = request.POST['action']
    except:
        action = 'add'

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

        try:
            new_user_email = request.POST['user_email']
            if new_user_email == '':
                error += ' You haven\'t provided your e-mail address.'
        except:
            error += ' No user e-mail address provided.'

        if error == '':
            new_event = Event(date=new_date, title=new_title, detail=new_detail, category=new_category, user_email=new_user_email)
            try:
                new_event.full_clean()
                try:
                    new_event.save()
                    message += 'Your event was added to the database.'
                except:
                    error += 'Failed to access the database.'
            except ValidationError as ve:
                for k in ve.message_dict.keys():
                    error_fields.append(k)
                    for m in ve.message_dict[k]:
                        error += m + ' '
                default_event = new_event

    if action == 'saveandaddanother' or action == 'add' or error != '':
        return render_to_response('feedback/event_add.html',
            {'categories': categories,
             'error': error,
             'added': added,
             'message': message,
             'error_fields': error_fields,
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
                 'error_fields': error_fields,
                 'event': default_event},
            context_instance=RequestContext(request))


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


def tags(request, error='', message='', tag_id=None):
    tags = Tag.objects.all()
    return render_to_response('feedback/tags.html', {
        'error': error,
        'message': message,
        'tags': tags, 'tag_id': tag_id,
        }, context_instance=RequestContext(request))


def tag_create(request, error='', message=''):
    error_fields=[]
    default_tag = Tag(name='',title='',color='#')

    try:
        added = bool(request.POST['add'])
    except:
        added = False
    try:
        action = request.POST['action']
    except:
        action = 'add'

    if added == True:
        try:
            new_name = request.POST['name']
            if new_name == '':
                error += ' Name is blank.'
            else:
                default_tag.name = new_name
        except:
            error += ' No name provided.'
        try:
            new_title = request.POST['title']
            if new_title == '':
                error += ' Title is blank.'
            else:
                default_tag.title = new_title
        except:
            error += ' No title provided.'
        try:
            new_color = request.POST['color']
            default_tag.color = new_color
            if len(new_color) != 7:
                error += ' Invalid colour - hex colours are 7 characters long, including the #.'
        except:
            error += ' No colour provided.'

        if error == '':
            try:
                new_tag = Tag(name=new_name, title=new_title, color=new_color)
                new_tag.full_clean()
                try:
                    new_tag.save()
                    message += 'Your tag was added to the database.'
                    default_tag = Tag(name='',title='',color='#')
                except:
                    error += 'Failed to access the database.'
            except ValidationError as ve:
                for k in ve.message_dict.keys():
                    error_fields.append(k)
                    for m in ve.message_dict[k]:
                        error += m + ' '

    if action == 'saveandaddanother' or action == 'add' or error != '':
        return render_to_response('feedback/tag_create.html',
                {'error': error,
                 'error_fields': error_fields,
                 'message': message,
                 'added': added,
                 'default_tag': default_tag},
            context_instance=RequestContext(request))
    elif action == 'save':
        return tags(request, error=error, message=message)
    else:
        error += 'Invalid submit action requested.'
        return render_to_response('feedback/tag_create.html',
                {'error': error,
                 'error_fields': error_fields,
                 'added': added,
                 'message': message,
                 'default_tag': default_tag},
            context_instance=RequestContext(request))


def tag_view(request, tag_id, error='', message=''):
    tag = Tag.objects.get(id=tag_id)
    return index(request=request, error=error, message=message, tag=tag, tag_id=tag_id)


def tag_delete(request, tag_id, error='', message=''):
    tag = Tag.objects.get(id=tag_id)
    try:
        name = tag.name
        tag.delete()
        message += tag.name + ' deleted.'
    except:
        error += 'Failed to delete tag ' + tag_id + '.'
    return tags(request=request, error=error, message=message, tag_id=tag_id)


def tag_comment(request, tag_id, comment_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        comment = Comment.objects.get(id=comment_id)
    except:
        error += 'Couldn\'t retrieve comment ' + comment_id + '.'

    if tag in comment.tags.all():
        error += 'This comment has already been tagged.'

    if not error:
        try:
            comment.tags.add(tag)
            message += 'Tagged comment ' + str(comment.id) + ' with ' + tag.name + '.'
        except:
            error += 'Couldn\'t tag comment.'
    return index(request=request, error=error, message=message, comment_id=comment_id, tag_id=tag_id)


def untag_comment(request, tag_id, comment_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        comment = Comment.objects.get(id=comment_id)
    except:
        error += 'Couldn\'t retrieve comment ' + comment_id + '.'

    if tag not in comment.tags.all():
        error += 'This comment isn\'t tagged with this tag.'

    if not error:
        try:
            comment.tags.remove(tag)
        except:
            error += 'Couldn\'t remove tag from comment.'
    return index(request=request, error=error, message=message, comment_id=comment_id, tag_id=tag_id)


def tag_event(request, tag_id, event_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        event = Event.objects.get(id=event_id)
    except:
        error += 'Couldn\'t retrieve event ' + event_id + '.'

    if tag in event.tags.all():
        error += 'This event has already been tagged.'

    if not error:
        try:
            event.tags.add(tag)
            message += 'Tagged event ' + str(event.id) + ' with ' + tag.name + '.'
        except:
            error += 'Couldn\'t tag event.'
    return index(request=request, error=error, message=message, event_id=event_id, tag_id=tag_id)


def untag_event(request, tag_id, event_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        event = Event.objects.get(id=event_id)
    except:
        error += 'Couldn\'t retrieve event ' + event_id + '.'

    if tag not in event.tags.all():
        error += 'This event isn\'t tagged with this tag.'

    if not error:
        try:
            event.tags.remove(tag)
        except:
            error += 'Couldn\'t remove tag from comment.'
    return index(request=request, error=error, message=message, event_id=event_id, tag_id=tag_id)


def tag_metric(request, tag_id, metric_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        metric = Metric.objects.get(id=metric_id)
    except:
        error += 'Couldn\'t retrieve metric ' + metric_id + '.'

    if tag in metric.tags.all():
        error += 'This metric has already been tagged.'

    if not error:
        try:
            metric.tags.add(tag)
            message += 'Tagged metric ' + str(metric.id) + ' with ' + tag.name + '.'
        except:
            error += 'Couldn\'t tag metric.'
    return index(request=request, error=error, message=message, metric_id=metric_id, tag_id=tag_id)


def untag_metric(request, tag_id, metric_id, error='', message=''):
    try:
        tag = Tag.objects.get(id=tag_id)
    except:
        error += 'Couldn\'t retrieve tag ' + tag_id + '.'
    try:
        metric = Metric.objects.get(id=metric_id)
    except:
        error += 'Couldn\'t retrieve metric ' + metric_id + '.'

    if tag not in metric.tags.all():
        error += 'This metric isn\'t tagged with this tag.'

    if not error:
        try:
            metric.tags.remove(tag)
        except:
            error += 'Couldn\'t remove tag from metric.'
    return index(request=request, error=error, message=message, metric_id=metric_id, tag_id=tag_id)