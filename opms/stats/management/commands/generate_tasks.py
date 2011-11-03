# Perform Scan for all Tasks in URLMonitorList
# Author: Carl Marshall
# Last Edited: 03-11-2011
from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from opms.stats.models import *
import datetime, sys
import urllib2, time
from random import shuffle

class Command(LabelCommand):
    help = 'Scan through URL Monitor Target entries and generate new Tasks'
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


    def handle_label(self, iterations = 10, comment = 'No Comment', **options):
        print "Generate Tasks started at " + str(datetime.datetime.utcnow()) + "\n"

        # Create an error log
        self._errorlog_start('generate_tasks.log')

        count = 0
        for target in URLMonitorTarget.objects.all():
            t = URLMonitorTask()
            t.url = target
            t.iterations = int(iterations)
            t.comment = str(comment)
            t.save()
            count += 1
        print str(count) + " tasks created"

        print "\nGenerate Tasks finished at " + str(datetime.datetime.utcnow())

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()

        return None


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