# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

# These tables can be manually dropped when the app and model is deleted. In the meantime, syncdb works as normal.

from django.db import models
from django.utils.encoding import smart_str, smart_unicode
from datetime import date
from opms.ffm.models import *


# These are local temporary linking tables designed to make syncing easier
class ImportFeedChannel(models.Model):
    """
    If a feed has been linked to this channel, then attempt to update that feed
    """
    feed = models.ForeignKey(Feed)
    channel = models.ForeignKey("Rg07Channels")

class ImportFeedGroupChannel(models.Model):
    """
    If a feedgroup has been linked to this channel, then attempt to update that feed
    """
    feedgroup = models.ForeignKey(FeedGroup)
    channel = models.ForeignKey("Rg07Channels")


class ImportFileItem(models.Model):
    """
    If a file has been linked to this item, then attempt to update that file
    """
    file = models.ForeignKey(File)
    item = models.ForeignKey("Rg07Items")

class ImportItemItem(models.Model):
    """
    If an item has been linked to this item, then attempt to update that item
    """
    ffm_item = models.ForeignKey(Item)
    item = models.ForeignKey("Rg07Items")



class Rg07Channels(models.Model):
    channel_categories = models.TextField() # csv, one of: complex-events, simple-events, ordinary, taxonomy or simple-podcasting
    channel_cc = models.IntegerField() # Apple category codes: 58 variants, typically 0, nnn, or nnnnnn.
    channel_emailaddress = models.CharField(max_length=256) # an email address. currently 85 variants
    channel_guid = models.CharField(max_length=80) # OxItems generated guid, not to be mistaken for the Item GUID, e.g. u'http://rss.oucs.ox.ac.uk/tag:2008-09-11:143546:911:bodlib/bodleian_gems-video'
    channel_image = models.CharField(max_length=256) # URL to album art. Some of these are empty
    channel_jorumopen_collection = models.TextField() # Pipe separated value, e.g. HE - Engineering|HE - Physical Sciences|HE - Social studies
    channel_licence = models.IntegerField() # Normally -1, some are 5 or 6.
    # value="-1" > Licence only for personal use
    # value="5" > Creative Commons licence (BY-NC-SA E and W)
    # value="6" > Creative Commons licence (BY-NC-ND E and W)
    channel_not_used_1 = models.TextField() # EMPTY
    channel_not_used_2 = models.TextField() # EMPTY
    channel_number_of_byncsa = models.IntegerField() # Apparent count of cc licence. Presumably derived from somewhere?
    channel_number_of_items = models.IntegerField() # Apparent count of items, presumably derived from somewhere?
    channel_short_name = models.TextField() # EMPTY
    channel_sort_values = models.TextField() # String to give some form of ordering. e.g.: Apublished, Atitle, Dstartdate
    channel_taxonomies = models.TextField() # NOT USED FOR PODCASTING
    channel_template = models.TextField() # NOT USED FOR PODCASTING
    channel_tpi = models.IntegerField() # Set to 0-3. To Publish In. Matches the publishing list
    # value="0" > Do not include in either podcasts.ox.ac.uk or iTunes U
    # value="1" > Include in podcasts.ox.ac.uk but not in iTunes U
    # value="2" > Include in iTunes U but not in podcasts.ox.ac.uk
    # value="3" > Include in podcasts.ox.ac.uk and also request inclusion in iTunes
    channel_updated = models.CharField(max_length=32) # Date as text.
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11) # SSO username
    description = models.TextField() # e.g. u'Exciting and rare materials to be found in the vast Bodleian Library Collections'
    id = models.IntegerField(primary_key=True)
    link = models.CharField(max_length=256) # Related link - u'http://www.ouls.ox.ac.uk/bodley'
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11) # SSO username
    name = models.CharField(max_length=128) # feedname, e.g. u'bodlib/bodleian_gems-video'
    oxpoints_units = models.TextField() # comma separated values of oxpoint names. Mostly blank
    title = models.CharField(max_length=128) # Title string - u'Gems of the Bodleian Library'
    class Meta:
        db_table = u'rg0_7_channels'

    def __unicode__(self):
        return str(date.strftime(self.modified,"%Y-%m-%d")) + ": Title=" + smart_unicode(self.title)


class Rg07AuthorsBlacklist(models.Model): # There's three records in here, all marked as deleted...
    channel = models.ForeignKey(Rg07Channels)
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    username = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_authors_blacklist'

class Rg07AuthorsWhitelist(models.Model):
    channel = models.ForeignKey(Rg07Channels)
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    username = models.CharField(max_length=11) # SSO Username of an author for a channel?
    class Meta:
        db_table = u'rg0_7_authors_whitelist'

class Rg07AuthorsGroups(models.Model): # Unclear. 71 rows most using group_name to show some sort of retired status.
    channel = models.ForeignKey(Rg07Channels)
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    group_name = models.CharField(max_length=42) # e.g. '/acserv/oucs:-ret' or '/:-'
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_authors_groups'

class Rg07Managers(models.Model):
    channel = models.ForeignKey(Rg07Channels)
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    username = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_managers'

