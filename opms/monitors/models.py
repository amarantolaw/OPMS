from django.db import models
from django.utils.encoding import smart_unicode
import django_tables2 as tables
from django_tables2.utils import A
from datetime import date, timedelta
import math

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
    CHOICES = (
        (0,"Unknown"),
        (1,"Institutional Scan"),
        (2,"Top Collections Scan"),
        (3,"Top Downloads Scan"),
        (4,"Institutions Scan")
        )
    time = models.DateTimeField(auto_now_add=True)
    mode = models.SmallIntegerField(default=0, choices=CHOICES) # Zero = Unknown mode
    comments = models.TextField(null=True)
    complete = models.BooleanField(default=False)
    institution = models.ForeignKey("ItuInstitution", null=True, blank=True)

    def mode_string(self,CHOICES=CHOICES):
        for mc in CHOICES:
            if mc[0] == self.mode:
                return mc[1]
    class Meta:
        verbose_name = "iTunes U Scanlog"
        verbose_name_plural = "iTunes U Scanlogs"
    def __unicode__(self):
        return smart_unicode(str(self.time) + ': ' + self.mode_string())


class ItuGenre(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField("iTunes U ID") #666 codes for unknown.
    url = models.URLField()

    def collections_in_chart(self):
        latest_collections_chart = ItuScanLog.objects.filter(mode=2,complete=True).order_by('-time')[0]
        return ItuCollectionChartScan.objects.filter(scanlog=latest_collections_chart,itucollectionhistorical__genre=self).count()
    def items_in_chart(self):
        latest_items_chart = ItuScanLog.objects.filter(mode=3,complete=True).order_by('-time')[0]
        return ItuItemChartScan.objects.filter(scanlog=latest_items_chart,ituitemhistorical__genre=self).count()
    class Meta:
        verbose_name = "iTunes U Genre"
        verbose_name_plural = "iTunes U Genres"
    def __unicode__(self):
        return smart_unicode(self.name)

class ItuInstitution(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField("iTunes U ID")
    url = models.URLField()
    # Institutional Stats - to be done as methods

    def collections_in_chart(self):
        latest_collections_chart = ItuScanLog.objects.filter(mode=2,complete=True).order_by('-time')[0]
        return ItuCollectionChartScan.objects.filter(scanlog=latest_collections_chart,itucollection__institution=self).count()
    def items_in_chart(self):
        latest_items_chart = ItuScanLog.objects.filter(mode=3,complete=True).order_by('-time')[0]
        return ItuItemChartScan.objects.filter(scanlog=latest_items_chart,ituitem__institution=self).count()
    class Meta:
        verbose_name = "iTunes U Institution"
        verbose_name_plural = "iTunes U Institutions"
    def __unicode__(self):
        return smart_unicode(self.name)

class ItuItem(models.Model):
    institution = models.ForeignKey(ItuInstitution)
    latest = models.ForeignKey("ItuItemHistorical", null=True, default=None, related_name="latest_historical_item_record")

    def find_latest(self):
        print('WARNING: Using find_latest will be inefficient! Don\'t do it!')
        hrecords = ItuItemHistorical.objects.filter(ituitem=self).order_by('version')
        return hrecords[len(hrecords) - 1]
    def find_original(self):
        print('WARNING: Using find_original will be inefficient! Don\'t do it!')
        hrecords = ItuItemHistorical.objects.filter(ituitem=self).order_by('version')
        return hrecords[0]

    class Meta:
        verbose_name = "iTunes U Item"
        verbose_name_plural = "iTunes U Items"
    def __unicode__(self):
        try:
            return smart_unicode(self.latest.name)
        except:
            return u'Unattached absolute item record.'

class ItuCollection(models.Model):
    institution = models.ForeignKey(ItuInstitution)
    latest = models.ForeignKey("ItuCollectionHistorical", null=True, default=None, related_name="latest_historical_collection_record")

    def find_latest(self):
        print('WARNING: Using find_latest will be inefficient! Don\'t do it!')
        hrecords = ItuCollectionHistorical.objects.filter(itucollection=self).order_by('version')
        return hrecords[len(hrecords) - 1]
    def find_original(self):
        hrecords = ItuCollectionHistorical.objects.filter(itucollection=self).order_by('version')
        return hrecords[0]

    class Meta:
        verbose_name = "iTunes U Collection"
        verbose_name_plural = "iTunes U Collections"
    def __unicode__(self):
        try:
            return smart_unicode(self.latest.name)
        except:
            return u'Unattached absolute collection record.'

class ItuCollectionHistorical(models.Model):
    name = models.CharField(max_length=255)
    itu_id = models.IntegerField("iTunes U ID", null=True) # Historical records don't have this :-(
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

    itucollection = models.ForeignKey(ItuCollection, verbose_name="Collection")

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
            n = l.next()
        return l

    def average_rating(self):
        rating_sum = 0.0
        n = 0.0
        for rating in ItuRating.objects.filter(itucollectionhistorical=self):
            rating_sum += rating.stars * rating.count
            n += rating.count
        if n > 0.0:
            return round(rating_sum/n,2)
        else:
            return None

    def rating_checksum(self): #Generate a checksum from all the ratings attached to this historical collection record to allow easy (and slightly faster) comparisons.
        checksum = 0
        for rating in ItuRating.objects.filter(itucollectionhistorical=self):
            checksum += pow(10,rating.stars) + (rating.count/1000000000)
        return checksum

    class Meta:
        verbose_name = "iTunes U Historical Record of Collection"
        verbose_name_plural = "iTunes U Historical Records of Collections"
    def save(self): #Update absolute record so that the last-saved historical record is the latest record.
        super(ItuCollectionHistorical, self).save()
        self.itucollection.latest = self
        self.itucollection.save()
    def __unicode__(self):
        return smart_unicode('%s, %s' % (self.name,str(self.scanlog.time)))


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
    def duration_datetime(self):
        return timedelta(microseconds=self.duration * 1000)
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

    ituitem = models.ForeignKey(ItuItem, verbose_name="Item")

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
            n = l.next()
        return l

    class Meta:
        verbose_name = "iTunes U Historical Record of Item"
        verbose_name_plural = "iTunes U Historical Records of Items"
    def save(self): #Update absolute record so that the last-saved historical record is the latest record.
        super(ItuItemHistorical, self).save()
        self.ituitem.latest = self
        self.ituitem.save()
    def __unicode__(self):
        return smart_unicode('%s, %s' % (self.name,str(self.scanlog.time)))


class ItuItemChartScan(models.Model):
    date = models.DateTimeField() # Date of chart scan - a duplicate of that in scanlog but will be efficient.
    position = models.SmallIntegerField()
    ituitemhistorical = models.ForeignKey(ItuItemHistorical, verbose_name="Historical Item Record")
    ituitem = models.ForeignKey(ItuItem, verbose_name="Item")
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('%s: %s' % (self.position, self.ituitemhistorical.name))


class ItuCollectionChartScan(models.Model):
    date = models.DateTimeField() # Date of chart scan - a duplicate of that in scanlog but will be efficient.
    position = models.SmallIntegerField()
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record")
    itucollection = models.ForeignKey(ItuCollection, verbose_name="Collection")
    # updated = models.DateTimeField(auto_now=True) # Update timestamp
    scanlog = models.ForeignKey(ItuScanLog)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('%s: %s' % (self.position, self.itucollectionhistorical.name))

class ItuRating(models.Model):
    stars = models.PositiveIntegerField(choices=((1,'*'),(2,'**'),(3,'***'),(4,'****'),(5,'*****')))
    count = models.PositiveIntegerField()
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record")
    def __unicode__(self):
        return smart_unicode('%s people rated %s with %s stars.' % (self.count, self.itucollectionhistorical.name, self.stars))

class ItuComment(models.Model):
    stars = models.PositiveIntegerField(choices=((1,'*'),(2,'**'),(3,'***'),(4,'****'),(5,'*****')))
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record")
    date = models.DateField(null=True, blank=True)
    detail = models.CharField(max_length=10000)
    source = models.CharField(max_length=100)
    ituinstitution = models.ForeignKey(ItuInstitution, verbose_name="Institution")

    class Meta:
        verbose_name = "iTunes U Comment"
        verbose_name_plural = "iTunes U Comments"
    def __unicode__(self):
        return smart_unicode(self.detail)

class InstitutionalCollectionTable(tables.Table):
    name = tables.LinkColumn('itu-collection', args=[A('pk')], accessor='latest.name', order_by='latest.name')
    contains_movies = tables.Column(accessor='latest.contains_movies', order_by='latest.contains_movies', verbose_name='Type')
    version = tables.Column(accessor='latest.version', order_by='latest.version')
    last_modified = tables.Column(accessor='latest.last_modified', order_by='latest.last_modified')
    genre = tables.LinkColumn('itu-genre', args=[A('latest.genre.pk')], accessor='latest.genre.name', order_by='latest.genre.name', verbose_name='Genre')

    def render_contains_movies(self, value):
        if value:
            return 'Video'
        else:
            return 'Audio'

    class Meta:
        attrs = {'class': 'paleblue'}
        order_by_field = True