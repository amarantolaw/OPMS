from django.db import models

# Create your models here.

# Summary record based on a column of data from the Summary tab
class Summary(models.Model):
    # Date from the column - typically from yyyy-mm-dd format
    week_ending = models.DateField("week ending")
    # User Actions section
    ua_browse = models.IntegerField("browse")
    ua_download_preview  = models.IntegerField("download preview")
    ua_download_preview_ios = models.IntegerField("download preview iOS", blank=True, null=True)
    ua_download_track = models.IntegerField("download track")
    ua_download_tracks = models.IntegerField("download tracks")
    ua_download_ios = models.IntegerField("download iOS", blank=True, null=True)
    ua_edit_files = models.IntegerField("edit files")
    ua_edit_page = models.IntegerField("edit page")
    ua_logout = models.IntegerField("logout")
    ua_search_results_page = models.IntegerField("search results page")
    ua_subscription = models.IntegerField("subscription")
    ua_subscription_enclosure = models.IntegerField("subscription enclosure")
    ua_subscription_feed = models.IntegerField("subscription feed")
    ua_upload = models.IntegerField("upload")
    ua_not_listed = models.IntegerField("not listed")
    # The total as calculated by Apple
    total_track_downloads = models.IntegerField("total track downloads")
    # Client Software section
    # note: the number of options here changes over time in the data, hence the blank=True option to allow for gaps in data import.
    cs_macintosh = models.IntegerField("?/?/Macintosh", blank=True, null=True)
    cs_windows = models.IntegerField("?/?/Windows", blank=True, null=True)
    cs_itunes_ipad_3_2 = models.IntegerField("iTunes-iPad/3.2/?", blank=True, null=True)
    cs_itunes_iphone_3_0 = models.IntegerField("iTunes-iPhone/3.0/?", blank=True, null=True)
    cs_itunes_iphone_3_1 = models.IntegerField("iTunes-iPhone/3.1/?", blank=True, null=True)
    cs_itunes_iphone_4_0 = models.IntegerField("iTunes-iPhone/4.0/?", blank=True, null=True)
    cs_itunes_iphone_4_1 = models.IntegerField("iTunes-iPhone/4.1/?", blank=True, null=True)
    cs_itunes_ipod_3_0 = models.IntegerField("iTunes-iPod/3.0/?", blank=True, null=True)
    cs_itunes_ipod_3_1 = models.IntegerField("iTunes-iPod/3.1/?", blank=True, null=True)
    cs_itunes_ipod_4_0 = models.IntegerField("iTunes-iPod/4.0/?", blank=True, null=True)
    cs_itunes_ipod_4_1 = models.IntegerField("iTunes-iPod/4.1/?", blank=True, null=True)
    cs_itunes_10_0_macintosh = models.IntegerField("iTunes/10.0/Macintosh", blank=True, null=True)
    cs_itunes_10_0_windows = models.IntegerField("iTunes/10.0/Windows", blank=True, null=True)
    cs_itunes_8_0_macintosh = models.IntegerField("iTunes/8.0/Macintosh", blank=True, null=True)
    cs_itunes_8_0_windows = models.IntegerField("iTunes/8.0/Windows", blank=True, null=True)
    cs_itunes_8_1_macintosh = models.IntegerField("iTunes/8.1/Macintosh", blank=True, null=True)
    cs_itunes_8_1_windows = models.IntegerField("iTunes/8.1/Windows", blank=True, null=True)
    cs_itunes_8_2_macintosh = models.IntegerField("iTunes/8.2/Macintosh", blank=True, null=True)
    cs_itunes_8_2_windows = models.IntegerField("iTunes/8.2/Windows", blank=True, null=True)
    cs_itunes_9_0_macintosh = models.IntegerField("iTunes/9.0/Macintosh", blank=True, null=True)
    cs_itunes_9_0_windows = models.IntegerField("iTunes/9.0/Windows", blank=True, null=True)
    cs_itunes_9_1_macintosh = models.IntegerField("iTunes/9.1/Macintosh", blank=True, null=True)
    cs_itunes_9_1_windows = models.IntegerField("iTunes/9.1/Windows", blank=True, null=True)
    cs_itunes_9_2_macintosh = models.IntegerField("iTunes/9.2/Macintosh", blank=True, null=True)
    cs_itunes_9_2_windows = models.IntegerField("iTunes/9.2/Windows", blank=True, null=True)
    cs_not_listed = models.IntegerField("not listed", blank=True, null=True)
    
    def __unicode__(self):
        return self.week_ending

