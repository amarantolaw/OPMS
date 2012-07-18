from django.contrib import admin
from django.contrib.auth.models import User
from feedback.models import Traffic, Comment, Event, Metric, Category
from django.forms.widgets import Select
import datetime

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

class SelectSwitcher(Select):
    def render(self, name, value, attrs=None, choices=()):
        from django.utils.html import escape
        self.choices = (u'choice1',u'choice2')
        if value is None: value = ''
        output = u"<select name=\"" + name + u"\">"
        for choice in self.choices:
                output += u"<option value=\"" + choice + u"\">" + choice + u"</option>"
        output += u"</select>"
        return output

class TrafficInline(admin.TabularInline):
    model = Traffic
    extra = 1

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

class EventInline(admin.StackedInline):
    model = Event
    extra = 1

class MetricAdmin(admin.ModelAdmin):
    inlines = [TrafficInline]
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = SelectSwitcher
        return super(MetricAdmin, self).formfield_for_dbfield(db_field, **kwargs)

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
admin.site.register(Traffic)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Event, EventAdmin)