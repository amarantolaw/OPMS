# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from django.utils.encoding import smart_str, smart_unicode
from datetime import date

class Rg07Channels(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    channel_guid = models.CharField(max_length=80)
    channel_updated = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    link = models.CharField(max_length=256)
    description = models.TextField()
    channel_image = models.CharField(max_length=256)
    deleter = models.CharField(max_length=11)
    channel_emailaddress = models.CharField(max_length=256)
    channel_taxonomies = models.TextField()
    channel_categories = models.TextField()
    channel_template = models.TextField()
    channel_not_used_1 = models.TextField()
    channel_not_used_2 = models.TextField()
    oxpoints_units = models.TextField()
    channel_short_name = models.TextField()
    channel_cc = models.IntegerField()
    channel_tpi = models.IntegerField()
    channel_sort_values = models.TextField()
    channel_licence = models.IntegerField()
    channel_number_of_items = models.IntegerField()
    channel_number_of_byncsa = models.IntegerField()
    channel_jorumopen_collection = models.TextField()
    class Meta:
        db_table = u'rg0_7_channels'

    def __unicode__(self):
        return str(date.strftime(self.modified,"%Y-%m-%d")) + ": Title=" + str(self.title)


class Rg07AuthorsBlacklist(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    username = models.CharField(max_length=11)
    channel = models.ForeignKey(Rg07Channels)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_authors_blacklist'

class Rg07Administrators(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    unit = models.CharField(max_length=42)
    username = models.CharField(max_length=11)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_administrators'

class Rg07Config(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    name = models.CharField(max_length=42)
    value = models.CharField(max_length=42)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_config'

class Rg07AuthorsWhitelist(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    username = models.CharField(max_length=11)
    channel = models.ForeignKey(Rg07Channels)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_authors_whitelist'

class Rg07Nicknames(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    unit = models.CharField(max_length=42)
    nickname = models.CharField(max_length=100)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_nicknames'

class Rg07AuthorsGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    group_name = models.CharField(max_length=42)
    channel = models.ForeignKey(Rg07Channels)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_authors_groups'


class Rg07Events(models.Model):
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

class Rg07Items(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    item_guid = models.CharField(max_length=80)
    item_author = models.CharField(max_length=42)
    item_channel = models.ForeignKey(Rg07Channels)
    item_not_used_5 = models.CharField(max_length=128)
    item_link = models.CharField(max_length=256)
    item_summary = models.TextField()
    item_content = models.TextField()
    item_type = models.CharField(max_length=42)
    item_not_used_2 = models.CharField(max_length=42)
    item_published = models.CharField(max_length=32)
    item_updated = models.CharField(max_length=32)
    item_expires = models.CharField(max_length=32)
    deleter = models.CharField(max_length=11)
    item_startdate = models.CharField(max_length=32)
    item_image = models.CharField(max_length=256)
    item_not_used_3 = models.TextField()
    item_special_categories = models.TextField()
    item_simple_categories = models.TextField()
    item_not_used_4 = models.IntegerField()
    item_event_guid = models.TextField()
    item_enclosure_href = models.TextField()
    item_enclosure_type = models.TextField()
    item_enclosure_length = models.TextField()
    item_title = models.TextField()
    item_enclosure_artists = models.TextField()
    item_enclosure_release = models.TextField()
    item_cc = models.IntegerField()
    item_duration = models.IntegerField()
    item_checked = models.IntegerField()
    item_licence = models.IntegerField()
    item_jacs_codes = models.TextField()
    item_recording_date = models.TextField()
    item_transcripts_available = models.IntegerField()
    item_legal_comments = models.TextField()
    item_other_comments = models.TextField()
    class Meta:
        db_table = u'rg0_7_items'

class Rg07Managers(models.Model):
    id = models.IntegerField(primary_key=True)
    modified = models.DateTimeField()
    modifier = models.CharField(max_length=11)
    deleted = models.BooleanField()
    username = models.CharField(max_length=11)
    channel = models.ForeignKey(Rg07Channels)
    deleter = models.CharField(max_length=11)
    class Meta:
        db_table = u'rg0_7_managers'
