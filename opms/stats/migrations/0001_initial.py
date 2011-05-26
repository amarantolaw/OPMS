# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LogFile'
        db.create_table('stats_logfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('file_name', self.gf('django.db.models.fields.TextField')()),
            ('file_path', self.gf('django.db.models.fields.TextField')()),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('stats', ['LogFile'])

        # Adding model 'Summary'
        db.create_table('stats_summary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('week_ending', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('browse', self.gf('django.db.models.fields.IntegerField')()),
            ('download_preview', self.gf('django.db.models.fields.IntegerField')()),
            ('download_preview_ios', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('download_track', self.gf('django.db.models.fields.IntegerField')()),
            ('download_tracks', self.gf('django.db.models.fields.IntegerField')()),
            ('download_ios', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('edit_files', self.gf('django.db.models.fields.IntegerField')()),
            ('edit_page', self.gf('django.db.models.fields.IntegerField')()),
            ('logout', self.gf('django.db.models.fields.IntegerField')()),
            ('search_results_page', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription_enclosure', self.gf('django.db.models.fields.IntegerField')()),
            ('subscription_feed', self.gf('django.db.models.fields.IntegerField')()),
            ('upload', self.gf('django.db.models.fields.IntegerField')()),
            ('not_listed', self.gf('django.db.models.fields.IntegerField')()),
            ('total_track_downloads', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('stats', ['Summary'])

        # Adding model 'ClientSoftware'
        db.create_table('stats_clientsoftware', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Summary'])),
            ('platform', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('version_major', self.gf('django.db.models.fields.IntegerField')()),
            ('version_minor', self.gf('django.db.models.fields.IntegerField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('stats', ['ClientSoftware'])

        # Adding model 'TrackPath'
        db.create_table('stats_trackpath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['TrackPath'])

        # Adding model 'TrackHandle'
        db.create_table('stats_trackhandle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.BigIntegerField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['TrackHandle'])

        # Adding model 'TrackGUID'
        db.create_table('stats_trackguid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.File'], null=True)),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['TrackGUID'])

        # Adding model 'TrackCount'
        db.create_table('stats_trackcount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Summary'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.TrackPath'])),
            ('handle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.TrackHandle'])),
            ('guid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.TrackGUID'])),
        ))
        db.send_create_signal('stats', ['TrackCount'])

        # Adding model 'BrowsePath'
        db.create_table('stats_browsepath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['BrowsePath'])

        # Adding model 'BrowseHandle'
        db.create_table('stats_browsehandle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.BigIntegerField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['BrowseHandle'])

        # Adding model 'BrowseGUID'
        db.create_table('stats_browseguid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['BrowseGUID'])

        # Adding model 'BrowseCount'
        db.create_table('stats_browsecount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Summary'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.BrowsePath'])),
            ('handle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.BrowseHandle'])),
            ('guid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.BrowseGUID'], null=True)),
        ))
        db.send_create_signal('stats', ['BrowseCount'])

        # Adding model 'PreviewPath'
        db.create_table('stats_previewpath', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['PreviewPath'])

        # Adding model 'PreviewHandle'
        db.create_table('stats_previewhandle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.BigIntegerField')()),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['PreviewHandle'])

        # Adding model 'PreviewGUID'
        db.create_table('stats_previewguid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
        ))
        db.send_create_signal('stats', ['PreviewGUID'])

        # Adding model 'PreviewCount'
        db.create_table('stats_previewcount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Summary'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.PreviewPath'])),
            ('handle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.PreviewHandle'])),
            ('guid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.PreviewGUID'])),
        ))
        db.send_create_signal('stats', ['PreviewCount'])

        # Adding model 'Rdns'
        db.create_table('stats_rdns', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('resolved_name', self.gf('django.db.models.fields.TextField')()),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('stats', ['Rdns'])

        # Adding model 'OS'
        db.create_table('stats_os', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('family', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('stats', ['OS'])

        # Adding model 'UA'
        db.create_table('stats_ua', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('family', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('stats', ['UA'])

        # Adding model 'UserAgent'
        db.create_table('stats_useragent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_string', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('os', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.OS'], null=True)),
            ('ua', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.UA'], null=True)),
        ))
        db.send_create_signal('stats', ['UserAgent'])

        # Adding model 'Referer'
        db.create_table('stats_referer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_string', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('stats', ['Referer'])

        # Adding model 'FileRequest'
        db.create_table('stats_filerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('uri_string', self.gf('django.db.models.fields.TextField')()),
            ('argument_string', self.gf('django.db.models.fields.TextField')()),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ffm.File'], null=True)),
        ))
        db.send_create_signal('stats', ['FileRequest'])

        # Adding model 'Tracking'
        db.create_table('stats_tracking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key_string', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value_string', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('stats', ['Tracking'])

        # Adding model 'Server'
        db.create_table('stats_server', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('stats', ['Server'])

        # Adding model 'LogEntry'
        db.create_table('stats_logentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('logfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.LogFile'])),
            ('time_of_request', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Server'])),
            ('remote_logname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('remote_user', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('remote_rdns', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Rdns'])),
            ('status_code', self.gf('django.db.models.fields.IntegerField')()),
            ('size_of_response', self.gf('django.db.models.fields.BigIntegerField')()),
            ('file_request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.FileRequest'])),
            ('referer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.Referer'])),
            ('user_agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['stats.UserAgent'])),
        ))
        db.send_create_signal('stats', ['LogEntry'])

        # Adding M2M table for field tracking on 'LogEntry'
        db.create_table('stats_logentry_tracking', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('logentry', models.ForeignKey(orm['stats.logentry'], null=False)),
            ('tracking', models.ForeignKey(orm['stats.tracking'], null=False))
        ))
        db.create_unique('stats_logentry_tracking', ['logentry_id', 'tracking_id'])


    def backwards(self, orm):
        
        # Deleting model 'LogFile'
        db.delete_table('stats_logfile')

        # Deleting model 'Summary'
        db.delete_table('stats_summary')

        # Deleting model 'ClientSoftware'
        db.delete_table('stats_clientsoftware')

        # Deleting model 'TrackPath'
        db.delete_table('stats_trackpath')

        # Deleting model 'TrackHandle'
        db.delete_table('stats_trackhandle')

        # Deleting model 'TrackGUID'
        db.delete_table('stats_trackguid')

        # Deleting model 'TrackCount'
        db.delete_table('stats_trackcount')

        # Deleting model 'BrowsePath'
        db.delete_table('stats_browsepath')

        # Deleting model 'BrowseHandle'
        db.delete_table('stats_browsehandle')

        # Deleting model 'BrowseGUID'
        db.delete_table('stats_browseguid')

        # Deleting model 'BrowseCount'
        db.delete_table('stats_browsecount')

        # Deleting model 'PreviewPath'
        db.delete_table('stats_previewpath')

        # Deleting model 'PreviewHandle'
        db.delete_table('stats_previewhandle')

        # Deleting model 'PreviewGUID'
        db.delete_table('stats_previewguid')

        # Deleting model 'PreviewCount'
        db.delete_table('stats_previewcount')

        # Deleting model 'Rdns'
        db.delete_table('stats_rdns')

        # Deleting model 'OS'
        db.delete_table('stats_os')

        # Deleting model 'UA'
        db.delete_table('stats_ua')

        # Deleting model 'UserAgent'
        db.delete_table('stats_useragent')

        # Deleting model 'Referer'
        db.delete_table('stats_referer')

        # Deleting model 'FileRequest'
        db.delete_table('stats_filerequest')

        # Deleting model 'Tracking'
        db.delete_table('stats_tracking')

        # Deleting model 'Server'
        db.delete_table('stats_server')

        # Deleting model 'LogEntry'
        db.delete_table('stats_logentry')

        # Removing M2M table for field tracking on 'LogEntry'
        db.delete_table('stats_logentry_tracking')


    models = {
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
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.browsehandle': {
            'Meta': {'object_name': 'BrowseHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.browsepath': {
            'Meta': {'object_name': 'BrowsePath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'path': ('django.db.models.fields.TextField', [], {})
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
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.previewhandle': {
            'Meta': {'object_name': 'PreviewHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.previewpath': {
            'Meta': {'object_name': 'PreviewPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"}),
            'path': ('django.db.models.fields.TextField', [], {})
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
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.LogFile']"})
        },
        'stats.trackhandle': {
            'Meta': {'object_name': 'TrackHandle'},
            'handle': ('django.db.models.fields.BigIntegerField', [], {}),
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
            'path': ('django.db.models.fields.TextField', [], {})
        },
        'stats.ua': {
            'Meta': {'object_name': 'UA'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
