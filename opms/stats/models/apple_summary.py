from django.db import models
from core import LogFile
from apple_managers import AppleWeeklySummaryManager, AppleTrackManager
from django.utils.encoding import smart_unicode
from datetime import date

####
# Apple Summary Data
####


# A Summary record based on a column of data from the Summary tab. Note there can be more than one for a given week (iTU + iTUPSM, or itu-raw + itu-psm)
# aka: "AppleEntry", like ApacheLogEntry, but for Apple data.
class AppleWeeklySummary(models.Model):
    SERVICE_NAME_CHOICES = (
        (u'itu', u'iTunes U v1'),
        (u'itu-psm', u'iTunes U PSM'),
        (u'itu-raw', u'iTunes U PSM Raw Logs'), # This is a virtual summary produced from the more detailed log data
        )
    # Date from the column - typically from yyyy-mm-dd format
    week_beginning = models.DateField("week beginning", db_index=True)

    # Logfile this data was pulled from
    logfile = models.ForeignKey(LogFile)
    # Repeating this field as a necessary evil for the sake of duplication checking on import
    service_name = models.CharField("service name associate with this log", max_length=20, choices=SERVICE_NAME_CHOICES)

    # User Actions section
    browse = models.IntegerField("browse")
    download_preview  = models.IntegerField("download preview")
    download_preview_ios = models.IntegerField("download preview iOS", blank=True, null=True)
    download_track = models.IntegerField("download track")
    download_tracks = models.IntegerField("download tracks")
    download_ios = models.IntegerField("download iOS", blank=True, null=True)
    edit_files = models.IntegerField("edit files", blank=True, null=True)
    edit_page = models.IntegerField("edit page", blank=True, null=True)
    logout = models.IntegerField("logout", blank=True, null=True)
    search_results_page = models.IntegerField("search results page", blank=True, null=True)
    subscription = models.IntegerField("subscription")
    subscription_enclosure = models.IntegerField("subscription enclosure")
    subscription_feed = models.IntegerField("subscription feed")
    upload = models.IntegerField("upload", blank=True, null=True)
    not_listed = models.IntegerField("not listed", blank=True, null=True)
    # The total as calculated by Apple
    total_track_downloads = models.IntegerField("total track downloads")

    merged = AppleWeeklySummaryManager() # Manager for merged data
    objects = models.Manager() # Default manager

    def __unicode__(self):
        return str(date.strftime(self.week_beginning,"%Y-%m-%d")) + ": Total Downloads=" + str(self.total_track_downloads)

    @property
    def service_name_string(self):
        for k,v in self.SERVICE_NAME_CHOICES:
            if k == self.service_name:
                return v
        return ''

    class Meta:
        app_label = 'stats'


# Removing this class as the data is basically a waste of space in hindsight.
#class ClientSoftware(models.Model):
#    summary = models.ForeignKey(AppleWeeklySummary)
#    # Client Software section
#    platform = models.CharField("platform", max_length=20)
#    version_major = models.IntegerField("major version number")
#    version_minor = models.IntegerField("minor version number")
#    count = models.IntegerField("count")


####
# Apple Track Records
####

