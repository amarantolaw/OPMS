from django.db import models
from django.utils.encoding import smart_str, smart_unicode
from datetime import date, datetime

# Remember: this application is managed by Django South so when you change this file, do the following:
# python manage.py schemamigration ffm --auto
# python manage.py migrate ffm

class Person(models.Model): # This should be in the CRM or OxDB App
    titles = models.CharField("Honorifics and Titles", max_length=100)
    first_name = models.CharField("First Name", max_length=50)
    middle_names = models.CharField("Middle Names", max_length=200)
    last_name = models.CharField("Last Name", max_length=50)
    additional_information = models.TextField("Additional Information (e.g. University of Oxford)")
    email = models.EmailField(null=True)

    def full_name(self):
        return smart_unicode(self.titles + ' ' + self.first_name + ' ' + self.middle_names + ' ' + self.last_name)

    def short_name(self):
        return smart_unicode(self.first_name + ' ' + self.last_name)

    def __unicode__(self):
        return self._full_name()


class Unit(models.Model):
    name = models.CharField("unit name", max_length=250)
    oxpoint_id = models.IntegerField("OxItems ID")

    def __unicode__(self):
        return self._full_name()


class TagGroup(models.Model):
    # Groups of Tags. How to create collection types
    description = models.TextField("Description")
    name = models.CharField("Name", max_length=50)

    def __unicode__(self):
        return smart_unicode(self.name)


class Tag(models.Model):
    # Text value used to group Items and Feeds
    group = models.ForeignKey(TagGroup, verbose_name="Group tag belongs to")
    name = models.TextField("Name of tag")

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + self.group.name + ')')


class Licence(models.Model):
    # Expandable data table of licences we can publish with or recognise
    description = models.TextField("Description of Licence")
    name = models.CharField("Name", max_length=100)
    url = models.URLField("URL for full licence", null=True)
    image = models.ForeignKey('File', limit_choices_to = {'function__file_category__contains':'image'},
                              null=True, verbose_name="image for licence")

    def __unicode__(self):
        return smart_unicode(self.name)


class Item(models.Model):
    description = models.TextField("Description", null=True)
    guid = models.CharField("GUID String", max_length=200)
    internal_comments = models.TextField("Private comments on this item")
    last_updated = models.DateTimeField("Datetime for last update", auto_now=True)
    license = models.ForeignKey(Licence, verbose_name="Licence")
    owning_unit = models.ForeignKey(Unit, verbose_name="Unit owning this item")
    people = models.ManyToManyField(Person, through='Role', verbose_name="Associated People")
    publish_start = models.DateTimeField("Publishing start date", default=datetime.now)
    publish_stop = models.DateTimeField("Publishing end date", null=True)
    recording_date = models.DateField("Date of recording", null=True)
    tags = models.ManyToManyField(Tag, verbose_name="Associated Tags")
    title = models.CharField("Item Title", max_length=256)

    @property
    def links(self):
        return file_set.filter(function__file_category__contains='link')

    @property
    def artwork(self):
        # use models.ImageField() in the future
        return file_set.filter(iexact='itemart')

    def __unicode__(self):
        return smart_unicode(self.title) or ''

    class Meta:
        verbose_name = 'Podcast item'
        verbose_name_plural = 'Podcast items'


class Role(models.Model):
    ROLES = [
        # From http://www.steeple.org.uk/wiki/Feeds/credit
        # NB: We could always use this extensive list... http://www.ebu.ch/metadata/cs/web/ebu_RoleCodeCS_p.xml.htm
        (u'presenter', u'Presenter'),
        (u'lecturer', u'Lecturer'),
        (u'moderator', u'Moderator'),
        (u'mc', u'Master of Ceremonies'),
        (u'interviewer', u'Interviewer'),
        (u'interviewee', u'Interviewee'),
        (u'creator', u'Creator'),
        (u'publisher', u'Publisher'),
    ]
    person = models.ForeignKey(Person, verbose_name="associated Person")
    item = models.ForeignKey(Item, verbose_name="associated Item")
    role = models.CharField("role of Person", max_length=20, choices=ROLES, db_index=True)

    def get_role_display(self):
        return ROLES.get(self.role, 'unknown')

    def __unicode__(self):
        return smart_unicode(self.person.short_name() + ' is a ' + ROLES.get(self.role) + ' for ' + self.item.title)


