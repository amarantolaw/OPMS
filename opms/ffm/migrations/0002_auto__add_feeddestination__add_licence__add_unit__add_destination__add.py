# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeedDestination'
        db.create_table('ffm_feeddestination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Feed'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Destination'])),
            ('guid', self.gf('django.db.models.fields.CharField')(default='OPMS-feed:550ff7c6-7d44-4ef3-857c-3d378af25428', max_length=100)),
            ('withhold', self.gf('django.db.models.fields.IntegerField')(default=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('ffm', ['FeedDestination'])

        # Adding model 'Licence'
        db.create_table('ffm_licence', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.File'], null=True)),
        ))
        db.send_create_signal('ffm', ['Licence'])

        # Adding model 'Unit'
        db.create_table('ffm_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('oxpoints_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('ffm', ['Unit'])

        # Adding model 'Destination'
        db.create_table('ffm_destination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('ffm', ['Destination'])

        # Adding model 'Link'
        db.create_table('ffm_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('name', self.gf('django.db.models.fields.TextField')(default='Unnamed Link')),
            ('url', self.gf('django.db.models.fields.URLField')(default='http://www.ox.ac.uk/', max_length=200)),
        ))
        db.send_create_signal('ffm', ['Link'])

        # Adding model 'FileFunction'
        db.create_table('ffm_filefunction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('category', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=20)),
        ))
        db.send_create_signal('ffm', ['FileFunction'])

        # Adding model 'TagGroup'
        db.create_table('ffm_taggroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('ffm', ['TagGroup'])

        # Deleting field 'Item.license'
        db.delete_column('ffm_item', 'license')

        # Deleting field 'Item.publish_status'
        db.delete_column('ffm_item', 'publish_status')

        # Deleting field 'Item.publish_date'
        db.delete_column('ffm_item', 'publish_date')

        # Adding field 'Item.internal_comments'
        db.add_column('ffm_item', 'internal_comments', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Item.last_updated'
        db.add_column('ffm_item', 'last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Item.publish_start'
        db.add_column('ffm_item', 'publish_start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)

        # Adding field 'Item.publish_stop'
        db.add_column('ffm_item', 'publish_stop', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding M2M table for field links on 'Item'
        db.create_table('ffm_item_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('item', models.ForeignKey(orm['ffm.item'], null=False)),
            ('link', models.ForeignKey(orm['ffm.link'], null=False))
        ))
        db.create_unique('ffm_item_links', ['item_id', 'link_id'])

        # Changing field 'Item.description'
        db.alter_column('ffm_item', 'description', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Item.owning_unit' to match new field type.
        db.rename_column('ffm_item', 'owning_unit', 'owning_unit_id')
        # Changing field 'Item.owning_unit'
        db.alter_column('ffm_item', 'owning_unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Unit']))

        # Adding index on 'Item', fields ['owning_unit']
        db.create_index('ffm_item', ['owning_unit_id'])

        # Changing field 'Item.title'
        db.alter_column('ffm_item', 'title', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Item.guid'
        db.alter_column('ffm_item', 'guid', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'Role.role'
        db.alter_column('ffm_role', 'role', self.gf('django.db.models.fields.CharField')(max_length=20))

        # Adding index on 'Role', fields ['role']
        db.create_index('ffm_role', ['role'])

        # Deleting field 'File.function'
        db.delete_column('ffm_file', 'function')

        # Changing field 'File.mimetype'
        db.alter_column('ffm_file', 'mimetype', self.gf('django.db.models.fields.TextField')())

        # Changing field 'File.url'
        db.alter_column('ffm_file', 'url', self.gf('django.db.models.fields.URLField')(default='http://127.0.0.1/#', max_length=200))

        # Changing field 'File.guid'
        db.alter_column('ffm_file', 'guid', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Deleting field 'FileInFeed.jacs_code'
        db.delete_column('ffm_fileinfeed', 'jacs_code')

        # Adding field 'FileInFeed.alternative_title'
        db.add_column('ffm_fileinfeed', 'alternative_title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True), keep_default=False)

        # Adding field 'FileInFeed.withhold'
        db.add_column('ffm_fileinfeed', 'withhold', self.gf('django.db.models.fields.IntegerField')(default=100), keep_default=False)

        # Adding field 'FileInFeed.jacs_codes'
        db.add_column('ffm_fileinfeed', 'jacs_codes', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Tag'], null=True), keep_default=False)

        # Changing field 'FileInFeed.itunesu_category'
        db.alter_column('ffm_fileinfeed', 'itunesu_category', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Deleting field 'Person.name'
        db.delete_column('ffm_person', 'name')

        # Adding field 'Person.titles'
        db.add_column('ffm_person', 'titles', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Person.first_name'
        db.add_column('ffm_person', 'first_name', self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=50), keep_default=False)

        # Adding field 'Person.middle_names'
        db.add_column('ffm_person', 'middle_names', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Person.last_name'
        db.add_column('ffm_person', 'last_name', self.gf('django.db.models.fields.CharField')(default='Person', max_length=50), keep_default=False)

        # Adding field 'Person.additional_information'
        db.add_column('ffm_person', 'additional_information', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Person.email'
        db.add_column('ffm_person', 'email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True), keep_default=False)

        # Adding field 'Tag.group'
        db.add_column('ffm_tag', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['ffm.TagGroup']), keep_default=False)

        # Deleting field 'Feed.source_url'
        db.delete_column('ffm_feed', 'source_url')

        # Deleting field 'Feed.source_service'
        db.delete_column('ffm_feed', 'source_service')

        # Deleting field 'Feed.feedart'
        db.delete_column('ffm_feed', 'feedart_id')

        # Deleting field 'Feed.publish_date'
        db.delete_column('ffm_feed', 'publish_date')

        # Adding field 'Feed.internal_comments'
        db.add_column('ffm_feed', 'internal_comments', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Feed.publish_start'
        db.add_column('ffm_feed', 'publish_start', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now), keep_default=False)

        # Adding field 'Feed.publish_stop'
        db.add_column('ffm_feed', 'publish_stop', self.gf('django.db.models.fields.DateField')(null=True), keep_default=False)

        # Adding M2M table for field links on 'Feed'
        db.create_table('ffm_feed_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feed', models.ForeignKey(orm['ffm.feed'], null=False)),
            ('link', models.ForeignKey(orm['ffm.link'], null=False))
        ))
        db.create_unique('ffm_feed_links', ['feed_id', 'link_id'])

        # Adding M2M table for field tags on 'Feed'
        db.create_table('ffm_feed_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feed', models.ForeignKey(orm['ffm.feed'], null=False)),
            ('tag', models.ForeignKey(orm['ffm.tag'], null=False))
        ))
        db.create_unique('ffm_feed_tags', ['feed_id', 'tag_id'])

        # Changing field 'Feed.description'
        db.alter_column('ffm_feed', 'description', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Feed.owning_unit' to match new field type.
        db.rename_column('ffm_feed', 'owning_unit', 'owning_unit_id')
        # Changing field 'Feed.owning_unit'
        db.alter_column('ffm_feed', 'owning_unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Unit']))

        # Adding index on 'Feed', fields ['owning_unit']
        db.create_index('ffm_feed', ['owning_unit_id'])

        # Changing field 'Feed.title'
        db.alter_column('ffm_feed', 'title', self.gf('django.db.models.fields.CharField')(default='Untitled Feed', max_length=150))


    def backwards(self, orm):
        
        # Removing index on 'Feed', fields ['owning_unit']
        db.delete_index('ffm_feed', ['owning_unit_id'])

        # Removing index on 'Role', fields ['role']
        db.delete_index('ffm_role', ['role'])

        # Removing index on 'Item', fields ['owning_unit']
        db.delete_index('ffm_item', ['owning_unit_id'])

        # Deleting model 'FeedDestination'
        db.delete_table('ffm_feeddestination')

        # Deleting model 'Licence'
        db.delete_table('ffm_licence')

        # Deleting model 'Unit'
        db.delete_table('ffm_unit')

        # Deleting model 'Destination'
        db.delete_table('ffm_destination')

        # Deleting model 'Link'
        db.delete_table('ffm_link')

        # Deleting model 'FileFunction'
        db.delete_table('ffm_filefunction')

        # Deleting model 'TagGroup'
        db.delete_table('ffm_taggroup')

        # Adding field 'Item.license'
        db.add_column('ffm_item', 'license', self.gf('django.db.models.fields.URLField')(max_length=200, null=True), keep_default=False)

        # Adding field 'Item.publish_status'
        db.add_column('ffm_item', 'publish_status', self.gf('django.db.models.fields.TextField')(default='published'), keep_default=False)

        # Adding field 'Item.publish_date'
        db.add_column('ffm_item', 'publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Deleting field 'Item.internal_comments'
        db.delete_column('ffm_item', 'internal_comments')

        # Deleting field 'Item.last_updated'
        db.delete_column('ffm_item', 'last_updated')

        # Deleting field 'Item.publish_start'
        db.delete_column('ffm_item', 'publish_start')

        # Deleting field 'Item.publish_stop'
        db.delete_column('ffm_item', 'publish_stop')

        # Removing M2M table for field links on 'Item'
        db.delete_table('ffm_item_links')

        # Changing field 'Item.description'
        db.alter_column('ffm_item', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Item.owning_unit' to match new field type.
        db.rename_column('ffm_item', 'owning_unit_id', 'owning_unit')
        # Changing field 'Item.owning_unit'
        db.alter_column('ffm_item', 'owning_unit', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Item.title'
        db.alter_column('ffm_item', 'title', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Item.guid'
        db.alter_column('ffm_item', 'guid', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Role.role'
        db.alter_column('ffm_role', 'role', self.gf('django.db.models.fields.TextField')())

        # Adding field 'File.function'
        db.add_column('ffm_file', 'function', self.gf('django.db.models.fields.TextField')(default='Unknown'), keep_default=False)

        # Changing field 'File.mimetype'
        db.alter_column('ffm_file', 'mimetype', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'File.url'
        db.alter_column('ffm_file', 'url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'File.guid'
        db.alter_column('ffm_file', 'guid', self.gf('django.db.models.fields.TextField')(null=True))

        # Adding field 'FileInFeed.jacs_code'
        db.add_column('ffm_fileinfeed', 'jacs_code', self.gf('django.db.models.fields.TextField')(null=True), keep_default=False)

        # Deleting field 'FileInFeed.alternative_title'
        db.delete_column('ffm_fileinfeed', 'alternative_title')

        # Deleting field 'FileInFeed.withhold'
        db.delete_column('ffm_fileinfeed', 'withhold')

        # Deleting field 'FileInFeed.jacs_codes'
        db.delete_column('ffm_fileinfeed', 'jacs_codes_id')

        # Changing field 'FileInFeed.itunesu_category'
        db.alter_column('ffm_fileinfeed', 'itunesu_category', self.gf('django.db.models.fields.IntegerField')())

        # User chose to not deal with backwards NULL issues for 'Person.name'
        raise RuntimeError("Cannot reverse this migration. 'Person.name' and its values cannot be restored.")

        # Deleting field 'Person.titles'
        db.delete_column('ffm_person', 'titles')

        # Deleting field 'Person.first_name'
        db.delete_column('ffm_person', 'first_name')

        # Deleting field 'Person.middle_names'
        db.delete_column('ffm_person', 'middle_names')

        # Deleting field 'Person.last_name'
        db.delete_column('ffm_person', 'last_name')

        # Deleting field 'Person.additional_information'
        db.delete_column('ffm_person', 'additional_information')

        # Deleting field 'Person.email'
        db.delete_column('ffm_person', 'email')

        # Deleting field 'Tag.group'
        db.delete_column('ffm_tag', 'group_id')

        # User chose to not deal with backwards NULL issues for 'Feed.source_url'
        raise RuntimeError("Cannot reverse this migration. 'Feed.source_url' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Feed.source_service'
        raise RuntimeError("Cannot reverse this migration. 'Feed.source_service' and its values cannot be restored.")

        # Adding field 'Feed.feedart'
        db.add_column('ffm_feed', 'feedart', self.gf('django.db.models.fields.related.ForeignKey')(related_name='albumartfor', null=True, to=orm['ffm.File']), keep_default=False)

        # Adding field 'Feed.publish_date'
        db.add_column('ffm_feed', 'publish_date', self.gf('django.db.models.fields.DateField')(null=True), keep_default=False)

        # Deleting field 'Feed.internal_comments'
        db.delete_column('ffm_feed', 'internal_comments')

        # Deleting field 'Feed.publish_start'
        db.delete_column('ffm_feed', 'publish_start')

        # Deleting field 'Feed.publish_stop'
        db.delete_column('ffm_feed', 'publish_stop')

        # Removing M2M table for field links on 'Feed'
        db.delete_table('ffm_feed_links')

        # Removing M2M table for field tags on 'Feed'
        db.delete_table('ffm_feed_tags')

        # Changing field 'Feed.description'
        db.alter_column('ffm_feed', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Feed.owning_unit' to match new field type.
        db.rename_column('ffm_feed', 'owning_unit_id', 'owning_unit')
        # Changing field 'Feed.owning_unit'
        db.alter_column('ffm_feed', 'owning_unit', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Feed.title'
        db.alter_column('ffm_feed', 'title', self.gf('django.db.models.fields.TextField')(null=True))


    models = {
        'ffm.destination': {
            'Meta': {'object_name': 'Destination'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'ffm.feed': {
            'Meta': {'object_name': 'Feed'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'destinations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Destination']", 'null': 'True', 'through': "orm['ffm.FeedDestination']", 'symmetrical': 'False'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.File']", 'null': 'True', 'through': "orm['ffm.FileInFeed']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Link']", 'null': 'True', 'symmetrical': 'False'}),
            'owning_unit': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.Unit']"}),
            'publish_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'publish_stop': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ffm.feeddestination': {
            'Meta': {'object_name': 'FeedDestination'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Destination']"}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-feed:ac4c2044-6fcf-4539-a3b6-15ac5c60a5c0'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'withhold': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'ffm.file': {
            'Meta': {'object_name': 'File'},
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-file:6d97f88f-752d-41fc-bf04-bddcbacba267'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Item']"}),
            'mimetype': ('django.db.models.fields.TextField', [], {'default': "'unknown'"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'ffm.filefunction': {
            'Meta': {'object_name': 'FileFunction'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ffm.fileinfeed': {
            'Meta': {'object_name': 'FileInFeed'},
            'alternative_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Feed']"}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itunesu_category': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'jacs_codes': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Tag']", 'null': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'withhold': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'ffm.item': {
            'Meta': {'object_name': 'Item'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Link']", 'null': 'True', 'symmetrical': 'False'}),
            'owning_unit': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.Unit']"}),
            'people': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Person']", 'through': "orm['ffm.Role']", 'symmetrical': 'False'}),
            'publish_start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'publish_stop': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'recording_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Untitled Item'", 'max_length': '256'})
        },
        'ffm.licence': {
            'Meta': {'object_name': 'Licence'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.File']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
        },
        'ffm.link': {
            'Meta': {'object_name': 'Link'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "'Unnamed Link'"}),
            'url': ('django.db.models.fields.URLField', [], {'default': "'http://www.ox.ac.uk/'", 'max_length': '200'})
        },
        'ffm.person': {
            'Meta': {'object_name': 'Person'},
            'additional_information': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "'Person'", 'max_length': '50'}),
            'middle_names': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'titles': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        'ffm.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Item']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Person']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        'ffm.tag': {
            'Meta': {'object_name': 'Tag'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.TagGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "'Unnamed Tag'"})
        },
        'ffm.taggroup': {
            'Meta': {'object_name': 'TagGroup'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ffm.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'oxpoints_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['ffm']
