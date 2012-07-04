# Perform Scan for all Tasks in URLMonitorList
# Author: Carl Marshall
# Last Edited: 04-19-2011
from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from opms.monitors.models import *
import datetime, sys, urllib2, time


class Command(LabelCommand):
    help = 'Scan through URL Monitor Target entries and generate new Tasks'
    option_list = LabelCommand.option_list + (
        make_option('--iterations', action='store', dest='iterations',
            default=10, help='Specify a number of iterations each URLs is to be scanned'),
    )

    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        super(Command, self).__init__()

    def handle_label(self, comment = '', **options):
        print "Scan URLs started at " + str(datetime.datetime.utcnow()) + "\n"

        # Some basic checking
        if comment == '':
           raise CommandError("Please specify a comment for this scan.\n\n")

        iterations = int(options.get('iterations', 10))

        # Create an error log
        self._errorlog_start('scan_urls.log')
        self._errorlog("Log started for: " + comment)

        t = URLMonitorTask()
        t.comment = str(comment)
        t.save()

        targets = URLMonitorURL.objects.filter(active__exact=True)
        count = 1
        for iter in range(1,iterations+1):
            for target in targets:
                s = URLMonitorScan()
                s.url = target
                s.task = t
                s.iteration = iter
                try:
                    s.status_code, s.time_of_request, s.ttfb, s.ttlb = self.scan_url(target.url)
                except urllib2.HTTPError, e:
                    s.status_code = e.code
                    s.time_of_request = datetime.datetime.utcnow()
                s.save()
                count += 1
        out_str = str(count-1) + " scans performed (" + str(iterations) + " iterations of " + str(len(targets)) + " urls)"
        print out_str
        self._errorlog(out_str)
        
        t.completed = True
        t.save()

        print "\nScan URLs finished at " + str(datetime.datetime.utcnow())

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()

        return None


    def scan_url(self, url):
        USER_AGENT = 'OPMS/1.0 (Ubuntu 10.04; Virtual Server) Django/1.4.0'
        request = urllib2.Request(url)
        request.add_header('User-Agent', USER_AGENT)
        opener = urllib2.build_opener()
        time_of_request = datetime.datetime.utcnow()
        start = time.time()
        request = opener.open(request)
        ttfb = time.time() - start
        output = request.read()
        status = 200 # Presumed because there would be an error otherwise
        ttlb = time.time() - start
        print str(time_of_request) + ":" + url + " - TTFB=" + str(ttfb) + " - TTLB=" + str(ttlb)
        return status, time_of_request, ttfb, ttlb


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