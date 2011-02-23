# Import script for Apache Logfiles from media servers
# Author: Carl Marshall
# Last Edited: 4-2-2011
from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from opms.stats.models import *
from opms.stats.uasparser import UASparser
import apachelog, datetime, sys, pygeoip
from dns import resolver,reversename
from IPy import IP

class Command(LabelCommand):
    args = 'filename'
    help = 'Imports the contents of the specified logfile into the database.'
    option_list = LabelCommand.option_list + (
        make_option('--startline', action='store', dest='start_at_line',
            default=1, help='Optional start line to allow resumption of large log files'),
    )
    
    def __init__(self):
        # Single GeoIP object for referencing
        self.geoip = pygeoip.GeoIP('/home/carl/Projects/opms_master/OPMS/data/geoip/GeoIP.dat',pygeoip.MMAP_CACHE)
        # Single UASparser instand for referencing
        self.uasp = UASparser(cache_dir="/home/carl/Projects/opms_master/OPMS/opms/stats/ua_data/")
        # datetime value for any rdns timeout problems
        self.rdns_timeout = 0
        # Toggle debug statements on/off
        self.debug = False
        # Record basic information about the import process for reporting
        self.import_stats = {}
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""
        # Cache objects to hold subtables in memory 
        self.cache_user_agent = list(UserAgent.objects.all())
        self.cache_rdns = list(Rdns.objects.all())
        self.cache_referer = list(Referer.objects.all())
        self.cache_file_request = list(FileRequest.objects.all())
        self.cache_server = list(Server.objects.all())
        self.cache_log_entry = []


    def handle_label(self, filename, **options):
        print "Import started at " + str(datetime.datetime.utcnow()) + "\n"

        # Some basic checking
        if filename.endswith('.gz'):
           raise CommandError("This file is still compressed. Uncompress and try again.\n\n")

        # Create an error log per import file
        self._errorlog_start(filename + '_import-error.log')
    
        # Assume mpoau logfiles
        format = r'%Y-%m-%dT%H:%M:%S%z %v %A:%p %h %l %u \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
        
        # Reset statistics
        self.import_stats['filename'] = filename
        self.import_stats['line_counter'] = 0
        self.import_stats['line_count'] = 0
        self.import_stats['duplicatecount'] = 0
        self.import_stats['import_starttime'] = datetime.datetime.utcnow()
        self.import_stats['import_startline'] = int(options.get('start_at_line', 1))
        
        
        # Send the file off to be parsed
        self._parsefile(filename, format, self.import_stats.get('import_startline'))

        # Final stats output at end of file
        try:
            self.import_stats['import_rate'] = float(self.import_stats.get('line_counter')-self.import_stats.get('import_startline')) /\
                float((datetime.datetime.utcnow() - self.import_stats.get('import_starttime')).seconds)
        except ZeroDivisionError:
            self.import_stats['import_rate'] = 0               
        
        print "\nImport finished at " + str(datetime.datetime.utcnow()) +\
            "\nLines parsed: " + str(self.import_stats.get('line_counter')) +\
            "\nDuplicates: " + str(self.import_stats.get('duplicatecount')) +\
            "\nImported at " + str(self.import_stats.get('import_rate'))[0:6] + " lines/sec\n"
        
        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()
            
        return None



    def _parsefile(self, filename, log_format, start_at_line):
        # This only needs setting/getting the once per call of this function
        logfile_obj = self._logfile(filename)
        
        # Create a parser for this file
        parser = apachelog.parser(log_format)

        
        # Attempt to determine the number of lines in the log
        log = open(filename)
        for line in log:
            self.import_stats['line_count'] = self.import_stats.get('line_count') + 1
        print str(self.import_stats.get('line_count')) + " lines to parse. Beginning at line " + str(start_at_line) + "\n"
        log.close()

        log = open(filename)
        
        previous_line = ""
        for line in log:
            # Update stats
            self.import_stats['line_counter'] += 1
            if int(self.import_stats.get('line_counter')) < start_at_line:
                # Skip through to the specified line number
                previous_line = line
                continue
            
            # Test for duplicate log entries immediately preceding
            if line == previous_line:
                self._errorlog("##### DUPLICATE LINE DETECTED ##### \n" +\
                    "Logfile line:" + str(self.import_stats.get('line_counter')) + "\n" +\
                    "====================" + "\n" +\
                    "Line    : " + str(line) + "\n" +\
                    "--------------------" + "\n" +\
                    "Previous: " + str(previous_line)  + "\n" +\
                    "====================\n\n")
                self.import_stats['duplicatecount'] += 1
            else:
                # Parse and store the line
                self._parseline(parser, line, logfile_obj)

            # Print progress report every 500 lines.
            if (self.import_stats.get('line_counter') % 500) == 0:
                # Calculate the average rate of import for the whole process
                try: 
                    self.import_stats['import_rate'] = \
                    float(self.import_stats.get('line_counter') - self.import_stats.get('import_startline')) /\
                    float((datetime.datetime.utcnow() - self.import_stats.get('import_starttime')).seconds)
                except ZeroDivisionError:
                    self.import_stats['import_rate'] = 1
                # Calculate how long till finished
                efs = int(\
                    (int(self.import_stats.get('line_count')) - int(self.import_stats.get('line_counter')))\
                    / self.import_stats.get('import_rate'))
                efhr = efs // (60*60)
                efs = efs % (60*60)
                efmin = efs // 60
                efsec = efs % 60
                efstring = str(efhr) + "h " + str(efmin) + "m " + str(efsec) + "s."
                
                # Output the status
                print str(datetime.datetime.utcnow()) + ": " +\
                    str((float(self.import_stats.get('line_counter')) / float(self.import_stats.get('line_count')))*100)[0:5] + "% completed. " +\
                    "Parsed " + str(self.import_stats.get('line_counter')) + " lines. " +\
                    "Duplicates: " + str(self.import_stats.get('duplicatecount')) + ". " +\
                    "Rate: " + str(self.import_stats.get('import_rate'))[0:6] + " lines/sec. " +\
                    "Est. finish in " + efstring

            # Update duplicate line string for next pass
            previous_line = line
            
        return None



    def _logfile(self, filename):
        "Get or create a LogFile record for the given filename"
        
        # Simple hack for this method initially...
        logfile = {}
        logfile['service_name'] = "mpoau"
        logfile['file_name'] = "testname.log"
        logfile['file_path'] = "/testpath/"
        logfile['last_updated'] = datetime.datetime.utcnow()
        
        obj, created = LogFile.objects.get_or_create(
            service_name = logfile.get('service_name'),
            file_name = logfile.get('file_name'),
            file_path = logfile.get('file_path'),
            defaults = logfile)
        
        # If this isn't the first time, and the datetime is significantly different from last access, update the time
        if not created and (logfile.get('last_updated') - obj.last_updated).days > 0:
            obj.last_updated = logfile.get('last_updated')
        
        obj.save()

        return obj



    def _parseline(self, parser_obj, line, logfile_obj):
        # Parse the raw line into a dictionary of data
        data = parser_obj.parse(line)
        
        #self._debug('============================')
        #self._debug('Data: ' + str(data))

        # Validate the data - Count the number of elements
        if len(data) <> 11:
            self._errorlog("#### TOO FEW ITEMS IN THIS ENTRY. Line: " + str(self.import_stats.get('line_counter'))\
            + "Data:" + str(data))
            return
        
        # Status code validation
        status_code = self._status_code_validation(int(data.get('%>s')))
        if status_code == 0:
            self._errorlog("#### STATUS CODE 0 PROBLEM WITH THIS ENTRY. Line: " + str(self.import_stats.get('line_counter'))\
            + "Data:" + str(data))
            return
        
        # Get or create the foreign key elements, Logfile, Rdns, FileRequest, Referer, UserAgent
        remote_rdns = self._ip_to_domainname(data.get('%h'))
        
        file_request = self._file_request(data.get('%r'))
        if file_request == None:
            self._errorlog("#### INVALID REQUEST STRING IN THIS ENTRY. Line: " + str(self.import_stats.get('line_counter'))\
            + "Data:" + str(data))
            return
        
        referer = self._referer(data.get('%{Referer}i'), status_code)
        
        user_agent = self._user_agent(data.get('%{User-Agent}i'))
                        
        # Pull apart the date time string
        date_string, time_string = data.get('%Y-%m-%dT%H:%M:%S%z').split('T')
        date_yyyy, date_mm, date_dd = date_string.split('-')
        time_hh, time_mm, time_ss = time_string.split(':')
        
        # Pull apart the server and port
        server_ip, server_port = data.get('%A:%p').split(':')
        server = self._server(data.get('%v'), server_ip, server_port)
        
        # Size of response validation. Can be '-' when status not 200
        size_of_response = data.get('%b')
        if size_of_response.isdigit():
            size_of_response = int(size_of_response)
        else:
            size_of_response = 0
        
        # Build the log entry dictionary
        log_entry = {
            'logfile': logfile_obj,
            'time_of_request': datetime.datetime(
                int(date_yyyy), 
                int(date_mm), 
                int(date_dd), 
                int(time_hh), 
                int(time_mm), 
                int(time_ss[0:2]) # Cut off the +0000
                ),
            'server': server,
            'remote_logname': data.get('%l'),
            'remote_user': data.get('%u'),
            'remote_rdns': remote_rdns,
            'status_code': status_code,
            'size_of_response': size_of_response,
            'file_request': file_request,
            'referer': referer,
            'user_agent': user_agent,
        }
        
        # self._debug('log_entry=' + str(log_entry))
        
        # Create if there isn't already a duplicate record in place
        obj, created = self._get_or_create_log_entry(
            time_of_request = log_entry.get('time_of_request'),
            server = log_entry.get('server'),
            remote_rdns = log_entry.get('remote_rdns'),
            size_of_response = log_entry.get('size_of_response'),
            status_code = log_entry.get('status_code'),
            file_request = log_entry.get('file_request'),
            defaults = log_entry)

        #if created:
            # obj.save()
            # self._debug('#### Record imported\n' + str(obj))

        # TRACKING information needs to be parsed and stored now.
    
    # Bonus code here to split the arguments into tracking elements
    # tracking_list = fs[1].split('&')
    # for key_value in tracking_list:
    #    print "Key-Value = %s" % key_value
    # STORE THIS DATA EVENTUALLY!

        # Analyse obj.file_request.argument_string & obj.referer.full_string

        # self._debug('============================')
        return None



    def _get_or_create_log_entry(self, time_of_request, server, remote_rdns, size_of_response, \
        status_code, file_request, defaults = {}):
        cache_size = 100
        # Trusting that items in the import log appear in chronological order
        if len(self.cache_log_entry) == 0 or len(self.cache_log_entry) > (cache_size*2):
            self.cache_log_entry = list(LogEntry.objects.filter(time_of_request__gte=time_of_request).order_by('time_of_request'))[0:cache_size]

        # Attempt to locate in memory cache
        for item in self.cache_log_entry:
            if item.time_of_request == time_of_request and item.server == server and \
                item.remote_rdns == remote_rdns and item.size_of_response == size_of_response and \
                item.status_code == status_code and item.file_request == file_request:
                    
                self._errorlog("##### DUPLICATE RECORD AT INSERTION DETECTED ##### \n" +\
                    "Database row id: " + str(item.id) + "\n" +\
                    "DB: " + str(item) + "\n" +\
                    "--------------------" + "\n" +\
                    "Logfile line number:" + str(self.import_stats.get('line_counter')) + "\n\n")
                self.import_stats['duplicatecount'] = self.import_stats.get('duplicatecount') + 1
                
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = LogEntry()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.logfile = defaults.get('logfile')
        obj.time_of_request = defaults.get('time_of_request')
        obj.server = defaults.get('server')
        obj.remote_logname = defaults.get('remote_logname')
        obj.remote_user = defaults.get('remote_user')
        obj.remote_rdns = defaults.get('remote_rdns')
        obj.status_code = defaults.get('status_code')
        obj.size_of_response = defaults.get('size_of_response')
        obj.file_request = defaults.get('file_request')
        obj.referer = defaults.get('referer')
        obj.user_agent = defaults.get('user_agent')
        obj.save()
        
        self.cache_log_entry.append(obj)
        
        
        return obj, True



    def _status_code_validation(self,status_code):
        "Check the supplied status code value against known good codes"
        for item in LogEntry.STATUS_CODE_CHOICES:
            if status_code == item[0]:
                return status_code
        return 0


    def _ip_to_domainname(self, ipaddress):
        "Returns the domain name for a given IP where known"
        # self._debug('_ip_to_domainname('+str(ipaddress)+') called')
        # validate IP address
        # try: 
        adr = IP(ipaddress)
        # else:
        # PUT ERROR HANDLING IN HERE!
        
        rdns = {}
        rdns['ip_address'] = adr.strNormal(0)
        # rdns['ip_int'] = int(adr.strDec(0)) - No Longer needed for GeoIP helping
        rdns['resolved_name'] = 'Unknown'
        rdns['last_updated'] = datetime.datetime.utcnow()
        
        # Now get or create an Rdns record for this IP address
        #obj, created = Rdns.objects.get_or_create(ip_address=rdns.get('ip_address'), defaults=rdns)
        obj, created = self._get_or_create_rdns(ip_address=rdns.get('ip_address'), defaults=rdns)
        
        if created:
            # Look for the RDNS string of this address -- Removing this to test speed impact
            # obj.resolved_name = self._rdns_lookup(rdns.get('ip_address'))
            obj.resolved_name = "Unknown"
            
            # Go get the location for this address
            obj.country_code = self.geoip.country_code_by_addr(rdns.get('ip_address'))
            obj.country_name = self.geoip.country_name_by_addr(rdns.get('ip_address'))
            
            obj.save()

        return obj
        
        

    def _get_or_create_rdns(self, ip_address, defaults={}):
        # self._debug("_get_or_create_rdns(" + str(ip_address) + "," + str(defaults) + ")")
        # Attempt to locate in memory cache
        for item in self.cache_rdns:
            if item.ip_address == ip_address:
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = Rdns()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.ip_address = defaults.get('ip_address')
        obj.resolved_name = defaults.get('resolved_name')
        obj.last_updated = defaults.get('last_updated')
        obj.save()
        self.cache_rdns.insert(0,obj)
        
        return obj, True
        


    def _rdns_lookup(self, ipaddress):
        "Attempt an RDNS lookup for this ipaddress"
        # Default answer is the failure state of "Unknown"
        resolved_name = 'Unknown'

        # self._debug('_rdns_lookup('+str(ipaddress)+'): self.rdns_timeout=' + str(self.rdns_timeout))
        # Has a timeout occurred already? Was the timeout more than 30 seconds ago?
        if self.rdns_timeout == 0 or (datetime.datetime.utcnow() - self.rdns_timeout).seconds > 30:
            self.rdns_timeout = 0
            # Attempt an RDNS lookup, and remember to save this back to the object
            try:
                addr = reversename.from_address(ipaddress)
                resolved_name = str(resolver.query(addr,"PTR")[0])
                    
            except resolver.NXDOMAIN:
                self._errorlog('NXDOMAIN error trying to resolve:'+str(addr))
                resolved_name = 'No Resolved Name'
                    
            # Timeouts can be a problem with batch importing, use this to skip the issue for sorting later
            except resolver.Timeout:
                self.rdns_timeout = datetime.datetime.utcnow()
                self._errorlog('_rdns_lookup() FAILED due to TIMEOUT at ' + str(self.rdns_timeout))
                
            except resolver.NoAnswer:
                self.rdns_timeout = datetime.datetime.utcnow() 
                self._errorlog('_rdns_lookup() FAILED due to NO ANSWER at ' + str(self.rdns_timeout))
        else:
            self._errorlog('_rdns_lookup('+str(ipaddress)+') FAILED due to TIMEOUT at ' + str(self.rdns_timeout))
            
        # self._debug('_rdns_lookup('+str(ipaddress)+'): rdns='+resolved_name)
        
        return resolved_name



    def _file_request(self, request_string):
        "Get or create a FileRequest object for a given request string"
        # self._debug('_file_request(' + request_string + ')')
        # Example request strings
        # GET /philfac/lockelectures/locke_album_cover.jpg HTTP/1.1
        # GET / HTTP/1.0
        # GET /oucs/oxonian_interviews/300by300_interview.png HTTP/1.0
        # GET /robots.txt HTTP/1.0
        # GET /astro/introduction/astronomy_intro-medium-audio.mp3?CAMEFROM=podcastsGET HTTP/1.1
        # \xc5^)         <--- Example bad data in log from 2011
        
        fr = {}
        
        # Crude splitting... first on spaces, then on file/querystring
        ts = request_string.split()
        if len(ts) != 3:
            # Something is wrong with this request string. Exit and stop processing this record
            return None
        
        fs = ts[1].split('?')
        
        fr['method'] = ts[0]
        fr['uri_string'] = fs[0]
        fr['protocol'] = ts[2]
        
        # Querystring is optional, so test for it first.
        if len(fs)==2:
            fr['argument_string'] = fs[1]
        else:
            fr['argument_string'] = ""
        
        # Crude file typing (in lieu of an actual file database...)
        # Take the last three letters of the filename and compare to known types
        ft = fr.get('uri_string')[-3:].lower()
        fr['file_type'] = ""
        for item in FileRequest.FILE_TYPE_CHOICES:
            if ft == item[0]:
                fr['file_type'] = ft
        
        # Now get or create a FileRequest record for this string
        obj, created = self._get_or_create_file_request(
            method = fr.get('method'), 
            uri_string = fr.get('uri_string'),
            argument_string = fr.get('argument_string'),
            protocol = fr.get('protocol'),
            defaults = fr)
        
        # Redundant in this instance as nothing is modified after the get_or_create
        #if created:
        #    obj.save()
        
        return obj



    def _get_or_create_file_request(self, method, uri_string, argument_string, protocol, defaults={}):
        # Attempt to locate in memory cache
        for item in self.cache_file_request:
            if item.method == method and item.uri_string == uri_string and \
                item.argument_string == argument_string and item.protocol == protocol:
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = FileRequest()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.method = defaults.get('method')
        obj.uri_string = defaults.get('uri_string')
        obj.protocol = defaults.get('protocol')
        obj.argument_string = defaults.get('argument_string')
        obj.file_type = defaults.get('file_type')
        obj.save()
        self.cache_file_request.insert(0,obj)
        
        return obj, True



    def _referer(self, referer_string, status_code):
        "Get or create a Referer record for the given string"
        ref = {}
        ref['full_string'] = ""
        
        if status_code in (200,206,304):
            ref['full_string'] = referer_string
        
        # Now get or create a Referer record for this string
        obj, created = self._get_or_create_referer(
            full_string = ref.get('full_string'),
            defaults = ref)
        
        #if created:
        #    obj.save()
        
        return obj
        
        

    def _get_or_create_referer(self, full_string, defaults={}):
        # Attempt to locate in memory cache
        for item in self.cache_referer:
            if item.full_string == full_string:
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = Referer()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.full_string = defaults.get('full_string')
        obj.save()
        self.cache_referer.insert(0,obj)
        
        return obj, True



    def _user_agent(self, agent_string):
        "Get or create a UserAgent record for the given string"
        user_agent = {}
        
        # Store the full string for later analysis
        user_agent['full_string'] = agent_string
        
        # Create some defaults that we'll likely overwrite. OS and UA can be null, so ignore.
        user_agent['type'] = ""
        
        # Now get or create a UserAgent record for this string
        obj, created = self._get_or_create_user_agent(
            full_string = user_agent.get('full_string'), 
            defaults = user_agent)
        
        if created:
            # Parse the string to extract the easy bits
            try:
                uas_dict = self.uasp.parse(obj.full_string)
    
                #Set the type string
                obj.type = uas_dict.get('typ')
                
                # Deal with the OS record
                os = {}
                os['company'] = uas_dict.get('os_company')
                os['family'] = uas_dict.get('os_family')
                os['name'] = uas_dict.get('os_name')
                
                # Now get or create an OS record
                obj.os, created = OS.objects.get_or_create(
                    company = os.get('company'), 
                    family = os.get('family'), 
                    name = os.get('name'), 
                    defaults = os)
                if created:
                    obj.os.save()
                    
                
                # Deal with the UA record
                ua = {}
                ua['company'] = uas_dict.get('ua_company')
                ua['family'] = uas_dict.get('ua_family')
                ua['name'] = uas_dict.get('ua_name')
                
                # Now get or create an UA record
                obj.ua, created = UA.objects.get_or_create(
                    company = ua.get('company'), 
                    family = ua.get('family'), 
                    name = ua.get('name'), 
                    defaults = ua)
                if created:
                    obj.ua.save()
                    
            except uasparser.UASException:
                self._errorlog('_user_agent() FAILED. agent_string=' + str(agent_string))
            
            # Finally store the new and updated UserAgent object
            obj.save()
        
        return obj



    def _get_or_create_user_agent(self, full_string, defaults={}):
        # Attempt to locate in memory cache
        for item in self.cache_user_agent:
            if item.full_string == full_string:
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = UserAgent()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.full_string = defaults.get('full_string')
        obj.type = defaults.get('type')
        obj.save()
        self.cache_user_agent.insert(0,obj)
        
        return obj, True



    def _server(self, server_name, server_ip, server_port):
        "Store the server information"
        server = {}
        server['name'] = server_name
        server['ip_address'] = server_ip
        server['port'] = int(server_port)
        
        # Now get or create a Referer record for this string
        obj, created = Server.objects.get_or_create(
            name = server.get('name'),
            ip_address = server.get('ip_address'),
            port = server.get('port'),
            defaults = server)
        
        #if created:
        #    obj.save()
        
        return obj



    def _get_or_create_server(self, name, ip_address, port, defaults={}):
        # Attempt to locate in memory cache
        for item in self.cache_server:
            if item.name == name and item.ip_address == ip_address and item.port == port:
                return item, False
        
        # Couldn't find it in the list, now create an object, write to database and to cache
        obj = Server()
        # Set this manually, longhand because the for key,value loop causes errors
        obj.name = defaults.get('name')
        obj.ip_address = defaults.get('ip_address')
        obj.port = defaults.get('port')
        obj.save()
        self.cache_server.insert(0,obj)
        
        return obj, True


    # DEBUG AND INTERNAL HELP METHODS ==============================================================

    def _debug(self,error_str):
        "Basic optional debug function. Print the string if enabled"
        if self.debug:
            print 'DEBUG:' + str(error_str) + '\n'
        return None
            

    def _errorlog(self,error_str):
        "Write errors to a log file"
        # sys.stderr.write('ERROR:' + str(error_str) + '\n')
        #self.error_log.write('ERROR:' + str(error_str) + '\n')
        self.error_cache += 'ERROR:' + str(error_str) + '\n'
        return None


    def _errorlog_start(self, path_to_file):
        try:
            self.error_log = open(path_to_file,'a') 
        except IOError:
            sys.stderr.write("WARNING: Could not open existing error file. New file being created")
            self.error_log = open(path_to_file,'w')
        
        self.error_log.write("Log started at " + str(datetime.datetime.utcnow()) + "\n")
        print "Writing errors to: " + path_to_file
        return None

    def _error_log_save(self):
        "Write errors to a log file"
        self.error_log.write(self.error_cache)
        self.error_cache = ""
        return None


    def _errorlog_stop(self):
        self.error_log.write("Log ended at " + str(datetime.datetime.utcnow()) + "\n")
        self.error_log.close()
        return None