class Rg07Items(models.Model): # > 35,000 items
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    id = models.IntegerField(primary_key=True)
    item_author = models.CharField(max_length=42) # 479 values, All appear to be full text names, presumably of the record's creator
    item_cc = models.IntegerField() # Apple Category Code, again -1, 0, nnn or nnnnnn
    item_channel = models.ForeignKey(Rg07Channels)
    item_checked = models.IntegerField() # Publish to iTunes U. 0=No or 1=Yes. Possible extension of values for a workflow?
    item_content = models.TextField() # Long text, with quite a bit of xHTML markup in it, intended for embedding somewhere.
    item_duration = models.IntegerField() # Estimated time in seconds? This needs to be compared to an actual file analysis.
    item_enclosure_artists = models.TextField() # The messy madness that is the item's speakers/presenters
    item_enclosure_href = models.TextField() # URL to the file. Make contain crap.
    item_enclosure_length = models.TextField() # Large integer values. Size in bytes?
    item_enclosure_release = models.TextField() # two options: '' or 'on'. ????
    item_enclosure_type = models.TextField() # Attempt at mime type description. Again, may have some odd values in.
    item_event_guid = models.TextField() # for events, can be IGNORED
    item_expires = models.CharField(max_length=32) # Datetime as a string e.g. u'2008-05-17T20:00:00+01:00'
    item_guid = models.CharField(max_length=80) # Hopefully the critical GUID for a podcast.
    item_image = models.CharField(max_length=256) # EMPTY
    item_jacs_codes = models.TextField() # csv JACS codes, e.g.: 'F800,C180,F810,F860'.
    item_legal_comments = models.TextField() # Open text. 322 examples
    item_licence = models.IntegerField() # -1, 5 or 6...
    # value="-1" > Licence only for personal use
    # value="5" > Creative Commons licence (BY-NC-SA E and W)
    # value="6" > Creative Commons licence (BY-NC-ND E and W)
    item_link = models.CharField(max_length=256) # Link URL stuff, IGNORE.
    item_not_used_2 = models.CharField(max_length=42) # EMPTY
    item_not_used_3 = models.TextField() # EMPTY
    item_not_used_4 = models.IntegerField() # EMPTY
    item_not_used_5 = models.CharField(max_length=128) # NOT EMPTY, but apparently junk?
    item_other_comments = models.TextField() # Open text. 10 examples
    item_published = models.CharField(max_length=32) # Datetime as text
    item_recording_date = models.TextField() # yyyy-mm-dd in a text field
    item_simple_categories = models.TextField() # csv fields: ,botanic gardens,gardening,medicine,health,botany,nitrogen,sugar,
    item_special_categories = models.TextField() # Looks like events categories... IGNORE, empty
    item_startdate = models.CharField(max_length=32) # Datetime as text
    item_summary = models.TextField() # long description of item, appears to get more use than item_content
    item_title = models.TextField() # Title
    item_transcripts_available = models.IntegerField() # 0,1 or 2. Relates to some outputting that's hardwired into the system
    item_type = models.CharField(max_length=42) # 'html'... it's all html
    item_updated = models.CharField(max_length=32) # Datetime as text
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_items'


class Rg07Administrators(models.Model):
    deleted = models.BooleanField()
    deleter = models.CharField(max_length=11)
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    unit = models.CharField(max_length=42) # OxItems unit code? from OakLDAP?
    username = models.CharField(max_length=11) # SSO Username of an administrator for a channel?
    class Meta:
        db_table = u'rg0_7_administrators'

class Rg07Config(models.Model): # OxItems app config flags and values, IGNORE.
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    name = models.CharField(max_length=42)
    value = models.CharField(max_length=42)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_config'

class Rg07Nicknames(models.Model): # Alternative names for clubs and societies, IGNORE
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    unit = models.CharField(max_length=42)
    nickname = models.CharField(max_length=100)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_nicknames'

class Rg07Events(models.Model): # IGNORE
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    start_date = models.TextField()
    start_month = models.TextField()
    start_year = models.TextField()
    start_hour = models.TextField()
    start_minute = models.TextField()
    end_date = models.TextField()
    end_month = models.TextField()
    end_year = models.TextField()
    end_hour = models.TextField()
    end_minute = models.TextField()
    event_room = models.TextField()
    event_title = models.TextField()
    event_first_speaker_givenname = models.TextField()
    event_first_speaker_lastname = models.TextField()
    event_description = models.TextField()
    item_event_guid = models.TextField()
    deleter = models.TextField()
    event_postcode = models.TextField()
    event_building = models.TextField()
    event_address = models.TextField()
    event_second_speaker_givenname = models.TextField()
    event_second_speaker_lastname = models.TextField()
    event_third_speaker_givenname = models.TextField()
    event_third_speaker_lastname = models.TextField()
    event_other_speaker_details = models.TextField()
    event_series_title = models.TextField()
    event_ticket_availability = models.TextField()
    event_enquiries_email_address = models.TextField()
    event_enquiries_phone_number = models.TextField()
    event_other_comments = models.TextField()
    start_allday = models.TextField()
    end_allday = models.TextField()
    end_duration_length = models.IntegerField()
    end_duration_units = models.TextField()
    transparency = models.TextField()
    event_latitude = models.TextField()
    event_longitude = models.TextField()
    class Meta:
        db_table = u'rg0_7_events'
