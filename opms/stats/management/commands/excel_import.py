# Import script for Apple iTunes U supplied Excel spreadsheets
# Author: Carl Marshall
# Last Edited: 17-5-2012

#from optparse import make_option
from django.core.management.base import LabelCommand, CommandError

from opms.stats.models import *
from xlrd import open_workbook, biffh
from datetime import datetime
import sys, uuid, os

class Command(LabelCommand):
    args = '<path/to/spreadsheets/>'
    help = 'Imports the contents of the specified directory of spreadsheets into the database'
    #option_list = LabelCommand.option_list + (
    #    make_option('--merge', action='store', dest='merge',
    #        default=False, help='Use this option to add this data to exisiting data, thus summing counts for records.'),
    #)

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
        self.track_path_cache = list(AppleTrackPath.objects.all())
        self.track_handle_cache = list(AppleTrackHandle.objects.all())
        self.track_guid_cache = list(AppleTrackGUID.objects.all())
        # Browse caches
        self.browse_path_cache = list(AppleBrowsePath.objects.all())
        self.browse_handle_cache = list(AppleBrowseHandle.objects.all())
        self.browse_guid_cache = list(AppleBrowseGUID.objects.all())
        # Preview caches
        self.preview_path_cache = list(ApplePreviewPath.objects.all())
        self.preview_handle_cache = list(ApplePreviewHandle.objects.all())
        self.preview_guid_cache = list(ApplePreviewGUID.objects.all())

    def _list_files(self, path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower()[-4:] == ".xls":
                    file_list.append(os.path.join(root)+"/"+file) # Yes, unix specific hack
        return file_list


    def handle_label(self, path, **options):
        print "Import started at " + str(datetime.utcnow()) + "\n"

        # Scan directory for files, compare them to names in the existing LogFile list. Import the first X new files.
        found_files_list = self._list_files(path)
        found_files_list.sort() # Trust the naming conventions to put a sortable date on them
        import_file_limit = len(found_files_list)
        if import_file_limit > 10:
            import_file_limit = 10
        print "%s files have been found for import. Processing %s of them now",(len(found_files_list), import_file_limit)
        for filename in found_files_list:
            print filename
            # This only needs setting/getting the once per call of this function
            logfile_obj, created = self._logfile(file)
            if created and import_file_limit > 0:
                # Create an error log per import file
                self._errorlog_start(filename + '_import-error.log')

                # Read the Worksheet
                wb = open_workbook(filename)

                # Start the parsing with the summary sheet
                self._parse_summary(logfile_obj, wb)

                import_file_limit -= 1

        print "\nImport finished at " + str(datetime.utcnow())
        self._errorlog_stop()
        return None



    def _logfile(self, filename):
        "Get or create a LogFile record for the given filename"
        logfile = {}

        # Some basic checking - the file list function should make this redundant
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

        logfile['last_updated'] = datetime.utcnow()

        obj, created = LogFile.objects.get_or_create(
            service_name = logfile.get('service_name'),
            file_name = logfile.get('file_name'),
            file_path = logfile.get('file_path'),
            defaults = logfile)

        # If this isn't the first time, and the datetime is significantly different from last access, update the time
        if not created and (logfile.get('last_updated') - obj.last_updated).days > 0:
            obj.last_updated = logfile.get('last_updated')

        obj.save()

        return obj, created


    # ===================================================== SUMMARY ================================

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
          {'service_name':logfile_obj.service_name, 'logfile':logfile_obj},
          {'service_name':logfile_obj.service_name, 'logfile':logfile_obj},
          {'service_name':logfile_obj.service_name, 'logfile':logfile_obj},
          {'service_name':logfile_obj.service_name, 'logfile':logfile_obj},
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
                    _summaryUA_set('total_track_downloads',row_id)
                    section = 'Client Software'

                elif summary.cell(row_id,week1).value != '':
                    if summary.cell(row_id,headings1).value in self.modelmapping:
                        header = self.modelmapping.get(summary.cell(row_id,headings1).value)
                        _summaryUA_set(header,row_id)
                    else:
                        err_str = "Key not recognised in col A, row " + str(row_id) + " - " + str(summary.cell(row_id,headings1).value)
                        self._errorlog(err_str)
                        raise CommandError(err_str)

            elif section == 'Client Software':
                if summary.cell(row_id,week1).value != '':
                    _summaryCS_set(summary.cell(row_id,headings1).value,row_id)

            else:
                # Should only happen at the start, and we're looking for week_beginning dates, and then User Actions
                if summary.cell(row_id,week1).value == '':
                    section = summary.cell(row_id,headings2).value
                else:
                    _summaryUA_set('week_beginning',row_id)

            # Write the error cache to disk
            self._error_log_save()
        self._debug('Summary data parsed')

        # Should now have 8 lists of dictionaries - 4 for Client Software, 4 for UserActions/Summarys
        for i in range(0,4):
            week = summaryUA[i]

            # This needs to account for different types of import file (public vs public_dz)
            summary_object, summary_created = AppleWeeklySummary.objects.get_or_create(
                week_ending=week.get('week_beginning'),
                service_name=logfile_obj.service_name,
                defaults=week)
            summary_object.save()

            if summary_created:
                print "Imported SUMMARY data for " + str(week.get('week_beginning'))

                # Now work through the related week's worth of Tracks, Browses and Previews. These sheets might be missing in early files.
                self._parse_related_sheets(summary_object, wb, week)

            else:
                print "NOTE: Data has previously been imported for " + str(logfile_obj.service_name) + "@" + str(week.get('week_beginning'))
                # Check the date of the excel file, and whether the total downloads match.
                # Apple change their results from time to time and this is to detect it
                if int(summary_object.total_track_downloads) != int(week.get('total_track_downloads')):
                    if summary_object.logfile.file_name[-14:-4] < logfile_obj.file_name[-14:-4]:
                        # I.e. if the record in the database is less recent than this excel file, report and overwrite...
                        err_msg = "WARNING: More recent data does not match previously imported data.\nOverwriting...\n" +\
                                  "Total was:" + str(summary_object.total_track_downloads) + ".\n" +\
                                  "New value:" + str(week.get('total_track_downloads')) + ".\n"
                        self._errorlog(err_msg)
                        print err_msg

                        # Overwrite the week's worth of data... delete first, then insert newer data
                        AppleWeeklyTrackCount.objects.filter(summary=summary_object).delete()
                        AppleWeeklyBrowseCount.objects.filter(summary=summary_object).delete()
                        AppleWeeklyPreviewCount.objects.filter(summary=summary_object).delete()
                        summary_object.delete()

                        # Create afresh... perhaps a little superfluous
                        summary_object, summary_created = AppleWeeklySummary.objects.get_or_create(
                            week_ending=week.get('week_beginning'),
                            service_name=logfile_obj.service_name,
                            defaults=week)
                        summary_object.save()

                        print "Re-imported SUMMARY data for " + str(week.get('week_beginning'))

                        self._parse_related_sheets(summary_object, wb, week)

                    else:
                        # Newer data exists already, so warn, but do nothing to change the data
                        err_msg = "WARNING: Existing more recent data does not match data attempting to be imported.\n" +\
                                  "Total is:" + str(summary_object.total_track_downloads) + ".\n" +\
                                  "Ignoring:" + str(week.get('total_track_downloads')) + " from the import.\n"
                        self._errorlog(err_msg)
                        print err_msg

                    self._error_log_save()
        return None


    def _parse_related_sheets(self, summary_object, wb, week):
        try:
            self._parse_tracks(summary_object, wb.sheet_by_name(str(week.get('week_beginning')) + ' Tracks'))
        except biffh.XLRDError:
            err_msg = "Sheet does not exist for " + str(week.get('week_beginning')) + " Tracks"
            self._errorlog(err_msg)
            print err_msg
        try:
            self._parse_browses(summary_object, wb.sheet_by_name(str(week.get('week_beginning')) + ' Browse'))
        except biffh.XLRDError:
            err_msg = "Sheet does not exist for " + str(week.get('week_beginning')) + " Browse"
            self._errorlog(err_msg)
            print err_msg
        try:
            self._parse_previews(summary_object, wb.sheet_by_name(str(week.get('week_beginning')) + ' Previews'))
        except biffh.XLRDError:
            err_msg = "Sheet does not exist for " + str(week.get('week_beginning')) + " Previews"
            self._errorlog(err_msg)
            print err_msg

            self._error_log_save()
        return None

    # ===================================================== TRACKS =================================

    def _parse_tracks(self, summary_object, sheet):
        "Parse a Tracks sheet for counts."
        # Can assume data duplication has already been accounted for in the parse_summary() process, so if we're here, import...
        count = 0

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            # Setup the basic count record
            tc = AppleWeeklyTrackCount()
            tc.summary = summary_object
            tc.count = int(sheet.cell(row_id,1).value)

            # Now link to path and handle
            tc.path = self._trackpath(summary_object.logfile, sheet.cell(row_id,0).value)
            tc.handle = self._trackhandle(summary_object.logfile, sheet.cell(row_id,2).value)

            # Guids don't appear until 24-05-2009. Prior to that there was no guid column, so this call will fail initially.
            try:
                tc.guid = self._trackguid(summary_object.logfile, sheet.cell(row_id,3).value[:255], tc)
            except IndexError:
                tc.guid = self._trackguid(summary_object.logfile, '', tc)
                self._errorlog('No GUID found for ' + str(tc.path) + '. Generated: ' + str(tc.guid))

            tc.save()
            count += 1

        print "Imported TRACK data for " + str(summary_object.week_ending) + " with " + str(count) + " rows added."
        return None


    def _trackpath(self, logfile_object, path):
        "Get or Create the AppleTrackPath information"
        tp = AppleTrackPath()
        tp.path = path
        tp.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.track_path_cache:
            if item.path == tp.path:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    tp = AppleTrackPath.objects.get(id=item.id)
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
        "Get or Create the AppleTrackHandle information"
        th = AppleTrackHandle()
        th.handle = handle
        th.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.track_handle_cache:
            if item.handle == th.handle:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    th = AppleTrackHandle.objects.get(id=item.id)
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
        "Get or Create the AppleTrackGUID information"
        tg = AppleTrackGUID()
        tg.logfile = logfile_object

        # If guid provided, search for and use.
        # If first time this guid has been seen, see if it applies to any previously unGUID'd tracks.
        # If no guid, find one (works fine for importing backwards). If still none available, make one.
        if guid != '':
            tg.guid = guid
            # Attempt to locate in memory cache, if found, then link to trackcount and stop
            for item in self.track_guid_cache:
                if item.guid == tg.guid:
                    # Check if the import path appears earlier than the stored path and update if needed
                    if item.logfile.last_updated > logfile_object.last_updated:
                        # Update the database
                        tg = AppleTrackGUID.objects.get(id=item.id)
                        tg.logfile = logfile_object
                        tg.save()
                        # Update the cache
                        item.logfile = logfile_object
                    return item

        # Match on handle (trust Apple to make these unique), or then path
        try:
            # Any existing AppleWeeklyTrackCount object should have a guid associated with it, thus, find one that has this handle, you've got it's guid
            tc = AppleWeeklyTrackCount.objects.filter(handle=trackcount_object.handle.id)
            if guid == '': # No guid, so use one found by a handle match
                return tc[0].guid

            else: # Update the prior trackcount objects to use the newly found GUID
                tg.save()
                for item in tc:
                    item.guid = tg
                    item.save()
        except IndexError:
            # First time this handle has been seen, so look for a path match
            try:
                tc = AppleWeeklyTrackCount.objects.filter(path=trackcount_object.path.id)
                if guid == '': # No guid, so use one found by a handle match
                    return tc[0].guid

                else: # Update the prior trackcount objects to use the newly found GUID
                    tg.save()
                    for item in tc:
                        item.guid = tg
                        item.save()
            except IndexError:
                # No path match found, really must be new, so generate a GUID (UUID)
                tg.guid = 'OPMS:' + str(uuid.uuid4())
                tg.save()
                self._errorlog("No AppleTrackGUID found for " +str(trackcount_object.path)+ "(" + str(trackcount_object.handle) + "). " +\
                  "Created: " + str(tg.guid))

        self.track_guid_cache.append(tg)
        # Note: Will likely need to do a manual clean out of defunct custom GUIDs as this process doesn't delete redundant records, just unlinks them
        return tg



    # ===================================================== BROWSES ================================

    def _parse_browses(self, summary_object, sheet):
        "Parse a Browse sheet for counts."
        # Can assume data duplication has already been accounted for in the parse_summary() process, so if we're here, import...
        count = 0

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            # Setup the basic count record
            bc = AppleWeeklyBrowseCount()
            bc.summary = summary_object
            bc.count = int(sheet.cell(row_id,1).value)

            # Now link to path and handle
            bc.path = self._browsepath(summary_object.logfile, sheet.cell(row_id,0).value)
            bc.handle = self._browsehandle(summary_object.logfile, sheet.cell(row_id,2).value)

            # Guids don't appear until 24-05-2009. Prior to that there was no guid column, so this call will fail initially.
            try:
                bc.guid = self._browseguid(summary_object.logfile, sheet.cell(row_id,3).value[:255], bc)
            except IndexError:
                bc.guid = self._browseguid(summary_object.logfile, '', bc)

            bc.save()
            count += 1

        print "Imported BROWSE data for " + str(summary_object.week_ending) + " with " + str(count) + " rows added."
        return None


    def _browsepath(self, logfile_object, path):
        "Get or Create the AppleBrowsePath information"
        bp = AppleBrowsePath()
        bp.path = path
        bp.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.browse_path_cache:
            if item.path == bp.path:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    bp = AppleBrowsePath.objects.get(id=item.id)
                    bp.logfile = logfile_object
                    bp.save()
                    # Update the cache
                    item.logfile = logfile_object
                return item

        # Nothing found, so save and update the cache
        bp.save()
        self.browse_path_cache.append(bp)

        return bp


    def _browsehandle(self, logfile_object, handle):
        "Get or Create the AppleBrowseHandle information"
        bh = AppleBrowseHandle()
        bh.handle = handle
        bh.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.browse_handle_cache:
            if item.handle == bh.handle:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    bh = AppleBrowseHandle.objects.get(id=item.id)
                    bh.logfile = logfile_object
                    bh.save()
                    # Update the cache
                    item.logfile = logfile_object
                return item

        # Nothing found, so save and update the cache
        bh.save()
        self.browse_handle_cache.append(bh)

        return bh


    def _browseguid(self, logfile_object, guid, browsecount_object):
        "Get or Create the AppleBrowseGUID information"
        bg = AppleBrowseGUID()
        bg.logfile = logfile_object

        # If guid provided, use. If not, find one. If none available, make one.
        if guid != '':
            bg.guid = guid
            # Attempt to locate in memory cache
            for item in self.browse_guid_cache:
                if item.guid == bg.guid:
                    # Check if the import path appears earlier than the stored path and update if needed
                    if item.logfile.last_updated > logfile_object.last_updated:
                        # Update the database
                        bg = AppleBrowseGUID.objects.get(id=item.id)
                        bg.logfile = logfile_object
                        bg.save()
                        # Update the cache
                        item.logfile = logfile_object
                    return item

            # Match on handle (trust Apple to make these unique), or then path
            try:
                # Any existing AppleWeeklyBrowseCount object should have a guid associated with it, thus, find one that has this handle, you've got it's guid
                bc = AppleWeeklyBrowseCount.objects.filter(handle=browsecount_object.handle.id)
                if guid == '':
                    return bc[0].guid

                else:
                    bg.save()
                    for item in bc:
                        item.guid = bg
                        item.save()
            except IndexError:
                # First time this handle has been seen, so look for a path match
                try:
                    bc = AppleWeeklyBrowseCount.objects.filter(path=browsecount_object.path.id)
                    if guid == '':
                        return bc[0].guid

                    else:
                        bg.save()
                        for item in bc:
                            item.guid = bg
                            item.save()
                except IndexError:
                    # No path match found, really must be new, so generate a GUID (UUID)
                    bg.guid = 'OPMS:' + str(uuid.uuid4())
                    bg.save()
                    self._errorlog("No AppleBrowseGUID found for " +str(browsecount_object.path)+ "(" + str(browsecount_object.handle) + "). " +\
                      "Created: " + str(bg.guid))

        # Nothing found, so save and update the cache
        self.browse_guid_cache.append(bg)
        # Note: Will likely need to do a manual clean out of defunct custom GUIDs as this process doesn't delete redundant records, just unlinks them
        return bg




    # ===================================================== PREVIEWS ===============================

    def _parse_previews(self, summary_object, sheet):
        "Parse a Previews sheet for counts."
        # Can assume data duplication has already been accounted for in the parse_summary() process, so if we're here, import...
        count = 0

        # Scan through all the rows, skipping the top row (headers).
        for row_id in range(1,sheet.nrows):
            # Setup the basic count record
            pc = AppleWeeklyPreviewCount()
            pc.summary = summary_object
            pc.count = int(sheet.cell(row_id,1).value)

            # Now link to path and handle
            pc.path = self._previewpath(summary_object.logfile, sheet.cell(row_id,0).value)
            pc.handle = self._previewhandle(summary_object.logfile, sheet.cell(row_id,2).value)

            # Guids don't appear until 24-05-2009. Prior to that there was no guid column, so this call will fail initially.
            try:
                pc.guid = self._previewguid(summary_object.logfile, sheet.cell(row_id,3).value[:255], pc)
            except IndexError:
                pc.guid = self._previewguid(summary_object.logfile, '', pc)

            pc.save()
            count += 1

        print "Imported PREVIEW data for " + str(summary_object.week_ending) + " with " + str(count) + " rows added."
        return None


    def _previewpath(self, logfile_object, path):
        "Get or Create the ApplePreviewPath information"
        pp = ApplePreviewPath()
        pp.path = path
        pp.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.preview_path_cache:
            if item.path == pp.path:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    pp = ApplePreviewPath.objects.get(id=item.id)
                    pp.logfile = logfile_object
                    pp.save()
                    # Update the cache
                    item.logfile = logfile_object
                return item

        # Nothing found, so save and update the cache
        pp.save()
        self.preview_path_cache.append(pp)

        return pp


    def _previewhandle(self, logfile_object, handle):
        "Get or Create the ApplePreviewHandle information"
        ph = ApplePreviewHandle()
        ph.handle = handle
        ph.logfile = logfile_object

        # Attempt to locate in memory cache
        for item in self.preview_handle_cache:
            if item.handle == ph.handle:
                # Check if the import path appears earlier than the stored path and update if needed
                if item.logfile.last_updated > logfile_object.last_updated:
                    # Update the database
                    ph = ApplePreviewHandle.objects.get(id=item.id)
                    ph.logfile = logfile_object
                    ph.save()
                    # Update the cache
                    item.logfile = logfile_object
                return item

        # Nothing found, so save and update the cache
        ph.save()
        self.preview_handle_cache.append(ph)

        return ph


    def _previewguid(self, logfile_object, guid, previewcount_object):
        "Get or Create the ApplePreviewGUID information"
        pg = ApplePreviewGUID()
        pg.logfile = logfile_object

        # If guid provided, use. If not, find one. If none available, make one.
        if guid != '':
            pg.guid = guid
            # Attempt to locate in memory cache
            for item in self.preview_guid_cache:
                if item.guid == pg.guid:
                    # Check if the import path appears earlier than the stored path and update if needed
                    if item.logfile.last_updated > logfile_object.last_updated:
                        # Update the database
                        pg = ApplePreviewGUID.objects.get(id=item.id)
                        pg.logfile = logfile_object
                        pg.save()
                        # Update the cache
                        item.logfile = logfile_object
                    return item

        # Match on handle (trust Apple to make these unique), or then path
        try:
            # Any existing AppleWeeklyPreviewCount object should have a guid associated with it, thus, find one that has this handle, you've got it's guid
            pc = AppleWeeklyPreviewCount.objects.filter(handle=previewcount_object.handle.id)
            if guid == '':
                return pc[0].guid

            else:
                pg.save()
                for item in pc:
                    item.guid = pg
                    item.save()
        except IndexError:
            # First time this handle has been seen, so look for a path match
            try:
                pc = AppleWeeklyPreviewCount.objects.filter(path=previewcount_object.path.id)
                if guid == '':
                    return pc[0].guid

                else:
                    pg.save()
                    for item in pc:
                        item.guid = pg
                        item.save()
            except IndexError:
                # No path match found, really must be new, so generate a GUID (UUID)
                pg.guid = 'OPMS:' + str(uuid.uuid4())
                pg.save()
                self._errorlog("No ApplePreviewGUID found for " +str(previewcount_object.path)+ "(" + str(previewcount_object.handle) + "). " +\
                  "Created: " + str(pg.guid))

        # Nothing found, so save and update the cache
        self.preview_guid_cache.append(pg)

        return pg




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