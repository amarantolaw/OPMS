from django.db import models
from core import LogFile
from apache_access import UserAgent, Rdns

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
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    title = models.TextField()
    url = models.URLField(max_length=1000) # There are some really long urls in the data
    episode_id = models.BigIntegerField(blank=True, null=True)
    episode_title = models.TextField(blank=True, null=True)
    episode_type = models.CharField(max_length=20, blank=True, null=True)
    storefront = models.IntegerField()
    user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
    ipaddress = models.ForeignKey(Rdns, blank=True, null=True)
    timestamp = models.DateTimeField()
    user_id = models.TextField(blank=True, null=True)

    @property
    def action_type_string(self):
        for k,v in self.ACTION_TYPE_CHOICES:
            if k == self.action_type:
                return v
        return ''

    def __unicode__(self):
        return "{} : {} : {}".format(
            self.timestamp,
            self.action_type_string,
            self.title
        )

    class Meta:
        app_label = 'stats'