class FileFunction(models.Model):
    FILE_CATEGORY_CHOICES = [
        (u'audio', u'Audio'),
        (u'video', u'Video'),
        (u'image', u'Image'),
        (u'text', u'Text'),
        (u'link', u'Link'),
        (u'transcript', u'Transcript'),
        (u'unknown', u'Unknown'),
    ]
    FILE_TYPE_CHOICES = [
        (u'mp3', u'Audio MP3'),
        (u'mp4', u'Video MP4'),
        (u'm4a', u'Audio M4A'),
        (u'm4b', u'Audiobook M4B'),
        (u'm4p', u'Audio Protected M4P'),
        (u'm4v', u'Video M4V'),
        (u'txt', u'Text TXT'),
        (u'gif', u'Image GIF'),
        (u'png', u'Image PNG'),
        (u'jpg', u'Image JPG'),
        (u'pdf', u'Portable Document Format'),
        (u'pub', u'Electronic Book'),
        (u'htm', u'Webpage'),
        (u'html', u'Webpage'),
        (u'php', u'php Webpage'),
        (u'', u'Unknown'),
    ]
    description = models.TextField("description")
    name = models.CharField("name", max_length=50)
    file_category = models.CharField("file category", max_length=20, choices=FILE_CATEGORY_CHOICES)
    file_type = models.CharField("file type", max_length=5, choices=FILE_TYPE_CHOICES)

    def get_filetype_display(self):
        return FILE_TYPE_CHOICES.get(self.file_type, 'unknown')

    def get_filecategory_display(self):
        return FILE_CATEGORY_CHOICES.get(self.file_category, 'unknown')

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + self.file_category + ')')


class File(models.Model):
    MIMETYPES = [
        (u'audio/x-mpeg', u'MP3 audio'),
        (u'video/mp4', u'MP4 video'),
        (u'MPEG4 Video', u'MP4 video'),
        (u'text/html', u'HTML document'),
        (u'audio/mpeg', u'MP3 audio'),
        (u'video/x-ms-wmv', u'WMV video'),
        (u'text/plain', u'plain text'),
        (u'application/pdf', u'PDF document'),
        (u'audio/x-m4b', u'MP4 audio'),
        (u'application/octet-stream', u'unknown'),
        (u'video/mpeg', u'MPEG video'),
        (u'video/x-m4v', u'MP4 video'),
        (u'audio/x-m4a', u'MP4 audio'),
        (u'application/epub+zip', u'ePub eBook'),
    ]
    duration = models.IntegerField("duration in seconds", null=True)
    #v2.0 file = models.FileField(upload_to='')
    function = models.ForeignKey(FileFunction, verbose_name="file function")
    guid = models.CharField("file GUID", max_length=100)
    item = models.ForeignKey(Item, verbose_name="Owning Item")
    mimetype = models.TextField("mime type", default='unknown', choices=MIMETYPES)
    size = models.IntegerField("file size in bytes", null=True)
    url = models.URLField("file url", verify_exists=True) # Everything in this system should be hosted on a URL

    @property
    def title(self):
        # return the title of this file via Item
        return self.item.title

    def get_mimetype_display(self):
        return MIMETYPES.get(self.mimetype, 'unknown')

    class Meta:
        verbose_name = 'Podcast enclosed data'
        verbose_name_plural = 'Podcast enclosed data'

    def __unicode__(self):
        return smart_unicode(self.url + ' (' + self.item.title +')')


class Destination(models.Model):
    # This is a publishing destination, used when it comes to generating specific feeds for output
    name = models.CharField("name", max_length=100)
    description = models.TextField("description")
    url = models.URLField("base url of destination")

    def __unicode__(self):
        return smart_unicode(self.name + ' (' + str(self.url) + ')')



class Feed(models.Model):
    description = models.TextField("description", default='')
    destinations = models.ManyToManyField(Destination, through='FeedDestination', verbose_name="destinations for this feed")
    files = models.ManyToManyField(File, through='FileInFeed', verbose_name="files related to this feed")
    guid = models.CharField("guid", max_length=100)
    last_updated = models.DateTimeField("last updated", auto_now=True)
    owning_unit = models.ForeignKey(Unit, verbose_name="unit owning this feed")
    publish_start = models.DateField("start publishing from date", default=datetime.now)
    publish_stop = models.DateField("stop publishing by date", null=True)
    slug = models.SlugField("seo feedname", unique=True) # aka, Feed name in OxItems parlance
    tags = models.ManyToManyField(Tag, verbose_name="tags categorising this feed")
    title = models.CharField("title", max_length=150)

    @property
    def podcasts(self):
        return files.filter(function__file_category__in=('audio', 'video'))

    @property
    def links(self):
        return files.filter(function__file_category__contains='link')

    @property
    def artwork(self):
        # use models.ImageField() in the future
        return files.filter(iexact='feedart')

    def __unicode__(self):
        return smart_unicode(self.title) or ''

    class Meta:
        verbose_name = 'Podcast feed'
        verbose_name_plural = 'Podcast feeds'
        # ordering = ('title',)


