# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ItuScanLog'
        db.create_table('stats_ituscanlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('starting_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('stats', ['ItuScanLog'])

        # Deleting field 'ItuItem.updated'
        db.delete_column('stats_ituitem', 'updated')

        # Adding field 'ItuItem.scanlog'
        db.add_column('stats_ituitem', 'scanlog', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['stats.ItuScanLog']), keep_default=False)

        # Deleting field 'ItuSeries.updated'
        db.delete_column('stats_ituseries', 'updated')

        # Adding field 'ItuSeries.scanlog'
        db.add_column('stats_ituseries', 'scanlog', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['stats.ItuScanLog']), keep_default=False)

        # Adding field 'ItuCollectionChart.scanlog'
        db.add_column('stats_itucollectionchart', 'scanlog', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['stats.ItuScanLog']), keep_default=False)

        # Adding field 'ItuDownloadChart.scanlog'
        db.add_column('stats_itudownloadchart', 'scanlog', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['stats.ItuScanLog']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'ItuScanLog'
        db.delete_table('stats_ituscanlog')

        # User chose to not deal with backwards NULL issues for 'ItuItem.updated'
        raise RuntimeError("Cannot reverse this migration. 'ItuItem.updated' and its values cannot be restored.")

        # Deleting field 'ItuItem.scanlog'
        db.delete_column('stats_ituitem', 'scanlog_id')

        # User chose to not deal with backwards NULL issues for 'ItuSeries.updated'
        raise RuntimeError("Cannot reverse this migration. 'ItuSeries.updated' and its values cannot be restored.")

        # Deleting field 'ItuSeries.scanlog'
        db.delete_column('stats_ituseries', 'scanlog_id')

        # Deleting field 'ItuCollectionChart.scanlog'
        db.delete_column('stats_itucollectionchart', 'scanlog_id')

        # Deleting field 'ItuDownloadChart.scanlog'
        db.delete_column('stats_itudownloadchart', 'scanlog_id')


    models = {
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'uri_string': ('django.db.models.fields.TextField', [], {})
        },
        'stats.itucollectionchart': {
            'Meta': {'object_name': 'ItuCollectionChart'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {}),
            'scanlog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuScanLog']"}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuSeries']"})
        },
        'stats.itudownloadchart': {
            'Meta': {'object_name': 'ItuDownloadChart'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuItem']"}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {}),
            'scanlog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuScanLog']"})
        },
        'stats.itugenre': {
            'Meta': {'object_name': 'ItuGenre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itu_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'stats.ituinstitution': {
            'Meta': {'object_name': 'ItuInstitution'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itu_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'stats.ituitem': {
            'Meta': {'object_name': 'ItuItem'},
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'explicit': ('django.db.models.fields.IntegerField', [], {}),
            'feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'file_extension': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuGenre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuInstitution']"}),
            'itu_id': ('django.db.models.fields.IntegerField', [], {}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'long_description': ('django.db.models.fields.TextField', [], {}),
            'missing': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'playlist_id': ('django.db.models.fields.IntegerField', [], {}),
            'playlist_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'popularity': ('django.db.models.fields.FloatField', [], {}),
            'preview_length': ('django.db.models.fields.IntegerField', [], {}),
            'preview_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {}),
            'scanlog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuScanLog']"}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuSeries']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'stats.ituscanlog': {
            'Meta': {'object_name': 'ItuScanLog'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'starting_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'stats.ituseries': {
            'Meta': {'object_name': 'ItuSeries'},
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuGenre']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img170': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'img75': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuInstitution']"}),
            'itu_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'last_modified': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'missing': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scanlog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['stats.ItuScanLog']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'})
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
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
