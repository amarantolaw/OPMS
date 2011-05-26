# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Tag'
        db.create_table('ffm_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ffm', ['Tag'])

        # Adding model 'Person'
        db.create_table('ffm_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ffm', ['Person'])

        # Adding model 'Item'
        db.create_table('ffm_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('guid', self.gf('django.db.models.fields.TextField')()),
            ('license', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('recording_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('owning_unit', self.gf('django.db.models.fields.IntegerField')()),
            ('publish_status', self.gf('django.db.models.fields.TextField')(default='published')),
        ))
        db.send_create_signal('ffm', ['Item'])

        # Adding M2M table for field tags on 'Item'
        db.create_table('ffm_item_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('item', models.ForeignKey(orm['ffm.item'], null=False)),
            ('tag', models.ForeignKey(orm['ffm.tag'], null=False))
        ))
        db.create_unique('ffm_item_tags', ['item_id', 'tag_id'])

        # Adding model 'Role'
        db.create_table('ffm_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Person'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Item'])),
            ('role', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ffm', ['Role'])

        # Adding model 'File'
        db.create_table('ffm_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Item'])),
            ('guid', self.gf('django.db.models.fields.TextField')(null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('mimetype', self.gf('django.db.models.fields.TextField')(null=True)),
            ('function', self.gf('django.db.models.fields.TextField')(default='Unknown')),
        ))
        db.send_create_signal('ffm', ['File'])

        # Adding model 'Feed'
        db.create_table('ffm_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('title', self.gf('django.db.models.fields.TextField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owning_unit', self.gf('django.db.models.fields.IntegerField')()),
            ('publish_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('source_service', self.gf('django.db.models.fields.TextField')()),
            ('feedart', self.gf('django.db.models.fields.related.ForeignKey')(related_name='albumartfor', null=True, to=orm['ffm.File'])),
        ))
        db.send_create_signal('ffm', ['Feed'])

        # Adding model 'FileInFeed'
        db.create_table('ffm_fileinfeed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.File'])),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.Feed'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('itunesu_category', self.gf('django.db.models.fields.IntegerField')(default=112)),
            ('jacs_code', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('ffm', ['FileInFeed'])


    def backwards(self, orm):
        
        # Deleting model 'Tag'
        db.delete_table('ffm_tag')

        # Deleting model 'Person'
        db.delete_table('ffm_person')

        # Deleting model 'Item'
        db.delete_table('ffm_item')

        # Removing M2M table for field tags on 'Item'
        db.delete_table('ffm_item_tags')

        # Deleting model 'Role'
        db.delete_table('ffm_role')

        # Deleting model 'File'
        db.delete_table('ffm_file')

        # Deleting model 'Feed'
        db.delete_table('ffm_feed')

        # Deleting model 'FileInFeed'
        db.delete_table('ffm_fileinfeed')


    models = {
        'ffm.feed': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Feed'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'feedart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'albumartfor'", 'null': 'True', 'to': "orm['ffm.File']"}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.File']", 'through': "orm['ffm.FileInFeed']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owning_unit': ('django.db.models.fields.IntegerField', [], {}),
            'publish_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'source_service': ('django.db.models.fields.TextField', [], {}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'ffm.file': {
            'Meta': {'object_name': 'File'},
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'function': ('django.db.models.fields.TextField', [], {'default': "'Unknown'"}),
            'guid': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Item']"}),
            'mimetype': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
        },
        'ffm.fileinfeed': {
            'Meta': {'object_name': 'FileInFeed'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Feed']"}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.File']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itunesu_category': ('django.db.models.fields.IntegerField', [], {'default': '112'}),
            'jacs_code': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'ffm.item': {
            'Meta': {'object_name': 'Item'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'guid': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'owning_unit': ('django.db.models.fields.IntegerField', [], {}),
            'people': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Person']", 'through': "orm['ffm.Role']", 'symmetrical': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'publish_status': ('django.db.models.fields.TextField', [], {'default': "'published'"}),
            'recording_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Tag']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'ffm.person': {
            'Meta': {'object_name': 'Person'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'ffm.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Item']"}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Person']"}),
            'role': ('django.db.models.fields.TextField', [], {})
        },
        'ffm.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['ffm']
