from django.conf.urls import patterns, include, url
from opms.feedback.views import *

urlpatterns = patterns('feedback.views',
    url(r'^$', 'index', name="index"),
    url(r'^comment/$', 'comment_add', name="comment-add"),
    url(r'^event/$', 'event_add', name="event-add"),
    url(r'^tags/$', 'tags', name="tags"),
    url(r'^tags/(?P<tag_id>\d+)/$', 'tag_view', name="tag-view"),
    url(r'^tags/(?P<tag_id>\d+)/delete/$', 'tag_delete', name="tag-delete"),
    url(r'^tags/create/$', 'tag_create', name="tag-create"),
    url(r'^tags/(?P<tag_id>\d+)/tag-comment/(?P<comment_id>\d+)/$', 'tag_comment', name="tag-comment"),
    url(r'^tags/(?P<tag_id>\d+)/untag-comment/(?P<comment_id>\d+)/$', 'untag_comment', name="untag-comment"),
    url(r'^tags/(?P<tag_id>\d+)/tag-event/(?P<event_id>\d+)/$', 'tag_event', name="tag-event"),
    url(r'^tags/(?P<tag_id>\d+)/untag-event/(?P<event_id>\d+)/$', 'untag_event', name="untag-event"),
    url(r'^tags/(?P<tag_id>\d+)/tag-metric/(?P<metric_id>\d+)/$', 'tag_metric', name="tag-metric"),
    url(r'^tags/(?P<tag_id>\d+)/untag-metric/(?P<metric_id>\d+)/$', 'untag_metric', name="untag-metric"),
    url(r'^taglist/comment-modal/(?P<comment_id>\d+)/$', 'comment_modal', name="comment-modal"),
    url(r'^taglist/event-modal/(?P<event_id>\d+)/$', 'event_modal', name="event-modal"),
    #    url(r'^email/$', 'email', name="email"),
)
