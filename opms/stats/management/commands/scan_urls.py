# Perform Scan for all Tasks in URLMonitorList
# Author: Carl Marshall
# Last Edited: 03-11-2011
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from opms.stats.models import *
import datetime, sys
import urllib2, time
from random import shuffle

class Command(NoArgsCommand):
    help = 'Scan through URL Monitor Task entries and log the scan results'
#    option_list = NoArgsCommand.option_list + (
#        make_option('--stop-at', action='store', dest='stopcount',
#            default=0, help='Optional limit to the number of IP addresses to parse'),
#    )

    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        super(Command, self).__init__()


    def handle_noargs(self, **options):
        print "Scan URLs started at " + str(datetime.datetime.utcnow()) + "\n"

        # Create an error log
        self._errorlog_start('scan_urls.log')

        # Loop through stats.URLMonitorTask entries, build list of urls to test
        tasks = []
        task_counter = {}
        for task in URLMonitorTask.objects.filter(time_of_scan__isnull=True):
            tasks.extend([task]*task.iterations)
            task_counter[task] = 1
            # Update the task to show it has been run
            task.time_of_scan = datetime.datetime.utcnow()
            task.save()
        shuffle(tasks)
        print str(len(tasks)) + " tasks created"

        for n, task in enumerate(tasks):
            request = URLMonitorRequest()
            request.task = task
            request.iteration = int(task_counter.get(task))
            task_counter[task] += 1
            request.time_of_request, request.ttfb, request.ttlb = self.scan_url(task.url.url)
            request.save()
            print "Scanned " + str(n+1) + " of " + str(len(tasks))

        print "\nScan URLs finished at " + str(datetime.datetime.utcnow())

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()

        return None


    def scan_url(self, url):
        USER_AGENT = 'OPMS/1.0 (Ubuntu 10.04; Virtual Server) Django/1.3.1'
        request = urllib2.Request(url)
        request.add_header('User-Agent', USER_AGENT)
        opener = urllib2.build_opener()
        time_of_request = datetime.datetime.utcnow()
        start = time.time()
        request = opener.open(request)
        ttfb = time.time() - start
        output = request.read()
        ttlb = time.time() - start
        print str(time_of_request) + ":" + url + " - TTFB=" + str(ttfb) + " - TTLB=" + str(ttlb)
        return time_of_request, ttfb, ttlb


#    def setup_tasks(iterations = 10, comment = 'No Comment'):
#        for target in URLMonitorTarget.objects.all():
#            t = URLMonitorTask()
#            t.url = target
#            t.iterations = int(iterations)
#            t.comment = str(comment)
#            t.save()
#        return None


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