# Track Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific track
class AppleTrackPath(models.Model):
    path = models.TextField("path", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this path first found?

    def __unicode__(self):
        return smart_unicode(self.path)

    class Meta:
        app_label = 'stats'


# Track Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific track
class AppleTrackHandle(models.Model):
    handle = models.BigIntegerField("handle", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this handle first found?

    def __unicode__(self):
        return str(self.handle)

    class Meta:
        app_label = 'stats'


# Track GUIDs change from time to time due to OxItems changes, but we want to keep them related to a specific track
# NB: This data should eventually be migrated to the FFM app, as it comes from the rss source, and is copied into the stats data by Apple
class AppleTrackGUID(models.Model):
    guid = models.CharField("GUID", max_length=255, db_index=True, unique=True)
    # Eventually there will be a link here to a File record from the FFM module
    # file = models.ForeignKey(ffm_models.File, null=True)
    logfile = models.ForeignKey(LogFile) # Where was this guid first found?
    # The following are optional fields of OxItems data imported in a basic fashion
    name = models.CharField(max_length=255, null=True, blank=True) # Rg07Items.item_title
    deleted = models.BooleanField(default=False) # Rg07Items.deleted


    def __unicode__(self):
        return smart_unicode(self.guid)

    class Meta:
        app_label = 'stats'


# This is a track count record, which will have multiple handles, paths and guids/files associated with it
class AppleWeeklyTrackCount(models.Model):
    summary = models.ForeignKey(AppleWeeklySummary) # aka: AppleEntry
    count = models.IntegerField("count")
    # A count record has a handle, path and guid associated. GUIDs may have been created by OPMS
    path = models.ForeignKey(AppleTrackPath)
    handle = models.ForeignKey(AppleTrackHandle)
    guid = models.ForeignKey(AppleTrackGUID)

    merged = AppleTrackManager() # Manager for merged data
    objects = models.Manager() # Default manager

    def __unicode__(self):
        return '%s:%s' % (self.summary.week_beginning,self.count)

    class Meta:
        app_label = 'stats'


####
# Apple Browse Records
####
# Browse Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific browse
class AppleBrowsePath(models.Model):
    path = models.TextField("path", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this path first found?

    def __unicode__(self):
        return smart_unicode(self.path)

    class Meta:
        app_label = 'stats'


# Browse Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific browse
class AppleBrowseHandle(models.Model):
    handle = models.BigIntegerField("handle", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this handle first found?

    def __unicode__(self):
        return str(self.handle)

    class Meta:
        app_label = 'stats'

# GUIDs for Browses are optional
class AppleBrowseGUID(models.Model):
    guid = models.CharField("GUID", max_length=255, unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this guid first found?

    def __unicode__(self):
        return smart_unicode(self.guid)

    class Meta:
        app_label = 'stats'


# This is a browse count record, which will have multiple handles, paths and guids/files associated with it
class AppleWeeklyBrowseCount(models.Model):
    summary = models.ForeignKey(AppleWeeklySummary)
    count = models.IntegerField("count")
    # A count record has a handle and path associated, and may have a guid also
    path = models.ForeignKey(AppleBrowsePath)
    handle = models.ForeignKey(AppleBrowseHandle)
    guid = models.ForeignKey(AppleBrowseGUID, null=True)

    def __unicode__(self):
        return '%s:%s' % (self.summary.week_beginning,self.count)

    class Meta:
        app_label = 'stats'




####
# Apple Preview Records
####
# Preview Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific preview
class ApplePreviewPath(models.Model):
    path = models.TextField("path", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this path first found?

    def __unicode__(self):
        return smart_unicode(self.path)

    class Meta:
        app_label = 'stats'


# Preview Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific preview
class ApplePreviewHandle(models.Model):
    handle = models.BigIntegerField("handle", unique=True)
    logfile = models.ForeignKey(LogFile) # Where was this handle first found?

    def __unicode__(self):
        return str(self.handle)

    class Meta:
        app_label = 'stats'


# Preview GUIDs change from time to time due to OxItems changes, but we want to keep them related to a specific preview
# NB: This data should eventually be migrated to the FFM app, as it comes from the rss source, and is copied into the stats data by Apple
class ApplePreviewGUID(models.Model):
    guid = models.CharField("GUID", max_length=255, db_index=True, unique=True)
    # Eventually there will be a link here to a File record from the FFM module
    logfile = models.ForeignKey(LogFile) # Where was this guid first found?

    def __unicode__(self):
        return smart_unicode(self.guid)

    class Meta:
        app_label = 'stats'


# This is a preview count record, which will have multiple handles, paths and guids/files associated with it
class AppleWeeklyPreviewCount(models.Model):
    summary = models.ForeignKey(AppleWeeklySummary)
    count = models.IntegerField("count")
    # A count record has a handle and path associated, and may have a guid also
    path = models.ForeignKey(ApplePreviewPath)
    handle = models.ForeignKey(ApplePreviewHandle)
    guid = models.ForeignKey(ApplePreviewGUID)

    def __unicode__(self):
        return '%s:%s' % (self.summary.week_beginning,self.count)

    class Meta:
        app_label = 'stats'


