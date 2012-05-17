from django.db import models
from apple_summary import *

class AppleWeeklySummaryManager(models.Manager):
    def get_query_set(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT week_beginning AS week_beginning,
                   sum(browse) AS browse,
                   sum(download_preview) AS download_preview,
                   sum(download_preview_ios) AS download_preview_ios,
                   sum(download_track) AS download_track,
                   sum(download_tracks) AS download_tracks,
                   sum(download_ios) AS download_ios,
                   sum(subscription) AS subscription,
                   sum(subscription_enclosure) AS subscription_enclosure,
                   sum(subscription_feed) AS subscription_feed,
                   sum(total_track_downloads) AS total_track_downloads
            FROM stats_appleweeklysummary
            GROUP BY week_beginning
            ORDER BY week_beginning ASC
        """)
        result_list = []
        previous_row = []
        cumulative_total = 0
        week_number = -5  # Want to be able to calculate this from a preset start date...
        for row in cursor.fetchall():
            r = self.model(week_beginning=row[0], browse=row[1], download_preview=row[2],
                download_preview_ios=row[3], download_track=row[4], download_tracks=row[5],
                download_ios=row[6], subscription=row[7], subscription_enclosure=row[8],
                subscription_feed=row[9], total_track_downloads=row[10])

            r.week_number = week_number
            try:
                r.total_track_downloads_change = int(row[10])-int(previous_row[10])
            except IndexError:
                r.total_track_downloads_change = 0
                # Add a cumulative count
            cumulative_total += r.total_track_downloads
            r.cumulative_total = cumulative_total

            result_list.append(r)

            week_number += 1
            previous_row = row
        return result_list



class AppleTrackManager(models.Manager):

    def psuedo_feeds(self):
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute('''
            SELECT sum(tc.count) AS count,
                   substring(tg.guid,52) AS psuedo_feed,
                   min(s.week_beginning) AS first_result,
                   max(s.week_beginning) AS last_result,
                   max(ic.item_count) AS item_count
            FROM stats_appleweeklytrackcount AS tc,
                 stats_appletrackguid AS tg,
                 stats_appleweeklysummary AS s,
                (SELECT substring(tg.guid,52) AS psuedo_feed, count(tg.guid) AS item_count
                 FROM stats_appletrackguid AS tg
                 WHERE substring(tg.guid,52) <> ''
                 GROUP BY substring(tg.guid,52)) AS ic
            WHERE tc.guid_id = tg.id
              AND tc.summary_id = s.id
              AND ic.psuedo_feed = substring(tg.guid,52)
              AND substring(tg.guid,52) <> ''
            GROUP BY substring(tg.guid,52)
            ORDER BY 1 DESC
        ''')

        result_list = []
        for row in cursor.fetchall():
            avg = int(row[0])/int(row[4])
            t = {'count':row[0], 'feed':row[1], 'min_date':row[2],
                 'max_date':row[3], 'item_count':row[4], 'item_avg':avg}
            result_list.append(t)
        return result_list


    def feed_weeks(self, partial_guid = ''):
        from django.db import connection
        cursor = connection.cursor()

        # get the weeks that data exists for a given feed
        cursor.execute('''
            SELECT DISTINCT s.week_beginning
              FROM stats_appleweeklytrackcount AS tc,
                   stats_appletrackguid AS tg,
                   stats_appleweeklysummary AS s
            WHERE tc.guid_id = tg.id
              AND tc.summary_id = s.id
              AND substring(tg.guid,52) = %s
            ORDER BY 1 ASC;
            ''', [partial_guid] )

        result_list = []
        for row in cursor.fetchall():
            result_list.append(str(row[0]))
        return result_list


    def feed_items(self, partial_guid = ''):
        from django.db import connection
        cursor = connection.cursor()

        # get the items that data exists for a given feed - if a guid exists, it is because we have data for it
        cursor.execute('''
            SELECT DISTINCT tg.guid
              FROM stats_appletrackguid AS tg
            WHERE substring(tg.guid,52) = %s
            ORDER BY 1 ASC;
            ''', [partial_guid] )

        result_list = []
        for row in cursor.fetchall():
            result_list.append(str(row[0]))
        return result_list


    def feed_counts(self, partial_guid = '', order_by=0):
        from django.db import connection
        cursor = connection.cursor()

        # get the count data for a given feed, such that it can be arranged against the above queries
        sql = '''
            SELECT s.week_beginning, max(tp.path), tg.guid, sum(tc.count)
              FROM stats_appleweeklytrackcount AS tc,
                   stats_appletrackpath AS tp,
                   stats_appletrackguid AS tg,
                   stats_appleweeklysummary AS s
            WHERE tc.path_id = tp.id
              AND tc.guid_id = tg.id
              AND tc.summary_id = s.id
              AND substring(tg.guid,52) = %s
            GROUP BY s.week_beginning, tg.guid
            '''
        if order_by > 0:
            sql += "ORDER BY 3 ASC, 1 ASC;"
        else:
            sql += "ORDER BY 1 ASC, 3 ASC;"
        cursor.execute(sql, [partial_guid])

        result_list = []
        for row in cursor.fetchall():
            t = {'week_beginning':str(date.strftime(row[0],"%Y-%m-%d")), 'path':row[1], 'guid':row[2], 'count':row[3]}
            result_list.append(t)

        return result_list


    def feed_week_counts(self, partial_guid = ''):
        from django.db import connection
        cursor = connection.cursor()

        # get the count data per week for a given feed
        sql = '''
            SELECT ss.week, sum(ss.count), max(ss.guid), count(ss.id)
            FROM (
                SELECT s.week_beginning || tg.guid AS id,
                       sum(tc.count) AS count,
                       max(s.week_beginning) AS week,
                       max(tg.guid) AS guid
                FROM stats_appleweeklytrackcount AS tc,
                     stats_appletrackguid AS tg,
                     stats_appleweeklysummary AS s
                WHERE tc.summary_id = s.id
                  AND tc.guid_id = tg.id
                  AND substring(tg.guid,52) = %s
                GROUP BY 1
                ) AS ss
            GROUP BY ss.week
            ORDER BY 1 ASC;
            '''
        cursor.execute(sql, [partial_guid])

        result_list = []
        for row in cursor.fetchall():
            t = {'week_beginning':str(date.strftime(row[0],"%Y-%m-%d")), 'count':row[1], 'guid':row[2], 'item_count':row[3]}
            result_list.append(t)

        return result_list

