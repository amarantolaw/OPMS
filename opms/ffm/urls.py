from django.conf.urls.defaults import *

urlpatterns = patterns('ffm.views',
    (r'^feeds/item/(?P<item_id>.*)$', 'item_detail'),
    (r'^feeds/(?P<feed_id>.*)$', 'feed_detail'),
    (r'^feeds/$', 'summary_feeds'),

    (r'^$', 'index'),
)