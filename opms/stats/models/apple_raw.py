from django.db import models
from core import LogFile
from apache_access import UserAgent, Rdns
#from monitors.models import
import django_tables2 as tables
from django_tables2.utils import A

class AppleRawLogEntry(models.Model):
    ACTION_TYPE_CHOICES = (
        (u'AutoDownload', u'Auto Download'),
        (u'Browse', u'Browse'),
        (u'Download', u'Download'),
        (u'DownloadAll', u'Download All'),
        (u'Stream', u'Stream'),
        (u'Subscribe', u'Subscribe'),
        (u'SubscriptionEnclosure', u'Subscription Enclosure'),
    )
    # Logfile this data was pulled from
    logfile = models.ForeignKey(LogFile)
    # Data from the logfile, a record per row
    artist_id = models.BigIntegerField()
    itunes_id = models.BigIntegerField()
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES, db_index=True)
    title = models.TextField()
    url = models.URLField(max_length=1000) # There are some really long urls in the data
    episode_id = models.BigIntegerField(blank=True, null=True)
    episode_title = models.TextField(blank=True, null=True)
    episode_type = models.CharField(max_length=20, blank=True, null=True)
    storefront = models.IntegerField()
    user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
    ipaddress = models.ForeignKey(Rdns, blank=True, null=True)
    timestamp = models.DateTimeField(db_index=True)
    user_id = models.TextField(blank=True, null=True)

    @property
    def action_type_string(self):
        for k,v in self.ACTION_TYPE_CHOICES:
            if k == self.action_type:
                return v
        return ''

    def __unicode__(self):
        try:
            return "{0} : {1} : {2} ({3})".format(
                self.timestamp,
                self.action_type_string,
                self.title,
                self.itunes_id
            )
        except UnicodeEncodeError:
            return "{UNICODE ERROR}"

    class Meta:
        app_label = 'stats'


class AppleRawLogDailySummary(models.Model):
    """
    A summary of data aggregated from the AppleRawLogEntry table, done for convenience and speed of processing and
    access.
    Lists a day (date) and then an integer count of the number of occurrences of each action type known to the system
    """
    updated = models.DateTimeField(auto_now=True)
    date = models.DateField(db_index=True)
    auto_download = models.IntegerField(default=0)
    browse = models.IntegerField(default=0)
    download = models.IntegerField(default=0)
    download_all = models.IntegerField(default=0)
    stream = models.IntegerField(default=0)
    subscribe = models.IntegerField(default=0)
    subscription_enclosure = models.IntegerField(default=0)

    def __unicode__(self):
        return "Summary for {0}".format(self.date)

    class Meta:
        app_label = 'stats'


class AppleRawLogDailyCollectionSummary(models.Model):
    """
    A summary of data aggregated from the AppleRawLogEntry table, done for convenience and speed of processing and
    access.
    Lists a day (date), itunes_id (collection), and then an integer count of the number of occurrences of each action
    type known to the
    system
    """
    updated = models.DateTimeField(auto_now=True)
    date = models.DateField(db_index=True)
    itunes_id = models.BigIntegerField()
    auto_download = models.IntegerField(default=0)
    browse = models.IntegerField(default=0)
    download = models.IntegerField(default=0)
    download_all = models.IntegerField(default=0)
    stream = models.IntegerField(default=0)
    subscribe = models.IntegerField(default=0)
    subscription_enclosure = models.IntegerField(default=0)

    def __unicode__(self):
        return "Summary for {0} - {1}".format(
            self.date,
            self.itunes_id
        )

    class Meta:
        app_label = 'stats'



#############
# Django Table Definitions
#############

class InstitutionalCollectionTable(tables.Table):
    """
    A table to enable pagination of all the collections belonging to a given institution,
    to enable stats browsing
    """
    name = tables.Column(accessor='latest.name',
                         order_by='latest.name',
                         verbose_name="Collection Name")
    collection_id = tables.LinkColumn('apple-raw-collection-detail', args=[A('latest.itu_id')],
                             accessor='latest.itu_id',
                             order_by='latest.itu_id',
                             verbose_name="Collection ID")
    contains_movies = tables.Column(accessor='latest.contains_movies',
                                    order_by='latest.contains_movies',
                                    verbose_name='Type')

    def render_contains_movies(self, value):
        if value:
            return 'Video'
        else:
            return 'Audio'

    class Meta:
        attrs = {'class': 'paleblue'}
        order_by_field = True