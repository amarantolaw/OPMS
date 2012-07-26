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

admin.site.register(ItuComment)


class ItuCollectionChartScanInline(admin.TabularInline):
    model = ItuCollectionChartScan
    extra = 0
    fields = ('date','position')

class ItuItemChartScanInline(admin.TabularInline):
    model = ItuItemChartScan
    extra = 0
    fields = ('date','position')

class ItuCollectionHistoricalInline(admin.StackedInline):
    model = ItuCollectionHistorical
    extra = 0
    fields = ('name','itu_id','img170','url','language','last_modified','contains_movies','version','scanlog','genre','institution')

class ItuCollectionAdmin(admin.ModelAdmin):
    inlines = [ItuCollectionChartScanInline,ItuCollectionHistoricalInline]

admin.site.register(ItuCollection, ItuCollectionAdmin)

class ItuItemHistoricalInline(admin.StackedInline):
    model = ItuItemHistorical
    extra = 0
    fields = ('name','itu_id','url','artist_name','description','duration','explicit','feed_url','file_extension','kind','long_description','playlist_id','playlist_name','popularity','preview_length','preview_url','rank','release_date','version','institution','genre','scanlog')

class ItuItemAdmin(admin.ModelAdmin):
    inlines = [ItuItemChartScanInline,ItuItemHistoricalInline]

admin.site.register(ItuItem, ItuItemAdmin)

class ItuRatingInline(admin.TabularInline):
    model = ItuRating
    extra = 0
    fields = ('stars','count')

class ItuCommentInline(admin.StackedInline):
    model = ItuComment
    extra = 0
    fields = ('date','detail','stars','source')

class ItuCollectionHistoricalAdmin(admin.ModelAdmin):
    inlines = [ItuRatingInline,ItuCommentInline,ItuCollectionChartScanInline]

admin.site.register(ItuCollectionHistorical, ItuCollectionHistoricalAdmin)

class ItuItemHistoricalAdmin(admin.ModelAdmin):
    inlines = [ItuItemChartScanInline]
    fields = ('name','itu_id','url','artist_name','description','duration','explicit','feed_url','file_extension','kind','long_description','playlist_id','playlist_name','popularity','preview_length','preview_url','rank','release_date','version','institution','genre','scanlog')

admin.site.register(ItuItemHistorical, ItuItemHistoricalAdmin)

class ItuScanLogAdmin(admin.ModelAdmin):
    inlines = [ItuCollectionChartScanInline,ItuItemChartScanInline]

admin.site.register(ItuScanLog, ItuScanLogAdmin)

class ItuGenreAdmin(admin.ModelAdmin):
    inlines = [ItuCollectionHistoricalInline]

admin.site.register(ItuGenre, ItuGenreAdmin)

admin.site.register(ItuInstitution)