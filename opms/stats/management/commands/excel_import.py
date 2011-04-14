# Import script for Apple iTunes U supplied Excel spreadsheets
# Author: Carl Marshall
# Last Edited: 29-3-2011

from optparse import make_option
from django.core.management.base import LabelCommand, CommandError

from opms.stats.models import *
from xlrd import open_workbook
from datetime import time, datetime
import sys, uuid
        
class Command(LabelCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'
    #option_list = LabelCommand.option_list + (
    #    make_option('--merge', action='store', dest='merge',
    #        default=False, help='Use this option to add this data to exisiting data, thus summing counts for records.'),
    #)
    
    def __init__(self):
        # Toggle debug statements on/off
        self.debug = True
        # Record basic information about the import process for reporting
        self.import_stats = {}
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""
        # To allow for report files to overlap, we have a merge option that will add to the counts
        self.merge = False
        # Define mapping between spreadsheet and model
        self.modelmapping = {
            # Spreadsheet -> Model
            'Browse':'browse',
            'DownloadPreview':'download_preview',
            'DownloadPreviewiOS':'download_preview_ios',
            'DownloadTrack':'download_track',
            'DownloadTracks':'download_tracks',
            'DownloadiOS':'download_ios',
            'EditFiles':'edit_files',
            'EditPage':'edit_page',
            'Logout':'logout',
            'SearchResultsPage':'search_results_page',
            'Subscription':'subscription',
            'SubscriptionEnclosure':'subscription_enclosure',
            'SubscriptionFeed':'subscription_feed',
            'Upload':'upload',
            'Not Listed':'not_listed',
            'Total Track Downloads':'total_track_downloads',
        }
        # Track caches
        self.track_path_cache = list(TrackPath.objects.all())
        self.track_handle_cache = list(TrackHandle.objects.all())
        self.track_guid_cache = list(TrackGUID.objects.all())
        # Browse caches
        self.browse_path_cache = list(BrowsePath.objects.all())
        self.browse_handle_cache = list(BrowseHandle.objects.all())
        self.browse_guid_cache = list(BrowseGUID.objects.all())
        # Preview caches
        self.preview_path_cache = list(PreviewPath.objects.all())
        self.preview_handle_cache = list(PreviewHandle.objects.all())
        self.preview_guid_cache = list(PreviewGUID.objects.all())
        
        return None


    def handle_label(self, filename, **options):
        print "Import started at " + str(datetime.utcnow()) + "\n"
        
        # Create an error log per import file
        self._errorlog_start(filename + '_import-error.log')

        if options.get('merge', False) != False:
            print "WARNING: Processing file to combine with existing records."
            self.merge = True
        
        # This only needs setting/getting the once per call of this function
        logfile_obj = self._logfile(filename)
        
        # Read the Worksheet
        wb = open_workbook(filename)
        
        # Start the parsing with the summary sheet
        self._parse_summary(logfile_obj, wb)
            
        print "\nImport finished at " + str(datetime.utcnow())
        self._errorlog_stop()
        return None



    def _logfile(self, filename):
        "Get or create a LogFile record for the given filename"
        logfile = {}

        # Some basic checking
        if filename.endswith('.xls') == False:
           raise CommandError("This is not a valid Excel 1998-2002 file. Must end in .xls\n\n")
        
        # Test the log_service option is valid. Use the same list as LogFile.SERVICE_NAME_CHOICES
        # Guess the service based on the filename
        try:
            xls = filename[filename.rindex('/')+1:]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            xls = filename
        # This may be Oxford specific?
        if xls.find('-dz-') > 0:
            logfile['service_name'] = 'itu-psm'
        elif xls.find('-public-') > 0:
            logfile['service_name'] = 'itu'
        else:
            raise CommandError("The service can not be determined from the filename.")
            
        try:
            logfile['file_name'] = filename[filename.rindex('/')+1:]
            logfile['file_path'] = filename[:filename.rindex('/')+1]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            logfile['file_name'] = filename
            logfile['file_path'] = "./"
            
        logfile['last_updated'] = datetime.datetime.utcnow()
        
        obj, created = LogFile.objects.get_or_create(
            service_name = logfile.get('service_name'),
            file_name = logfile.get('file_name'),
            file_path = logfile.get('file_path'),
            defaults = logfile)
        
        # If this isn't the first time, and the datetime is significantly different from last access, update the time
        if not created and (logfile.get('last_updated') - obj.last_updated).days > 0:
            obj.last_updated = logfile.get('last_updated')
        
        obj.save()

        return obj
        


    def _parse_summary(self, logfile_obj, wb):
        # Scan down the sheet, looking for the four columns of data and matching to header data
        # Work between modes, saving the results to the db at the end.
        summary = wb.sheet_by_name('Summary')
        
        # Some reference constants
        headings1 = 1 # Most headings are in Col B, hence this is headings1
        headings2 = 0
        week1 = 2
        week2 = 3
        week3 = 4
        week4 = 5 # Ignoring the totals column after this week
        # List of Dictionaries to hold the data scanned in from the sheet
        summaryUA = [
          {'service_name':logfile_obj.service_name},
          {'service_name':logfile_obj.service_name},
          {'service_name':logfile_obj.service_name},
          {'service_name':logfile_obj.service_name},
        ] # Four columns of data on each sheet, we'll scan in parallel
        summaryCS = [{},{},{},{}] # Four columns of data on each sheet, we'll scan in parallel
        # Mode switch
        section = ''
        
        def _summaryUA_set(header_key, row_id):
            summaryUA[0][header_key] = summary.cell(row_id,week1).value
            summaryUA[1][header_key] = summary.cell(row_id,week2).value
            summaryUA[2][header_key] = summary.cell(row_id,week3).value
            summaryUA[3][header_key] = summary.cell(row_id,week4).value
            return None
        
        def _summaryCS_set(header_key, row_id):
            summaryCS[0][header_key] = summary.cell(row_id,week1).value
            summaryCS[1][header_key] = summary.cell(row_id,week2).value
            summaryCS[2][header_key] = summary.cell(row_id,week3).value
            summaryCS[3][header_key] = summary.cell(row_id,week4).value
            return None
        
        for row_id in range(summary.nrows):
            if section == 'User Actions':
                if summary.cell(row_id,headings1).value == 'Total Track Downloads' or \
                    summary.cell(row_id,headings2).value == 'Total Track Downloads':
                    self._summaryUA_set('total_track_downloads',row_id)
                    section = 'Client Software'
                    
                elif summary.cell(row_id,week1).value != '':
                    if summary.cell(row_id,heading_col2).value in self.modelmapping:
                        header = self.modelmapping.get(summary.cell(row_id,heading_col2).value)
                        self._summaryUA_set(header,row_id)
                    else:
                        err_str = "Key not recognised in col A, row " + str(row_id) + " - " + str(summary.cell(row_id,heading_col2).value)
                        self._errorlog(err_str)
                        raise CommandError(err_str)

            elif section == 'Client Software':
                if summary.cell(row_id,week1).value != '':
                    self._summaryCS_set(summary.cell(row_id,headings1).value,row_id)
                    
            else:
                # Should only happen at the start, and we're looking for week_ending dates, and then User Actions
                if summary.cell(row_id,week1).value == '':
                    section = summary.cell(row_id,headings2).value
                else:
                    self._summaryUA_set('week_ending',row_id)
                    self._summaryCS_set('week_ending',row_id)

            # Write the error cache to disk
            self._error_log_save()
            
        # Should now have 8 lists of dictionaries - 4 for Client Software, 4 for UserActions
        for i in range(0,3):
            week = summaryUA[i]
            
            # This needs to account for different types of import file (public vs public_dz)
            summary_object, summary_created = Summary.objects.get_or_create(
                week_ending=week.get('week_ending'), 
                service_name=logfile_obj.service_name
                defaults=week)
            summary_object.logfile = logfile_obj
            summary_object.save()
            
            if summary_created:
                for k,v in summaryCS[i].items():
                    # Parse each key to create a related ClientSoftware object
                    cs_object = ClientSoftware()
                    cs_object.logfile = logfile_obj
                    cs_object.summary = summary_object
                    cs_object.version_major = 0
                    cs_object.version_minor = 0
                    cs_object.count = int(v)
                                 
                    strings = k.split('/')
                    if len(strings) > 1:
                        version = strings[1].split('.')
                        if len(version) > 1:
                            # Most items will fall into this pattern Application/M.m/Platform
                            if strings[2] == '?':
                                cs_object.platform = str(strings[0])[:20] #iTunes-iPod, etc
                            else:
                                cs_object.platform = str(strings[2])[:20] #Macintosh, Windows
                            cs_object.version_major = int(version[0])
                            cs_object.version_minor = int(version[1])
                        else:
                            # This is likely to be the ?/?/Platform
                            cs_object.platform = str(strings[2])[:20] #Macintosh, Windows
                    else:
                        # Likely to be 'Not Listed'
                        cs_object.platform = 'Unknown'
                    
                    cs_object.save()
                
                # Parse this week's tracks
                self._parse_tracks(summary_object, wb.sheet_by_name(str(week.get('week_ending')) + ' Tracks'))
                self._error_log_save()
                # Parse this week's previews
                # self._parse_previews(summary_object, wb.sheet_by_name(str(week.get('week_ending')) + ' Previews'))
                # self._error_log_save()
                # Parse this week's browses
                # self._parse_browses(summary_object, wb.sheet_by_name(str(week.get('week_ending')) + ' Browse'))
                # self._error_log_save()
            else:
                print "Data has already been imported for " str(logfile_obj.service_name) + "@" + str(week.get('week_ending'))
        
        return None



    def _parse_tracks(self, summary_object, sheet):
        "Parse a Tracks sheet for counts."
        # Can assume data duplication has already been accounted for in the parse_summary() process, so if we're here, import...
        
        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            # Setup the basic count record
            tc = TrackCount()
            tc.summary = summary_object
            tc.count = int(sheet.cell(row_id,1).value)
            
            # Now link to path and handle
            tc.path = self._trackpath(summary_object.logfile, sheet.cell(row_id,0).value)
            tc.handle = self._trackhandle(summary_object.logfile, sheet.cell(row_id,2).value)
            tc.guid = self._trackguid(summary_object.logfile, sheet.cell(row_id,3).value[:255], tc)
            
            tc.save()
            
        # print "Imported TRACK data for " + str(week_ending) + " with " + str(count) + " out of " + str(sheet.nrows-1) + " added."
        return None


    def _trackpath(self, logfile_object, path):
        "Get or Create the TrackPath information"
        tp = TrackPath()
        tp.path = path
        tp.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.track_path_cache:
            if item.path == tp.path:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    tp = TrackPath.objects.get(id=item.id)
                    tp.logfile = logfile_object   
                    tp.save()
                    # Update the cache
                    item.logfile = logfile_object 
                return item
        
        # Nothing found, so save and update the cache
        tp.save()
        self.track_path_cache.append(tp)
        
        return tp


    def _trackhandle(self, logfile_object, handle):
        "Get or Create the TrackHandle information"
        th = TrackHandle()
        th.handle = handle
        th.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.track_handle_cache:
            if item.path == th.handle:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    th = TrackHandle.objects.get(id=item.id)
                    th.logfile = logfile_object   
                    th.save()
                    # Update the cache
                    item.logfile = logfile_object 
                return item
        
        # Nothing found, so save and update the cache
        th.save()
        self.track_handle_cache.append(th)
        
        return th
        

    def _trackguid(self, logfile_object, guid, trackcount_object):
        "Get or Create the TrackHandle information"
        tg = TrackGUID()
        tg.logfile = logfile_object
        
        # If guid provided, use. If not, find one. If none available, make one.
        if guid != '':
            tg.guid = guid
            # Attempt to locate in memory cache
            for item in self.track_guid_cache:
                if item.guid == tg.guid:
                    # Check if the import path appears earlier than the stored path and update if needed
                    if item.logfile.last_updated > logfile_object.last_updated:
                        # Update the database
                        tg = TrackGUID.objects.get(id=item.id)
                        tg.logfile = logfile_object   
                        tg.save()
                        # Update the cache
                        item.logfile = logfile_object 
                    return item
        else:
            # Match on handle (trust Apple to make these unique), or then path
            try:
                # Any existing TrackCount object should have a guid associated with it, thus, find one that has this handle, you've got it's guid
                tc = TrackCount.objects.get(handle=trackcount_object.handle.id)
                tg.guid = tc.guid.guid
            except TrackCount.DoesNotExist:
                # First time this handle has been seen, so look for a path match
                try:
                    tc = TrackCount.objects.get(path=trackcount_object.path.id)
                    tg.guid = tc.guid.guid
                except TrackPath.DoesNotExist:
                    # No path match found, really must be new, so generate a GUID (UUID)
                    tg.guid = str(uuid.uuid4())

        # Nothing found, so save and update the cache
        tg.save()
        self.track_guid_cache.append(tg)
        
        return tg




    def _parse_browses(self, logfile_obj, sheet, week_ending):
        # print "Beginning import for BROWSE:", sheet_name
        cache = list(Browse.objects.filter(week_ending=week_ending).order_by('handle'))
        # Reset variables
        count = 0
        

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            created = True
            report = Browse()
            report.week_ending = week_ending #Not: time.strptime(week_ending,'%Y-%m-%d')
            report.path = sheet.cell(row_id,0).value
            report.count = int(sheet.cell(row_id,1).value)
            report.handle = long(sheet.cell(row_id,2).value)
            report.guid = sheet.cell(row_id,3).value

            # Check the cache
            for item in cache:
                if item.handle == report.handle and item.count == report.count:
                    self._errorlog("Browse row "+str(row_id)+" has already been imported")
                    created = False
                    continue

            if created:
                count += 1
                report.save()
                cache.insert(0,report)
                
        print "Imported BROWSE data for " + str(week_ending) + " with " + str(count) + " out of " + str(sheet.nrows-1) + " added."
        return None





    def _parse_previews(self, logfile_obj, sheet, week_ending):
        # print "Beginning import for PREVIEW:", sheet_name
        cache = list(Preview.objects.filter(week_ending=week_ending).order_by('handle'))
        # Reset variables
        count = 0
        

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            created = True
            report = Preview()
            report.week_ending = week_ending #Not: time.strptime(week_ending,'%Y-%m-%d')
            report.path = sheet.cell(row_id,0).value
            report.count = int(sheet.cell(row_id,1).value)
            report.handle = long(sheet.cell(row_id,2).value)
            report.guid = sheet.cell(row_id,3).value

            # Check the cache
            for item in cache:
                # print "item:" + str(item.handle) + ". report:" + str(report.handle) + " Match=" + str(item.handle == report.handle)
                if item.handle == report.handle:
                    self._errorlog("Preview row "+str(row_id)+" has already been imported")
                    created = False
                    continue

            if created:
                count += 1
                report.save()
                cache.insert(0,report)
                
        print "Imported PREVIEW data for " + str(week_ending) + " with " + str(count) + " out of " + str(sheet.nrows-1) + " added."
        return None







    # DEBUG AND INTERNAL HELP METHODS ==============================================================

    def _debug(self,error_str):
        "Basic optional debug function. Print the string if enabled"
        if self.debug:
            print 'DEBUG:' + str(error_str) + '\n'
        return None
            

    def _errorlog(self,error_str):
        "Write errors to a log file"
        self.error_cache += 'ERROR:' + str(error_str) + '\n'
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