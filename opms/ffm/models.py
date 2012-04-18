from django.db import models
from django.utils.encoding import smart_unicode
from datetime import datetime
from opms.core.models import Person
from django.contrib.auth.models import User
import uuid

# Remember: this application is managed by Django South so when you change this file, do the following:
# python manage.py schemamigration ffm --auto
# python manage.py migrate ffm
# NB: Can't convert existing fields to foreignkeys in one step. Need to do two migrations. http://south.aeracode.org/ticket/498

# Common fields
#    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
#    created_on = models.DateTimeField(auto_now_add=True)
#    # c1
#    name = models.CharField("name", max_length=100, default="")
#    description = models.TextField("description", default="")
#    # c2 & c3
#    replaced_by = models.ForeignKey("", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
#    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
#    deleted_on = models.DateTimeField(null=True)
#    # c4
#    last_modified_by = models.ForeignKey(User, null=True)
#    last_modified_on = models.DateTimeField(auto_now=True)

EBU_ROLES = [
    # From http://www.steeple.org.uk/wiki/Feeds/credit -> defering to the mRSS preferred list of EBU...
    # NB: Using section 25 TALENT http://www.ebu.ch/metadata/cs/web/ebu_RoleCodeCS_p.xml.htm
    (u'25.1', u'Key Character'),
    (u'25.2', u'Key Talents'),
    (u'25.3', u'Scenarist'),
    (u'25.4', u'Essayist'),
    (u'25.5', u'Sculptor'),
    (u'25.6', u'Variety Artist'),
    (u'25.7', u'Voice Over Artist'),
    (u'25.8', u'Artist / Performer'),
    (u'25.9', u'Actor'),
    (u'25.10', u'Anchor / Moderator / Presenter'),
    (u'25.11', u'Interviewer'),
    (u'25.12', u'Interviewed Guest'),
    (u'25.13', u'Guest'),
    (u'25.14', u'Host'),
    (u'25.15', u'Narrator / Storyteller / Reader'),
    (u'25.16', u'Speaker / Lecturer / Causeur'),  # This is the likely default option for podcasts
    (u'25.17', u'Choreographer'),
    (u'25.18', u'Dancer'),
    (u'25.19', u'Participant'),
    (u'25.20', u'Panelist'),
    (u'25.21', u'Commentator'),
    (u'25.22', u'Dubber'),
    ]

class Tag(models.Model):
    TAG_GROUP_CHOICES = [
        (1,u'Unsorted Tags'), # Old and assorted tags often imported from OxItems and need migrating
        (2,u'JACS Codes'), # Codes used for OER markup of items
        (3,u'JorumOPEN Collection'), # Codes used for JorumOPEN markup of feeds
        (4,u'iTunes U Category'), # List from: http://deimos.apple.com/rsrc/doc/iTunesUAdministrationGuide/iTunesUintheiTunesStore/chapter_13_section_3.html
    ]
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default='')
    description = models.TextField("description", default='')
    replaced_by = models.ForeignKey("Tag", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)

#    group = models.ForeignKey(TagGroup, verbose_name="Group tag belongs to", default=1)
    group = models.SmallIntegerField("tag group", choices=TAG_GROUP_CHOICES, default=1)
    parent = models.ForeignKey("Tag", null=True, related_name="%(app_label)s_%(class)s_parent")

    def get_group_name(self):
        return self.TAG_GROUP_CHOICES.get(self.group, 'Unknown')

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + self.get_group_name() + ')')


class Licence(models.Model):
    """
    Expandable data table of licences we can publish with or recognise
    """
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    last_modified_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_last_modified_by")
    last_modified_on = models.DateTimeField(auto_now=True)

    url = models.URLField("URL for full licence", null=True)
#    logo = models.ImageField(null=True, upload_to="") # Requires PIL to be installed

    def __unicode__(self):
        return smart_unicode(self.name)


