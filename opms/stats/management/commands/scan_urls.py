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

        # Loop through stats.URLMonitorTask entries, build list of tasks to execute
        tasks = []
        for task in URLMonitorTask.objects.all():
            tasks.append(task)
        shuffle(tasks)


            record.resolved_name = self._rdns_lookup(record.ip_address)
            self.update_stats['update_count'] += 1
            if record.resolved_name == 'Unknown':
                self.update_stats['update_timeoutskips'] += 1

            # Update the record! - even if it comes back as Unknown, as the timestamp needs updating.
            record.last_updated = datetime.datetime.utcnow()
            record.save()

            if (self.update_stats.get('update_count') % 10) == 0:
                # Output the status
                try:
                    self.update_stats['update_rate'] = float(self.update_stats.get('update_count')) /\
                        float((datetime.datetime.utcnow() - self.update_stats.get('update_starttime')).seconds)
                except ZeroDivisionError:
                    self.update_stats['update_rate'] = 0

                print str(datetime.datetime.utcnow()) + ": " +\
                    "Parsed " + str(self.update_stats.get('update_count')) + " IP Addresses. " +\
                    "Skipped " + str(self.update_stats.get('update_timeoutskips')) + " IP Addresses. " +\
                    "Rate: " + str(self.update_stats.get('update_rate'))[0:6] + " IP Addresses/sec. "

                # Write the error cache to disk
                self._error_log_save()

            if self.stopcount > 0 and self.update_stats.get('update_count') > self.stopcount:
                print 'Stopping now having reached update limit\n'
                break

        # Final stats output at end of file
        try:
            self.update_stats['update_rate'] = float(self.update_stats.get('update_count')) /\
                float((datetime.datetime.utcnow() - self.update_stats.get('update_starttime')).seconds)
        except ZeroDivisionError:
            self.update_stats['update_rate'] = 0

        print "\nUpdate finished at " + str(datetime.datetime.utcnow()) +\
            "\nSkipped " + str(self.update_stats.get('update_timeoutskips')) + " IP Addresses. " +\
            "\nIP addresses parsed: " + str(self.update_stats.get('update_count')) +\
            "\nImported at " + str(self.update_stats.get('update_rate'))[0:6] + " IP Addresses/sec\n"

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()

        return None


def scan_url(url):
    USER_AGENT = 'OPMS/1.0 (Ubuntu 10.04; Virtual Server) Django/1.3.1'
    request = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)
    opener = urllib2.build_opener()
    time_of_request = time.localtime()
    start = time.time()
    request = opener.open(request)
    ttfb = time.time() - start
    output = request.read()
    ttlb = time.time() - start
    return url, time_of_request, ttfb, ttlb