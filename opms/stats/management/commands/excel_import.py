# Import script for Apple iTunes U supplied Excel spreadsheets
# Author: Carl Marshall
# Last Edited: 4-2-2011

from optparse import make_option
from django.core.management.base import LabelCommand, CommandError

from opms.stats.models import *
from xlrd import open_workbook
import time, sys
        
class Command(LabelCommand):
    args = '<spreadsheet.xls>'
    help = 'Imports the contents of the specified spreadsheet into the database'
    
    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Record basic information about the import process for reporting
        self.import_stats = {}
        # Error logging file and string cache
        self.error_log = ""
        self.error_cache = ""
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
            'iTunes/10.0/Macintosh':'cs_itunes_10_0_macintosh',
            'iTunes/10.0/Windows':'cs_itunes_10_0_windows',
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
            'iTunes/9.2/Windows':'cs_itunes_9_2_windows'
        }
        return None


    def handle_label(self, filename, **options):
        print "Import started at " + str(datetime.datetime.utcnow()) + "\n"
        
        # Create an error log per import file
        self._errorlog_start(filename + '_import-error.log')
        
        # Some basic checking
        if filename.endswith('.xls') == False:
           raise CommandError("This is not a valid Excel 1998-2002 file. Must end in .xls\n\n")        
        
        # Read the Worksheet
        wb = open_workbook(filename)
        
        # Scan through the worksheets
        for sheet_name in wb.sheet_names():
            if sheet_name == 'Summary':
                self._parse_summary(wb.sheet_by_name(sheet_name))
            elif sheet_name.endswith(" Tracks"):
                self._parse_tracks(wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Browse"):
                self._parse_browses(wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Edits"):
                self._parse_edits(wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Previews"):
                self._parse_previews(wb.sheet_by_name(sheet_name), sheet_name[0:10])
            elif sheet_name.endswith(" Users"):
                self._parse_users(wb.sheet_by_name(sheet_name), sheet_name[0:10])
            else:
                err_str = "Unidentified Worksheet in this report (" + str(sheet_name) + "). Please investigate"
                self._errorlog(err_str)
                raise CommandError(err_str)
            # Write the error cache to disk
            self._error_log_save()
            
        print "\nImport finished at " + str(datetime.datetime.utcnow())
        self._errorlog_stop()
        return None


    def _parse_summary(self, summary):
        # Define some constants
        heading_col1 = 1
        heading_col2 = 0

        # Iterate through the four columns of data
        for col_id in range(2,6):
            # Iterate through this week of data matching cell heading to model and assigning the value
            report = {}
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
                            if summary.cell(row_id,heading_col1).value in self.modelmapping:
                                header = self.modelmapping.get(summary.cell(row_id,heading_col1).value)
                            # There are two rows labelled "Not Listed". The first is a User Action, the second a Client Software field.
                            elif summary.cell(row_id,heading_col1).value == "Not Listed":
                                if first_not_listed:
                                    header = 'ua_not_listed' 
                                    first_not_listed = False
                                else:
                                    header = 'cs_not_listed'
                            else:
                                self._errorlog("Key not recognised in col B - " + str(summary.cell(row_id,heading_col1).value))
                        elif summary.cell(row_id,heading_col2).value != '':
                            if summary.cell(row_id,heading_col2).value in self.modelmapping:
                                header = self.modelmapping.get(summary.cell(row_id,heading_col2).value)
                            else:
                                self._errorlog("Key not recognised in col A - " + str(summary.cell(row_id,heading_col2).value))
                        else:
                            header = 'ERROR: UNKNOWN HEADER'

                        # Now store the sheet value in the dictionary against the model fieldname
                        report[header] = col_value
    
            # Now try and save this week's worth of data
            obj, created = Summary.objects.get_or_create(week_ending=report.get('week_ending'), defaults=report)

            # Summary report for keeping track of progress
            if created:
                print "Data for week ending",obj.week_ending,", has been added to the database"
                obj.save()
            else:
                print "Data for week ending",obj.week_ending,", was found in the database. Not updated."
        return None


    def _parse_tracks(self, sheet, week_ending):
        # print "Beginning import for TRACKS:", sheet_name
        # Reset variables
        report = {}
        report['week_ending'] = week_ending
        count = 0

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            report['path'] = sheet.cell(row_id,0).value
            report['count'] = sheet.cell(row_id,1).value
            report['handle'] = sheet.cell(row_id,2).value
            report['guid'] = sheet.cell(row_id,3).value

            # Now test to see if this has been imported already. Note, use date and handle beucase Guid isn't present for tracks thathave been deleted, thus they show up as errors, even though there is valid data.
            obj, created = Track.objects.get_or_create(week_ending=report.get('week_ending'), handle=report.get('handle'), defaults=report)
            
            if created:
                count += 1
                obj.save()
            else:
                self._errorlog("Track row"+str(row_id)+"has already been imported")
            
        print "Imported TRACK data for", report.get('week_ending'), "with", count, "out of", sheet.nrows-1, "added."
        return None



    def _parse_browses(self, sheet, week_ending):
        # print "Beginning import for BROWSE:", sheet_name
        # Reset variables
        report = {}
        report['week_ending'] = week_ending
        count = 0

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            report['path'] = sheet.cell(row_id,0).value
            report['count'] = sheet.cell(row_id,1).value
            report['handle'] = sheet.cell(row_id,2).value
            report['guid'] = sheet.cell(row_id,3).value

            # Now test to see if this has been imported already. Note, use date and handle beucase Guid isn't present for tracks thathave been deleted, thus they show up as errors, even though there is valid data.
            obj, created = Browse.objects.get_or_create(
                week_ending=report.get('week_ending'), 
                handle=report.get('handle'),
                count=report.get('count'), # Because there are so many duplicates in Browse, add the data, we'll sort it later
                defaults=report)

            if created:
                count += 1
                obj.save()
            else:
                self._errorlog("Browse row"+ str(row_id) + "has already been imported")
        print "Imported Browse data for", report.get('week_ending'), "with", count, "out of", sheet.nrows-1, "added."
        return None



    def _parse_edits(self, sheet, week_ending):
        print "Found EDITS:",sheet_name,". Skipping edit import."
        return None



    def _parse_previews(self, sheet, week_ending):
        # print "Beginning import for PREVIEW:", sheet_name
        # Reset variables
        report = {}
        report['week_ending'] = week_ending
        count = 0
                                           
        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            report['path'] = sheet.cell(row_id,0).value
            report['count'] = sheet.cell(row_id,1).value
            report['handle'] = sheet.cell(row_id,2).value
            report['guid'] = sheet.cell(row_id,3).value

            # Now test to see if this has been imported already. Note, use date and handle beucase Guid isn't present for tracks thathave been deleted, thus they show up as errors, even though there is valid data.
            obj, created = Preview.objects.get_or_create(week_ending=report.get('week_ending'), handle=report.get('handle'), defaults=report)

            if created:
                count += 1
                obj.save()
            else:
                self._errorlog("Preview row" + str(row_id) + "has already been imported")
        print "Imported Preview data for", report.get('week_ending'), "with", count, "out of", sheet.nrows-1, "added."
        return None



    def _parse_users(self, sheet, week_ending):
        print "Found USERS:", sheet_name, ". Skipping user import."
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