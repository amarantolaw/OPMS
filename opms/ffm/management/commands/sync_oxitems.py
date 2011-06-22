# Copy OxItems data into OPMS
# Author: Carl Marshall
# Last Edited: 21-06-2011
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from opms.ffm.models import *
from opms.oxitems.models import *
import datetime, sys

class Command(NoArgsCommand):
    help = 'Scan through OxItems database and import into OPMS:FFM'
    #option_list = NoArgsCommand.option_list + (
    #    make_option('--stop-at', action='store', dest='stopcount',
    #        default=0, help='Optional limit to the number of IP addresses to parse'),
    #)

    def __init__(self):
        """
        Setup variables used by the command
        """
        # Toggle debug statements on/off
        self.debug = True
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        self.import_stats = {}

        # Cache objects to hold ffm subtables in memory
        #self.cache_links = list(Link.objects.all())
        #self.cache_people = list(Person.objects.all())
        #self.cache_licences = list(Licence.objects.all())
        #self.cache_taggroups = list(TagGroup.objects.all())
        #self.cache_tags = list(Tag.objects.all()) # Probably need to rethink this!
        #self.cache_file_functions = list(FileFunction.objects.all())
        #self.cache_destinations = list(Destination.objects.all())
        #self.cache_units = list(Unit.objects.all())

        # Cache objects to hold oxitems-local subtables in memory
        #self.cache_importfeedchannel = ''
        #self.cache_importfeeddestinationchannel = ''
        #self.cache_importfileitem = ''
        #self.cache_importfileinfeeditem = ''
        #self.cache_importitemitem = ''

        super(Command, self).__init__()


    def handle_noargs(self, **options):
        print "Import started at " + str(datetime.datetime.utcnow()) + "\n"

        # Create an error log
        self._errorlog_start('sync_oxitems.log')

        # Reset statistics
        self.import_stats['update_count'] = 0
        self.import_stats['update_timeoutskips'] = 0
        self.import_stats['update_starttime'] = datetime.datetime.utcnow()

        self.stopcount = int(options.get('stopcount', 0))

        if not self.debug:
            # Copy Oxitems remote to Oxitems local, overwrite existing
            remote_channels = Rg07Channels.objects.using('oxitems').filter(channel_categories__icontains='simple-podcasting')
            total_count = len(remote_channels)
            for counter, row in enumerate(remote_channels):
                row.save(using='default')
                if counter == 0 or (counter % 100) == 0:
                    self._debug("Copied %s of %s channels" % (counter,total_count))
            self._debug("Channels copy finished")

            remote_items = Rg07Items.objects.using('oxitems').filter(item_channel__channel_categories__icontains='simple-podcasting')
            total_count = len(remote_items)
            for counter, row in enumerate(remote_items):
                row.save(using='default')
                if counter == 0 or (counter % 100) == 0:
                    self._debug("Copied %s of %s items" % (counter,total_count))
            self._debug("Items copy finished")


        # Import OxItems.Channels
        oxitems_channels = Rg07Channels.objects.filter(deleted=False)
        total_count = len(oxitems_channels)
        for counter, row in enumerate(oxitems_channels):
            # Update or create? Work from FeedGroup, through to Feed and beyond.
            if len(row.importfeedgroupchannel_set.all()) == 0:
                # Does this need merging with an existing feedgroup? Compare with existing titles. Basic exact match first...
                feed_group = {'title': row.title}
                fg, created = FeedGroup.objects.get_or_create(title=row.title, defaults=feed_group)
                if created:
                    self._debug("New FeedGroup created, id: " + str(fg.id) + ". Title=" + fg.title)
                    fg.save()
                else:
                    self._debug("FeedGroup found for merger, id: " + str(fg.id) + ". Title=" + fg.title)

                # Make link to import
                ifgc = ImportFeedGroupChannel()
                ifgc.feedgroup = fg
                ifgc.channel = row
                ifgc.save()
            else:
                fg = row.importfeedgroupchannel_set.get(channel=row) #NB: Channels N -> 1 FeedGroup relationship, even though it looks M2M
                self._debug("FeedGroup found, id: " + str(fg.id) + ". Title=" + fg.title)

            fg.title = row.title
            fg.description = row.description
            fg.internal_comments = row.channel_emailaddress
            fg.owning_unit = self._get_or_create_owning_unit(row.oxpoints_units)
            fg.save()

            
            self._debug("slug=" + row.name)
            #f.slug = row.name # NB: THESE ARE NOT UNIQUE IN OXITEMS. For the moment, cheat. Don't imported deleted, hence no duplicates.
            #f.last_updated = row.channel_updated
            #f.save()

            # Things to do after the Feed is created
            #self._set_feed_destinations(f, row.channel_guid, row.channel_tpi, row.deleted)
            #self._get_or_create_link(f, row.link)
            #self._parse_items(f, row.id, row.channel_sort_values)
            #self._set_jorum_tags(f, row.channel_jorumopen_collection)
            #self._get_or_create_artwork(f, row.channel_image)

            if counter == 0 or (counter % 50) == 0:
                self._debug("Parsed %s of %s Channels" % (counter,total_count))
            

        # Final stats output at end of file
        #try:
        #    self.import_stats['update_rate'] = float(self.import_stats.get('update_count')) /\
        #        float((datetime.datetime.utcnow() - self.import_stats.get('update_starttime')).seconds)
        #except ZeroDivisionError:
        #    self.import_stats['update_rate'] = 0

        print "\nUpdate finished at " + str(datetime.datetime.utcnow()) +\
        ""
        #    "\nSkipped " + str(self.import_stats.get('update_timeoutskips')) + " IP Addresses. " +\
        #    "\nIP addresses parsed: " + str(self.import_stats.get('update_count')) +\
        #    "\nImported at " + str(self.import_stats.get('update_rate'))[0:6] + " IP Addresses/sec\n"

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()
        return None


    def _get_or_create_owning_unit(self, oxpoints_unit):
        return Unit.objects.get(pk=1)

    def _set_jorum_tags(self, feed_obj, collection_string):
        return None

    def _get_or_create_link(self, feed_obj, url):
        return None

    # Import OxItems.Items, but done on a channel by channel basis
    def _parse_items(self, feed_obj, channel_id, sort_order):
        return None

    def _get_or_create_artwork(self, feed_obj, url):
        artwork = File()
        return None

    def _set_feed_destinations(self, feed_obj, itunesu_guid, oxitems_destination, oxitems_deleted):

        fd = FeedDestination()
        if oxitems_deleted == True:
            fd.withhold = 1000 # TODO: Need to determine some workflow values and descriptions for withhold
        return None

    """
        # Loop through stats.rdns entries that show as Unknown, attempt rdns lookup
        for record in Rdns.objects.filter(resolved_name='Unknown').order_by('last_updated'):
            record.resolved_name = self._rdns_lookup(record.ip_address)
            self.import_stats['update_count'] += 1
            if record.resolved_name == 'Unknown':
                self.import_stats['update_timeoutskips'] += 1

            # Update the record! - even if it comes back as Unknown, as the timestamp needs updating.
            record.last_updated = datetime.datetime.utcnow()
            record.save()

            if (self.import_stats.get('update_count') % 10) == 0:
                # Output the status
                try:
                    self.import_stats['update_rate'] = float(self.import_stats.get('update_count')) /\
                        float((datetime.datetime.utcnow() - self.import_stats.get('update_starttime')).seconds)
                except ZeroDivisionError:
                    self.import_stats['update_rate'] = 0

                print str(datetime.datetime.utcnow()) + ": " +\
                    "Parsed " + str(self.import_stats.get('update_count')) + " IP Addresses. " +\
                    "Skipped " + str(self.import_stats.get('update_timeoutskips')) + " IP Addresses. " +\
                    "Rate: " + str(self.import_stats.get('update_rate'))[0:6] + " IP Addresses/sec. "

                # Write the error cache to disk
                self._error_log_save()

            if self.stopcount > 0 and self.import_stats.get('update_count') > self.stopcount:
                print 'Stopping now having reached update limit\n'
                break



        return None
    """





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