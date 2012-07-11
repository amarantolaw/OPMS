from django.db import models
import datetime

class Metric(models.Model):
    "A measure of web traffic"
    description = models.CharField(max_length=200)  #A description of the metric eg. 'Complete downloads'
    linecolor = models.CharField(max_length=7)      #The colour of the line when this metric is plotted on a chart
    fillcolor = models.CharField(max_length=7)      #The colour of the gradient under the said line
    mouseover = models.BooleanField()               #Whether rolling the mouse over a point will display the precise position of the point as an overlay
    defaultvisibility = models.BooleanField()       #Whether the metric is visible by default
    def mouseover_timeplot(self):
        return str(self.mouseover).lower()
    def __unicode__(self):
        return self.description

class Category(models.Model):
    "A group of Comments and/or Events which can be toggled together and displayed identically"
    description = models.CharField(max_length=200)  #A description of the category eg. 'Comments made by e-mail' or 'iTunes store upgrades'
    color = models.CharField(max_length=7)          #The colour of the line on the chart representing events and/or comments in this category
    defaultvisibility = models.BooleanField()       #Whether the metric is visible by default
    def __unicode__(self):
        return self.description

class Traffic(models.Model):
    "A day's worth of traffic to a website according to some metric."
    date = models.DateField()                   #The day on which this traffic occurred
    def date_timeplot(self):                    #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    count = models.PositiveIntegerField()       #The number of occurrences of this metric of traffic on that day
    metric = models.ForeignKey(Metric)          #The ID of the metric used to measure traffic
    def __unicode__(self):
        return '\"' + self.metric.description + '\" = ' + str(self.count) + ' on ' + str(self.date)

class Comment(models.Model):
    "A comment made about the website on a certain day"
    date = models.DateField()                   #The day when the comment was made
    def date_timeplot(self):                    #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    def datetime_timeplotxml(self):
        return self.date.strftime("%b %d %Y") + " " + self.time.strftime("%H:%M:%S") + " GMT"
    time = models.TimeField()                   #The time at which the comment was made
    source = models.CharField(max_length=200)   #The source of the comment (DELIBERATELY VAGUE FOR THE MOMENT!)
    detail = models.TextField()                 #The text of the comment
    category = models.ForeignKey(Category)      #Categories may include Events as well as Comments
    def __unicode__(self):
        return self.detail

class Event(models.Model):
    "An event which occurred on a certain day"
    date = models.DateField()                   #The date on which the event occurred
    def date_timeplot(self):                    #Date in yyyy-mm-dd format so that timeplot can eat it. Code is here since str() can't be used in templates.
        return str(self.date)
    def datetime_timeplotxml(self):
        return self.date.strftime("%b %d %Y") + " " + "00:00:00" + " GMT"
    title = models.CharField(max_length=50)     #The title of the event. Needs to be short enough to look pretty.
    detail = models.TextField()                 #Potentially useful details about the event
    category = models.ForeignKey(Category)      #Categories may include Comments as well as Events
    def __unicode__(self):
        return self.title