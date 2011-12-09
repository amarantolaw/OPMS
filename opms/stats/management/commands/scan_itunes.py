# Perform various scans of URLs from iTunes Store
# Author: Carl Marshall
# Last Edited: 08-12-2011
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from opms.stats.models import *
from opms.stats.utils import itunes as itunes
import datetime, sys, urllib2, time


class Command(BaseCommand):
    help = 'Scan iTunes U Service (1:Institutional collection <default>; 2:Top Collections; 3:Top Downloads)'
    args = "<url>"
    label = "url"
    option_list = BaseCommand.option_list + (
        make_option('--mode', action='store', dest='mode',
            default=1, help='Specify the type of scan to be done (1,2,3)'),
    )

    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        super(Command, self).__init__()

    def handle(self, url = None,**options):
        # Some basic error checking
        mode = options.get("mode",1)
        if not mode.isdigit() or mode < 1 or mode > 3:
           raise CommandError("""Please specify a mode for this scan.
               1) Scan an institution's collection
               2) Scan the Top Collections chart
               3) Scan the Top Downloads chart
               """)
        if url is None:
            raise CommandError("Please specify the url to scan.")

        print "Scan iTunes started at " + str(datetime.datetime.utcnow()) + "\n"
        # Create an error log
        self._errorlog_start('scan_itunes.log')

        if mode == 1:
            comment = "Scan of an Institution's collection from %s" % url
            self._errorlog("Log started for: %s" % comment)

            # TODO: Check that the pattern of the URL looks like what we expect of an institutional url
            # TODO: Get the institutions collections
            #collection = itunes.get_institution_collections(url)
            # TODO: Iterate, parse and store the items from the collection
            #series = itunes.get_collection_items(series_url)
            print comment
        elif mode == 2:
            comment = "Scan of an Top Collections Chart from %s" % url
            self._errorlog("Log started for: %s" % comment)
            print comment

        elif mode == 3:
            comment = "Scan of an Top Downloads Chart from %s" % url
            self._errorlog("Log started for: %s" % comment)
            print comment
        else:
            comment = "We shouldn't ever get this scan..."
            print comment


        print "\nScan iTunes finished at " + str(datetime.datetime.utcnow())

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