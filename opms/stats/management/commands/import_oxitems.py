# Import basic OxItems data into OPMS:stats
# Author: Carl Marshall
# Last Edited: 16-04-2012
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from opms.stats.models import TrackGUID
from opms.oxitems.models import Rg07Channels, Rg07Items
import sys
from datetime import datetime
from django.utils.encoding import smart_str, smart_unicode

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--no-sync', action='store', dest='no_sync', default=False,
            help='Use this to skip the sync with OxItems live data'),
        )
    help = 'Scan through OxItems database and import basic info into OPMS:Stats'

    def __init__(self):
        """
        Setup variables used by the command
        """
        # Toggle debug statements on/off
        self.debug = False
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        self.import_stats = {}
        self.no_sync = False

        super(Command, self).__init__()


    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 0))
        if verbosity > 1:
            self.debug = True


        # Create an error log
        print "Import started at " + str(datetime.utcnow()) + "\n"
        self._errorlog_start('import_oxitems.log')

        # Reset statistics
        self.import_stats['channel_count'] = 0
        self.import_stats['item_count'] = 0
        self.import_stats['update_starttime'] = datetime.utcnow()

        self.no_sync = bool(options.get('no_sync', False))

        if not self.debug and not self.no_sync:
            print "Synchronising Databases (OxItems -> OPMS)"
            # Copy Oxitems remote to Oxitems local, overwrite existing
            remote_channels = Rg07Channels.objects.using('oxitems').filter(channel_categories__icontains='simple-podcasting')
            total_count = len(remote_channels)
            for counter, row in enumerate(remote_channels):
                row.save(using='default')
                if counter == 0 or (counter % 50) == 0:
                    print "Copied %s of %s channels" % (counter,total_count)
            print "Channels copy finished"

            remote_items = Rg07Items.objects.using('oxitems').filter(item_channel__channel_categories__icontains='simple-podcasting')
            total_count = len(remote_items)
            for counter, row in enumerate(remote_items):
                row.save(using='default')
                divisor = int(total_count / 20)
                if counter == 0 or (counter % divisor) == 0: # Aim for reports every 5% complete
                    percentage = int((float(counter) / total_count) * 100)
                    print "Copied %s (%s%%) of %s items" % (counter, percentage, total_count)
            print "Items copy finished"
        else:
            print "Skipping Database Synchronisation"

        # Get list of Oxitems data to scan through
        oxitems = list(Rg07Items.objects.order_by('item_guid','-modified'))
        print "OxItems Import beginning scan of Track records"
        for track in TrackGUID.objects.all():
            for item in oxitems:
                if track.guid == item.item_guid:
                    self._debug(track.guid + ' - ' + item.item_title)
                    track.name = item.item_title
                    track.deleted = item.deleted
                    track.save()
            else:
                self._debug(track.guid + ' - *************** UNKNOWN GUID *************** ')
        print "OxItems import finished"
        return None


    # DEBUG AND INTERNAL HELP METHODS ==============================================================

    def _debug(self,error_str):
        "Basic optional debug function. Print the string if enabled"
        if self.debug:
            print 'DEBUG:' + smart_unicode(error_str) + '\n'
        return None

    def _errorlog(self,error_str):
        "Write errors to a log file"
        self.error_cache += 'ERROR:' + smart_unicode(error_str) + '\n'
        return None


    def _errorlog_start(self, path_to_file):
        try:
            self.error_log = open(path_to_file,'a')
        except IOError:
            sys.stderr.write("WARNING: Could not open existing error file. New file being created")
            self.error_log = open(path_to_file,'w')

        self.error_log.write("Log started at " + str(datetime.utcnow()) + "\n")
        print "Writing errors to: " + path_to_file
        return None

    def _error_log_save(self):
        "Write errors to a log file"
        self.error_log.write(self.error_cache)
        self.error_cache = ""
        return None


    def _errorlog_stop(self):
        self.error_log.write("Log ended at " + str(datetime.utcnow()) + "\n")
        self.error_log.close()
        return None