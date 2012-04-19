from opms.monitors.models import URLMonitorTarget, URLMonitorTask
from django.contrib import admin


class URLMonitorTaskAdmin(admin.ModelAdmin):
    list_display = ('comment', 'completed')
    list_filter = ('completed')

admin.site.register(URLMonitorTask, URLMonitorTaskAdmin)



class URLMonitorTargetAdmin(admin.ModelAdmin):
    list_display = ('url', 'active')
    list_filter = ('active')

admin.site.register(URLMonitorTarget, URLMonitorTargetAdmin)