# Perform Scan for all Tasks in URLMonitorList
# Author: Carl Marshall
# Last Edited: 04-19-2011
from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from opms.monitors.models import *
from opms.utils import debug
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
        verbosity = int(options.get('verbosity', 0))
        if verbosity > 1:
            debug.DEBUG = True

        print "Scan URLs started at {0}\n".format(datetime.datetime.utcnow())

        # Some basic checking
        if comment == '':
           raise CommandError("Please specify a comment for this scan.\n\n")

        iterations = int(options.get('iterations', 10))

        # Create an error log
        debug.errorlog_start('scan_urls.log')
        debug.errorlog("Log started for: " + comment)

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
        out_str = "{0} scans performed ({1} iterations of {2} urls)".format(count-1, iterations, len(targets))
        print out_str
        debug.errorlog(out_str)
        
        t.completed = True
        t.save()

        print "\nScan URLs finished at " + str(datetime.datetime.utcnow())

        # Write the error cache to disk
        debug.errorlog_stop()

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
        debug.onscreen("{0}:{1} - TTFB={2} - TTLB={3}".format(time_of_request, url, ttfb, ttlb))
        return status, time_of_request, ttfb, ttlb
