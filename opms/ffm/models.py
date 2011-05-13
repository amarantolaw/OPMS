from django.db import models
from django.core.urlresolvers import reverse
from opms.ffm.data import licenses

class Tag(models.Model):    
    name = models.TextField()

class Person(models.Model):
    name = models.TextField()

class Item(models.Model):
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    publish_date = models.DateTimeField(null=True)
    guid = models.TextField()
    people = models.ManyToManyField(Person, through='Role')
    license = models.URLField(null=True)
    tags = models.ManyToManyField(Tag)
    recording_date = models.DateField(null=True)
    owning_unit = models.IntegerField()
    publish_status = models.TextField(default='published')

    def __unicode__(self):
        return self.title or ''
        
    @property
    def license_data(self):
        return licenses.get(self.license) or licenses.get(self.podcast.license)

    class Meta:
        verbose_name = 'Podcast item'
        verbose_name_plural = 'Podcast items'

class Role(models.Model):
    person = models.ForeignKey(Person)
    item = models.ForeignKey(Item)
    role = models.TextField()

MIMETYPES = {
    'audio/x-mpeg': 'MP3 audio',
    'video/mp4': 'MP4 video',
    'MPEG4 Video': 'MP4 video',
    'text/html': 'HTML document',
    'audio/mpeg': 'MP3 audio',
    'video/x-ms-wmv': 'WMV video',
    'text/plain': 'plain text',
    'application/pdf': 'PDF document',
    'audio/x-m4b': 'MP4 audio',
    'application/octet-stream': 'unknown',
    'video/mpeg': 'MPEG video',
    'video/x-m4v': 'MP4 video',
    'audio/x-m4a': 'MP4 audio',
    'application/epub+zip': 'ePub eBook'
}

class File(models.Model):
    item = models.ForeignKey(Item)
    guid = models.TextField(null=True)
    url = models.URLField(null=True)
    size = models.IntegerField(null=True)
    duration = models.IntegerField(null=True)
    mimetype = models.TextField(null=True)
    function = models.TextField(default='Unknown',
                                choices=(
                                        ('Unknown', 'Unknown'),
                                        ('FeedArt', 'Feed art'),
                                    ))
    
    @property
    def medium(self):
        medium = {'application/pdf': 'document', 'MPEG4 Video': 'video'}.get(self.mimetype)
        if medium:
            return medium
        elif not self.mimetype:
            return self.podcast_item.podcast.medium or 'unknown'
        elif self.mimetype.startswith('audio/'):
            return 'audio'
        elif self.mimetype.startswith('video/'):
            return 'video'
        else:
            return self.podcast_item.podcast.medium or 'unknown'
    
    def get_mimetype_display(self):
        return MIMETYPES.get(self.mimetype, 'unknown')
    
    class Meta:
        verbose_name = 'Podcast enclosed data'
        verbose_name_plural = 'Podcast enclosed data'

class Feed(models.Model):
    slug = models.SlugField(unique=True)
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    source_url = models.URLField()
    last_updated = models.DateTimeField(auto_now=True)
    owning_unit = models.IntegerField()
    publish_date = models.DateField()
    source_service = models.TextField()
    feedart = models.ForeignKey(File)
    files = models.ManyToManyField(File, through='FileInFeed')
        
    def __unicode__(self):
        return self.title or ''
        
    @property
    def license_data(self):
        return licenses.get(self.license)

    class Meta:
        verbose_name = 'Podcast feed'
        verbose_name_plural = 'Podcast feeds'
        ordering = ('title',)

class FileInFeed(models.Model):
    file = models.ForeignKey(File)
    feed = models.ForeignKey(Feed)
    order = models.IntegerField(default=0)
    itunesu_category = models.IntegerField(default=112)
    jacs_code = models.TextField(null=True)
