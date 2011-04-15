from django.conf.urls.defaults import *

urlpatterns = patterns('stats.views',
    # These URLS will all change!
    #(r'^report/pr/item/(?P<guid>.+)', 'pr_report3'),
    #(r'^report/pr/partial-guid/(?P<partial_guid>.+)', 'pr_report2'),
    #(r'^report/pr/(?P<sort_by>.*)', 'pr_report1'),
    (r'^report/summary/$', 'summary_index'),
    (r'^$', 'index'),
)
