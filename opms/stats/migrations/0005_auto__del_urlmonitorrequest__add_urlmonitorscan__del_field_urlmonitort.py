# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'URLMonitorRequest'
        db.delete_table('stats_urlmonitorrequest')

        # Adding model 'URLMonitorScan'
        db.create_table('stats_urlmonitorscan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.URLMonitorTask'])),
            ('url', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.URLMonitorTarget'])),
            ('iteration', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('status_code', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('ttfb', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('ttlb', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('time_of_request', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('stats', ['URLMonitorScan'])

        # Deleting field 'URLMonitorTask.url'
        db.delete_column('stats_urlmonitortask', 'url_id')

        # Deleting field 'URLMonitorTask.iterations'
        db.delete_column('stats_urlmonitortask', 'iterations')

        # Deleting field 'URLMonitorTask.time_of_scan'
        db.delete_column('stats_urlmonitortask', 'time_of_scan')

        # Adding field 'URLMonitorTask.completed'
        db.add_column('stats_urlmonitortask', 'completed', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'URLMonitorRequest'
        db.create_table('stats_urlmonitorrequest', (
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.URLMonitorTask'])),
            ('iteration', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('time_of_request', self.gf('django.db.models.fields.DateTimeField')()),
            ('ttlb', self.gf('django.db.models.fields.FloatField')()),
            ('ttfb', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('stats', ['URLMonitorRequest'])

        # Deleting model 'URLMonitorScan'
        db.delete_table('stats_urlmonitorscan')

        # User chose to not deal with backwards NULL issues for 'URLMonitorTask.url'
        raise RuntimeError("Cannot reverse this migration. 'URLMonitorTask.url' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'URLMonitorTask.iterations'
        raise RuntimeError("Cannot reverse this migration. 'URLMonitorTask.iterations' and its values cannot be restored.")

        # Adding field 'URLMonitorTask.time_of_scan'
        db.add_column('stats_urlmonitortask', 'time_of_scan', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Deleting field 'URLMonitorTask.completed'
        db.delete_column('stats_urlmonitortask', 'completed')


    models = {
        'ffm.file': {
            'Meta': {'object_name': 'File'},
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'function': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['ffm.FileFunction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ffm.Item']", 'null': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'ffm.filefunction': {
            'Meta': {'object_name': 'FileFunction'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'ffm.item': {
            'Meta': {'object_name': 'Item'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'guid': ('django.db.models.fields.CharField', [], {'default': "'OPMS-item:8f15c8f2-e106-40c9-87a5-4cc0c2241231'", 'max_length': '100'}),
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
        },
        'stats.browsecount': {
            'Meta': {'object_name': 'BrowseCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'guid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.BrowseGUID']", 'null': 'True'}),
            'handle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.BrowseHandle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.BrowsePath']"}),
            'summary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Summary']"})
        },
        'stats.browseguid': {
            'Meta': {'object_name': 'BrowseGUID'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.browsehandle': {
            'Meta': {'object_name': 'BrowseHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.browsepath': {
            'Meta': {'object_name': 'BrowsePath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'path': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'stats.clientsoftware': {
            'Meta': {'object_name': 'ClientSoftware'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'summary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Summary']"}),
            'version_major': ('django.db.models.fields.IntegerField', [], {}),
            'version_minor': ('django.db.models.fields.IntegerField', [], {})
        },
        'stats.filerequest': {
            'Meta': {'object_name': 'FileRequest'},
            'argument_string': ('django.db.models.fields.TextField', [], {}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.File']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'uri_string': ('django.db.models.fields.TextField', [], {})
        },
        'stats.logentry': {
            'Meta': {'object_name': 'LogEntry'},
            'file_request': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.FileRequest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'referer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Referer']"}),
            'remote_logname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'remote_rdns': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Rdns']"}),
            'remote_user': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Server']"}),
            'size_of_response': ('django.db.models.fields.BigIntegerField', [], {}),
            'status_code': ('django.db.models.fields.IntegerField', [], {}),
            'time_of_request': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'tracking': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['stats.Tracking']", 'symmetrical': 'False'}),
            'user_agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.UserAgent']"})
        },
        'stats.logfile': {
            'Meta': {'object_name': 'LogFile'},
            'file_name': ('django.db.models.fields.TextField', [], {}),
            'file_path': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'stats.os': {
            'Meta': {'object_name': 'OS'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'stats.previewcount': {
            'Meta': {'object_name': 'PreviewCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'guid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.PreviewGUID']"}),
            'handle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.PreviewHandle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.PreviewPath']"}),
            'summary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Summary']"})
        },
        'stats.previewguid': {
            'Meta': {'object_name': 'PreviewGUID'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.previewhandle': {
            'Meta': {'object_name': 'PreviewHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.previewpath': {
            'Meta': {'object_name': 'PreviewPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'path': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'stats.rdns': {
            'Meta': {'object_name': 'Rdns'},
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'resolved_name': ('django.db.models.fields.TextField', [], {})
        },
        'stats.referer': {
            'Meta': {'object_name': 'Referer'},
            'full_string': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'stats.server': {
            'Meta': {'object_name': 'Server'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'port': ('django.db.models.fields.IntegerField', [], {})
        },
        'stats.summary': {
            'Meta': {'object_name': 'Summary'},
            'browse': ('django.db.models.fields.IntegerField', [], {}),
            'download_ios': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'download_preview': ('django.db.models.fields.IntegerField', [], {}),
            'download_preview_ios': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'download_track': ('django.db.models.fields.IntegerField', [], {}),
            'download_tracks': ('django.db.models.fields.IntegerField', [], {}),
            'edit_files': ('django.db.models.fields.IntegerField', [], {}),
            'edit_page': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'logout': ('django.db.models.fields.IntegerField', [], {}),
            'not_listed': ('django.db.models.fields.IntegerField', [], {}),
            'search_results_page': ('django.db.models.fields.IntegerField', [], {}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subscription': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_enclosure': ('django.db.models.fields.IntegerField', [], {}),
            'subscription_feed': ('django.db.models.fields.IntegerField', [], {}),
            'total_track_downloads': ('django.db.models.fields.IntegerField', [], {}),
            'upload': ('django.db.models.fields.IntegerField', [], {}),
            'week_ending': ('django.db.models.fields.DateField', [], {'db_index': 'True'})
        },
        'stats.trackcount': {
            'Meta': {'object_name': 'TrackCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'guid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.TrackGUID']"}),
            'handle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.TrackHandle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.TrackPath']"}),
            'summary': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.Summary']"})
        },
        'stats.trackguid': {
            'Meta': {'object_name': 'TrackGUID'},
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ffm.File']", 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.trackhandle': {
            'Meta': {'object_name': 'TrackHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.tracking': {
            'Meta': {'object_name': 'Tracking'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_string': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'value_string': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'stats.trackpath': {
            'Meta': {'object_name': 'TrackPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'path': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'stats.ua': {
            'Meta': {'object_name': 'UA'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'stats.urlmonitorscan': {
            'Meta': {'object_name': 'URLMonitorScan'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iteration': ('django.db.models.fields.SmallIntegerField', [], {}),
            'status_code': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.URLMonitorTask']"}),
            'time_of_request': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'ttfb': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'ttlb': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.URLMonitorTarget']"})
        },
        'stats.urlmonitortarget': {
            'Meta': {'object_name': 'URLMonitorTarget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'stats.urlmonitortask': {
            'Meta': {'object_name': 'URLMonitorTask'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "'No Comment Set'", 'max_length': '200'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'stats.useragent': {
            'Meta': {'object_name': 'UserAgent'},
            'full_string': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'os': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.OS']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ua': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.UA']", 'null': 'True'})
        }
    }

    complete_apps = ['stats']
