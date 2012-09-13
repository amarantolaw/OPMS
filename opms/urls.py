from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.conf.urls.defaults import *
from core.views import *
from views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Stats module urls
    (r'^analytics/', include('stats.urls')),

    # Monitors module urls
    (r'^monitoring/', include('monitors.urls')),

    # Feedback module urls
    (r'^monitoring/feedback/', include('feedback.urls')),

    # FFM module urls
    #(r'^ffm/', include('ffm.urls')),
    
    # Root homepage
    (r'^$', home),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
)
