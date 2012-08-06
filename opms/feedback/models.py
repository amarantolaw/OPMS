from django.db import models
from django.contrib.auth.models import User
import datetime

class Metric(models.Model):
    "A measure of web traffic"
    METRIC_SOURCES = (
        ('feedback', 'Stored in feedback app'),
        ('appleweekly', 'Apple weekly summary data')
    )
    description = models.CharField(max_length=200, unique=True)     #A description of the metric eg. 'Complete downloads'
    linecolor = models.CharField(max_length=7)                      #The colour of the line when this metric is plotted on a chart
    fillcolor = models.CharField(max_length=7)                      #The colour of the gradient under the said line
    mouseover = models.BooleanField()                               #Whether rolling the mouse over a point will display the precise position of the point as an overlay
    defaultvisibility = models.BooleanField()                       #Whether the metric is visible by default
    source = models.CharField(max_length=20, choices=METRIC_SOURCES, default='feedback')

    appleweeklyfield = models.CharField(max_length=200, default=None, blank=True, null=True)

    def mouseover_timeplot(self):
        return str(self.mouseover).lower()
    def __unicode__(self):
        return self.description

class Category(models.Model):
    "A group of Comments and/or Events which can be toggled together and displayed identically"
    description = models.CharField(max_length=200, unique=True)     #A description of the category eg. 'Comments made by e-mail' or 'iTunes store upgrades'
    color = models.CharField(max_length=7)                          #The colour of the line on the chart representing events and/or comments in this category
    defaultvisibility = models.BooleanField()                       #Whether the metric is visible by default
    class Meta:
        verbose_name_plural = "categories"
    def __unicode__(self):
        return self.description

class Traffic(models.Model):
    "A day's worth of traffic to a website according to some metric."
    date = models.DateField()                                       #The day on which this traffic occurred
    def date_timeplot(self):                                        #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    count = models.PositiveIntegerField()                           #The number of occurrences of this metric of traffic on that day
    metric = models.ForeignKey(Metric)                              #The ID of the metric used to measure traffic
    class Meta:
        verbose_name_plural = "traffic"
    def __unicode__(self):
        return '\"' + self.metric.description + '\" = ' + str(self.count) + ' on ' + str(self.date)

class Comment(models.Model):
    "A comment made about the website on a certain day"
    date = models.DateField(null=True, blank=True)                                      #The day when the comment was made
    def date_timeplot(self):                                                            #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    def datetime_timeplotxml(self):
        if self.time:
            return self.date.strftime("%b %d %Y") + " " + self.time.strftime("%H:%M:%S") + " GMT"
        else:
            return self.date.strftime("%b %d %Y") + " " + "00:00:00" + " GMT"
    time = models.TimeField(null=True, blank=True)                                      #The time at which the comment was made
    source = models.CharField(max_length=200)                                           #The source of the comment (DELIBERATELY VAGUE FOR THE MOMENT!)
    detail = models.TextField(unique=True)                                              #The text of the comment
    category = models.ForeignKey(Category)                                              #Categories may include Events as well as Comments
    moderated = models.BooleanField("Approved",default=False)                           #Has this comment been moderated yet?
    user_email = models.EmailField()                                                    #The e-mail address of the person uploading the comment - unlikely to be the e-mail address of the person who made the comment in the first place.
    dt_uploaded = models.DateTimeField("Datetime uploaded",auto_now_add=True)           #The datetime at which the comment was originally uploaded.
    dt_moderated = models.DateTimeField("Datetime approved",blank=True,null=True)       #The datetime at which the comment was moderated. Should be blank if the comment has yet to be moderated.
    moderator = models.ForeignKey(User,blank=True,null=True)                            #The django admin user who moderated the comment.
    def __unicode__(self):
        return self.detail

class Event(models.Model):
    "An event which occurred on a certain day"
    date = models.DateField()                                                           #The date on which the event occurred
    def date_timeplot(self):                                                            #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    def datetime_timeplotxml(self):
        return self.date.strftime("%b %d %Y") + " " + "00:00:00" + " GMT"
    title = models.CharField(max_length=50,unique_for_date="date")                      #The title of the event. Needs to be short enough to look pretty.
    detail = models.TextField()                                                         #Potentially useful details about the event
    category = models.ForeignKey(Category)                                              #Categories may include Comments as well as Events
    moderated = models.BooleanField("Approved",default=False)                           #Has this event been moderated yet?
    user_email = models.EmailField()                                                    #The e-mail address of the person uploading the event.
    dt_uploaded = models.DateTimeField("Datetime uploaded",auto_now_add=True)           #The datetime at which the event was originally uploaded.
    dt_moderated = models.DateTimeField("Datetime approved",blank=True,null=True)       #The datetime at which the event was moderated. Should be blank if the event has yet to be moderated.
    moderator = models.ForeignKey(User,blank=True,null=True)                            #The django admin user who moderated the event.
    def __unicode__(self):
        return self.title