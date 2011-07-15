# Copy OxItems data into OPMS
# Author: Carl Marshall
# Last Edited: 21-06-2011
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from opms.ffm.models import *
from opms.oxitems.models import *
import sys, re
from datetime import datetime
from dateutil import parser
from django.utils.encoding import smart_str, smart_unicode

class Command(NoArgsCommand):
    help = 'Scan through OxItems database and import into OPMS:FFM'
    option_list = NoArgsCommand.option_list + (
        make_option('--no-sync', action='store', dest='no_sync',
            default=False, help='Use this to skip the sync with OxItems live data'),
    )

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

        super(Command, self).__init__()


    def handle_noargs(self, **options):
        print "Import started at " + str(datetime.utcnow()) + "\n"

        # Create an error log
        self._errorlog_start('sync_oxitems.log')

        # Reset statistics
        self.import_stats['channel_count'] = 0
        self.import_stats['item_count'] = 0
        self.import_stats['person_created'] = 0
        self.import_stats['tag_created'] = 0
        self.import_stats['file_created'] = 0
        self.import_stats['feed_created'] = 0
        self.import_stats['feedgroup_created'] = 0
        self.import_stats['update_starttime'] = datetime.utcnow()

        self.no_sync = bool(options.get('no_sync', False))

        if not self.debug or self.no_sync:
            print "Synchronising Databases (OxItems -> OPMS)"
            # Copy Oxitems remote to Oxitems local, overwrite existing
            remote_channels = Rg07Channels.objects.using('oxitems').filter(channel_categories__icontains='simple-podcasting')
            total_count = len(remote_channels)
            for counter, row in enumerate(remote_channels):
                row.save(using='default')
                if counter == 0 or (counter % 100) == 0:
                    print "Copied %s of %s channels" % (counter,total_count)
            print "Channels copy finished"

            remote_items = Rg07Items.objects.using('oxitems').filter(item_channel__channel_categories__icontains='simple-podcasting')
            total_count = len(remote_items)
            for counter, row in enumerate(remote_items):
                row.save(using='default')
                if counter == 0 or (counter % int(total_count / 10)) == 0: # Aim for reports every 10% complete
                    # print "Copied %s of %s items" % (counter,total_count)
                    percentage = int(counter / int(total_count / 10)) * 10
                    print "Copied %s%% of items" % (percentage)
            print "Items copy finished"


        # Import OxItems.Channels
        oxitems_channels = Rg07Channels.objects.all() # filter(deleted=False)
        total_count = len(oxitems_channels)
        print "Processing OxItems Channel Data into OPMS (" + str(total_count) + " rows to do)"
        for counter, row in enumerate(oxitems_channels):
            # Update or create ***FeedGroup***
            if len(row.importfeedgroupchannel_set.all()) == 0:
                # Does this need merging with an existing feedgroup? Compare with existing titles. Basic exact match first...
                feed_group = {
                    'title': row.title, 
                    'description':row.description,
                    'internal_comments':row.channel_emailaddress,
                    'owning_unit':self._get_or_create_owning_unit(row.oxpoints_units)
                }
                fg, created = FeedGroup.objects.get_or_create(title=row.title, defaults=feed_group)
                if created:
                    self._debug("New FeedGroup created, id: " + str(fg.id) + ". Title=" + fg.title)
                    self.import_stats['feedgroup_created'] = self.import_stats.get('feedgroup_created') + 1
                    fg.save()
                else:
                    self._debug("FeedGroup found for merger, id: " + str(fg.id) + ". Title=" + fg.title)

                # Make link to import
                ifgc = ImportFeedGroupChannel()
                ifgc.feedgroup = fg
                ifgc.channel = row
                ifgc.save()
            else:
                fg = row.importfeedgroupchannel_set.get(channel=row).feedgroup #NB: Channels N -> 1 FeedGroup relationship, even though it looks M2M
                self._debug("FeedGroup found, id: " + str(fg.id) + ". Title=" + fg.title)

            # Update the information if this is not a deleted record
            if not row.deleted:
                fg.title = row.title
                fg.description = row.description
                fg.internal_comments = row.channel_emailaddress
                fg.owning_unit = self._get_or_create_owning_unit(row.oxpoints_units)
                fg.save()
            # Things to do after the FeedGroup is created/found, regardless of deleted state
            self._get_or_create_link(fg, row.link)
            self._set_jorum_tags(fg, row.channel_jorumopen_collection)

            # Update or create ***Feed***
            if len(row.importfeedchannel_set.all()) == 0: # Create Feed
                feed = {
                    'slug':row.name,
                    'feed_group':fg,
                    'last_updated':row.channel_updated
                }
                f, created = Feed.objects.get_or_create(slug=row.name, defaults=feed)
                if created:
                    f.save()
                    self._debug("Feed created, id:" + str(f.id) + ". slug=" + f.slug)
                    self.import_stats['feed_created'] = self.import_stats.get('feed_created') + 1
                else:
                    self._debug("Feed found for merger, id: " + str(f.id) + ". slug=" + f.slug)

                # Make link to import
                ifc = ImportFeedChannel()
                ifc.feed = f
                ifc.channel = row
                ifc.save()
            else:
                f = row.importfeedchannel_set.get(channel=row).feed #NB: Channels N -> 1 Feed relationship, even though it looks M2M
                self._debug("Feed found, id:" + str(f.id) + ". slug=" + row.name)

            # NB: Slugs/name ARE NOT UNIQUE IN OXITEMS. So merge with existing, but only update if not deleted
            if not row.deleted:
                f.last_updated = row.channel_updated
                f.feed_group = fg
                f.save()

            # Things to do after the Feed is created
            self._set_feed_destinations(f, row.channel_guid, row.channel_tpi, row.deleted)
            self._get_or_create_feedartwork(f, row.channel_image)
            self._parse_items(f, row)

            if counter == 0 or (counter % 50) == 0:
                self._debug("Parsed %s of %s Channels" % (counter,total_count))
            

        # Final stats output at end of file
        #try:
        #    self.import_stats['update_rate'] = float(self.import_stats.get('update_count')) /\
        #        float((datetime.utcnow() - self.import_stats.get('update_starttime')).seconds)
        #except ZeroDivisionError:
        #    self.import_stats['update_rate'] = 0

        print "\nUpdate finished at " + str(datetime.utcnow()) +\
            "\nFeedGroups created: " + str(self.import_stats.get('feedgroup_created')) + "." +\
            "\nFeeds created: " + str(self.import_stats.get('feed_created')) + "." +\
        ""
        #    "\nIP addresses parsed: " + str(self.import_stats.get('update_count')) +\
        #    "\nImported at " + str(self.import_stats.get('update_rate'))[0:6] + " IP Addresses/sec\n"

        # Write the error cache to disk
        self._error_log_save()
        self._errorlog_stop()
        return None


    def _get_or_create_owning_unit(self, oxpoints_unit=''):
        # Datafield is blank so we improvise in the meantime
        # TODO: Work out how to determine owning units for these objects, both Items and FeedGroups
        return Unit.objects.get(pk=1)


    def _set_feed_destinations(self, feed_obj, itunesu_guid, oxitems_destination, oxitems_deleted):
        # determine how many destinations are needed
        destinations = []
        if oxitems_destination == 0:
            # This isn't appearing anywhere, so exit now
            self._errorlog("set_feed_destination() found no destinations for feed:" + feed_obj.slug)
            return None
        elif oxitems_destination == 1:
            destinations.append(Destination.objects.get(pk=1)) # POAU
            destinations.append(Destination.objects.get(pk=2)) # POAU-Beta
            destinations.append(Destination.objects.get(pk=4)) # m.ox
        elif oxitems_destination == 2:
            destinations.append(Destination.objects.get(pk=3)) # iTunesU
            destinations.append(Destination.objects.get(pk=4)) # m.ox
        elif oxitems_destination == 3:
            destinations.append(Destination.objects.get(pk=1)) # POAU
            destinations.append(Destination.objects.get(pk=2)) # POAU-Beta
            destinations.append(Destination.objects.get(pk=3)) # iTunesU
            destinations.append(Destination.objects.get(pk=4)) # m.ox
        else:
            # Something strange happened here...
            self._errorlog("set_feed_destination() could not identify destination for feed:" + feed_obj.slug)
            return None

        # self._debug("set_feed_destination about to link feed to " + str(len(destinations)) + " destinations")
        # For this sync we just wipe and recreate, no need to try to sync
        FeedDestination.objects.filter(feed=feed_obj).delete()
        for dest in destinations:
            feed_destination = FeedDestination()
            feed_destination.feed = feed_obj
            feed_destination.destination = dest
            if dest.id == 3: # iTunes U from fixtures/db
                feed_destination.guid = itunesu_guid # This is largely ignored and unused...
            if oxitems_deleted == True: # NB: whilst hacking out the slug duplicates by ignoring deleted items, this is untested...
                feed_destination.withhold = 1000 # TODO: Need to determine some workflow values and descriptions for withhold
            feed_destination.save()
            # self._debug(feed_obj.slug + " linked to " + dest.name)
        return None


    def _get_or_create_link(self, obj, url):
        # Handle the M2M relationship between Feed and Link
        link, created = Link.objects.get_or_create(url=url, defaults={'url':url})
        if created:
            link.save()
            # self._debug("Link created for: " + str(url))
        else:
            # self._debug("Link found @" + str(link.id) + " for: " + str(url))
            pass

        # Same call for both Item and FeedGroup objects, no need to type check
        obj.links.add(link)
        return None


    def _set_jorum_tags(self, feedgroup_obj, collection_string):
        if len(collection_string) < 10:
            return None

        g = TagGroup.objects.get(pk=3) # Hardcoded for fixture loaded Jorumopen collection group
        tags = collection_string.split('|')
        for t in tags:
            tag, created = Tag.objects.get_or_create(name=t,group=g, defaults={'name':t, 'group':g})
            if created:
                tag.save()
                # self._debug("_set_jorum_tags(): Tag created for: " + str(tag.name))
                # TODO: Raise an error here because we should have all the jorumopen collection codes already in a fixture and loaded
            else:
                # self._debug("_set_jorum_tags(): Tag found @" + str(tag.id) + " for:" + str(tag.name))
                pass

            feedgroup_obj.tags.add(tag) # Indented this one more level, need to test...
        return None


    def _get_or_create_feedartwork(self, feed_obj, url):
        # TODO: Test the url is valid and do the full file analysis eventually
        if url == '':
            return None
        # Trust the URL for the timebeing...
        function = FileFunction.objects.get(pk=3) # Hardcoded for fixture loaded FileFunction FeedArt
        artwork, created = File.objects.get_or_create(url=url, function=function, defaults={'url':url, 'function':function})
        if created:
            artwork.save()
            # self._debug("Artwork item created: " + str(url))
        else:
            # self._debug("Artwork item found @" + str(artwork.id) + " for: " + str(url))
            pass

        fif, created = FileInFeed.objects.get_or_create(file=artwork, feed=feed_obj, defaults={
            'file':artwork, 'feed':feed_obj, 'withhold':0
        })
        if created:
            fif.save()
        return None


    # Import OxItems.Items, but done on a channel by channel basis
    def _parse_items(self, feed_obj, channel_obj):
        oxitems = Rg07Items.objects.filter(item_channel=channel_obj)
        print "Found " + str(len(oxitems)) + " OxItems to process for " + str(feed_obj.slug)

        for counter, item_row in enumerate(oxitems):
            # Update or create an ***Item***
            if len(item_row.importitemitem_set.all()) == 0:
                # Does this need merging with an existing Item? Compare with existing titles...
                item = {'title':item_row.item_title} # NB: May fail without a person record to store...
                i, created = Item.objects.get_or_create(title=item_row.item_title, defaults=item)
                if created:
                    i = self._update_item(i, item_row)
                    i.save()
                    # self._debug("New Item created, id: " + str(i.id) + ". Title=" + i.title)
                else:
                    # self._debug("Item found for merger, id: " + str(i.id) + ". Title=" + i.title)
                    pass

                # Make import link
                iii = ImportItemItem()
                iii.ffm_item = i
                iii.item = item_row
                iii.save()
            else:
                i = item_row.importitemitem_set.get(item=item_row).ffm_item
                # self._debug("Item found, id: " + str(i.id) + ". Title=" + i.title)

            if not item_row.deleted: #Only overwrite the item information if this is not a deleted item
                i = self._update_item(i, item_row)
                i.save()
                # self._debug("Item details updated from oxitems row:" + str(item_row.id))
            else:
                # TODO: Consider what happens if all the items we're grouping here are deleted
                # Consider whether we really even need to do anything after determining that this item has been deleted
                pass

            # Things to do once you've got the item...
            self._parse_people(item_row, i)
            # self._get_or_create_link() - There are no links in Oxitems Items :(
            self._parse_keywords(item_row, i)

            # Update or create ***File*** for this Item
            if len(item_row.importfileitem_set.all()) == 0:
                # Does this file already exist?
                # Search by guid...
                f = FileInFeed.objects.filter(guid__iexact=item_row.item_guid)[0]
                if len(f)<1:
                    # Search by url
                    f = FeedURL.objects.filter(url__iexact=item_row.item_enclosure_href)[0]
                    if len(f)<1:
                        # Not found anything to match it by (and no filehash checking yet), so create a new File
                        file = {'url':item_row.item_enclosure_href} # TODO: Can't match on URL really, as this is now an external table field
                        f, created = File.objects.get_or_create(url=item_row.item_enclosure_href, defaults=file)
                        if created:
                            f = self._update_file(f, item_row, i)
                            f.save()
                            # self._debug("New File created, id: " + str(f.id) + ". Url=" + f.url)
                        else:
                            # self._debug("File found, id: " + str(f.id) + ". Url=" + f.url)
                            pass
                # TODO: YOU ARE WORKING HERE

                # Make import link
                ifi = ImportFileItem()
                ifi.file = f
                ifi.item = item_row
                ifi.save()
            else:
                f = item_row.importfileitem_set.get(item=item_row).file

            if not item_row.deleted:
                f = self._update_file(f, item_row, i)
                f.save()

            # feed_obj.files.add(f) -- Not a simple M2M link
            # Update or create a link for this FileInFeed. There is always a link for historical tracking reasons
            fileinfeed = {'file':f, 'feed':feed_obj, 'withhold':item_row.item_checked, 'itunesu_category':item_row.item_cc}
            fif, created = FileInFeed.objects.get_or_create(file=f, feed=feed_obj, defaults=fileinfeed)
            if created:
                fif.save()
            else:
                fif.withhold = item_row.deleted
                fif.itunesu_category = item_row.item_cc
            if item_row.deleted:
                fif.withhold = 1000
            fif.save()
            self._parse_jacs_code(fif,item_row.item_jacs_codes)

        # TODO: Determine fif.order values based on channel_sort_values
        return None


    def _update_item(self, item_obj, oxitem_obj):
        # self._debug("item_updated='" + oxitem_obj.item_updated + "'")
        if len(oxitem_obj.item_updated) > 6:
            item_obj.last_updated = parser.parse(oxitem_obj.item_updated)

        item_obj.description = oxitem_obj.item_summary
        if item_obj.description != '':
            item_obj.description += (" :: " + oxitem_obj.item_content)
        else:
            item_obj.description = oxitem_obj.item_content

        # self._debug("item_startdate='" + oxitem_obj.item_startdate + "'")
        if len(oxitem_obj.item_startdate) > 6:
            item_obj.publish_start = parser.parse(oxitem_obj.item_startdate)

        self._debug("item_recording_date='" + oxitem_obj.item_recording_date + "'")
        if len(oxitem_obj.item_recording_date) > 6:
            item_obj.recording_date = parser.parse(oxitem_obj.item_recording_date)

        item_obj.internal_comments = oxitem_obj.item_other_comments
        if item_obj.internal_comments != '':
            item_obj.internal_comments += (" :: " + oxitem_obj.item_legal_comments)
        else:
            item_obj.internal_comments = oxitem_obj.item_legal_comments

        # self._debug("item_expires='" + oxitem_obj.item_expires + "'")
        if len(oxitem_obj.item_expires) > 6:
            item_obj.publish_stop = parser.parse(oxitem_obj.item_expires)

        item_obj.license = self._get_licence(oxitem_obj.item_licence) # TODO: Correct and standardise all spellings of licence/license
        item_obj.owning_unit = self._get_or_create_owning_unit('')
        return item_obj


    def _update_file(self, file_obj, oxitem_obj, item_obj):
        file_obj.guid = oxitem_obj.item_guid
        file_obj.item = item_obj
        if len(oxitem_obj.item_enclosure_length)>0:
            file_obj.size = int(oxitem_obj.item_enclosure_length)
        file_obj.duration = int(oxitem_obj.item_duration)
        # TODO: determine file function
        # TODO: determine file mimetype
        # TODO: determine proper duration and size from the file...
        return file_obj


    def _get_licence(self, oxitems_licence):
        if  oxitems_licence == 5:
            return Licence.objects.get(pk=2) # CC BY-NC-SA Licence hardcoded from Fixtures
        elif  oxitems_licence == 6:
            return Licence.objects.get(pk=3) # CC BY-NC-ND Licence hardcoded from Fixtures
        else:
            return Licence.objects.get(pk=1) # Personal Licence hardcoded from Fixtures


    def _parse_people(self, oxitem_obj, item_obj):
        # In = String of text, mostly CSV-like
        in_str = oxitem_obj.item_enclosure_artists

        # Clear out any existing role links
        item_obj.people.clear()

        if len(in_str) < 3:
            # TODO: This should likely throw some sort of error about missing people?
            return None

        # Some manual exceptions for people parsing...
        if oxitem_obj.id == 15314 or oxitem_obj.id == 15315 or oxitem_obj.id == 24581:
            return None

        def _person(name, person_dict):
            # Check for titles
            title = name[0].lower()
            if title.startswith("prof") or title.startswith("dr") or title.startswith("lord")\
                or title.startswith("mr") or title.startswith("ms") or title.startswith("rt")\
                or title.startswith("lieutenant") or title.startswith("president")\
                or title.startswith("baron") or title.startswith("dame") or title.startswith("sir"):
                person_dict["titles"] = name[0][:100]
                try:
                    person_dict["first_name"] = name[1][:50]
                except IndexError:
                    # TODO: Throw an error here as this name is likely screwy
                    person_dict["first_name"] = name[0][:50]
            else:
                person_dict["first_name"] = name[0][:50]
            person_dict["last_name"] = name[-1][:50]

            # Get or create a person record for this one
            person, created = Person.objects.get_or_create(
                additional_information=person_dict.get("additional_information"),
                defaults=person_dict)
            if created:
                person.save()
                # self._debug("_parse_people(): Person created for: " + person.short_name())
            else:
                # self._debug("_parse_people(): Person found @" + str(person.id) + " for: " + person.short_name())
                pass

            # Create a role link
            role = Role()
            role.person = person
            role.item = item_obj
            role.role = u'25.16' # From models.py: ROLES: u'Speaker / Lecturer / Causeur')
            role.save()
            return None

        # Remove anything in brackets ()
        br = re.compile('\(.*?\)', re.DOTALL)
        # Split on commas outside of brackets - http://stackoverflow.com/questions/1648537/how-to-split-a-string-by-commas-positioned-outside-of-parenthesis
        cs = re.compile('(?:[^,(]|\([^)]*\))+',re.DOTALL)
        if in_str.count(";") > 0: # Deal with names separated by semi colons
            names = in_str.strip().split(";")
            for n in names:
                if len(n)<1:
                    continue
                person = {}
                person["additional_information"] = n.strip()
                # self._debug("_parse_people(): Examining(;):" + n.strip())
                name = cs.findall(n)[0].strip().split(" ")
                _person(name, person)
        else: # Deal with names separated by comma
            names = cs.findall(in_str)
            for n in names:
                if br.sub('',n).count(" and ") > 0:
                    names2 = br.sub('',n).split(" and ")
                    for n2 in names2:
                        person = {}
                        person["additional_information"] = n2.strip()
                        # self._debug("_parse_people(): Examining(and):" + n2.strip())
                        name2 = br.sub('',n2).strip().split(" ")
                        _person(name2, person)
                else:
                    person = {}
                    person["additional_information"] = n.strip()
                    # self._debug("_parse_people(): Examining(,):" + n.strip())
                    name = br.sub('',n).strip().split(" ") # Presumes names don't exist in brackets - though, yes, there are some
                    _person(name, person)

        # TODO: Will need to have a merge records method for manual use
        return None


    def _parse_keywords(self, oxitem_obj, item_obj):
        # Clean up any existing tag associations first
        item_obj.tags.clear()
        # Likely to default to general keywords, supplied as a csv string, with a comma first
        if len(oxitem_obj.item_simple_categories) < 3:
            return None

        g = TagGroup.objects.get(pk=1) # Hardcoded for fixture loaded Unsorted Tags collection group
        tags = oxitem_obj.item_simple_categories.lower().split(',')
        for t in tags:
            if len(t) < 1:
                continue
            tag, created = Tag.objects.get_or_create(name=t,group=g, defaults={'name':t, 'group':g})
            if created:
                tag.save()
                # self._debug("_parse_keywords(): Tag created for: " + tag.name)
            else:
                # self._debug("_parse_keywords(): Tag found @" + str(tag.id) + " for:" + tag.name)
                pass

            item_obj.tags.add(tag)
        return None

    def _parse_jacs_code(self, fif_obj,code_string):
        fif_obj.jacs_codes.clear()
        # Likely to default to short 4 character codes, supplied as a csv string, with a comma first
        if len(code_string) < 3:
            return None

        # Note: JACS Codes are complex and numerous, so not easy to check - http://en.wikipedia.org/wiki/Joint_Academic_Classification_of_Subjects
        g = TagGroup.objects.get(pk=2) # Hardcoded for fixture loaded JACS Codes collection group
        tags = code_string.upper().split(',')
        for t in tags:
            if len(t) < 1:
                continue
            tag, created = Tag.objects.get_or_create(name=t,group=g, defaults={'name':t, 'group':g})
            if created:
                tag.save()
                # self._debug("_parse_jacs_code(): Tag created for: " + tag.name)
            else:
                # self._debug("_parse_jacs_code(): Tag found @" + str(tag.id) + " for:" + tag.name)
                pass

            fif_obj.jacs_codes.add(tag)
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