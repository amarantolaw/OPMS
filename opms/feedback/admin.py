from django.contrib import admin
from feedback.models import Traffic, Comment, Event, Metric, Category

class TrafficInline(admin.TabularInline):
    model = Traffic
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class EventInline(admin.TabularInline):
    model = Event
    extra = 1

class MetricAdmin(admin.ModelAdmin):
    inlines = [TrafficInline]

class CategoryAdmin(admin.ModelAdmin):
    inlines = [CommentInline, EventInline]

admin.site.register(Metric, MetricAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Traffic)
admin.site.register(Comment)
admin.site.register(Event)