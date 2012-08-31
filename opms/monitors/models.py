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
    """A time when scan_itunes was run."""
    CHOICES = (
        (0,"Unknown"),
        (1,"Institutional Scan"),
        (2,"Top Collections Scan"),
        (3,"Top Downloads Scan"),
        (4,"Institutions Scan")
        )
    time = models.DateTimeField(auto_now_add=True,unique=True, help_text="The datetime when scan_itunes was run.")
    mode = models.SmallIntegerField(default=0, choices=CHOICES, help_text="The mode of the scan (Zero = Unknown mode).")
    comments = models.TextField(null=True, help_text="Field to record anything about this scan that needs to be recorded manually.")
    complete = models.BooleanField(default=False, help_text="Whether the scan completed or not - an incomplete scan could either be still in progress or have crashed.")
    institution = models.ForeignKey("ItuInstitution", null=True, blank=True, help_text="If the scan was a mode 1 scan, then this is the institution scanned. Otherwise this is null.")

    def mode_string(self,CHOICES=CHOICES):
        """Returns a string describing the mode of the scan eg. 'Institutions Scan'"""
        for mc in CHOICES:
            if mc[0] == self.mode:
                return mc[1]
    class Meta:
        verbose_name = "iTunes U Scanlog"
        verbose_name_plural = "iTunes U Scanlogs"
    def __unicode__(self):
        return smart_unicode(str(self.time) + ': ' + self.mode_string())


class ItuGenre(models.Model):
    name = models.CharField(max_length=255,unique=True, help_text="The name of the genre.")
    itu_id = models.IntegerField("iTunes U ID", help_text="The genre's ID according to iTunes U; 666 codes for unknown.")
    url = models.URLField(help_text="The URL of the genre's page on iTunes U")

    def collections_in_chart(self):
        """Returns the number of collections in this genre currently in the top collections chart."""
        scans = ItuScanLog.objects.filter(mode=2,complete=True)
        if scans.exists():
            latest_collections_chart = scans.order_by('-time')[0]
            return ItuCollectionChartScan.objects.filter(scanlog=latest_collections_chart,itucollectionhistorical__genre=self).count()
        else:
            return 0
    def items_in_chart(self):
        """Returns the number of items in this genre currently in the top items chart."""
        scans = ItuScanLog.objects.filter(mode=3,complete=True)
        if scans.exists():
            latest_items_chart = scans.order_by('-time')[0]
            return ItuItemChartScan.objects.filter(scanlog=latest_items_chart,ituitemhistorical__genre=self).count()
        else:
            return 0
    class Meta:
        verbose_name = "iTunes U Genre"
        verbose_name_plural = "iTunes U Genres"
    def __unicode__(self):
        return smart_unicode(self.name)


class ItuInstitution(models.Model):
    """An academic institution with podcasts on iTunes U."""
    name = models.CharField(max_length=255,unique=True, help_text="The name of this institution.")
    itu_id = models.IntegerField("iTunes U ID", help_text="The ID of this institution according to iTunes U.")
    url = models.URLField(help_text="The URL of this institution's page on iTunes U.")

    def collections_in_chart(self):
        """Returns the number of collections belonging to this institution currently in the top collections chart."""
        scans = ItuScanLog.objects.filter(mode=2,complete=True)
        if scans.exists():
            latest_collections_chart = scans.order_by('-time')[0]
            return ItuCollectionChartScan.objects.filter(scanlog=latest_collections_chart,itucollection__institution=self).count()
        else:
            return 0
    def items_in_chart(self):
        """Returns the number of items belonging to this institution currently in the top items chart."""
        scans = ItuScanLog.objects.filter(mode=3,complete=True)
        if scans.exists():
            latest_items_chart = scans.order_by('-time')[0]
            return ItuItemChartScan.objects.filter(scanlog=latest_items_chart,ituitem__institution=self).count()
        else:
            return 0
    class Meta:
        verbose_name = "iTunes U Institution"
        verbose_name_plural = "iTunes U Institutions"
    def __unicode__(self):
        return smart_unicode(self.name)

