from django.conf.urls import patterns, include, url
from opms.feedback.views import *

urlpatterns = patterns('feedback.views',
    url(r'^$', 'index'),
    url(r'^comment/$', 'comment_add'),
    url(r'^comment/(?P<comment_id>\d+)/$', 'comment_detail', name="comment-detail"),
    url(r'^comment/(?P<comment_id>\d+)/edit/$', 'comment_edit', name="comment-edit"),
    url(r'^comment/(?P<comment_id>\d+)/delete/$', 'comment_delete', name="comment-delete"),
    url(r'^event/$', 'event_add'),
    url(r'^event/(?P<event_id>\d+)/$', 'event_detail', name="event-detail"),
    url(r'^event/(?P<event_id>\d+)/edit/$', 'event_edit', name="event-edit"),
    url(r'^event/(?P<event_id>\d+)/delete/$', 'event_delete', name="event-delete"),
)
