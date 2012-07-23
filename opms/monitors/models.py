from django.db import models
from django.utils.encoding import smart_unicode
from datetime import date

#TODO: Add this to south, eventually...
# Remember: this application is managed by Django South so when you change this file, do the following:
# python manage.py schemamigration monitors --auto
# python manage.py migrate monitors

######
# URL Monitoring Task/Metrics
######

#The following models are used in testing a series of urls (Targets) on a periodic basis (Tasks) and
#recording some simple metrics on the results.
class URLMonitorTask(models.Model):
    comment = models.CharField(max_length=200, default="No Comment Set")
    completed = models.BooleanField(default=False)

    def iterations(self): # Count the number of Scans related to this task
        return self.urlmonitorscan_set.count()

    def __unicode__(self):
        if self.completed:
            return smart_unicode(self.comment + " has completed")
        else:
            return smart_unicode(self.comment + " has not yet run")


class URLMonitorURL(models.Model):
    url = models.URLField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return smart_unicode(self.url)


class URLMonitorScan(models.Model):
    task = models.ForeignKey(URLMonitorTask)
    url = models.ForeignKey(URLMonitorURL)
    iteration = models.SmallIntegerField()
    status_code = models.SmallIntegerField(null=True)
    ttfb = models.FloatField(null=True)
    ttlb = models.FloatField(null=True)
    time_of_request = models.DateTimeField(null=True)

    def __unicode__(self):
        return smart_unicode(str(date.strftime(self.time_of_request,"%Y-%m-%d %H:%i:%s")) + ": " +\
                             str(self.url.url) + " #" + str(self.iteration) + ": TTFB:" + str(self.ttfb))



######
# iTU Store analysis classes
######

class ItuScanLog(models.Model):
    MODE_CHOICES = (
        (0,"Unknown"),
        (1,"Institutional Scan"),
        (2,"Top Collections Scan"),
        (3,"Top Downloads Scan")
        )
    starting_url = models.URLField(null=True)
    time = models.DateTimeField(auto_now_add=True)
    mode = models.SmallIntegerField(default=0, choices=MODE_CHOICES) # Zero = Unknown mode
    comments = models.TextField(null=True)
    complete = models.BooleanField(default=False)

    @property
    def mode_string(self):
        return self.MODE_CHOICES.get(self.mode,'')

    def __unicode__(self):
        return smart_unicode('Scanlog: %s=%s' % (self.name,self.url))


class ItuGenre(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField()
    url = models.URLField()

    def __unicode__(self):
        return smart_unicode('Genre: %s=%s' % (self.name,self.url))

class ItuInstitution(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField()
    url = models.URLField()
    # Institutional Stats - to be done as methods

    def __unicode__(self):
        return smart_unicode('Institution: %s=%s' % (self.name,self.url))

class ItuItem(models.Model):
    institution = models.ForeignKey(ItuInstitution)
    def __unicode__(self):
        return smart_unicode('Item: %s' % (self.id))

class ItuCollection(models.Model):
    institution = models.ForeignKey(ItuInstitution)
    def __unicode__(self):
        return smart_unicode('Collection: %s' % (self.id))

class ItuCollectionHistorical(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField(null=True) # Historical records don't have this :-(
    img170 = models.URLField(null=True)
    url = models.URLField(null=True) # Historical records don't have this :-(
    language = models.CharField(max_length=100, null=True) # Historical records don't have this
    last_modified = models.DateField(null=True) # Historical records don't have this
    genre = models.ForeignKey(ItuGenre, null=True) # Historical records don't have this)
    institution = models.ForeignKey(ItuInstitution)
    contains_movies = models.BooleanField()
    # Series Stats - to be done as methods
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog, related_name='ich_scanlog')
    missing = models.ForeignKey(ItuScanLog, null=True, related_name='missing_ich_scanlog') # The scanlog when we first detected this was missing.
    # Eventual link to an FFM feed (not Feedgroup because iTU only does feeds)
    #    feed = models.ForeignKey(ffm_models.Feed, null=True)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    itucollection = models.ForeignKey(ItuCollection)

    version = models.PositiveIntegerField(default=1)
    previous = models.ForeignKey('self', null=True, blank=True)

    def next(self):
        try:
            n = ItuCollectionHistorical.objects.filter(previous=self)[0]
            return n
        except:
            return None
    def original(self):
        p = self.previous
        o = self
        while p:
            o = p
            p = p.previous
        return o
    def latest(self):
        l = self
        n = self.next()
        while n:
            l = n
            n = l.next
        return l
    def __unicode__(self):
        return smart_unicode('Series: %s=%s' % (self.name,self.url))


class ItuItemHistorical(models.Model):
    name = models.CharField(max_length=255) # Labelled as "songName" in plist
    itu_id = models.IntegerField() # Labelled as "itemId" in plist
    url = models.URLField()
    genre = models.ForeignKey(ItuGenre)
    institution = models.ForeignKey(ItuInstitution)
    series = models.ForeignKey(ItuCollectionHistorical)
    # anonymous = models.BooleanField()
    artist_name = models.CharField(max_length=255) # Length rather arbitrary
    # buy_params = models.URLField()
    description = models.TextField()
    duration = models.IntegerField(null=True)
    explicit = models.BooleanField()
    feed_url = models.URLField()
    file_extension = models.CharField(max_length=20)
    # is_episode = models.BooleanField()
    kind = models.CharField(max_length=100)
    long_description = models.TextField()
    playlist_id = models.IntegerField()
    playlist_name = models.CharField(max_length=255)
    popularity = models.FloatField()
    preview_length = models.IntegerField()
    preview_url = models.URLField()
    # price = models.FloatField()
    # price_display = models.CharField()
    rank = models.IntegerField()
    release_date = models.DateTimeField()
    # s = models.IntegerField()
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog, related_name='iih_scanlog')
    missing = models.ForeignKey(ItuScanLog, null=True, related_name='missing_iih_scanlog') # The scanlog when we first detected this was missing.
    # Eventual link to an FFM FileInFeed, because all we really know is which FileInFeed should have been used here
    #    fileinfeed = models.ForeignKey(ffm_models.FileInFeed, null=True)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    ituitem = models.ForeignKey(ItuItem)

    version = models.PositiveIntegerField(default=1)
    previous = models.ForeignKey('self', null=True, blank=True)

    def next(self):
        try:
            n = ItuItemHistorical.objects.filter(previous=self)[0]
            return n
        except:
            return None
    def original(self):
        p = self.previous
        o = self
        while p:
            o = p
            p = p.previous
        return o
    def latest(self):
        l = self
        n = self.next()
        while n:
            l = n
            n = l.next
        return l
    def __unicode__(self):
        return smart_unicode('Item: %s=%s' % (self.name, self.url))


class ItuItemChartScan(models.Model):
    date = models.DateTimeField() # Date of chart scan
    position = models.SmallIntegerField()
    ituitemperiodic = models.ForeignKey(ItuItemHistorical)
    ituitem = models.ForeignKey(ItuItem)
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('Download@%s: %s (%s)' % (self.position, self.item.name, self.item.itu_id))


class ItuCollectionChartScan(models.Model):
    date = models.DateTimeField() # Date of chart scan
    position = models.SmallIntegerField()
    itucollectionperiodic = models.ForeignKey(ItuCollectionHistorical)
    itucollection = models.ForeignKey(ItuCollection)
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('Collection@%s: %s (%s)' % (self.position, self.series.name, self.series.itu_id))