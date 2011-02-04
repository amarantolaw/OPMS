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
        
# Locate file
# Open file
# Read line by line
#  parse line
#  store in relevant fields
#  do associated lookups and stores

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
                
                # Pull apart the date time string
                date_string, time_string = data.get('%Y-%m-%dT%H:%M:%S%z').split('T')
                date_yyyy, date_mm, date_dd = date_string.split('-')
                time_hh, time_mm, time_ss = time_string.split(':')
                # Pull apart the server and port
                server_ip, server_port = data.get('%A:%p').split(':')
                
                log_entry = {
                    'logfile': filename,
                    'time_of_request': datetime.datetime(date_yyyy, date_mm, date_dd, time_hh, time_mm, time_ss),
                    'server_name': data.get('%v'),
                    'server_ip': server_ip,
                    'server_port': int(server_port),
                    'remote_ip': data.get('%h'),
                    'remote_logname': data.get('%l'),
                    'remote_user': data.get('%u'),
                    'remote_rdns': self._ip_to_domainname(data.get('%h')),
                    'status_code': int(data.get('%>s')),
                    'size_of_response': int(data.get('%b')),
                    'file_request': data.get('%r'),
                    'referer': data.get('%{Referer}i'),
                    'user_agent': data.get('%{User-Agent}i'),
                }
                
                print data
                print log_entry
                
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


# Reverse DNS====
# from dns import resolver,reversename
# addr=reversename.from_address("192.168.0.1")
# str(resolver.query(addr,"PTR")[0])

    def _ip_to_domainname(ipaddress):
        return "www.%s.com" % ipaddress