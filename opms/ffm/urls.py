from django.conf.urls.defaults import *

urlpatterns = patterns('ffm.views',
    (r'^feeds/item/(?P<item_id>\d+)$', 'item_detail'),
    (r'^feeds/(?P<feed_id>\d+)$', 'feed_detail'),
    (r'^feeds/$', 'summary_feeds'),

    (r'^$', 'index'),
)