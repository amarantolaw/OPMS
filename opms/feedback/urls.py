from django.conf.urls import patterns, include, url
from opms.feedback.views import *

urlpatterns = patterns('feedback.views',
    url(r'^$', 'index', name="index"),
    url(r'^comment/$', 'comment_add', name="comment-add"),
    url(r'^comment/(?P<comment_id>\d+)/$', 'comment_detail', name="comment-detail"),
    url(r'^event/$', 'event_add', name="event-add"),
    url(r'^event/(?P<event_id>\d+)/$', 'event_detail', name="event-detail"),
    url(r'^email/$', 'email', name="email"),
)