class ItuItem(models.Model):
    """An individual podcast."""
    institution = models.ForeignKey(ItuInstitution, help_text="The institution this item belongs to.")
    latest = models.ForeignKey("ItuItemHistorical", null=True, default=None, related_name="latest_historical_item_record", unique=True, help_text="The latest historical record of this item.")

    def find_latest(self):
        """Explicitly looks up the latest historical record of this item (Shouldn't be used except in repairing database corruption.)"""
        print('WARNING: Using find_latest will be inefficient! Don\'t do it!')
        hrecords = ItuItemHistorical.objects.filter(ituitem=self).order_by('version')
        return hrecords[len(hrecords) - 1]
    def find_original(self):
        """Explicitly looks up the original historical record of this item."""
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
    """A series of podcasts, as categorised on iTunes U. Oxford University's video and audio podcasts are in separate collections, but this isn't true for most institutions."""
    institution = models.ForeignKey(ItuInstitution, help_text="The institution this collection belongs to.")
    latest = models.ForeignKey("ItuCollectionHistorical", null=True, default=None, related_name="latest_historical_collection_record", unique=True, help_text="The latest historical record of this collection.")

    def find_latest(self):
        """Explicitly looks up the latest historical record of this collection (Shouldn't be used except in repairing database corruption.)"""
        print('WARNING: Using find_latest will be inefficient! Don\'t do it!')
        hrecords = ItuCollectionHistorical.objects.filter(itucollection=self).order_by('version')
        return hrecords[len(hrecords) - 1]
    def find_original(self):
        """Explicitly looks up the original historical record of this collection."""
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
    """A snapshot of a collection at a give point in time."""
    name = models.CharField(max_length=255, help_text="The name of the collection at this time.")
    itu_id = models.IntegerField("iTunes U ID", null=True, help_text="The ID of this collection, according to iTunes U.") # Historical records don't have this :-(
    img170 = models.URLField(null=True, help_text="The URL of the 170x170 icon for this collection.")
    url = models.URLField(null=True, help_text="The URL of this collection at this time on iTunes U.") # Historical records don't have this :-(
    language = models.CharField(max_length=100, null=True, help_text="The language this collection is presented in.") # Historical records don't have this
    last_modified = models.DateField(null=True, help_text="The last date on which this collection was modified according to iTunes U.") # Historical records don't have this
    genre = models.ForeignKey(ItuGenre, null=True, help_text="The genre this collection is in.") # Historical records don't have this)
    institution = models.ForeignKey(ItuInstitution, help_text="The institution this collection belongs to.")
    contains_movies = models.BooleanField(help_text="Whether the collection contained movies at this time.")
    scanlog = models.ForeignKey(ItuScanLog, related_name='ich_scanlog', help_text="The scanlog on which this record was created.")
    missing = models.ForeignKey(ItuScanLog, null=True, related_name='missing_ich_scanlog', help_text="The scanlog when we first detected this was missing.")
    # Eventual link to an FFM feed (not Feedgroup because iTU only does feeds)
    #    feed = models.ForeignKey(ffm_models.Feed, null=True)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    itucollection = models.ForeignKey(ItuCollection, verbose_name="Collection", help_text="The absolute record of this collection.")

    version = models.PositiveIntegerField(default=1, help_text="The version number of this historical record.")
    previous = models.ForeignKey('self', null=True, blank=True, help_text="The previous historical record of this collection.")

    def next(self):
        """Find the next historical record of this collection."""
        try:
            n = ItuCollectionHistorical.objects.filter(previous=self)[0]
            return n
        except:
            return None
    def original(self):
        """Find the original historical record of this collection."""
        p = self.previous
        o = self
        while p:
            o = p
            p = p.previous
        return o
    def latest(self):
        """Find the latest historical record of this collection."""
        l = self
        n = self.next()
        while n:
            l = n
            n = l.next()
        return l

    def average_rating(self):
        """Calculate the average rating from all the ratings given for this historical collection record."""
        rating_sum = 0.0
        n = 0.0
        for rating in ItuRating.objects.filter(itucollectionhistorical=self):
            rating_sum += rating.stars * rating.count
            n += rating.count
        if n > 0.0:
            return round(rating_sum/n,2)
        else:
            return None

    def rating_checksum(self):
        """Generate a checksum from all the ratings attached to this historical collection record to allow easy (and slightly faster) comparisons."""
        checksum = 0
        for rating in ItuRating.objects.filter(itucollectionhistorical=self):
            checksum += pow(10,rating.stars) + (rating.count/1000000000)
        return checksum

    class Meta:
        verbose_name = "iTunes U Historical Collection Record"
        verbose_name_plural = "iTunes U Historical Collection Records"
    def save(self):
        """Update absolute record so that the last-saved historical record is the latest record."""
        super(ItuCollectionHistorical, self).save()
        self.itucollection.latest = self
        self.itucollection.save()
    def __unicode__(self):
        return smart_unicode('%s, %s' % (self.name,str(self.scanlog.time)))