# Track record based on Aug 2010 Excel "yyyy-mm-dd Tracks" datastructure. Each record is a line in the sheet
class TrackManager(models.Manager):
    def grouped_by_feed(self, sort_by):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, sum(count) AS count, week_ending, path, handle, guid 
            FROM stats_track
            GROUP BY substring(guid,52)
            ORDER BY %s''' % sort_by)

        result_list = []
        for row in cursor.fetchall():
            t = self.model(id=row[0], count=row[1], week_ending=row[2], path=row[3], handle=row[4], guid=row[5])
            if len(row[5]) > 50:
                t.psudeo_feed = row[5][51:]
            else:
                t.psudeo_feed = row[5]
            result_list.append(t)

        return result_list

    def items_by_feed(self, partial_guid):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, sum(count) AS count, week_ending, path, handle, guid
            FROM stats_track
            WHERE substring(guid,52) = %s
            GROUP BY guid''', [partial_guid])

        result_list = []
        for row in cursor.fetchall():
            t = self.model(id=row[0], count=row[1], week_ending=row[2], path=row[3], handle=row[4], guid=row[5])
            if len(row[5]) > 50:
                t.psudeo_feed = row[5][51:]
            else:
                t.psudeo_feed = row[5]
            result_list.append(t)

        return result_list
        


class Track(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)

    objects = TrackManager()
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)



# Browse record based on Aug 2010 Excel "yyyy-mm-dd Browse" datastructure. Each record is a line in the sheet
class Browse(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)


# Preview record based on Aug 2010 Excel "yyyy-mm-dd Previews" datastructure. Each record is a line in the sheet
class Preview(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)


######
# Apache log analysis classes
######

# GeoIP data lookup table based on data from Geocode?
class IPLocation(models.Model):
    ip_range_start = models.IPAddressField("ip range start")
    ip_range_end = models.IPAddressField("ip range end")
    ip_int_start = models.IntegerField("ip integer range start")
    ip_int_end = models.IntegerField("ip integer range end")
    country_code = models.CharField("country code", max_length=2)
    country_name = models.CharField("country name", max_length=200)
    last_updated = models.DateTimeField("last updated")
    
    def __unicode__(self):
        return self.country_name

# Reverse DNS Lookup cache. Because we don't want to be always hitting DNS servers.
class Rdns(models.Model:)
    ip_address = models.IPAddressField("ip address")
    ip_int = models.IntegerField("ip as an integer")
    ip_location = models.ForeignKey(IPLocation, verbose_name="IP geo-location")
    resolved_name = models.TextField("resolved dns name")
    last_updated = models.DateTimeField("last updated")
    
    def __unicode__(self):
        return self.resolved_name
    
# Quite possible to have multiple log file sources, use this as a lookup table
class LogFile(models.Model):
    SERVICE_NAME_CHOICES = (
        (u'mpoau', u'Media.podcasts Hosting'),
        (u'poau1', u'Podcasts.ox v1'),
        (u'poau-beta', u'beta.podcasts.ox.uk'),
        (u'oxitems', u'OxItems'),
        (u'mox', u'mobile.ox.ac.uk'),
    )
    service_name = models.CharField("service name associate with this log", max_length=20, choices=SERVICE_NAME_CHOICES)
    file_name = models.TextField("file name")
    file_path = models.TextField("path to file")
    last_updated = models.DateTimeField("last updated") # Acts as date of import
    
    def __unicode__(self):
        return self.file_name


# Lookup table for Browsers and versions - this allows us to dynamically add more values as we find them
class BrowserVersion(models.Model):
    browser_token = models.CharField("browser token string", max_length=50)
    browser_name = models.CharField("browser name", max_length=200)
    
    def __unicode__(self):
        return self.browser_name

