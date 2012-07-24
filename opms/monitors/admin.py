from opms.monitors.models import *
from django.contrib import admin

class URLMonitorTaskAdmin(admin.ModelAdmin):
    list_display = ('comment', 'completed')
    list_filter = ['completed']

admin.site.register(URLMonitorTask, URLMonitorTaskAdmin)

class URLMonitorURLAdmin(admin.ModelAdmin):
    list_display = ('url', 'active')
    list_filter = ['active']

admin.site.register(URLMonitorURL, URLMonitorURLAdmin)

admin.site.register(ItuInstitution)
admin.site.register(ItuGenre)
admin.site.register(ItuComment)

class ItuCollectionChartScanInline(admin.StackedInline):
    model = ItuCollectionChartScan
    extra = 0

class ItuItemChartScanInline(admin.StackedInline):
    model = ItuItemChartScan
    extra = 0

class ItuCollectionHistoricalInline(admin.StackedInline):
    model = ItuCollectionHistorical
    extra = 0

class ItuCollectionAdmin(admin.ModelAdmin):
    inlines = [ItuCollectionChartScanInline,ItuCollectionHistoricalInline]

admin.site.register(ItuCollection, ItuCollectionAdmin)

class ItuItemHistoricalInline(admin.StackedInline):
    model = ItuItemHistorical
    extra = 0

class ItuItemAdmin(admin.ModelAdmin):
    inlines = [ItuItemChartScanInline,ItuItemHistoricalInline]

admin.site.register(ItuItem, ItuItemAdmin)

class ItuRatingInline(admin.TabularInline):
    model = ItuRating
    extra = 0

class ItuCommentInline(admin.StackedInline):
    model = ItuComment
    extra = 0

class ItuCollectionHistoricalAdmin(admin.ModelAdmin):
    inlines = [ItuRatingInline,ItuCommentInline]

admin.site.register(ItuCollectionHistorical, ItuCollectionHistoricalAdmin)

#class ItuItemHistoricalAdmin(admin.ModelAdmin):
#    inlines = [ItuItemChartScanInline]

admin.site.register(ItuItemHistorical)

class ItuScanLogAdmin(admin.ModelAdmin):
    inlines = [ItuCollectionChartScanInline,ItuItemChartScanInline]

admin.site.register(ItuScanLog, ItuScanLogAdmin)