class ItuItemHistorical(models.Model):
    """A snapshot of a particular podcast at a particular time."""
    name = models.CharField(max_length=255, help_text="The name of the podcast at this time.") # Labelled as "songName" in plist
    itu_id = models.IntegerField(help_text="The ID of this item on iTunes U.") # Labelled as "itemId" in plist
    url = models.URLField(help_text="The URL of this item on iTunes U.")
    genre = models.ForeignKey(ItuGenre, help_text="The genre of this item.")
    institution = models.ForeignKey(ItuInstitution, help_text="The institution to which this item belongs.")
    series = models.ForeignKey(ItuCollectionHistorical, help_text="The historical collection record this historical item record is in.")
    artist_name = models.CharField(max_length=255, help_text="The artist(s) who made this podcast.") # Length rather arbitrary
    description = models.TextField(help_text="A description of this item.")
    duration = models.IntegerField(null=True, help_text="The length of this item in milliseconds.")
    def duration_datetime(self):
        """Returns 'duration', converted into a timedelta."""
        return timedelta(microseconds=self.duration * 1000)
    explicit = models.BooleanField(help_text="Whether this item contains explicit content.")
    feed_url = models.URLField(help_text="What this is exactly needs investigating.")
    file_extension = models.CharField(max_length=20, help_text="The file extension of the file of this podcast.")
    kind = models.CharField(max_length=100, help_text="Is this podcast audio, video etc.?")
    long_description = models.TextField(help_text="Potentially, a more verbose description of this item.")
    playlist_id = models.IntegerField()
    playlist_name = models.CharField(max_length=255)
    popularity = models.FloatField(help_text="An arbitrary % measurement of the popularity of this item.")
    preview_length = models.IntegerField(help_text="The length of the preview file.")
    preview_url = models.URLField(help_text="The URL of the preview file.")
    # price = models.FloatField()
    # price_display = models.CharField()
    rank = models.IntegerField(help_text="The position of this item in its collection.")
    release_date = models.DateTimeField(help_text="The date on which this item was first released.")
    scanlog = models.ForeignKey(ItuScanLog, related_name='iih_scanlog', help_text="The scanlog when this historical record was recorded.")
    missing = models.ForeignKey(ItuScanLog, null=True, related_name='missing_iih_scanlog', help_text="The scanlog when we first detected this was missing.")
    # Eventual link to an FFM FileInFeed, because all we really know is which FileInFeed should have been used here
    #    fileinfeed = models.ForeignKey(ffm_models.FileInFeed, null=True)
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    ituitem = models.ForeignKey(ItuItem, verbose_name="Item", help_text="The absolute record of this item.")

    version = models.PositiveIntegerField(default=1, help_text="The version number of this historical item record.")
    previous = models.ForeignKey('self', null=True, blank=True, help_text="The previous version of this historical item record.")

    def next(self):
        """Retrieves the next version of this historical item record."""
        try:
            n = ItuItemHistorical.objects.filter(previous=self)[0]
            return n
        except:
            return None
    def original(self):
        """Retrieves the original version of this historical item record."""
        p = self.previous
        o = self
        while p:
            o = p
            p = p.previous
        return o
    def latest(self):
        """Retrieves the latest version of this historical item record."""
        l = self
        n = self.next()
        while n:
            l = n
            n = l.next()
        return l

    class Meta:
        verbose_name = "iTunes U Historical Record of Item"
        verbose_name_plural = "iTunes U Historical Records of Items"
    def save(self):
        """Update absolute record so that the last-saved historical record is the latest record."""
        super(ItuItemHistorical, self).save()
        self.ituitem.latest = self
        self.ituitem.save()
    def __unicode__(self):
        return smart_unicode('%s, %s' % (self.name,str(self.scanlog.time)))


