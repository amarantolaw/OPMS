# Import script for Apache Logfiles from media servers
# Author: Carl Marshall
# Last Edited: 4-2-2011

from django.core.management.base import BaseCommand, CommandError
from opms.stats.models import *
import apachelog, datetime, sys
from dns import resolver,reversename
        
class Command(BaseCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'

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
                    'server_ip': server_ip,
                    'server_port': int(server_port),
                    'remote_ip': data.get('%h'),
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


        
# Locate file
# Open file
# Read line by line
#  parse line
#  store in relevant fields
#  do associated lookups and stores
                
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

            print "Import finished\n\n"


    def _logfile(self, filename):
        "Get or create a LogFile record for the given filename"
        return filename

# Reverse DNS====
# from dns import resolver,reversename
# addr=reversename.from_address("192.168.0.1")
# str(resolver.query(addr,"PTR")[0])

    def _ip_to_domainname(self, ipaddress):
        "Returns the domain name for a given IP where known"
        return "www.%s.com" % ipaddress

    def _file_request(self, request_string):
        "Get or create a FileRequest object for a given request string"
        return request_string
        
    def _referer(self, referer_string):
        "Get or create a Referer record for the given string"
        return referer_string
        
    def _user_agent(self, agent_string):
        "Get or create a UserAgent record for the given string"
        # Split the string into likely parts
        # ua, created = UserAgent.objects.get_or_create(field=value, field=value, defaults=everything)

        # obj, created = Preview.objects.get_or_create(week_ending=report.get('week_ending'), handle=report.get('handle'), defaults=report)
            
        # if created:
        #     obj.save()
        # else:

        return agent_string
        
