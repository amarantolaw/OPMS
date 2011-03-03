from django.db import models
from datetime import date



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
    )
    service_name = models.CharField("service name associate with this log", max_length=20, choices=SERVICE_NAME_CHOICES)
    file_name = models.TextField("file name")
    file_path = models.TextField("path to file")
    last_updated = models.DateTimeField("last updated") # Acts as date of import
    
    def __unicode__(self):
        return self.file_name
        

####
# Apple Summary Data
####

# A 'virtual' Summary record based on a column of data from the Summary tab split across several tables
class Summary(models.Model):
    # user_actions = models.ManyToManyField(LogFile, through='UserActions')
    # client_software = models.ManyToManyField(LogFile, through='ClientSoftware')
    # Date from the column - typically from yyyy-mm-dd format
    week_ending = models.DateField("week ending", db_index=True)
    # The total as calculated by Apple
    total_track_downloads = models.IntegerField("total track downloads")
    
    def __unicode__(self):
        return str(date.strftime(self.week_ending,"%Y-%m-%d")) + ": Total Downloads=" + str(self.total_track_downloads)

class UserActions(models.Model):
    summary = models.ForeignKey(Summary)
    logfile = models.ForeignKey(LogFile)
    # User Actions section
    browse = models.IntegerField("browse")
    download_preview  = models.IntegerField("download preview")
    download_preview_ios = models.IntegerField("download preview iOS", blank=True, null=True)
    download_track = models.IntegerField("download track")
    download_tracks = models.IntegerField("download tracks")
    download_ios = models.IntegerField("download iOS", blank=True, null=True)
    edit_files = models.IntegerField("edit files")
    edit_page = models.IntegerField("edit page")
    logout = models.IntegerField("logout")
    search_results_page = models.IntegerField("search results page")
    subscription = models.IntegerField("subscription")
    subscription_enclosure = models.IntegerField("subscription enclosure")
    subscription_feed = models.IntegerField("subscription feed")
    upload = models.IntegerField("upload")
    not_listed = models.IntegerField("not listed")

class ClientSoftware(models.Model):
    PLATFORM_CHOICES = (
        (u'ipad', u'iTunes on iPad'),
        (u'ipod', u'iTunes on iPod'),
        (u'iphone', u'iTunes on iPhone'),
        (u'macintosh', u'iTunes on Macintosh'),
        (u'windows', u'iTunes on Windows'),
        (u'not listed', u'Unknown'),
    )
    summary = models.ForeignKey(Summary)
    logfile = models.ForeignKey(LogFile)
    # Client Software section
    platform = models.CharField("platform", max_length=20, choices=PLATFORM_CHOICES)
    version_major = models.IntegerField("major version number")
    version_minor = models.IntegerField("minor version number")
    count = models.IntegerField("count")



####
# Apple Track Records
####

class TrackManager(models.Manager):
# THIS IS LIKELY REDUNDANT ALREADY!
    def grouped_by_feed(self, sort_by):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT sum(count) AS count, substring(guid,52) 
            FROM stats_track
            GROUP BY substring(guid,52)
            ORDER BY %s''' % sort_by)

        result_list = []
        for row in cursor.fetchall():
            t = self.model(count=row[0], guid=row[1])
            t.psudeo_feed = row[1]
            result_list.append(t)

        return result_list

    def items_by_feed(self, partial_guid):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT sum(count), min(path), min(guid)
            FROM stats_track
            WHERE substring(guid,52) = %s
            GROUP BY guid''', [partial_guid])

        result_list = []
        for row in cursor.fetchall():
            t = self.model(count=row[0], path=row[1], guid=row[2])
            result_list.append(t)

        return result_list
    

# This is a 'virtual' track entity, which will have multiple handles, paths and counts associated with it
class Track(models.Model):
    counts = models.ManyToManyField(LogFile, through='TrackCount', verbose_name="count values")
    handles = models.ManyToManyField(LogFile, through='TrackHandle', verbose_name="handle values")
    paths = models.ManyToManyField(LogFile, through='TrackPath', verbose_name="path values")
    week_ending = models.DateField("week ending")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True, db_index=True)
    # Eventually there will be a link here to a File record from the FFM module

    objects = TrackManager()
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)
        

# Track Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific track
class TrackPath(models.Model):
    track = models.ForeignKey(Track)
    logfile = models.ForeignKey(LogFile)
    path = models.TextField("path")
    
    def __unicode__(self):
        return str(self.path)


# Track Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific track
class TrackHandle(models.Model):
    track = models.ForeignKey(Track)
    logfile = models.ForeignKey(LogFile)
    handle = models.BigIntegerField("handle")
    
    def __unicode__(self):
        return str(self.handle)