class Link(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    replaced_by = models.ForeignKey("Link", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)

    url = models.URLField("link url including http: etc", default='http://www.ox.ac.uk/')


class ItemTag(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("ItemTag", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    ordering = models.SmallIntegerField("manual ordering", default=1)
    tag = models.ForeignKey(Tag, verbose_name="associated tag", related_name="%(app_label)s_%(class)s_tag")
    item = models.ForeignKey("Item", verbose_name="associated item", related_name="%(app_label)s_%(class)s_item")

    def __unicode__(self):
        return smart_unicode(self.tag.name + ' is associated with ' + self.item.name)

class ItemRole(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("ItemRole", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    role = models.CharField("role of Person", max_length=20, choices=EBU_ROLES, db_index=True)
    person = models.ForeignKey(opms.core.models.Person, verbose_name="associated person", related_name="%(app_label)s_%(class)s_person")
    item = models.ForeignKey("Item", verbose_name="associated item", related_name="%(app_label)s_%(class)s_item")

    def get_role_display(self):
        return EBU_ROLES.get(self.role, 'unknown')

    def __unicode__(self):
        return smart_unicode(self.person.short_name() + ' is a ' + EBU_ROLES.get(self.role) + ' for ' + self.item.name)


class ItemLink(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("ItemLink", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    link = models.ForeignKey(Link, verbose_name="associated link", related_name="%(app_label)s_%(class)s_link")
    item = models.ForeignKey("Item", verbose_name="associated item", related_name="%(app_label)s_%(class)s_item")

    def __unicode__(self):
        return smart_unicode(self.link.name + ' is associated with ' + self.item.name)


class Item(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    replaced_by = models.ForeignKey("Item", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    publish_start = models.DateTimeField("publishing start date", default=datetime.now)
    publish_stop = models.DateTimeField("publishing end date", null=True)
    recording_date = models.DateField("date of recording", null=True)
    licence_confirmed = models.BooleanField("licence confirmed?", default=False)
    licence = models.ForeignKey(Licence, verbose_name="licence", default=1,
        related_name="%(app_label)s_%(class)s_licence")
    tags = models.ManyToManyField(Tag, through="ItemTag", related_name="%(app_label)s_%(class)s_tags")
    people = models.ManyToManyField(opms.core.models.Person, through="ItemRole", verbose_name="associated people",
        related_name="%(app_label)s_%(class)s_people")
    links = models.ManyToManyField(Link, through="ItemLink", verbose_name="associated links",
        related_name="%(app_label)s_%(class)s_links")
    collections = models.ManyToManyField("Collection", through="Association", verbose_name="associated collections",
        related_name="%(app_label)s_%(class)s_collections")

    #    def create_guid():
    #        return 'OPMS-item:' + str(uuid.uuid4())
    #    guid = models.CharField("GUID String", max_length=100, default=create_guid)

    #    @property
    #    def artwork(self):
    #        # use models.ImageField() in the future
    #        return self.file_set.filter(function__name__iexact='itemart')

    def __unicode__(self):
        return smart_unicode(self.name)

    class Meta:
        verbose_name = 'Podcast item'
        verbose_name_plural = 'Podcast items'


class Collection(models.Model):
    TYPE_CHOICES = [
        (u"manual",u"Manual"),
        (u"smart",u"Smart")
    ]
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    replaced_by = models.ForeignKey("Collection", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    publish_start = models.DateField("start publishing from date", default=datetime.now)
    publish_stop = models.DateField("stop publishing by date", null=True)
    type = models.CharField("type",max_length=10,choices=TYPE_CHOICES,default="manual")
    tags = models.ManyToManyField(Tag, through="CollectionTag", related_name="%(app_label)s_%(class)s_tags")
    people = models.ManyToManyField(Person, through="CollectionRole", verbose_name="associated people",
                                    related_name="%(app_label)s_%(class)s_people")
    links = models.ManyToManyField(Link, through="CollectionLink", verbose_name="associated links",
                                   related_name="%(app_label)s_%(class)s_links")
    items = models.ManyToManyField(Item, through="Association", verbose_name="associated collections",
                                   related_name="%(app_label)s_%(class)s_items")

#    @property
#    def jorumopen_collections(self):
#        return self.tags.filter(group__name__iexact='JorumOPEN Collection')

    def __unicode__(self):
        return smart_unicode(self.name) or ''


class CollectionTag(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("CollectionTag", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    ordering = models.SmallIntegerField("manual ordering", default=1)
    tag = models.ForeignKey(Tag, verbose_name="associated tag", related_name="%(app_label)s_%(class)s_tag")
    collection = models.ForeignKey(Collection, verbose_name="associated collection", related_name="%(app_label)s_%(class)s_collection")

    def __unicode__(self):
        return smart_unicode(self.tag.name + ' is associated with ' + self.collection.name)


class CollectionRole(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("CollectionRole", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    role = models.CharField("role of Person", max_length=20, choices=EBU_ROLES, db_index=True)
    person = models.ForeignKey(Person, verbose_name="associated person", related_name="%(app_label)s_%(class)s_person")
    collection = models.ForeignKey(Collection, verbose_name="associated collection", related_name="%(app_label)s_%(class)s_collection")

    def get_role_display(self):
        return EBU_ROLES.get(self.role, 'unknown')

    def __unicode__(self):
        return smart_unicode(self.person.short_name() + ' is a ' + EBU_ROLES.get(self.role) + ' for ' + self.collection.name)


class CollectionLink(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("CollectionLink", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    link = models.ForeignKey(Link, verbose_name="associated link", related_name="%(app_label)s_%(class)s_link")
    collection = models.ForeignKey(Collection, verbose_name="associated collection", related_name="%(app_label)s_%(class)s_collection")

    def __unicode__(self):
        return smart_unicode(self.link.name + ' is associated with ' + self.collection.name)


class Association(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("Association", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    ordering = models.SmallIntegerField("manual ordering", default=1)
    item = models.ForeignKey(Item, verbose_name="associated item", related_name="%(app_label)s_%(class)s_item")
    collection = models.ForeignKey(Collection, verbose_name="associated collection", related_name="%(app_label)s_%(class)s_collection")

    def __unicode__(self):
        return smart_unicode(self.item.name + ' is associated with ' + self.collection.name)

class AssociationTag(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("AssociationTag", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    ordering = models.SmallIntegerField("manual ordering", default=1)
    tag = models.ForeignKey(Tag, verbose_name="associated tag", related_name="%(app_label)s_%(class)s_tag")
    association = models.ForeignKey(Association, verbose_name="associated association", related_name="%(app_label)s_%(class)s_association")

    def __unicode__(self):
        return smart_unicode(self.tag.name + ' is associated with ' + str(self.association.id))


class FileType(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    last_modified_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_last_modified_by")
    last_modified_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + self.description + ')')


class FeedTemplate(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    last_modified_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_last_modified_by")
    last_modified_on = models.DateTimeField(auto_now=True)
    filetypes = models.ManyToManyField(FileType, through="Supports", verbose_name="supported filetypes",
                                       related_name="%(app_label)s_%(class)s_filetypes")

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + self.description + ')')


class Supports(models.Model):
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("Supports", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    filetype = models.ForeignKey(FileType, related_name="%(app_label)s_%(class)s_filetype")
    feedtemplate = models.ForeignKey(FeedTemplate)

    def __unicode__(self):
        return smart_unicode(self.feedtemplate.name + ' supports ' + self.filetype.name)

#    MIMETYPES = [
#        (u'audio/x-mpeg', u'MP3 audio'),
#        (u'video/mp4', u'MP4 video'),
#        (u'MPEG4 Video', u'MP4 video'),
#        (u'text/html', u'HTML document'),
#        (u'audio/mpeg', u'MP3 audio'),
#        (u'video/x-ms-wmv', u'WMV video'),
#        (u'text/plain', u'plain text'),
#        (u'application/pdf', u'PDF document'),
#        (u'audio/x-m4b', u'MP4 audio'),
#        (u'application/octet-stream', u'unknown'),
#        (u'video/mpeg', u'MPEG video'),
#        (u'video/x-m4v', u'MP4 video'),
#        (u'audio/x-m4a', u'MP4 audio'),
#        (u'application/epub+zip', u'ePub eBook'),
#    ]
#
#    def get_mimetype_display(self):
#        return MIMETYPES.get(self.mimetype, 'unknown')
#
#    mimetype = models.CharField("mime type", max_length=50, choices=MIMETYPES, default='unknown')


class File(models.Model):
    PUBLISH_CHOICES = [
        (0,u'Published'),
        (1,u'Withheld')
    ]

    def get_publish_status(self):
        return self.PUBLISH_CHOICES.get(self.publish_status, 'unknown')

    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("File", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    checksum = models.CharField("checksum", max_length=255, null=True) # As nice as this would be to be mandatory, I'll save that option till later
    # Filehash notes at: http://docs.python.org/library/hashlib.html; http://en.wikipedia.org/wiki/Cryptographic_hash_function#Cryptographic_hash_algorithms
    # and a memory friendly method of applying this at http://stackoverflow.com/questions/1131220/get-md5-hash-of-a-files-without-open-it-in-python
    # Also note filecomparison functions at http://docs.python.org/library/filecmp.html
    publish_status = models.SmallIntegerField("publish status", choices=PUBLISH_CHOICES, default=0)
    item = models.ForeignKey(Item, verbose_name="Owning Item", related_name="%(app_label)s_%(class)s_item")
    type = models.ForeignKey(FileType, verbose_name="file function", default=1, related_name="%(app_label)s_%(class)s_type")

    # Optional extras
    duration = models.IntegerField("duration in seconds", null=True)
    size = models.IntegerField("file size in bytes", null=True)

    @property
    def name(self):
        # return the name of this file via Item
        if not self.item:
            return "Can not find parent Item"
        else:
            return self.item.name

    def __unicode__(self):
        return smart_unicode(self.name)



class FileURL(models.Model):
    # A unique file can be presented on multiple URLS, use this table to track and associate them
    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("FileURL", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    # TODO: Investigate http://docs.python.org/library/urlparse.html for url parsing
    file = models.ForeignKey(File, verbose_name="file urls", related_name="%(app_label)s_%(class)s_file")
    url = models.URLField("file url", verify_exists=True) # Everything in this system should be hosted on a URL

    def __unicode__(self):
        return smart_unicode(self.url)


class Feed(models.Model):
    PUBLISH_CHOICES = [
        (0,u'Published'),
        (1,u'Withheld')
    ]

    def get_publish_status(self):
        return self.PUBLISH_CHOICES.get(self.publish_status, 'unknown')

    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField("name", max_length=100, default="")
    description = models.TextField("description", default="")
    replaced_by = models.ForeignKey("Feed", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    publish_status = models.SmallIntegerField("publish status", choices=PUBLISH_CHOICES, default=0)
    collection = models.ForeignKey(Collection, verbose_name="associated collection", related_name="%(app_label)s_%(class)s_collection")
    template = models.ForeignKey(FeedTemplate, verbose_name="associated template", related_name="%(app_label)s_%(class)s_template")
    files = models.ManyToManyField(File, through="FileInFeed", verbose_name="files related to this feed",
                                   related_name="%(app_label)s_%(class)s_files")

#    @property
#    def podcasts(self):
#        return files.filter(function__file_category__in=('audio', 'video', 'document'))

#    @property
#    def artwork(self):
#        # use models.ImageField() in the future
#        try:
#            return self.files.filter(function__name__iexact='feedart')[0]
#        except IndexError:
#            return None
    artwork = models.URLField("artwork url", verify_exists=True, null=True)

    def __unicode__(self):
        return smart_unicode(self.name) or ''

    class Meta:
        verbose_name = 'Podcast feed'
        verbose_name_plural = 'Podcast feeds'
        # ordering = ('title',)


class FileInFeed(models.Model):
    def create_guid(self):
        return 'OPMS-file:' + str(uuid.uuid4())

    created_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_created_by")
    created_on = models.DateTimeField(auto_now_add=True)
    replaced_by = models.ForeignKey("FileInFeed", null=True, related_name="%(app_label)s_%(class)s_replaced_by")
    deleted_by = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_deleted_by")
    deleted_on = models.DateTimeField(null=True)
    guid = models.CharField("file GUID", max_length=200, default=create_guid) # Used to identify a file uniquely
    # dependant on the feed it is placed in (tracking)
    file = models.ForeignKey(File, verbose_name="file", related_name="%(app_label)s_%(class)s_file")
    feed = models.ForeignKey(Feed, verbose_name="feed", related_name="%(app_label)s_%(class)s_feed")

    def __unicode__(self):
        return smart_unicode(self.file.name + ' in ' + self.feed.name)


class OxitemsMapping(models.Model):
    """
    This maps the OxItems feed name (Rg07Channels.name) to a corresponding Feed. This mapping isn't completely clean
    because OxItems is based around feeds (and typically "name+audio/video/document" format),
    whereas FFM has the idea of Collections, with a feed created to map a Collection to a specific type of
    FeedTemplate, which are Marko's idea for relating filetypes from a collection to a specific destination.

    However, we need this name to allow us to relate some of the stats data more easily back to Collections,
    and as a form of lookup in other as-yet-undefined use cases.
    """
    feed = models.ForeignKey(Feed)
    feed_name = models.CharField("short name", max_length=255)