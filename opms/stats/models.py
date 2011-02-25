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


# Reverse DNS Lookup cache. Because we don't want to be always hitting DNS servers.
class Rdns(models.Model):
    ip_address = models.IPAddressField("ip address")
    resolved_name = models.TextField("resolved dns name")
    country_code = models.CharField("country code", max_length=2)
    country_name = models.CharField("country name", max_length=200)
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
    #full_string = models.TextField("first line of request")
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
    #server_name = models.CharField("server dns name", max_length=200)
    #server_ip = models.IPAddressField("server ip address")
    #server_port = models.IntegerField("server port number")
    #REDUNDANT, use remote_rdns.ip_address - remote_ip = models.IPAddressField("remote ip address")
    remote_logname = models.CharField("remote log name", max_length=200,)
    remote_user = models.CharField("remote user name", max_length=200,)
    remote_rdns = models.ForeignKey(Rdns, verbose_name="remote reverse dns name")
    status_code = models.IntegerField("status code")
    size_of_response = models.BigIntegerField("size of response in bytes")
    # The following three fields need expanding into separate tables and parsing for duplicates and indexing purposes
    file_request = models.ForeignKey(FileRequest, verbose_name="first line of request string")
    referer = models.ForeignKey(Referer, verbose_name="referer string")
    user_agent = models.ForeignKey(UserAgent, verbose_name="user agent string")
    # This needs to be optional, as there may 0-n tracking tags on this entry
    tracking = models.ManyToManyField(Tracking, verbose_name="tracking on this entry")
    
    def __unicode__(self):
        return '%s:%s' % (self.time_of_request,self.file_request)
