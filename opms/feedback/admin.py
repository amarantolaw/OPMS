from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import User
from feedback.models import Traffic, Comment, Event, Metric, Category
from django import forms
from django.utils.encoding import force_unicode
import datetime
from stats.models import AppleWeeklySummary

APPLEWEEKLY_FIELDS = [(None,'N/A')]
for field in AppleWeeklySummary._meta._fields():
    APPLEWEEKLY_FIELDS.append((field.verbose_name,field.verbose_name))

def moderate(modeladmin, request, queryset):
    queryset.update(moderated=True)
    queryset.update(dt_moderated=datetime.datetime.now())
    queryset.update(moderator=request.user)
moderate.short_description = "Approve feedback"

def unmoderate(modeladmin, request, queryset):
    queryset.update(moderated=False)
    queryset.update(dt_moderated=None)
    queryset.update(moderator=None)
unmoderate.short_description = "Reject feedback"

class TrafficInline(admin.TabularInline):
    model = Traffic
    extra = 1

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

class EventInline(admin.StackedInline):
    model = Event
    extra = 1

class MetricForm(forms.ModelForm):
    class Meta:
        model = Metric
        widgets = {
            'appleweeklyfield': forms.Select(choices=APPLEWEEKLY_FIELDS),
            }

class MetricAdmin(admin.ModelAdmin):
    inlines = [TrafficInline]
    form = MetricForm

class CategoryAdmin(admin.ModelAdmin):
    inlines = [CommentInline, EventInline]

class CommentAdmin(admin.ModelAdmin):
    list_display = ['detail','moderated','source','date','time','category','user_email','dt_uploaded']
    ordering = ['dt_uploaded']
    actions = [moderate,unmoderate]

class EventAdmin(admin.ModelAdmin):
    list_display = ['title','moderated','detail','date','category','user_email','dt_uploaded']
    ordering = ['dt_uploaded']
    actions = [moderate,unmoderate]

admin.site.register(Metric, MetricAdmin)
admin.site.register(Category, CategoryAdmin)
#admin.site.register(Traffic)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Event, EventAdmin)