class ItuItemChartScan(models.Model):
    """A record of an item's position in the top items chart at a particular time."""
    date = models.DateTimeField(help_text="Date of chart scan - a duplicate of that in scanlog but will be efficient.")
    position = models.SmallIntegerField(help_text="The position in the chart this item was at.")
    ituitemhistorical = models.ForeignKey(ItuItemHistorical, verbose_name="Historical Item Record", help_text="The historical item record at this position.")
    ituitem = models.ForeignKey(ItuItem, verbose_name="Item", help_text="The absolute item record at this position.")
    scanlog = models.ForeignKey(ItuScanLog, help_text="The top items scan when this record was recorded.")
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('%s: %s' % (self.position, self.ituitemhistorical.name))


class ItuCollectionChartScan(models.Model):
    """A record of a collection's position in the top collections chart at a particular time."""
    date = models.DateTimeField(help_text="Date of chart scan - a duplicate of that in scanlog but will be efficient.")
    position = models.SmallIntegerField(help_text="The position in the chart this item was at.")
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record", help_text="The historical collection record at this position.")
    itucollection = models.ForeignKey(ItuCollection, verbose_name="Collection", help_text="The absolute collection record at this position.")
    scanlog = models.ForeignKey(ItuScanLog, help_text="The top collections scan when this record was recorded.")
    #
    #    @property
    #    def updated(self):
    #        return self.scanlog.time

    def __unicode__(self):
        return smart_unicode('%s: %s' % (self.position, self.itucollectionhistorical.name))


class ItuRating(models.Model):
    """The number of people who rated a given historical collection record with a certain number of stars."""
    stars = models.PositiveIntegerField(choices=((1,'*'),(2,'**'),(3,'***'),(4,'****'),(5,'*****')), help_text="The number of stars with which these people rated the collection.")
    count = models.PositiveIntegerField(help_text="The number of people who rated this collection with this many stars.")
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record", help_text="The historical collection record when this rating was found.")
    def __unicode__(self):
        return smart_unicode('%s people rated %s with %s stars.' % (self.count, self.itucollectionhistorical.name, self.stars))


class ItuComment(models.Model):
    """A comment on a collection."""
    stars = models.PositiveIntegerField(choices=((1,'*'),(2,'**'),(3,'***'),(4,'****'),(5,'*****')), help_text="The rating attached to this comment.")
    itucollectionhistorical = models.ForeignKey(ItuCollectionHistorical, verbose_name="Historical Collection Record", help_text="The historical record this comment was first found attached to.")
    date = models.DateField(null=True, blank=True, help_text="The date this comment was made.")
    detail = models.CharField(max_length=10000, help_text="The text of the comment.")
    source = models.CharField(max_length=100, help_text="The username of the person who made the comment.")
    ituinstitution = models.ForeignKey(ItuInstitution, verbose_name="Institution", help_text="The institution who owns the collection about which this comment was made.")

    class Meta:
        verbose_name = "iTunes U Comment"
        verbose_name_plural = "iTunes U Comments"
    def __unicode__(self):
        return smart_unicode(self.detail)


class InstitutionalCollectionTable(tables.Table):
    """A table to enable pagination of all the collections belonging to a given institution."""
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