# A count is collected for each service (logfile.service_name) in the records
class TrackCount(models.Model):
    track = models.ForeignKey(Track)
    logfile = models.ForeignKey(LogFile)
    count = models.IntegerField("count")
    
    def __unicode__(self):
        return str(self.count)



####
# Apple Browse Records
####
    
# This is a 'virtual' track entity, which will have multiple handles, paths and counts associated with it
class Browse(models.Model):
    counts = models.ManyToManyField(LogFile, through='BrowseCount', verbose_name="count values")
    handles = models.ManyToManyField(LogFile, through='BrowseHandle', verbose_name="handle values")
    paths = models.ManyToManyField(LogFile, through='BrowsePath', verbose_name="path values")
    week_ending = models.DateField("week ending")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True, db_index=True)
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)

# Browse Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific page
class BrowsePath(models.Model):
    browse = models.ForeignKey(Browse)
    logfile = models.ForeignKey(LogFile)
    path = models.TextField("path")
    
    def __unicode__(self):
        return str(self.path)


# Browse Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific page
class BrowseHandle(models.Model):
    browse = models.ForeignKey(Browse)
    logfile = models.ForeignKey(LogFile)
    handle = models.BigIntegerField("handle")
    
    def __unicode__(self):
        return str(self.handle)


# A count is collected for each service (logfile.service_name) in the records
class BrowseCount(models.Model):
    browse = models.ForeignKey(Browse)
    logfile = models.ForeignKey(LogFile)
    count = models.IntegerField("count")
    
    def __unicode__(self):
        return str(self.count)



####
# Apple Preview Records
####

# This is a 'virtual' track entity, which will have multiple handles, paths and counts associated with it
class Preview(models.Model):
    counts = models.ManyToManyField(LogFile, through='PreviewCount', verbose_name="count values")
    handles = models.ManyToManyField(LogFile, through='PreviewHandle', verbose_name="handle values")
    paths = models.ManyToManyField(LogFile, through='PreviewPath', verbose_name="path values")
    week_ending = models.DateField("week ending")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True, db_index=True)
    # Eventually there will be a link here to a File record from the FFM module
    
    def __unicode__(self):
        return '%s:%s' % (self.week_ending,self.guid)

# Preview Paths have changed as the system has evolved and migrated, but we want to keep them related to a specific track preview
class PreviewPath(models.Model):
    preview = models.ForeignKey(Preview)
    logfile = models.ForeignKey(LogFile)
    path = models.TextField("path")
    
    def __unicode__(self):
        return str(self.path)


# Preview Handles change from time to time due to tweaks in the system, but we want to keep them related to a specific track preview
class PreviewHandle(models.Model):
    preview = models.ForeignKey(Preview)
    logfile = models.ForeignKey(LogFile)
    handle = models.BigIntegerField("handle")
    
    def __unicode__(self):
        return str(self.handle)


# A count is collected for each service (logfile.service_name) in the records
class PreviewCount(models.Model):
    preview = models.ForeignKey(Preview)
    logfile = models.ForeignKey(LogFile)
    count = models.IntegerField("count")
    
    def __unicode__(self):
        return str(self.count)
        



######
# Apache log analysis classes
######


# Reverse DNS Lookup cache. Because we don't want to be always hitting DNS servers.
class Rdns(models.Model):
    ip_address = models.IPAddressField("ip address")
    resolved_name = models.TextField("resolved dns name")
    country_code = models.CharField("country code", max_length=2)
    country_name = models.CharField("country name", max_length=200)
    last_updated = models.DateTimeField("last updated")
    
    def __unicode__(self):
        return self.resolved_name


# Lookup table for Operating Systems and versions
class OS(models.Model):
    company = models.CharField("operating system company", max_length=200)
    family = models.CharField("operating system family", max_length=100)
    name = models.CharField("operating system identity", max_length=200)
    
    def __unicode__(self):
        return self.name


# Lookup table for User Agents and versions
class UA(models.Model):
    company = models.CharField("user agent company", max_length=200)
    family = models.CharField("user agent family", max_length=100)
    name = models.CharField("user agent identity", max_length=200)
    
    def __unicode__(self):
        return self.name


