# Import script for Apple Raw Logfiles from Apple PSM Reports page
# Author: Carl Marshall
# Last Edited: 29-5-2012
from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from opms.stats.models import LogFile, AppleRawLogEntry, UserAgent, Rdns
from opms.stats.uasparser import UASparser, UASException
import datetime, time, sys, os, pygeoip, csv
from datetime import timedelta
from IPy import IP
from settings import PROJECT_ROOT

class Command(LabelCommand):
    args = 'filename'
    help = 'Imports the contents of the specified logfile into the database.'
    option_list = LabelCommand.option_list + (
        make_option('--startline', action='store', dest='start_at_line',
            default=1, help='Optional start line to allow resumption of large log files. Default is 1.'),
#        make_option('--single-import', action='store', dest='single_import',
#            default=True, help='Speeds up import rate by disabling support for parallel imports.'),
    )
    
    def __init__(self):
        # Single GeoIP object for referencing
        self.geoip = pygeoip.GeoIP(os.path.join(PROJECT_ROOT, "stats/geoip_data/GeoIP.dat"),pygeoip.MMAP_CACHE)
        # Single UASparser instand for referencing
        self.uasp = UASparser(cache_dir=os.path.join(PROJECT_ROOT, "stats/ua_data/"))
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
#        # Option flag to enable or disable the parallel import safety checks
#        self.single_import = True
        
        super(Command, self).__init__()


    def handle_label(self, filename, **options):
        print "Import started at {0:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.utcnow())

        # Some basic checking
        if not filename.endswith('.txt'):
           raise CommandError("This is not a text (.txt) log file.\n\n")

        # Create an error log per import file
        self._errorlog_start(filename + '_import-error.log')

        # Reset statistics
        self.import_stats['filename'] = filename
        self.import_stats['line_counter'] = 0
        self.import_stats['line_count'] = 0
#        self.import_stats['duplicatecount'] = 0
        self.import_stats['import_starttime'] = datetime.datetime.utcnow()
        self.import_stats['import_startline'] = int(options.get('start_at_line', 1))

        # This only needs setting/getting the once per call of this function
        logfile_obj = self._logfile(filename, 'itu-raw')

        # Send the file off to be parsed
        self._parsefile(logfile_obj)
#
        # Final stats output at end of file
        try:
            self.import_stats['import_duration'] = float((datetime.datetime.utcnow() - self.import_stats.get('import_starttime')).seconds)
            self.import_stats['import_rate'] = float(self.import_stats.get('line_counter')-self.import_stats.get('import_startline')) /\
                                                    self.import_stats['import_duration']
        except ZeroDivisionError:
            self.import_stats['import_rate'] = 0

        print """
            Import finished at {0:%Y-%m-%d %H:%M:%S}
            {1:d} Lines parsed over {2:.1f} seconds
            Giving a rate of {3:.3f} lines/sec
            """.format(
                datetime.datetime.utcnow(),
                self.import_stats.get('line_counter'),
                self.import_stats.get('import_duration'),
                self.import_stats.get('import_rate')
            )
        
        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()
            
        return None



    def _logfile(self, filename, log_service):
        """Get or create a LogFile record for the given filename"""
        
        # Simple hack for this method initially...
        logfile = dict()
        logfile['service_name'] = log_service
        try:
            logfile['file_name'] = filename[filename.rindex('/')+1:]
            logfile['file_path'] = filename[:filename.rindex('/')+1]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            logfile['file_name'] = filename
            logfile['file_path'] = "./"
            
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



    def _parsefile(self, logfile_obj):
        filename = logfile_obj.file_path + logfile_obj.file_name

        datareader = csv.reader(open(filename), dialect='excel-tab')
        tsvdata = []
        # The data structure changes over time, and new columns are added (and perhaps removed) so map each file to a dictionary
        column_headers = []
        for i,row in enumerate(datareader):
            if i==0:
                for col, title in enumerate(row):
                    column_headers.append(title.lower())
            else:
                row_dict = dict()
                for col, title in enumerate(column_headers):
                    row_dict[title] = row[col]
                tsvdata.append(row_dict)
            self.import_stats['line_counter'] = i
        self.import_stats['line_count'] = len(tsvdata)
        # Reset line counter for parsing scan
        self.import_stats['line_counter'] = self.import_stats.get('import_startline')

        for i in range(self.import_stats.get('line_counter'),len(tsvdata)):
            self._parseline(tsvdata[i], logfile_obj)
            self.import_stats['line_counter'] = i

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
                try:
                    efs = int(
                        float(self.import_stats.get('line_count') - self.import_stats.get('line_counter')) /\
                        float(self.import_stats.get('import_rate'))
                    )
                except ZeroDivisionError:
                    efs = 1
                efhr = efs // (60*60)
                efs = efs % (60*60)
                efmin = efs // 60
                efsec = efs % 60
                efstring = "{0:d}h {1:d}m {2:d}s".format(efhr,efmin,efsec)

                # Output the status
                print "{0:%Y-%m-%d %H:%M:%S} : {1:.1%} completed. Parsed {2:d} lines. Rate: {3:.2f} lines/sec. Estimated finish in {4}".format(
                    datetime.datetime.utcnow(),
                    (float(self.import_stats.get('line_counter')) / float(self.import_stats.get('line_count')))*100,
                    self.import_stats.get('line_counter'),
                    self.import_stats.get('import_rate'),
                    efstring
                )

                # Write the error cache to disk
                self._error_log_save()
        return None



    def _parseline(self, entrydict, logfile_obj):
