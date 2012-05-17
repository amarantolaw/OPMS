from django.db import models


# Quite possible to have multiple log file sources, use this as a lookup table
class LogFile(models.Model):
    SERVICE_NAME_CHOICES = (
        (u'mpoau', u'Media.podcasts Hosting'),
        (u'poau1', u'Podcasts.ox v1'),
        (u'poau-beta', u'beta.podcasts.ox.uk'),
        (u'oxitems', u'OxItems'),
        (u'mox', u'mobile.ox.ac.uk'),
        (u'itu', u'iTunes U v1'),
        (u'itu-psm', u'iTunes U PSM'),
        (u'itu-raw', u'iTunes U Raw Logfile'),
        )
    service_name = models.CharField("service name associated with this log", max_length=20, choices=SERVICE_NAME_CHOICES)
    file_name = models.TextField("file name")
    file_path = models.TextField("path to file")
    last_updated = models.DateTimeField("last updated") # Acts as date of import

    def __unicode__(self):
        return self.file_name

    class Meta:
        app_label = 'stats'