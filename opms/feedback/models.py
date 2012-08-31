from django.db import models
from django.contrib.auth.models import User
from monitors.models import ItuComment, ItuItem, ItuCollection, ItuInstitution
import datetime

class Tag(models.Model):
    """A short name which metrics, comments and events may be assigned, defining a page which may be used as a custom-built report."""
    name = models.CharField(max_length=10, unique=True, help_text="Unique identifier, for display in tables.")
    title = models.CharField(max_length=200, help_text="Title of reports about this tag.")
    color = models.CharField(max_length=7, help_text="Tag colour")

class Metric(models.Model):
    """A measure of web traffic"""
    METRIC_SOURCES = (
        ('feedback', 'Stored in feedback app'),
        ('appleweekly', 'Apple weekly summary data')
    )
    description = models.CharField(max_length=200, unique=True, help_text="A description of the metric eg. 'Complete downloads'")
    linecolor = models.CharField(max_length=7, help_text="The colour of the line when this metric is plotted on a chart")
    fillcolor = models.CharField(max_length=7, help_text="The colour of the gradient under the said line")
    mouseover = models.BooleanField(help_text="Whether rolling the mouse over a point will display the precise position of the point as an overlay")
    defaultvisibility = models.BooleanField(help_text="Whether the metric is visible by default")
    source = models.CharField(max_length=20, choices=METRIC_SOURCES, default='feedback', help_text="Magic tag to determine whether to try builtin stats app database lookup routines.")
    itucollection = models.ForeignKey(ItuCollection, null=True, blank=True, default=None, help_text="If this is a chart of collection chart progress, which collection?")
    ituitem = models.ForeignKey(ItuItem, null=True, blank=True, default=None, help_text="If this is a chart of item chart progress, which item?")
    ituinstitution = models.ForeignKey(ItuInstitution, null=True, blank=True, default=None, help_text="If this is a chart of institutional chart progress, which institution?")

    appleweeklyfield = models.CharField(max_length=200, default=None, blank=True, null=True, help_text="Which metric in the apple weekly summary data table should this be a plot of (if source='appleweekly')?")

    tags = models.ManyToManyField(Tag,null=True,blank=True, help_text="Tags attached to this metric.")

    def mouseover_timeplot(self):
        """A nice javascript true/false instead of True/False."""
        return str(self.mouseover).lower()
    def __unicode__(self):
        return self.description

class Category(models.Model):
    """A group of Comments and/or Events which can be toggled together and displayed identically"""
    description = models.CharField(max_length=200, unique=True, help_text="A description of the category eg. 'Comments made by e-mail' or 'iTunes store upgrades'")
    color = models.CharField(max_length=7, help_text="The colour of the line on the chart representing events and/or comments in this category")
    defaultvisibility = models.BooleanField(help_text="Whether the metric is visible by default")
    class Meta:
        verbose_name_plural = "categories"
    def __unicode__(self):
        return self.description

class Traffic(models.Model):
    """A day's worth of traffic to a website according to some metric."""
    date = models.DateField(help_text="The day on which this traffic occurred")
    def date_timeplot(self):
        """Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates."""
        return str(self.date)
    count = models.PositiveIntegerField(help_text="The number of occurrences of this metric of traffic on that day")
    metric = models.ForeignKey(Metric, help_text="The ID of the metric used to measure traffic")
    class Meta:
        verbose_name_plural = "traffic"
    def __unicode__(self):
        return '\"' + self.metric.description + '\" = ' + str(self.count) + ' on ' + str(self.date)

class Comment(models.Model):
    """A comment made about the website on a certain day"""
    date = models.DateField(null=True, blank=True, help_text="The day when the comment was made")
    def date_timeplot(self):
        """Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates."""
        return str(self.date)
    def datetime_timeplotxml(self):
        """Datetime in a format suitable for generating fake XML files to feed timeplot."""
        if self.time:
            return self.date.strftime("%b %d %Y") + " " + self.time.strftime("%H:%M:%S") + " GMT"
        else:
            return self.date.strftime("%b %d %Y") + " " + "00:00:00" + " GMT"
    time = models.TimeField(null=True, blank=True, help_text="The time at which the comment was made")
    source = models.CharField(max_length=200, help_text="The source of the comment (DELIBERATELY VAGUE FOR THE MOMENT!)")
    detail = models.TextField(unique=True, help_text="The text of the comment")
    category = models.ForeignKey(Category, help_text="Categories may include Events as well as Comments")
    moderated = models.BooleanField("Approved",default=False, help_text="Has this comment been moderated yet?")
    user_email = models.EmailField(help_text="The e-mail address of the person uploading the comment - unlikely to be the e-mail address of the person who made the comment in the first place.")
    dt_uploaded = models.DateTimeField("Datetime uploaded",auto_now_add=True, help_text="The datetime at which the comment was originally uploaded.")
    dt_moderated = models.DateTimeField("Datetime approved",blank=True,null=True, help_text="The datetime at which the comment was moderated. Should be blank if the comment has yet to be moderated.")
    moderator = models.ForeignKey(User,blank=True,null=True, help_text="The django admin user who moderated the comment.")
    tags = models.ManyToManyField(Tag,null=True,blank=True, help_text="Tags this comment is tagged with.")
    itu_source = models.ForeignKey(ItuComment,null=True,blank=True,default=None, help_text="If this comment is from iTunes U, this is the comment in the iTunes U monitoring database representing this comment.")
    def __unicode__(self):
        return self.detail

class Event(models.Model):
    """An event which occurred on a certain day"""
    date = models.DateField(help_text="The date on which the event occurred")
    def date_timeplot(self):
        """Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates."""
        return str(self.date)
    def datetime_timeplotxml(self):
        """Datetime in a format suitable for generating fake XML files to feed timeplot."""
        return self.date.strftime("%b %d %Y") + " " + "00:00:00" + " GMT"
    title = models.CharField(max_length=50,unique_for_date="date", help_text="The title of the event. Needs to be short enough to look pretty.")
    detail = models.TextField(help_text="Potentially useful details about the event")
    category = models.ForeignKey(Category, help_text="Categories may include Comments as well as Events")
    moderated = models.BooleanField("Approved",default=False, help_text="Has this event been moderated yet?")
    user_email = models.EmailField(help_text="The e-mail address of the person uploading the event.")
    dt_uploaded = models.DateTimeField("Datetime uploaded",auto_now_add=True, help_text="The datetime at which the event was originally uploaded.")
    dt_moderated = models.DateTimeField("Datetime approved",blank=True,null=True, help_text="The datetime at which the event was moderated. Should be blank if the event has yet to be moderated.")
    moderator = models.ForeignKey(User,blank=True,null=True, help_text="The django admin user who moderated the event.")
    tags = models.ManyToManyField(Tag,null=True,blank=True, help_text="Tags this event is tagged with.")
    def __unicode__(self):
        return self.title