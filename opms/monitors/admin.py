from opms.stats.models import *
from django.contrib import admin

class URLMonitorTargetAdmin(admin.ModelAdmin):
    list_display = ('url', 'active')
    list_filter = ['active']
    
admin.site.register(URLMonitorTarget, URLMonitorTargetAdmin)


class URLMonitorTaskAdmin(admin.ModelAdmin):
    list_display = ('comment', 'completed')
    list_filter = ['completed']

admin.site.register(URLMonitorTask, URLMonitorTaskAdmin)

