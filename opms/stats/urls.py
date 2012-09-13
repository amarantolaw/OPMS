from django.conf.urls import patterns, url
from stats.views import *

urlpatterns = patterns('stats.views',
    # Graphs generated by Stats -- REDUNDANT, replaced by HighChart.js
#    url(r'^apple/graph/summary-total.png', graph_apple_summary_totals),
#    url(r'^apple/graph/summary-feeds.png', graph_apple_summary_feeds),
#    url(r'^apple/graph/feed_by_week/(?P<feed>.+).png', graph_apple_feed_weeks),
    # Pages in Stats
    url(r'^apple/feeds/partial-guid/(?P<partial_guid>.+)', feed_detail, name="apple-feed-byguid"),
    url(r'^apple/feeds/$', summary_feeds),
    url(r'^apple/guid/(?P<trackguid_id>\d+)', guid_detail, name="apple-guid-detail"),

    url(r'^apple/raw/animation$', apple_raw_animation, name="apple-raw-animation"),
    url(r'^apple/raw/$', apple_raw_summary, name="apple-raw-summary"),

    url(r'^apple/summary/$', summary_index),
    url(r'^apple/$', apple_index),

    #(r'report/authors/$', 'summary_authors'), # Consider this dead for now

    # Default page (aka, Stats home)
    url(r'^$', index),
)