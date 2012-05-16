from django.db import models
from core import LogFile
from apache_access import UserAgent, Rdns

class AppleRawLogEntry(models.Model):
    # Logfile this data was pulled from
    logfile = models.ForeignKey(LogFile)
    # Data from the logfile, a record per row
    artist_id = models.BigIntegerField()
    itunes_id = models.BigIntegerField()
    action_type = models.CharField(max_length=30)
    title = models.TextField()
    url = models.URLField()
    episode_id = models.BigIntegerField(blank=True, null=True)
    episode_title = models.TextField(blank=True, null=True)
    episode_type = models.CharField(max_length=20, blank=True, null=True)
    storefront = models.IntegerField()
    user_agent = models.ForeignKey(UserAgent, blank=True, null=True)
    ipaddress = models.ForeignKey(Rdns, blank=True, null=True)
    timestamp = models.DateTimeField()
    user_id = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '%s:%s:%s' % (self.timestamp,self.action_type, self.title)

    class Meta:
        app_label = 'stats'