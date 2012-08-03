# Load a CSV file containing comments exported from podcasts.ox.ac.uk
# Author: Steven Legg
# Last Edited: 08-03-2012
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from collections import deque
from feedback.models import Metric, Traffic, Category, Comment, Event
import datetime


class Command(BaseCommand):
    help = 'Load a CSV file containing comments exported from podcasts.ox.ac.uk.'

    def handle(self, filepath='', **options):
        # Some basic checking
        if filepath == '':
            raise CommandError("Please specify a file to import.")
        try:
            file = open(filepath)
        except:
            raise CommandError("Could not open file.")
        try:
            file_text = file.read()
        except:
            raise CommandError("Could not read file.")
        file.close()
        lines = deque(file_text.split(
            '\n/')) #New rows begin with this; we can't just use either \n or / because they both appear in comments...
        comments = []
        lines.popleft() #Remove header row
        for line in lines:
            comment = {}
            comma_separated_chunks = line.split(',')
            unix_timestamp = int(comma_separated_chunks.pop()) #Throw away a long number
            try:
                comment['date'] = datetime.datetime.fromtimestamp(unix_timestamp).date()
                comment['time'] = datetime.datetime.fromtimestamp(unix_timestamp).time()
            except:
                raise CommandError('Failed to convert timestamp ' + str(unix_timestamp) + ' to a date and a time.')
            comma_separated_chunks.pop() #Throw away 'Let us know'
            comma_separated_chunks = deque(comma_separated_chunks)
            comment['feed'] = comma_separated_chunks.popleft()
            throw_away = ''
            while throw_away != 'feedback':
                try:
                    throw_away = comma_separated_chunks.popleft() #Throw away everything else up to and including 'feedback'
                except KeyError:
                    raise CommandError("One line lacks the string 'feedback'.")
            comment['detail'] = ','.join(comma_separated_chunks)
            if comment['detail']:
                if not Comment.objects.filter(detail=comment['detail'],
                    source=comment['feed']): #Have we seen this comment before? If so, don't add it to comments.
                    comments.append(comment)
            else:
                print('Ignoring blank comment about feed ' + comment['feed'] + '.')

        for comment in comments:
            try:
                category = Category.objects.get(description='podcasts.ox.ac.uk')
            except:
                raise CommandError("Could not find podcasts.ox.ac.uk category.")
            try:
                comment_to_save = Comment(date=comment['date'], time=comment['time'], source=comment['feed'], detail=comment['detail'],
                    user_email='load_drupal_comments@manage.py', category=category)
                comment_to_save.save()
            except:
                raise CommandError("Could not save comment \"" + str(comment) + '\".')
