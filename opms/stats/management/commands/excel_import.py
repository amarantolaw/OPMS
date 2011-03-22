# Import script for Apple iTunes U supplied Excel spreadsheets
# Author: Carl Marshall
# Last Edited: 22-3-2011

from optparse import make_option
from django.core.management.base import LabelCommand, CommandError

from opms.stats.models import *
from xlrd import open_workbook
from datetime import time, datetime
import sys
        
class Command(LabelCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'
    option_list = LabelCommand.option_list + (
        make_option('--merge', action='store', dest='merge',
            default=False, help='Use this option to add this data to exisiting data, thus summing counts for records.'),
    )
    
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
            'Browse':'ua_browse',
            'DownloadPreview':'ua_download_preview',
            'DownloadPreviewiOS':'ua_download_preview_ios',
            'DownloadTrack':'ua_download_track',
            'DownloadTracks':'ua_download_tracks',
            'DownloadiOS':'ua_download_ios',
            'EditFiles':'ua_edit_files',
            'EditPage':'ua_edit_page',
            'Logout':'ua_logout',
            'SearchResultsPage':'ua_search_results_page',
            'Subscription':'ua_subscription',
            'SubscriptionEnclosure':'ua_subscription_enclosure',
            'SubscriptionFeed':'ua_subscription_feed',
            'Upload':'ua_upload',
            'Total Track Downloads':'total_track_downloads',
            '?/?/Macintosh':'cs_macintosh',
            '?/?/Windows':'cs_windows',
            'iTunes-iPad/3.2/?':'cs_itunes_ipad_3_2',
            'iTunes-iPhone/3.0/?':'cs_itunes_iphone_3_0',
            'iTunes-iPhone/3.1/?':'cs_itunes_iphone_3_1',
            'iTunes-iPhone/4.0/?':'cs_itunes_iphone_4_0',
            'iTunes-iPhone/4.1/?':'cs_itunes_iphone_4_1',
            'iTunes-iPod/3.0/?':'cs_itunes_ipod_3_0',
            'iTunes-iPod/3.1/?':'cs_itunes_ipod_3_1',
            'iTunes-iPod/4.0/?':'cs_itunes_ipod_4_0',
            'iTunes-iPod/4.1/?':'cs_itunes_ipod_4_1',
            'iTunes/4.4/Macintosh':'cs_itunes_4_4_macintosh',
            'iTunes/4.4/Windows':'cs_itunes_4_4_windows',
            'iTunes/4.5/Macintosh':'cs_itunes_4_5_macintosh',
            'iTunes/4.5/Windows':'cs_itunes_4_5_windows',
            'iTunes/4.6/Macintosh':'cs_itunes_4_6_macintosh',
            'iTunes/4.6/Windows':'cs_itunes_4_6_windows',
            'iTunes/4.7/Macintosh':'cs_itunes_4_7_macintosh',
            'iTunes/4.7/Windows':'cs_itunes_4_7_windows',
            'iTunes/4.8/Macintosh':'cs_itunes_4_8_macintosh',
            'iTunes/4.8/Windows':'cs_itunes_4_8_windows',
            'iTunes/4.9/Macintosh':'cs_itunes_4_9_macintosh',
            'iTunes/4.9/Windows':'cs_itunes_4_9_windows',
            'iTunes/5.0/Macintosh':'cs_itunes_5_0_macintosh',
            'iTunes/5.0/Windows':'cs_itunes_5_0_windows',
            'iTunes/6.0/Macintosh':'cs_itunes_6_0_macintosh',
            'iTunes/6.0/Windows':'cs_itunes_6_0_windows',
            'iTunes/7.0/Macintosh':'cs_itunes_7_0_macintosh',
            'iTunes/7.0/Windows':'cs_itunes_7_0_windows',
            'iTunes/7.1/Macintosh':'cs_itunes_7_1_macintosh',
            'iTunes/7.1/Windows':'cs_itunes_7_1_windows',
            'iTunes/7.2/Macintosh':'cs_itunes_7_2_macintosh',
            'iTunes/7.2/Windows':'cs_itunes_7_2_windows',
            'iTunes/7.3/Macintosh':'cs_itunes_7_3_macintosh',
            'iTunes/7.3/Windows':'cs_itunes_7_3_windows',
            'iTunes/7.4/Macintosh':'cs_itunes_7_4_macintosh',
            'iTunes/7.4/Windows':'cs_itunes_7_4_windows',
            'iTunes/7.5/Macintosh':'cs_itunes_7_5_macintosh',
            'iTunes/7.5/Windows':'cs_itunes_7_5_windows',
            'iTunes/7.6/Macintosh':'cs_itunes_7_6_macintosh',
            'iTunes/7.6/Windows':'cs_itunes_7_6_windows',
            'iTunes/7.7/Macintosh':'cs_itunes_7_7_macintosh',
            'iTunes/7.7/Windows':'cs_itunes_7_7_windows',
            'iTunes/8.0/Macintosh':'cs_itunes_8_0_macintosh',
            'iTunes/8.0/Windows':'cs_itunes_8_0_windows',
            'iTunes/8.1/Macintosh':'cs_itunes_8_1_macintosh',
            'iTunes/8.1/Windows':'cs_itunes_8_1_windows',
            'iTunes/8.2/Macintosh':'cs_itunes_8_2_macintosh',
            'iTunes/8.2/Windows':'cs_itunes_8_2_windows',
            'iTunes/9.0/Macintosh':'cs_itunes_9_0_macintosh',
            'iTunes/9.0/Windows':'cs_itunes_9_0_windows',
            'iTunes/9.1/Macintosh':'cs_itunes_9_1_macintosh',
            'iTunes/9.1/Windows':'cs_itunes_9_1_windows',
            'iTunes/9.2/Macintosh':'cs_itunes_9_2_macintosh',
            'iTunes/9.2/Windows':'cs_itunes_9_2_windows',
            'iTunes/10.0/Macintosh':'cs_itunes_10_0_macintosh',
            'iTunes/10.0/Windows':'cs_itunes_10_0_windows',
        }
        return None


    def handle_label(self, filename, **options):
        print "Import started at " + str(datetime.utcnow()) + "\n"
        
        # Create an error log per import file
        self._errorlog_start(filename + '_import-error.log')

        if options.get('merge', False) != False:
            print "WARNING: Processing file to combine with existing records."
            self.merge = True

        # Some basic checking
        if filename.endswith('.xls') == False:
           raise CommandError("This is not a valid Excel 1998-2002 file. Must end in .xls\n\n")
        
        # Test the log_service option is valid. Use the same list as LogFile.SERVICE_NAME_CHOICES
        # Guess the service based on the filename
        try:
            xls =filename[filename.rindex('/')+1:]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            xls = filename
        # This may be Oxford specific?
        if xls.find('-dz-') > 0:
            log_service = 'itu-psm'
        elif xls.find('-public-') > 0:
            log_service = 'itu'
        else:
            raise CommandError("The service can not be determined from the filename.")
        
        # This only needs setting/getting the once per call of this function
        logfile_obj = self._logfile(filename, log_service)
        
        # Read the Worksheet
        wb = open_workbook(filename)
        
        # Scan through the worksheets
        for sheet_name in wb.sheet_names():
            if sheet_name == 'Summary':
                self._parse_summary(logfile_obj, wb.sheet_by_name(sheet_name))
            elif sheet_name.endswith(" Tracks"):
                self._parse_tracks(logfile_obj, wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Browse"):
                self._parse_browses(logfile_obj, wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Edits"):
                self._parse_edits(logfile_obj, wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Previews"):
                self._parse_previews(logfile_obj, wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Users"):
                self._parse_users(logfile_obj, wb.sheet_by_name(sheet_name), sheet_name[0:10])
            else:
                err_str = "Unidentified Worksheet in this report (" + str(sheet_name) + "). Please investigate"
                self._errorlog(err_str)
                raise CommandError(err_str)
            # Write the error cache to disk
            self._error_log_save()
            
        print "\nImport finished at " + str(datetime.utcnow())
        self._errorlog_stop()
        return None



    def _logfile(self, filename, log_service):
        "Get or create a LogFile record for the given filename"
        logfile = {}
        logfile['service_name'] = log_service
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
        


    def _parse_summary(self, logfile_obj, summary):
        # Scan down the sheet, looking for the four columns of data and matching to header data
        # Work between modes, saving the results at the end.
        section = ''
        for row_id in range(summary.nrows):
            if section == '':
                # Should only happen at the start, and we're looking for week_ending dates, and then User Actions
            elif section == 'User Actions':
            elif section == 'Total Track Downloads':
            elif section == 'Client Software':
            
            
            
            
            
            
            
            
    
    
        # Define some constants
        heading_col1 = 1
        heading_col2 = 0

        # Iterate through the four columns of data
        for col_id in range(2,6):
            # Iterate through this week of data matching cell heading to model and assigning the value
            report = {}
            report['logfile'] = logfile_obj
            week_ending = ''
            first_not_listed = True
            obj = ''
            created = False
            for row_id, col_value in enumerate(summary.col_values(col_id)):
                if col_value != '':
                    if week_ending == '':
                        week_ending = col_value # test using a sting in place of a datetime object
                        report['week_ending'] = week_ending
                    else:
                        # Get header by looking in column B first, then in  column A if nothing present
                        header = ''
                        if summary.cell(row_id,heading_col1).value != '':
                            # There are two rows labelled "Not Listed". The first is a User Action, the second a Client Software field.
                            if summary.cell(row_id,heading_col1).value == "Not Listed":
                                if first_not_listed:
                                    header = 'ua_not_listed' 
                                    first_not_listed = False
                                else:
                                    header = 'cs_not_listed'
                            else:
                                header = summary.cell(row_id,heading_col1).value
                                #err_str = "Key not recognised in col B, row " + str(row_id) + " - " + str(summary.cell(row_id,heading_col1).value)
                                #self._errorlog(err_str)
                                #raise CommandError(err_str)
                        elif summary.cell(row_id,heading_col2).value != '':
                            if summary.cell(row_id,heading_col2).value in self.modelmapping:
                                header = self.modelmapping.get(summary.cell(row_id,heading_col2).value)
                            else:
                                err_str = "Key not recognised in col A, row " + str(row_id) + " - " + str(summary.cell(row_id,heading_col2).value)
                                self._errorlog(err_str)
                                raise CommandError(err_str)
                        else:
                            err_str = "UNKNOWN HEADER: Missing key row " + str(row_id)
                            self._errorlog(err_str)
                            raise CommandError(err_str)

                        # Now store the sheet value in the dictionary against the model fieldname
                        report[header] = col_value
    
            # Now try and save this week's worth of data
            obj, created = Summary.objects.get_or_create(week_ending=report.get('week_ending'), defaults=report)

            # Summary report for keeping track of progress
            if created:
                print "Data for week ending",obj.week_ending,", has been added to the database"
                obj.save()
            else:
                if self.merge or report.get('logfile').service_name != obj.logfile.service_name:
                    # take the values in report[] and merge with the values in obj
                    for k,v in report.items():
                        try:
                            merged_value = int(getattr(obj, k)) + int(v)
                            self._debug("k:"+ str(k) +". obj-v:" + str(int(getattr(obj, k))) + ". new-v:" + str(int(v)) + ". Merged result:" + str(merged_value))
                            setattr(obj, k, merged_value)
                        except TypeError:
                            pass # Because all we're testing for is whether these are two integers to sum
                    print "Data for week ending",obj.week_ending,", has been merged into the database"
                    obj.save()
                else:
                    print "Data for week ending",obj.week_ending,", was found in the database. Not updated."
        return None


    def _parse_tracks(self, logfile_obj, sheet, week_ending):
        # week_ending is a given from the sheet name
        # count may need to be added to if this is from a duplicate data source (e.g. excel sheets from two different sites)
        # if present, treat guid as the key, and add subsquent path and handle codes, noting when the oldest date for them 
        #    arises (i.e. just after they changed)
        # guid may not be present in early data, if missing... match on handle and path. If handle exists, add a new path. 
        # If no handle found, look for an existing path and add handle, otherwise create new.
        
        track_cache = list(Track.objects.filter(week_ending=week_ending).order_by('guid'))
    
        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            # Put together a basic model structure from the raw data
            report = Track()
            report.logfile = logfile_obj
            report.week_ending = week_ending #Not: time.strptime(week_ending,'%Y-%m-%d')
            report.count = int(sheet.cell(row_id,1).value)
            report.guid = sheet.cell(row_id,3).value[:255]
            
            report.path = TrackPath()
            report.path.logfile = logfile_obj
            report.path.path = sheet.cell(row_id,0).value
            report.path.week_ending = week_ending
            
            report.handle = TrackHandle()
            report.handle.logfile = logfile_obj
            report.handle.handle = long(sheet.cell(row_id,2).value)
            report.handle.week_ending = week_ending
            # Create a holder for and existing track object, to be found in the cache
            track_obj = ''
        
            if report.guid != '':    
                # Check the cache
                for item in cache:
                    # Look to see if this data come from an alternative service or merge has been forced
                    if report.logfile.service_name != item.logfile.service_name or self.merge:
                        # Leave logfile
                    
                    # Don't need to check the date! Data can only be for this date...
                    if item.guid == report.guid:
                        self._errorlog("Track row "+str(row_id)+" has already been imported")
                        
                        tp = item.path
                        # Test if path matches, then update the date to find the earliest example of this path
                        if tp.path == report.path.path and \
                        tp.week_ending > datetime.strptime(report.path.week_ending,'%Y-%m-%d').date():
                            # compare dates, if this path existed earlier than the date shows, update the date and logfile
                            tp.week_ending = report.path.week_ending
                            tp.logfile = report.path.logfile
                            tp.save()
                        # If the path doesn't match, then it has changed, so we should create another path object
                        elif tp.path != report.path.path:
                        
                        th = item.handle
                        if th.handle == report.handle.handle and \
                        th.week_ending > datetime.strptime(report.handle.week_ending,'%Y-%m-%d').date():
                            # compare dates, if this path existed earlier than the date shows, update the date and logfile
                            th.week_ending = report.handle.week_ending
                            th.logfile = report.handle.logfile
                            th.save()
                        
                        track_obj = item
                        continue


            # If created...
            if track_obj == '':
                count += 1
                report.save()
                cache.append(report)
                
    
        # print "Beginning import for TRACKS:", sheet_name
        # Reset variables
        count = 0

            

            if created:
            elif self.merge:
                try:
                    merged_value = int(obj.count) + report.count
                    self._debug("obj.count:" + str(obj.count) + ". report.count:" + str(report.count) + ". Merged result:" + str(merged_value))
                    obj.count = merged_value
                    
                    obj.save()
                    count += 1
                except TypeError:
                    pass # Because all we're testing for is whether these are two integers to sum
                
            
        print "Imported TRACK data for " + str(week_ending) + " with " + str(count) + " out of " + str(sheet.nrows-1) + " added."
        return None



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



    def _parse_edits(self, logfile_obj, sheet, week_ending):
        print "Found 'EDITS " + str(week_ending) + "'. Skipping edit import."
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



    def _parse_users(self, logfile_obj, sheet, week_ending):
        print "Found 'USERS " + str(week_ending) + "'. Skipping user import."
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