# Lookup table for Platforms and versions
class PlatformVersion(models.Model):
    PLATFORM_SHORTNAME_CHOICES = (
        (u'Windows', u'Windows'),
        (u'Mac OS', u'Mac OS'),
        (u'iOS', u'iOS'),
        (u'Other', u'Other'),
        (u'Unknown', u'Unknown'),        
    )
    platform_token = models.CharField("platform token string", max_length=50)
    platform_name = models.CharField("platform full name", max_length=200)
    platform_shortname = models.CharField("platform short name", max_length=50, choices=PLATFORM_SHORTNAME_CHOICES)
    
    def __unicode__(self):
        return self.platform_name

# Lookup table for User Agent entries
class UserAgent(models.Model):
# Examples from https://developer.mozilla.org/en/Gecko_user_agent_string_reference
# http://msdn.microsoft.com/en-us/library/ms537503(v=vs.85).aspx
# Application Name/App Version (Compatibility flag; Version Token; Platform token;) Misc other
# Need to account for blank user agents - "No User Agent"
#
# Quick analysis of one log file from 1-2-11 gave 750 User Agent strings... From 14-1-09 gave 129!
# awk -F\" '{print $6}' access.log-20110201 | sort | uniq -c | sort -fr >user-agents-2.txt
    full_string = models.TextField("contents of user agent")
    application_name = models.CharField("application name", max_length=200)
    application_version = models.CharField("application version", max_length=10)
    platform_version = models.ForeignKey(PlatformVersion, verbose_name="platform information")
    browser_version = models.ForeignKey(BrowserVersion, verbose_name="browser information")

    def __unicode__(self):
        return self.full_string

# Lookup table for Referer entries
# awk -F\" '{print $4}' access.log-20110201 | sort | uniq -c | sort -fr > referer2.txt
class Referer(models.Model):
    full_string = models.TextField("contents of referer")

    def __unicode__(self):
        return self.full_string

# Lookup table for request string entries
class FileRequest(models.Model):
    #full_string = models.TextField("first line of request")
    uri_string = models.TextField("uri path in request string")
    argument_string = models.TextField("arguments in request string")

    def __unicode__(self):
        return self.uri_string

# Because we're specically interested in doing tracking activities, we can duplicate and extract
# some key value pairs related to tracking terms.
# e.g. CAMEFROM=value; lfi=value; DESTINATION=value;
# These may be found in the URL argument string, or in the Referer string
class Tracking(models.Model):
    key_string = models.CharField("key string", max_length=50)
    value_string = models.CharField("value string", max_length=200)

    def __unicode__(self):
        return '%s=%s' % (self.key_string,value_string)
    

# Log file request table. Each row is a request from a log file
class LogEntry(models.Model):
    logfile = models.ForeignKey(LogFile, verbose_name="log file this entry is taken from")
    time_of_request = models.DateTimeField("time of request")
    server_name = models.CharField("server dns name", max_length=200)
    server_ip = models.IPAddressField("server ip address")
    server_port = models.IntegerField("server port number")
    remote_ip = models.IPAddressField("remote ip address")
    remote_ip_int = models.IntegerField("remote ip address as integer")
    remote_logname = models.CharField("remote log name", max_length=200,)
    remote_user = models.CharField("remote user name", max_length=200,)
    remote_iplocation = models.ForeignKey(IPLocation, verbose_name="remote geo-location")
    remote_rnds = models.ForeignKey(Rdns, verbose_name="remote reverse dns name")
    status_code = models.IntegerField("status code")
    size_of_response = models.BigIntegerField("size of response in bytes")
    # The following three fields need expanding into separate tables and parsing for duplicates and indexing purposes
    # request_string = models.TextField("first line of request")
    file_request = models.ForeignKey(FileRequest, verbose_name="first line of request string")
    # referer_string = models.TextField("contents of referer")
    referer = models.ForeignKey(Referer, verbose_name="referer string")
    # user_agent_string = models.TextField("contents of user agent")
    user_agent = models.ForeignKey(UserAgent, verbose_name="user agent string")
    # This needs to be optional, as there may 0-n tracking tags on this entry
    tracking = models.ManyToManyField(Tracking, verbose_name="tracking on this entry")
    
    def __unicode__(self):
        return '%s:%s' % (self.time_of_request,file_request)
