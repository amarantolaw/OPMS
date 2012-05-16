from django.db import models
from core import LogFile

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

    class Meta:
        app_label = 'stats'


# Lookup table for Operating Systems and versions
class OS(models.Model):
    company = models.CharField("operating system company", max_length=200)
    family = models.CharField("operating system family", max_length=100)
    name = models.CharField("operating system identity", max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'stats'


# Lookup table for User Agents and versions
class UA(models.Model):
    company = models.CharField("user agent company", max_length=200)
    family = models.CharField("user agent family", max_length=100)
    name = models.CharField("user agent identity", max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'stats'


# Lookup table for User Agent entries
class UserAgent(models.Model):
    full_string = models.TextField("full contents of user agent string")
    type = models.CharField("user agent type", max_length=50)
    os = models.ForeignKey(OS, verbose_name="operating system information", null=True)
    ua = models.ForeignKey(UA, verbose_name="user agent information", null=True)

    def __unicode__(self):
        return self.full_string

    class Meta:
        app_label = 'stats'


# Lookup table for Referer entries
# awk -F\" '{print $4}' access.log-20110201 | sort | uniq -c | sort -fr > referer2.txt
class Referer(models.Model):
    full_string = models.TextField("contents of referer")

    def __unicode__(self):
        return self.full_string

    class Meta:
        app_label = 'stats'


# Lookup table for request string entries
class FileRequest(models.Model):
    METHOD_CHOICES = (
        (u'GET', u'GET'),
        (u'POST', u'POST'),
        (u'HEAD', u'HEAD'),
        )
    method = models.CharField("request method", max_length=5, choices=METHOD_CHOICES)
    uri_string = models.TextField("uri path in request string")
    argument_string = models.TextField("arguments in request string")
    protocol = models.CharField("request protocol", max_length=20)
    # Eventually there will be a link here to a File record from the FFM module
    # file = models.ForeignKey(ffm_models.File, null=True)

    def __unicode__(self):
        return self.uri_string

    class Meta:
        app_label = 'stats'


# NOT YET IMPLEMENTED
# Because we're specically interested in doing tracking activities, we can duplicate and extract
# some key value pairs related to tracking terms.
# e.g. CAMEFROM=value; lfi=value; DESTINATION=value;
# These may be found in the URL argument string, or in the Referer string
#class Tracking(models.Model):
#    SOURCE_CHOICES = (
#        (u'FileRequest', u'File Request'),
#        (u'Referer', u'Referer'),
#        (u'Manual', u'Manually Tagged'),
#        )
#    key_string = models.CharField("key string", max_length=50)
#    value_string = models.CharField("value string", max_length=200)
#    source = models.CharField("data source", max_length=20, choices=SOURCE_CHOICES)
#
#    def __unicode__(self):
#        return '%s=%s' % (self.key_string,self.value_string)


# Replace three repetitive fields with one id
class Server(models.Model):
    name = models.CharField("server dns name", max_length=200)
    ip_address = models.IPAddressField("server ip address")
    port = models.IntegerField("server port number")

    def __unicode__(self):
        return '%s=%s' % (self.name,self.ip_address)

    class Meta:
        app_label = 'stats'


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
#    tracking = models.ManyToManyField(Tracking, verbose_name="tracking on this entry")

    @property
    def status_code_string(self):
        return self.STATUS_CODE_CHOICES.get(self.status_code,'')

    def __unicode__(self):
        return '%s:%s' % (self.time_of_request,self.file_request)

    class Meta:
        app_label = 'stats'