# Lookup table for User Agent entries
class UserAgent(models.Model):
    full_string = models.TextField("full contents of user agent string")
    type = models.CharField("user agent type", max_length=50)
    os = models.ForeignKey(OS, verbose_name="operating system information", null=True)
    ua = models.ForeignKey(UA, verbose_name="user agent information", null=True)

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
    METHOD_CHOICES = (
        (u'GET', u'GET'),
        (u'POST', u'POST'),
        (u'HEAD', u'HEAD'),
    )
    FILE_TYPE_CHOICES = (
        (u'mp3', u'Audio MP3'),
        (u'mp4', u'Video MP4'),
        (u'm4a', u'Audio M4A'),
        (u'm4b', u'Audiobook M4B'),
        (u'm4p', u'Audio Protected M4P'),
        (u'm4v', u'Video M4V'),
        (u'txt', u'Text TXT'),
        (u'gif', u'Image GIF'),
        (u'png', u'Image PNG'),
        (u'jpg', u'Image JPG'),
        (u'', u'Unknown'),
    )
    method = models.CharField("request method", max_length=5, choices=METHOD_CHOICES)
    uri_string = models.TextField("uri path in request string")
    argument_string = models.TextField("arguments in request string")
    protocol = models.CharField("request protocol", max_length=20)
    file_type = models.CharField("file type", max_length=3, choices=FILE_TYPE_CHOICES)

    def __unicode__(self):
        return self.uri_string


# Because we're specically interested in doing tracking activities, we can duplicate and extract
# some key value pairs related to tracking terms.
# e.g. CAMEFROM=value; lfi=value; DESTINATION=value;
# These may be found in the URL argument string, or in the Referer string
class Tracking(models.Model):
    SOURCE_CHOICES = (
        (u'FileRequest', u'File Request'),
        (u'Referer', u'Referer'),
        (u'Manual', u'Manually Tagged'),
    )
    key_string = models.CharField("key string", max_length=50)
    value_string = models.CharField("value string", max_length=200)
    source = models.CharField("data source", max_length=20, choices=SOURCE_CHOICES)

    def __unicode__(self):
        return '%s=%s' % (self.key_string,self.value_string)

    
# Replace three repetative fields with one id
class Server(models.Model):
    name = models.CharField("server dns name", max_length=200)
    ip_address = models.IPAddressField("server ip address")
    port = models.IntegerField("server port number")

    def __unicode__(self):
        return '%s=%s' % (self.name,self.ip_address)
        

# Log file request table. Each row is a request from a log file
class LogEntry(models.Model):
    # Status codes from: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    STATUS_CODE_CHOICES = (
        (100, u'100 Continue'),
        (101, u'101 Switching Protocols'),
        (200, u'200 OK'),
        (201, u'201 Created'),
        (202, u'202 Accepted'),
        (203, u'203 Non-Authoritative Information'),
        (204, u'204 No Content'),
        (205, u'205 Reset Content'),
        (206, u'206 Partial Content'),
        (300, u'300 Multiple Choices'),
        (301, u'301 Moved Permanently'),
        (302, u'302 Found'),
        (303, u'303 See Other'),
        (304, u'304 Not Modified'),
        (305, u'305 Use Proxy'),
        (306, u'306 (Unused)'),
        (307, u'307 Temporary Redirect'),
        (400, u'400 Bad Request'),
        (401, u'401 Unauthorized'),
        (402, u'402 Payment Required'),
        (403, u'403 Forbidden'),
        (404, u'404 Not Found'),
        (405, u'405 Method Not Allowed'),
        (406, u'406 Not Acceptable'),
        (407, u'407 Proxy Authentication Required'),
        (408, u'408 Request Timeout'),
        (409, u'409 Conflict'),
        (410, u'410 Gone'),
        (411, u'411 Length Required'),
        (412, u'412 Precondition Failed'),
        (413, u'413 Request Entity Too Large'),
        (414, u'414 Request-URI Too Long'),
        (415, u'415 Unsupported Media Type'),
        (416, u'416 Requested Range Not Satisfiable'),
        (417, u'417 Expectation Failed'),
        (500, u'500 Internal Server Error'),
        (501, u'501 Not Implemented'),
        (502, u'502 Bad Gateway'),
        (503, u'503 Service Unavailable'),
        (504, u'504 Gateway Timeout'),
        (505, u'505 HTTP Version Not Supported')
    )
    logfile = models.ForeignKey(LogFile, verbose_name="log file this entry is taken from")
    time_of_request = models.DateTimeField("time of request", db_index=True)
    server = models.ForeignKey(Server, verbose_name="server")
    remote_logname = models.CharField("remote log name", max_length=200,)
    remote_user = models.CharField("remote user name", max_length=200,)
    remote_rdns = models.ForeignKey(Rdns, verbose_name="remote reverse dns name")
    status_code = models.IntegerField("status code")
    size_of_response = models.BigIntegerField("size of response in bytes")
    file_request = models.ForeignKey(FileRequest, verbose_name="first line of request string")
    referer = models.ForeignKey(Referer, verbose_name="referer string")
    user_agent = models.ForeignKey(UserAgent, verbose_name="user agent string")
    # This needs to be optional, as there may 0-n tracking tags on this entry
    tracking = models.ManyToManyField(Tracking, verbose_name="tracking on this entry")
    
    def __unicode__(self):
        return '%s:%s' % (self.time_of_request,self.file_request)
