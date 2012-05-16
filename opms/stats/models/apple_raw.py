from django.db import models
from core import LogFile
from apache_access import UserAgent, Rdns
from django.utils.encoding import smart_unicode
from datetime import date

class AppleRawLogEntry(models.Model):
    # Logfile this data was pulled from
    logfile = models.ForeignKey(LogFile)
    # Data from the logfile, a record per row
    artist_id = models.BigIntegerField()
    itunes_id = models.BigIntegerField()
    action_type = models.CharField(max_length=30)
    title = models.TextField()
    url = models.URLField()
    episode_id = models.BigIntegerField()
    episode_title = models.TextField()
    episode_type = models.CharField(max_length=20)
    storefront = models.BigIntegerField()
    user_agent = models.ForeignKey(UserAgent)
    ipaddress = models.ForeignKey(Rdns)
    timestamp = models.DateTimeField()
    user_id = models.TextField()

    def __unicode__(self):
        return '%s:%s:%s' % (self.timestamp,self.action_type, self.title)