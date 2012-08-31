# Perform various scans of URLs from iTunes Store
import datetime
import pytz
import sys

from dateutil.parser import *
import urllib2
import codecs
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core import management
from django.db.models import Q, F
from settings import *

from opms.utils import debug
from monitors.utils import itunes as itunes
from monitors.models import ItuCollectionChartScan, ItuCollectionHistorical, ItuCollection, ItuItemChartScan, ItuItemHistorical, ItuItem, ItuScanLog, ItuGenre, ItuInstitution, ItuRating, ItuComment
from feedback.models import Metric, Traffic, Category, Comment, Event

class Command(BaseCommand):
    help = 'Scan iTunes U Service; Modes available:\n1:Institutional collection <default>\n2:Top Collections\n3:Top Downloads\n4:Institutions'
    args = "[<institution>]"
#    label = "institution"
    option_list = BaseCommand.option_list + (
        make_option('--mode', action='store', dest='mode',
                    default=1, help='Specify the type of scan to be done (1,2,3,4)'),
    )

    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""

        super(Command, self).__init__()

    def handle(self, institution_name = YOUR_INSTITUTION, **options):
        verbosity = int(options.get('verbosity', 0))
        if verbosity > 1:
            debug.DEBUG = True
        # Create an error log
        debug.errorlog_start('scan_itunes.log')
        # Some basic error checking
        if institution_name is None:
            debug.errorlog("Please specify the institution to scan.")
            return False

        try:
            mode = int(options.get("mode",1))
        except ValueError:
            debug.errorlog("""Please specify a valid mode for this scan.
               1) Scan an institution's collection
               2) Scan the Top Collections chart
               3) Scan the Top Downloads chart
               4) Scan the list of institutions
               """)
            return False
        if mode < 1 or mode > 4:
            debug.errorlog("""Please specify a valid mode for this scan.
               1) Scan an institution's collection
               2) Scan the Top Collections chart
               3) Scan the Top Downloads chart
               4) Scan the list of institutions
               """)
            return False

        scantime = datetime.datetime.now(pytz.utc)
        print "Scan iTunes started at " + str(scantime) + "\n"

        scanlog = ItuScanLog(mode=mode, time=scantime, comments="")
        scanlog.save()

        if mode == 1:
            try:
                institution = ItuInstitution.objects.filter(name__iexact=institution_name)[0]
            except:
                debug.errorlog(institution_name + u" is not a recognised institution.")
                scanlog.delete()
                return False

            scanlog.institution = institution
            scanlog.save()

            comment = u"Scan (and update) of " + institution_name + u"\'s collection from %s" % institution.url
            debug.log(u"Log started for: %s" % unicode(comment))
            print comment

            print("Getting information about collections...")
            collections = itunes.get_institution_collections(institution, hurry=True)
            print("Processing collection information and scanning individual items...")
            collections_spotted = []
            items_spotted = []
            for collection_itunes in collections:
                if collection_itunes:
