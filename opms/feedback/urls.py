from django.conf.urls import patterns, include, url
from opms.feedback.views import *

urlpatterns = patterns('feedback.views',
    url(r'^$', 'index', name="index"),
    url(r'^comment/$', 'comment_add', name="comment-add"),
    url(r'^event/$', 'event_add', name="event-add"),
#    url(r'^email/$', 'email', name="email"),
)