#        # Build the log entry dictionary
#        arle = {
#            "logfile" : logfile_obj,
#            "artist_id" : long(entrydict.get("artist_id")),
#            "itunes_id" : long(entrydict.get("itunes_id")),
#            "action_type" : self._action_type_validation(entrydict.get("action_type")),
#            "title" : entrydict.get("title","Unknown"),
#            "url" : entrydict.get("url",""),
#            "episode_id" : long(entrydict.get("episode_id",0)),
#            "episode_title" : entrydict.get("episode_title",None),
#            "episode_type" : entrydict.get("episode_type",None),
#            "storefront" : int(entrydict.get("storefront",0)),
#            "user_agent" : self._user_agent(entrydict.get("useragent","")),
#            "ipaddress" : self._ip_to_domainname(entrydict.get("ip_address",None)),
#            "timestamp" : self._parse_timestamp(entrydict.get("timestamp")),
#            "user_id" : entrydict.get("user_id","")
#        }

        # Build the log entry dictionary
        arle = AppleRawLogEntry()
        arle.logfile = logfile_obj
        arle.artist_id = long(entrydict.get("artist_id"))
        arle.itunes_id = long(entrydict.get("itunes_id"))
        arle.action_type = self._action_type_validation(entrydict.get("action_type"))
        arle.title = entrydict.get("title","Unknown")
        arle.url = entrydict.get("url","")
        arle.episode_id = long(entrydict.get("episode_id",0))
        arle.episode_title = entrydict.get("episode_title",None)
        arle.episode_type = entrydict.get("episode_type",None)
        arle.storefront = int(entrydict.get("storefront",0))
        arle.user_agent = self._user_agent(entrydict.get("useragent",""))
        arle.ipaddress = self._ip_to_domainname(entrydict.get("ip_address",None))
        arle.timestamp = self._parse_timestamp(entrydict.get("timestamp"))
        arle.user_id = entrydict.get("user_id","")
        arle.save(force_insert=True)

        return None


    def _action_type_validation(self, action_string):
        """Analyse the supplied action type string, and see if it's one we know about already. If it isn't, then
        don't panic, and store it anyway. We just need to update the choices list based on what we see in the error
        logs """
        for item in AppleRawLogEntry.ACTION_TYPE_CHOICES:
            if action_string == item[0]:
                return action_string
        self._errorlog(
            "#### PROBLEM WITH THIS ENTRY. Unknown Action Type ({0}) Line: {1:d}\n".format(
                action_string,
                self.import_stats.get('line_counter')
            )
        )
        return action_string




    def _ip_to_domainname(self, ipaddress):
        """Returns the domain name for a given IP where known"""
        # self._debug('_ip_to_domainname('+str(ipaddress)+') called')
        # These are partial ipaddress of the format nnn.nnn.x.x so replace the x with 0 as a guess.
        if ipaddress: # i.e. not None
            adr = IP(ipaddress.replace('x','0'))

            rdns = Rdns()
            rdns.ip_address = adr.strNormal(0)
            rdns.resolved_name = 'Partial'
            rdns.last_updated = datetime.datetime.utcnow()

            # Attempt to locate in memory cache
            for item in self.cache_rdns:
                if item.ip_address == rdns.ip_address:
                    return item

            # Couldn't find it in the list
            rdns.country_code = self.geoip.country_code_by_addr(rdns.ip_address)
            rdns.country_name = self.geoip.country_name_by_addr(rdns.ip_address)
            rdns.save()

            self.cache_rdns.insert(0,rdns)
        
            return rdns
        else:
            return None
        


    def _user_agent(self, agent_string):
        "Get or create a UserAgent record for the given string"
        user_agent = UserAgent()
        
        # Store the full string for later analysis
        user_agent.full_string = agent_string
        
        # Create some defaults that we'll likely overwrite. OS and UA can be null, so ignore.
        user_agent.type = ""            
            
        # Attempt to locate in memory cache
        for item in self.cache_user_agent:
            if item.full_string == user_agent.full_string:
                return item
                
        # Parse the string to extract the easy bits
        try:
            uas_dict = self.uasp.parse(user_agent.full_string)

            #Set the type string
            user_agent.type = uas_dict.get('typ')[:50]

            # Deal with the OS record
            os = {}
            os['company'] = uas_dict.get('os_company')[:200]
            os['family'] = uas_dict.get('os_family')[:100]
            os['name'] = uas_dict.get('os_name')[:200]

            # Now get or create an OS record
            user_agent.os, created = OS.objects.get_or_create(
                company = os.get('company'),
                family = os.get('family'),
                name = os.get('name'),
                defaults = os)
            if created:
                user_agent.os.save()

            # Deal with the UA record
            ua = {}
            ua['company'] = uas_dict.get('ua_company')[:200]
            ua['family'] = uas_dict.get('ua_family')[:100]
            ua['name'] = uas_dict.get('ua_name')[:200]

            # Now get or create an UA record
            user_agent.ua, created = UA.objects.get_or_create(
                company = ua.get('company'),
                family = ua.get('family'),
                name = ua.get('name'),
                defaults = ua)
            if created:
                user_agent.ua.save()

        except UASException:
            self._errorlog('_user_agent() parsing FAILED. agent_string=' + str(agent_string) + "\n")

        #Not there, so write to database
        user_agent.save()
        
        # Update the cache
        self.cache_user_agent.insert(0,user_agent)
        
        return user_agent



    def _parse_timestamp(self,initialstring):
        """Adjust timestamp supplied to GMT and returns a datetime object"""
        input_format = "%Y-%m-%d %H:%M:%S"
        base_time = time.strptime(initialstring[:-9],input_format)
        try:
            offset = int(initialstring[-5:])
            delta = timedelta(hours = offset / 100)
            ts = base_time - delta
        except:
            ts = base_time
        dt = datetime.datetime.fromtimestamp(time.mktime(ts))
        return dt #"{0:%Y-%m-%d %H:%M:%S}".format(ts)


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