class FileInFeed(models.Model):
    ITUNESU_CATEGORIES = [
        # List from: http://deimos.apple.com/rsrc/doc/iTunesUAdministrationGuide/iTunesUintheiTunesStore/chapter_13_section_3.html
        (100, u'Business'),
        (100100, u'Economics'),
        (100101, u'Finance'),
        (100102, u'Hospitality'),
        (100103, u'Management'),
        (100104, u'Marketing'),
        (100105, u'Personal Finance'),
        (100106, u'Real Estate'),

        (101, u'Engineering'),
        (101100, u'Chemical & Petroleum'),
        (101101, u'Civil'),
        (101102, u'Computer Science'),
        (101103, u'Electrical'),
        (101104, u'Environmental'),
        (101105, u'Mechanical'),

        (102, u'Fine Arts'),
        (102100, u'Architecture'),
        (102101, u'Art'),
        (102102, u'Art History'),
        (102103, u'Dance'),
        (102104, u'Film'),
        (102105, u'Graphic Design'),
        (102106, u'Interior Design'),
        (102107, u'Music'),
        (102108, u'Theater'),

        (103, u'Health & Medicine'),
        (103100, u'Anatomy & Physiology'),
        (103101, u'Behavioral Science'),
        (103102, u'Dentistry'),
        (103103, u'Diet & Nutrition'),
        (103104, u'Emergency'),
        (103105, u'Genetics'),
        (103106, u'Gerontology'),
        (103107, u'Health & Exercise Science'),
        (103108, u'Immunology'),
        (103109, u'Neuroscience'),
        (103110, u'Pharmacology & Toxicology'),
        (103111, u'Psychiatry'),
        (103112, u'Public Health'),
        (103113, u'Radiology'),

        (104, u'History'),
        (104100, u'Ancient'),
        (104101, u'Medieval'),
        (104102, u'Military'),
        (104103, u'Modern'),
        (104104, u'African'),
        (104105, u'Asian'),
        (104106, u'European'),
        (104107, u'Middle Eastern'),
        (104108, u'North American'),
        (104109, u'South American'),

        (105, u'Humanities'),
        (105100, u'Communications'),
        (105101, u'Philosophy'),
        (105102, u'Religion'),

        (106, u'Language'),
        (106100, u'African'),
        (106101, u'Ancient'),
        (106102, u'Asian'),
        (106103, u'Eastern European/Slavic'),
        (106104, u'English'),
        (106105, u'English Language Learners'),
        (106106, u'French'),
        (106107, u'German'),
        (106108, u'Italian'),
        (106109, u'Linguistics'),
        (106110, u'Middle Eastern'),
        (106111, u'Spanish & Portuguese'),
        (106112, u'Speech Pathology'),

        (107, u'Literature'),
        (107100, u'Anthologies'),
        (107101, u'Biography'),
        (107102, u'Classics'),
        (107103, u'Criticism'),
        (107104, u'Fiction'),
        (107105, u'Poetry'),

        (108, u'Mathematics'),
        (108100, u'Advanced Mathematics'),
        (108101, u'Algebra'),
        (108102, u'Arithmetic'),
        (108103, u'Calculus'),
        (108104, u'Geometry'),
        (108105, u'Statistics'),

        (109, u'Science'),
        (109100, u'Agricultural'),
        (109101, u'Astronomy'),
        (109102, u'Atmospheric'),
        (109103, u'Biology'),
        (109104, u'Chemistry'),
        (109105, u'Ecology'),
        (109106, u'Geography'),
        (109107, u'Geology'),
        (109108, u'Physics'),

        (110, u'Social Science'),
        (110100, u'Law'),
        (110101, u'Political Science'),
        (110102, u'Public Administration'),
        (110103, u'Psychology'),
        (110104, u'Social Welfare'),
        (110105, u'Sociology'),

        (111, u'Society'),
        (111100, u'African-American Studies'),
        (111101, u'Asian Studies'),
        (111102, u'European & Russian Studies'),
        (111103, u'Indigenous Studies'),
        (111104, u'Latin & Caribbean Studies'),
        (111105, u'Middle Eastern Studies'),
        (111106, u'Women''s Studies'),

        (112, u'Teaching & Education'),
        (112100, u'Curriculum & Teaching'),
        (112101, u'Educational Leadership'),
        (112102, u'Family & Childcare'),
        (112103, u'Learning Resources'),
        (112104, u'Psychology & Research'),
        (112105, u'Special Education'),
    ]
    file = models.ForeignKey(File, verbose_name="file")
    feed = models.ForeignKey(Feed, verbose_name="feed")
    alternative_title = models.CharField("alternative file title", max_length=256, null=True)
    order = models.IntegerField("manual sort order for feed", default=0)
    withhold = models.IntegerField("publishing status", default=100) # Default to being withheld
    # Optional additional categorising information
    itunesu_category = models.IntegerField("iTunesU category", choices=ITUNESU_CATEGORIES, null=True)
    jacs_codes = models.ForeignKey(Tag,
                                   limit_choices_to = {'group__name__contains': 'JACS codes'},
                                   null=True,
                                   verbose_name="JACS codes")

    def get_itunesu_category_display(self):
        return ITUNESU_CATEGORIES.get(self.itunesu_category, '112')

    def __unicode__(self):
        return smart_unicode(self.file.name + ' in ' + self.feed.title)


class FeedDestination(models.Model):
    feed = models.ForeignKey(Feed, verbose_name="feed")
    destination = models.ForeignKey(Destination, verbose_name="destination")
    withhold = models.IntegerField("publishing status", default=100) # Default to being withheld
    url = models.URLField("url of this feed")

    def __unicode__(self):
        return smart_unicode(self.feed.title + ' for ' + self.destination.name + ' at:' + self.url)