from django.contrib import admin
from stats.models import Summary, Track, Preview, Browse

"""
Iterates through models in an app and adds them to Admin UI
"""

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('week_ending', 'total_track_downloads')
    date_hierarchy = 'week_ending'

    fieldsets = [
        (None,                 {'fields':['total_track_downloads']}),
        ('User Actions',       {
	    'fields':['ua_browse','ua_download_preview','ua_download_preview_ios',
	    'ua_download_track','ua_download_tracks','ua_download_ios','ua_edit_files',
	    'ua_edit_page','ua_logout','ua_search_results_page','ua_subscription',
	    'ua_subscription_enclosure','ua_subscription_feed','ua_upload','ua_not_listed'],
	    'classes':['collapse']
	    }),
	('Client Software',    {
	    'fields':['cs_macintosh','cs_windows',
	    'cs_itunes_ipad_3_2',
	    'cs_itunes_iphone_3_0','cs_itunes_iphone_3_1','cs_itunes_iphone_4_0','cs_itunes_iphone_4_1',
	    'cs_itunes_ipod_3_0','cs_itunes_ipod_3_1','cs_itunes_ipod_4_0','cs_itunes_ipod_4_1',
	    'cs_itunes_10_0_macintosh','cs_itunes_10_0_windows',
	    'cs_itunes_8_0_macintosh','cs_itunes_8_0_windows','cs_itunes_8_1_macintosh','cs_itunes_8_1_windows','cs_itunes_8_2_macintosh','cs_itunes_8_2_windows',
	    'cs_itunes_9_0_macintosh','cs_itunes_9_0_windows','cs_itunes_9_1_macintosh','cs_itunes_9_1_windows','cs_itunes_9_2_macintosh','cs_itunes_9_2_windows',
	    'cs_not_listed'],
	    'classes':['collapse']
	    }),
    ]


class TrackAdmin(admin.ModelAdmin):
    list_display = ('week_ending', 'path', 'count')
    date_hierarchy = 'week_ending'

class PreviewAdmin(admin.ModelAdmin):
    list_display = ('week_ending', 'path', 'count')
    date_hierarchy = 'week_ending'

class BrowseAdmin(admin.ModelAdmin):
    list_display = ('week_ending', 'path', 'count')
    date_hierarchy = 'week_ending'

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Preview, PreviewAdmin)
admin.site.register(Browse, BrowseAdmin)

