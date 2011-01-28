from django.db import models

# Create your models here.

# Summary record based on a column of data from the Summary tab
class Summary(models.Model):
    # Date from the column - typically from yyyy-mm-dd format
    week_ending = models.DateField("week ending")
    # User Actions section
    ua_browse = models.IntegerField("browse")
    ua_download_preview  = models.IntegerField("download preview")
    ua_download_preview_ios = models.IntegerField("download preview iOS", blank=True, null=True)
    ua_download_track = models.IntegerField("download track")
    ua_download_tracks = models.IntegerField("download tracks")
    ua_download_ios = models.IntegerField("download iOS", blank=True, null=True)
    ua_edit_files = models.IntegerField("edit files")
    ua_edit_page = models.IntegerField("edit page")
    ua_logout = models.IntegerField("logout")
    ua_search_results_page = models.IntegerField("search results page")
    ua_subscription = models.IntegerField("subscription")
    ua_subscription_enclosure = models.IntegerField("subscription enclosure")
    ua_subscription_feed = models.IntegerField("subscription feed")
    ua_upload = models.IntegerField("upload")
    ua_not_listed = models.IntegerField("not listed")
    # The total as calculated by Apple
    total_track_downloads = models.IntegerField("total track downloads")
    # Client Software section
    # note: the number of options here changes over time in the data, hence the blank=True option to allow for gaps in data import.
    cs_macintosh = models.IntegerField("?/?/Macintosh", blank=True, null=True)
    cs_windows = models.IntegerField("?/?/Windows", blank=True, null=True)
    cs_itunes_ipad_3_2 = models.IntegerField("iTunes-iPad/3.2/?", blank=True, null=True)
    cs_itunes_iphone_3_0 = models.IntegerField("iTunes-iPhone/3.0/?", blank=True, null=True)
    cs_itunes_iphone_3_1 = models.IntegerField("iTunes-iPhone/3.1/?", blank=True, null=True)
    cs_itunes_iphone_4_0 = models.IntegerField("iTunes-iPhone/4.0/?", blank=True, null=True)
    cs_itunes_iphone_4_1 = models.IntegerField("iTunes-iPhone/4.1/?", blank=True, null=True)
    cs_itunes_ipod_3_0 = models.IntegerField("iTunes-iPod/3.0/?", blank=True, null=True)
    cs_itunes_ipod_3_1 = models.IntegerField("iTunes-iPod/3.1/?", blank=True, null=True)
    cs_itunes_ipod_4_0 = models.IntegerField("iTunes-iPod/4.0/?", blank=True, null=True)
    cs_itunes_ipod_4_1 = models.IntegerField("iTunes-iPod/4.1/?", blank=True, null=True)
    cs_itunes_10_0_macintosh = models.IntegerField("iTunes/10.0/Macintosh", blank=True, null=True)
    cs_itunes_10_0_windows = models.IntegerField("iTunes/10.0/Windows", blank=True, null=True)
    cs_itunes_8_0_macintosh = models.IntegerField("iTunes/8.0/Macintosh", blank=True, null=True)
    cs_itunes_8_0_windows = models.IntegerField("iTunes/8.0/Windows", blank=True, null=True)
    cs_itunes_8_1_macintosh = models.IntegerField("iTunes/8.1/Macintosh", blank=True, null=True)
    cs_itunes_8_1_windows = models.IntegerField("iTunes/8.1/Windows", blank=True, null=True)
    cs_itunes_8_2_macintosh = models.IntegerField("iTunes/8.2/Macintosh", blank=True, null=True)
    cs_itunes_8_2_windows = models.IntegerField("iTunes/8.2/Windows", blank=True, null=True)
    cs_itunes_9_0_macintosh = models.IntegerField("iTunes/9.0/Macintosh", blank=True, null=True)
    cs_itunes_9_0_windows = models.IntegerField("iTunes/9.0/Windows", blank=True, null=True)
    cs_itunes_9_1_macintosh = models.IntegerField("iTunes/9.1/Macintosh", blank=True, null=True)
    cs_itunes_9_1_windows = models.IntegerField("iTunes/9.1/Windows", blank=True, null=True)
    cs_itunes_9_2_macintosh = models.IntegerField("iTunes/9.2/Macintosh", blank=True, null=True)
    cs_itunes_9_2_windows = models.IntegerField("iTunes/9.2/Windows", blank=True, null=True)
    cs_not_listed = models.IntegerField("not listed", blank=True, null=True)
    

# Track record based on Aug 2010 Excel "yyyy-mm-dd Tracks" datastructure. Each record is a line in the sheet
class TrackManager(models.Manager):
    def grouped_by_feed(self, sort_by):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, sum(count) AS count, week_ending, path, handle, guid 
            FROM stats_track
            GROUP BY substring(guid,52)
            ORDER BY %s''' % sort_by)

        result_list = []
        for row in cursor.fetchall():
            t = self.model(id=row[0], count=row[1], week_ending=row[2], path=row[3], handle=row[4], guid=row[5])
            if len(row[5]) > 50:
                t.psudeo_feed = row[5][51:]
            else:
                t.psudeo_feed = row[5]
            result_list.append(t)

        return result_list

    def items_by_feed(self, partial_guid):
        from django.db import connection, transaction
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, sum(count) AS count, week_ending, path, handle, guid
            FROM stats_track
            WHERE substring(guid,52) = %s
            GROUP BY guid''', [partial_guid])

        result_list = []
        for row in cursor.fetchall():
            t = self.model(id=row[0], count=row[1], week_ending=row[2], path=row[3], handle=row[4], guid=row[5])
            if len(row[5]) > 50:
                t.psudeo_feed = row[5][51:]
            else:
                t.psudeo_feed = row[5]
            result_list.append(t)

        return result_list
        


class Track(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)

    objects = TrackManager()



# Browse record based on Aug 2010 Excel "yyyy-mm-dd Browse" datastructure. Each record is a line in the sheet
class Browse(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)


# Preview record based on Aug 2010 Excel "yyyy-mm-dd Previews" datastructure. Each record is a line in the sheet
class Preview(models.Model):
    week_ending = models.DateField("week ending")
    path = models.TextField("path")
    count = models.IntegerField("count")
    handle = models.BigIntegerField("handle")
    guid = models.CharField("GUID", max_length=255,blank=True, null=True)



