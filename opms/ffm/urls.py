from django.conf.urls.defaults import *

urlpatterns = patterns('ffm.views',
    (r'^items/(?P<item_id>\d+)$', 'item_detail'),
    (r'^items/$', 'summary_items'),

    (r'^feeds/(?P<feed_id>\d+)$', 'feed_detail'),
    (r'^feeds/$', 'summary_feeds'),

    (r'^people/(?P<person_id>\d+)$', 'person_detail'),
    (r'^people/$', 'summary_people'),

    (r'^$', 'index'),
)