#                    for k in collection_itunes.keys():
#                        print(k + ': ' + collection_itunes[k])

                    #Check if this collection's genre exists - if not, create it.
                    genre = ItuGenre(name=collection_itunes['genre'], itu_id=int(collection_itunes['genre_id']), url=collection_itunes['genre_url'])
                    genre_exists = False
                    for saved_genre in ItuGenre.objects.all():
                        if int(genre.itu_id) == int(saved_genre.itu_id) and genre.name==saved_genre.name and genre.url==saved_genre.url:
                            genre_exists = True
                            genre = saved_genre
                    if not genre_exists:
                        debug.log(u'Created new genre ' + unicode(genre.name))
                        genre.save()

                    collection_record_absolute = ItuCollection(institution=institution)
                    if collection_itunes['last modified']:
                        last_modified = parse(collection_itunes['last modified']).date()
                    else:
                        last_modified = None
                    collection_record_historical = ItuCollectionHistorical(name=collection_itunes['series'],
                                                 itu_id=int(collection_itunes['series_id']),
                                                 img170=collection_itunes['series_img_170'],
                                                 url=collection_itunes['series_url'],
                                                 language=collection_itunes['language'],
                                                 last_modified=last_modified,
                                                 contains_movies=collection_itunes['contains_movies'],
                                                 missing=None,
                                                 version=1,
                                                 institution=institution,
                                                 scanlog=scanlog,
                                                 genre=genre,
                                                 previous=None,
                                                 itucollection=collection_record_absolute)

                    rating_checksum = 0
                    for rating in collection_itunes['ratings']:
                        rating_checksum += pow(10,rating['stars']) + (rating['count']/1000000000)

                    #Put together a list of saved collection_record_historicals that look like they're the same as our collection_record_historical, really.
                    similar_collection_records_historical = []
                    collection_record_historical_exists = False
                    for collection_record_historical_saved in ItuCollectionHistorical.objects.filter((Q(name=collection_record_historical.name) & Q(contains_movies=collection_record_historical.contains_movies)) | Q(itu_id=collection_record_historical.itu_id) | Q(url=collection_record_historical.url)): #name AND Video/Audio
                        if collection_record_historical.url != collection_record_historical_saved.url: #Don't add similar collection_record_historical if the URLs are different, but both are accessible.
                            try:
                                urllib2.urlopen(collection_record_historical.url)
                                urllib2.urlopen(collection_record_historical_saved.url)
                            except urllib2.URLError:
                                similar_collection_records_historical.append(collection_record_historical_saved)
                        else:
                            similar_collection_records_historical.append(collection_record_historical_saved)
                            if collection_record_historical.name==collection_record_historical_saved.name and collection_record_historical.contains_movies==collection_record_historical_saved.contains_movies and int(collection_record_historical.itu_id)==int(collection_record_historical_saved.itu_id) and collection_record_historical.url==collection_record_historical_saved.url and collection_record_historical.img170==collection_record_historical_saved.img170 and collection_record_historical.language==collection_record_historical_saved.language and rating_checksum==collection_record_historical_saved.rating_checksum():
                                collection_record_historical_exists=True
                                collection_record_historical = collection_record_historical_saved
                            else:
                                similar_collection_records_historical.append(collection_record_historical_saved)
                    if not collection_record_historical_exists:
                        if similar_collection_records_historical:
                            similar_collection_records_historical.sort(key=lambda this_collection_record_historical: this_collection_record_historical.version)
                            latest_similar_collection_record_historical = similar_collection_records_historical[-1]
                            collection_record_historical.previous = latest_similar_collection_record_historical
                            collection_record_historical.version = latest_similar_collection_record_historical.version + 1
                            collection_record_historical.itucollection = latest_similar_collection_record_historical.itucollection
                        else:
                            collection_record_absolute.save()
                            collection_record_historical.itucollection = collection_record_absolute
                        debug.log(u'Created new historical collection record for ' + unicode(collection_record_historical.name) + u', version ' + unicode(collection_record_historical.version))
                        collection_record_historical.save()

                        for r in collection_itunes['ratings']:
                            try:
                                rating = ItuRating(stars=r['stars'],
                                               count=r['count'],
                                               itucollectionhistorical=collection_record_historical)
                                rating.save()
                            except:
                                debug.log(u'WARNING: Failed to save rating.')

                    for comment in collection_itunes['comments']:
                        if comment and len(ItuComment.objects.filter(detail=comment['detail'])) == 0:
                            try:
                                new_comment = ItuComment(itucollectionhistorical=collection_record_historical,
                                                         stars=comment['rating'],
                                                         date=comment['date'],
                                                         detail=comment['detail'],
                                                         source=comment['source'],
                                                         ituinstitution=institution)
                                new_comment.save()
                                debug.log(u'Saved new comment by ' + unicode(new_comment.source) + u': \"' + unicode(new_comment.detail) + u'\".')
                            except:
                                debug.log(u'WARNING: Failed to save comment.')

                    collections_spotted.append(collection_record_historical)

                    #Acquire the list of items for this collection.
                    try:
                        items = itunes.get_collection_items(collection_record_historical.url, hurry=True)
                    except:
                        debug.errorlog('Could not get items for collection ' + collection_record_historical.name + '.')
                        items = []
                    for item in items:
                        if item is not {}: #Dictionary will be blank if we have failed to retrieve data on an item. If so, don't do anything with the item.
                            item_record_absolute = ItuItem(institution=institution)
                            try:
                                #Deal with things with no duration (like PDFs...)
                                if 'duration' in item.keys():
                                    item['duration'] = int(item['duration'])
                                else:
                                    item['duration'] = None
                                if 'songName' not in item.keys():
                                    item['songName'] = item['playlistName'] + ' ' + str(item['rank']) + ' {UNKNOWN NAME}'
                                item_record_historical = ItuItemHistorical(name=item['songName'],
                                                            itu_id=item['itemId'],
                                                            url=item['url'],
                                                            artist_name=item['artistName'],
                                                            description=item['description'],
                                                            duration=item['duration'],
                                                            explicit=bool(item['explicit']),
                                                            feed_url=item['feedURL'],
                                                            file_extension=item['fileExtension'],
                                                            kind=item['kind'],
                                                            long_description=item['longDescription'],
                                                            playlist_id=int(item['playlistId']),
                                                            playlist_name=item['playlistName'],
                                                            popularity=float(item['popularity']),
                                                            preview_length=int(item['previewLength']),
                                                            preview_url=item['previewURL'],
                                                            rank=int(item['rank']),
                                                            release_date=pytz.utc.localize(parse(item['releaseDate'],ignoretz=True)),
                                                            missing=None,
                                                            version=1,
                                                            previous=None,
                                                            ituitem=item_record_absolute,
                                                            institution=institution,
                                                            genre=genre,
                                                            scanlog=scanlog,
                                                            series=collection_record_historical)
                            except KeyError: #See if we've got data from a last-ditch attempt at downloading it instead.
                                try:
                                    duration = 0
                                    feedurl = ""
                                    for offerkey in item['store-offers'].keys(): #offerkey is something like 'standard-audio'. This code works on the assumption that, whatever the key, we want all the items in its list.
                                        try:
                                            duration = item['store-offers'][offerkey]['duration']
                                        except KeyError:
                                            duration = None
                                        feedurl = item['store-offers'][offerkey]['asset-url']
                                    item_record_historical = ItuItemHistorical(name=item['title'],
                                                              itu_id=item['item-id'],
                                                              url=item['url'],
                                                              artist_name=item['artist-name'],
                                                              description=item['description'],
                                                              duration=duration,
                                                              explicit=False,
                                                              feed_url=feedurl,
                                                              file_extension=feedurl.split('.')[-1],
                                                              kind='unknown',
                                                              long_description=item['long-description'],
                                                              playlist_id=collection_record_historical.id,
                                                              playlist_name=collection_record_historical.name,
                                                              popularity=0.0,
                                                              preview_length=0,
                                                              preview_url='unknown',
                                                              rank=int(item['track-number']),
                                                              release_date=item['release-date'],
                                                              missing=None,
                                                              version=1,
                                                              previous=None,
                                                              ituitem=item_record_absolute,
                                                              institution=institution,
                                                              genre=genre,
                                                              scanlog=scanlog,
                                                              series=collection_record_historical)
                                except KeyError:
                                    debug.errorlog(u'Missing key when trying to create an ItuItemHistorical. item=' + unicode(item))
                                except:
                                    debug.errorlog(u'Failed to process ItuItemHistorical.')

                            try: #We can't afford this bit to die in the middle of the night.
