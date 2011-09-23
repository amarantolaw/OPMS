# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field jacs_codes on 'FileInFeed'
        db.create_table('ffm_fileinfeed_jacs_codes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fileinfeed', models.ForeignKey(orm['ffm.fileinfeed'], null=False)),
            ('tag', models.ForeignKey(orm['ffm.tag'], null=False))
        ))
        db.create_unique('ffm_fileinfeed_jacs_codes', ['fileinfeed_id', 'tag_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field jacs_codes on 'FileInFeed'
        db.delete_table('ffm_fileinfeed_jacs_codes')


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
            'destinations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Destination']", 'null': 'True', 'through': "orm['ffm.FeedDestination']", 'symmetrical': 'False'}),
            'feed_group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.FeedGroup']"}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.File']", 'null': 'True', 'through': "orm['ffm.FileInFeed']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'ffm.feeddestination': {
            'Meta': {'object_name': 'FeedDestination'},
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Destination']"}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-feed:876de5d2-0265-4f21-a36d-04d4cb6c8d57'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'withhold': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'ffm.feedgroup': {
            'Meta': {'object_name': 'FeedGroup'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Link']", 'null': 'True', 'symmetrical': 'False'}),
            'owning_unit': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.Unit']"}),
            'publish_start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'publish_stop': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'Untitled Feed'", 'max_length': '150'})
        },
        'ffm.file': {
            'Meta': {'object_name': 'File'},
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.FileFunction']"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-file:9190d6bc-e485-426e-a7f8-ae8647278cd9'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ffm.Item']", 'null': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '50'}),
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
            'jacs_codes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ffm.Tag']", 'null': 'True', 'symmetrical': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'withhold': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'ffm.item': {
            'Meta': {'object_name': 'Item'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-item:5f826b0c-0463-44e2-a761-a600d0b8f0a4'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.Licence']"}),
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
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed Link'", 'max_length': '100'}),
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
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed Tag'", 'max_length': '200'})
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
