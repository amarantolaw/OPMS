# Import script for Apache Logfiles from media servers
# Author: Carl Marshall
# Last Edited: 4-2-2011

from django.core.management.base import BaseCommand, CommandError
from opms.stats.models import *
import apachelog, datetime, sys, pygeoip
from dns import resolver,reversename
from IPy import IP
        
class Command(BaseCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'
    
    def __init__(self):
        self.geoip = pygeoip.GeoIP('/home/carl/Projects/opms_master/OPMS/data/geoip/GeoIP.dat',pygeoip.MMAP_CACHE)

    def handle(self, *args, **options):

        for filename in args:
            # Some basic checking
            if filename.endswith('.gz'):
               raise CommandError("This file is still compressed. Uncompress and try again.\n\n")
               # sys.exit(1)
            else:
               print "################  Beginning IMPORT from", filename
        
            # Assume mpoau logfiles
            format = r'%Y-%m-%dT%H:%M:%S%z %v %A:%p %h %l %u \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
            p = apachelog.parser(format)
            
            log = open(filename)
            
            for line in log:
                data = p.parse(line)
                
# data.items()    
#[('%Y-%m-%dT%H:%M:%S%z', '2009-01-14T06:20:59+0000'),
# ('%l', '-'),
# ('%>s', '200'),
# ('%h', '163.1.2.86'),
# ('%A:%p', '163.1.3.25:80'),
# ('%{User-Agent}i', 'check_http/1.96 (nagios-plugins 1.4.5)'),
# ('%b', '207'),
# ('%{Referer}i', '-'),
# ('%u', '-'),
# ('%v', 'media.podcasts.ox.ac.uk'),
# ('%r', 'GET / HTTP/1.0')]
 
 
# data.get('%{User-Agent}i')
# 'check_http/1.96 (nagios-plugins 1.4.5)'
                
                # Validate the data - Count the number of elements
                if len(data) <> 11:
                    print "#### Houston, we have a problem with this entry: %s" % data
                
                
                # Get or create the foreign key elements, Logfile, Rdns, FileRequest, Referer, UserAgent
                logfile = self._logfile(filename)
                remote_rdns = self._ip_to_domainname(data.get('%h'))
                file_request = self._file_request(data.get('%r'))
                referer = self._referer(data.get('%{Referer}i'))
                user_agent = self._user_agent(data.get('%{User-Agent}i'))
                
                # Tracking needs dealing with later...
                
                # Pull apart the date time string
                date_string, time_string = data.get('%Y-%m-%dT%H:%M:%S%z').split('T')
                date_yyyy, date_mm, date_dd = date_string.split('-')
                time_hh, time_mm, time_ss = time_string.split(':')
                
                # Pull apart the server and port
                server_ip, server_port = data.get('%A:%p').split(':')
                
                # Size of response validation. Can be '-' when status not 200
                size_of_response = data.get('%b')
                if size_of_response.isdigit():
                    size_of_response = int(size_of_response)
                else:
                    size_of_response = 0
                
                # Status code validation
                status_code = int(data.get('%>s'))
                
                # Build the log entry dictionary
                log_entry = {
                    'logfile': logfile,
                    'time_of_request': datetime.datetime(
                        int(date_yyyy), 
                        int(date_mm), 
                        int(date_dd), 
                        int(time_hh), 
                        int(time_mm), 
                        int(time_ss[0:2]) # Cut off the +0000
                        ),
                    'server_name': data.get('%v'),
                    'server_ip': IP(server_ip).strNormal(0),
                    'server_port': int(server_port),
                    'remote_ip': remote_rdns.get['ip_address'],
                    'remote_logname': data.get('%l'),
                    'remote_user': data.get('%u'),
                    'remote_rdns': remote_rdns,
                    'status_code': status_code,
                    'size_of_response': size_of_response,
                    'file_request': file_request,
                    'referer': referer,
                    'user_agent': user_agent,
                }
                
                print '============================\n'
                print data,'\n'
                print log_entry,'\n'
                
                # Create if there isn't already a duplicate record in place
                obj, created = LogEntry.objects.get_or_create(
                    time_of_request=log_entry.get('time_of_request'),  
                    server_ip=log_entry.get('server_ip'), 
                    remote_ip=log_entry.get('remote_ip'), 
                    size_of_response=log_entry.get('size_of_response'), 
                    file_request=log_entry.get('file_request'), 
                    defaults=log_entry)
        
                if created:
                    print "Record imported: %s" % log_entry
                else:
                    print "DUPLICATE RECORD DETECTED: %s" % log_entry


            print "Import finished\n\n"


    def _logfile(self, filename):
        "Get or create a LogFile record for the given filename"
        return filename



    def _ip_to_domainname(self, ipaddress):
        "Returns the domain name for a given IP where known"
        # validate IP address
        # try: 
        adr = IP(ipaddress)
        # else:
        # PUT ERROR HANDLING IN HERE!
        
        rdns = {}
        rdns['ip_address'] = adr.strNormal(0)
        rdns['ip_int'] = adr.strDec(0)
        rdns['resolved_name'] = 'No Resolved Name'
        rdns['last_updated'] = datetime.datetime.utcnow()
        
        # Now get or create an Rdns record for this IP address
        obj, created = Rdns.objects.get_or_create(ip_address=rdns.get('ip_address'), defaults=rdns)
        
        if created:
            # Attempt an RDNS lookup, and remember to save this back to the object
            addr=reversename.from_address(rdns['ip_address'])
            # try:
            rdns['resolved_name'] = str(resolver.query(addr,"PTR")[0])
            # else:
            # PUT ERROR HANDLING IN HERE!
            obj['resolved_name'] = rdns.get('resolved_name')
            
            # Go get the location for this address
            rdns['country_code'] = self.geoip.country_code_by_addr(rdns.get('ip_address'))
            rdns['country_name'] = self.geoip.country_name_by_addr(rdns.get('ip_address'))
            
            obj.save()
        
        return obj



    def _file_request(self, request_string):
        "Get or create a FileRequest object for a given request string"
        return request_string



    def _referer(self, referer_string):
        "Get or create a Referer record for the given string"
        return referer_string



    def _user_agent(self, agent_string):
        "Get or create a UserAgent record for the given string"
        # Split the string into likely parts
        return agent_string