#                                Put together a list of saved item_record_historicals that look like they're the same as our item_record_historical, really.
                                similar_item_record_historicals = []
                                item_record_historical_exists = False
                                for saved_item_record_historical in ItuItemHistorical.objects.filter(Q(series__itucollection=collection_record_historical.itucollection) & (Q(name=item_record_historical.name) | Q(itu_id=item_record_historical.itu_id) | Q(url=item_record_historical.url)) & Q(file_extension=item_record_historical.file_extension)): #name AND Video/Audio
                                    if item_record_historical.url != saved_item_record_historical.url: #Don't add similar item_record_historical if the URLs are different, but both are accessible.
                                        try:
                                            urllib2.urlopen(item_record_historical.url)
                                            urllib2.urlopen(saved_item_record_historical.url)
                                        except urllib2.URLError:
                                            similar_item_record_historicals.append(saved_item_record_historical)
                                    else:
                                        if item_record_historical.name==saved_item_record_historical.name and item_record_historical.itu_id==saved_item_record_historical.itu_id and item_record_historical.url==saved_item_record_historical.url and item_record_historical.artist_name==saved_item_record_historical.artist_name and item_record_historical.description==saved_item_record_historical.description and item_record_historical.duration==saved_item_record_historical.duration and item_record_historical.explicit==saved_item_record_historical.explicit and item_record_historical.feed_url==saved_item_record_historical.feed_url and item_record_historical.file_extension==saved_item_record_historical.file_extension and item_record_historical.kind==saved_item_record_historical.kind and item_record_historical.long_description==saved_item_record_historical.long_description and item_record_historical.playlist_id==saved_item_record_historical.playlist_id and item_record_historical.playlist_name==saved_item_record_historical.playlist_name and item_record_historical.popularity==saved_item_record_historical.popularity and item_record_historical.preview_length==saved_item_record_historical.preview_length and item_record_historical.preview_url==saved_item_record_historical.preview_url and item_record_historical.rank==saved_item_record_historical.rank and item_record_historical.release_date==saved_item_record_historical.release_date:
                                            item_record_historical_exists = True
                                            item_record_historical = saved_item_record_historical
                                        else:
                                            similar_item_record_historicals.append(saved_item_record_historical)
                                if not item_record_historical_exists:
                                    if similar_item_record_historicals:
                                        similar_item_record_historicals.sort(key=lambda this_item_record_historical: this_item_record_historical.version)
                                        latest_similar_item_record_historical = similar_item_record_historicals[-1]
                                        item_record_historical.previous = latest_similar_item_record_historical
                                        item_record_historical.version = latest_similar_item_record_historical.version + 1
                                        item_record_historical.ituitem = latest_similar_item_record_historical.ituitem
                                    else:
                                        item_record_absolute.save()
                                        item_record_historical.ituitem = item_record_absolute
                                    debug.log(u'Created new historical item record for ' + unicode(item_record_historical.name) + u', version ' + unicode(item_record_historical.version))
                                    item_record_historical.save()
                                items_spotted.append(item_record_historical)
                            except:
                                debug.errorlog(u'Failed to process potential historical item record.')
                        else:
                            debug.log(u'WARNING: Blank item - perhaps we couldn\'t download the appropriate page?')
                else:
                    debug.log(u'WARNING: Blank category - perhaps we couldn\'t download the appropriate page?')
            print(u"Checking whether anything has gone missing or reappeared...")
            if collections:
                counter = 0
                for historical_collection_record in ItuCollectionHistorical.objects.filter(Q(institution=institution) & Q(itucollection__latest=F('id'))):
                    if historical_collection_record not in collections_spotted and historical_collection_record.missing == None:
                        debug.log(unicode(historical_collection_record.name) + u" appears to have gone missing! We last saw it at " + unicode(historical_collection_record.scanlog.time))
                        historical_collection_record.missing = scanlog
                        historical_collection_record.save()
                    elif historical_collection_record in collections_spotted and historical_collection_record.missing:
                        debug.log(unicode(historical_collection_record.name) + u" has reappeared! It went missing at " + unicode(historical_collection_record.missing.time))
                        historical_collection_record.missing = None
                        historical_collection_record.save()
                    counter += 1
                    if float(counter)/100.0 == int(float(counter)/100.0):
                        print (u'Still checking... (at object ' + unicode(counter) + u')')
                for historical_item_record in ItuItemHistorical.objects.filter(Q(institution=institution) & Q(ituitem__latest=F('id'))):
                    if historical_item_record not in items_spotted and historical_item_record.missing == None:
                        debug.log(unicode(historical_item_record.name) + u" appears to have gone missing! We last saw it at " + unicode(historical_item_record.scanlog.time))
                        historical_item_record.missing = scanlog
                        historical_item_record.save()
                    elif historical_item_record in items_spotted and historical_item_record.missing:
                        debug.log(unicode(historical_item_record.name) + u" has reappeared! It went missing at " + unicode(historical_item_record.missing.time))
                        historical_item_record.missing = None
                        historical_item_record.save()
                    counter += 1
                    if float(counter)/100.0 == int(float(counter)/100.0):
                        print (u'Still checking... (at object ' + unicode(counter) + u')')
            else:
                debug.log(u"WARNING: No collections found. Perhaps you scanned an institution that only publishes courses?")
        elif mode == 2:
            comment = u"Scan of the Top Collections Chart..."
            debug.log(u"Log started for: %s" % unicode(comment))
            updated_institutions = False
            collections = itunes.get_topcollections()
            for collection in collections:
                if collection:
                    try:
                        historical_collections=ItuCollectionHistorical.objects.filter(url=collection['series_url'])
                        if not historical_collections:
                            debug.log(u'WARNING: Couldn\'t find an historical record of collection at ' + unicode(collection['series_url']) + u'. Attempting an historical scan of ' + unicode(collection['institution']) + u' first...')
                            if not updated_institutions:
                                management.call_command('scan_itunes', mode=4)
                                updated_institutions = True
                            try:
                                management.call_command('scan_itunes', collection['institution'], mode=1)
                            except:
                                try: #Deal with institutions which aren't listed by Apple.
                                    institution = ItuInstitution(name = collection['institution'],
                                                                 itu_id = int(collection['institution_id']),
                                                                 url = collection['institution_url'])
                                    institution.save()
                                    management.call_command('scan_itunes', collection['institution'], mode=1)
                                except:
                                    debug.errorlog('Failed to scan institution ' + collection['institution'] + '. Perhaps this institution isn\'t listed by Apple?')
                            historical_collections=ItuCollectionHistorical.objects.filter(url=collection['series_url'])
                        if historical_collections.exists():
                            historical_collection=historical_collections[0].latest()
                            debug.log(u'Creating new chart row: ' + unicode(historical_collection.name) + u' Position: ' + unicode(collection['chart_position']))
                            chartrow=ItuCollectionChartScan(position=int(collection['chart_position']),
                                                            itucollection=historical_collection.itucollection,
                                                            itucollectionhistorical=historical_collection,
                                                            scanlog=scanlog,
                                                            date=scanlog.time)
                            chartrow.save()
                        else:
                            debug.errorlog(u'Couldn\'tfind an historical record of collection at ' + unicode(collection['series_url']) + u' despite updating the database.')
                    except KeyError:
                        debug.errorlog('WARNING: Couldn\'t access collection (KeyError):' + str(collection))

        elif mode == 3:
            comment = u"Scan of the Top Downloads Chart..."
            debug.log(u"Log started for: %s" % unicode(comment))
            updated_institutions = False
            items = itunes.get_topdownloads()
            for item in items:
                if item:
                    try:
                        historical_items=ItuItemHistorical.objects.filter(name=item['item'])
                        if not historical_items:
                            debug.log(u'WARNING: Couldn\'t find an historical record of item at ' + unicode(item['item_url']) + u'. Attempting an historical scan of ' + unicode(item['institution']) + u' first...')
                            if not updated_institutions:
                                management.call_command('scan_itunes', mode=4)
                                updated_institutions = True
                            try:
                                management.call_command('scan_itunes', item['institution'], mode=1)
                            except:
                                try: #Deal with institutions which aren't listed by Apple.
                                    institution = ItuInstitution(name = item['institution'],
                                                                 itu_id = int(item['institution_id']),
                                                                 url = item['institution_url'])
                                    institution.save()
                                    management.call_command('scan_itunes', item['institution'], mode=1)
                                except:
                                    debug.errorlog('Failed to scan institution ' + item['institution'] + '. This is a bug.')
                            historical_items=ItuItemHistorical.objects.filter(name=item['item'])
                        if historical_items.exists():
                            historical_item=historical_items[0].latest()
                            debug.log(u'Created new download chart row: ' + unicode(historical_item.name) + u' Position: ' + unicode(item['chart_position']))
                            chartrow=ItuItemChartScan(position=int(item['chart_position']),
                                                      ituitem=historical_item.ituitem,
                                                      ituitemhistorical=historical_item,
                                                      scanlog=scanlog,
                                                      date=scanlog.time)
                            chartrow.save()
                        else:
                            debug.errorlog(u'Couldn\'t find an historical record of item at ' + unicode(item['item_url']) + u' despite updating the database.')
                    except KeyError:
                        debug.errorlog('WARNING: Couldn\'t access item (KeyError):' + str(item))
        elif mode == 4:
            comment = "Scan of list of institutions..."
            debug.log(u"Log started for: %s" % unicode(comment))
            print comment
            institutions = itunes.get_institutions()
            for institution_itunes in institutions:
                if institution_itunes:
                    institution = ItuInstitution(name = institution_itunes['text'],
                                                 itu_id = int(institution_itunes['itu_id']),
                                                 url = institution_itunes['url'])
                    need_update = False
                    need_create = True
                    for saved_institution in ItuInstitution.objects.filter(Q(itu_id=institution.itu_id) | Q(name=institution.name) | Q(url = institution.url)):
                        if saved_institution.itu_id == institution.itu_id and saved_institution.name == institution.name and saved_institution.url == institution.url:
                            need_update = False
                            need_create = False
                        else:
                            need_update = True
                            need_create = False
                            saved_institution.itu_id = institution.itu_id
                            saved_institution.name = institution.name
                            saved_institution.url = institution.url
                            institution = saved_institution
                    if need_update:
                        debug.log(u'Updated institution ' + unicode(institution.name))
                        institution.save()
                    elif need_create:
                        debug.log(u'Created new institution ' + unicode(institution.name))
                        institution.save()
        else:
            debug.errorlog(u"We shouldn't ever get this scan...")

        print "\nScan iTunes finished at " + str(datetime.datetime.now(pytz.utc))

        # Write the error cache to disk
        debug.error_log_save()
        debug.errorlog_stop()
        scanlog.complete = True
        scanlog.save()
        return None