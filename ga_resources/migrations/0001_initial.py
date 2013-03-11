# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataResource'
        db.create_table('ga_resources_dataresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('method', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('resource_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('resource_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('resource_irods_env', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_irods.RodsEnvironment'], null=True)),
            ('resource_irods_file', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('time_represented', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('anonymous_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('perform_caching', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cache_ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('data_cache', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True, blank=True)),
            ('bounding_box', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='vector', max_length=24)),
            ('driver', self.gf('django.db.models.fields.CharField')(default='ga_resources.drivers.ogr', max_length=255)),
        ))
        db.send_create_signal('ga_resources', ['DataResource'])

        # Adding M2M table for field access_groups on 'DataResource'
        db.create_table('ga_resources_dataresource_access_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataresource', models.ForeignKey(orm['ga_resources.dataresource'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('ga_resources_dataresource_access_groups', ['dataresource_id', 'group_id'])

        # Adding M2M table for field modify_groups on 'DataResource'
        db.create_table('ga_resources_dataresource_modify_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataresource', models.ForeignKey(orm['ga_resources.dataresource'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('ga_resources_dataresource_modify_groups', ['dataresource_id', 'group_id'])

        # Adding model 'ResourceGroup'
        db.create_table('ga_resources_resourcegroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('is_timeseries', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('min_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('max_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('ga_resources', ['ResourceGroup'])

        # Adding M2M table for field resources on 'ResourceGroup'
        db.create_table('ga_resources_resourcegroup_resources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resourcegroup', models.ForeignKey(orm['ga_resources.resourcegroup'], null=False)),
            ('dataresource', models.ForeignKey(orm['ga_resources.dataresource'], null=False))
        ))
        db.create_unique('ga_resources_resourcegroup_resources', ['resourcegroup_id', 'dataresource_id'])

        # Adding model 'AncillaryResource'
        db.create_table('ga_resources_ancillaryresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('sqlite_cache', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True)),
            ('foreign_key_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('foreign_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('local_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('ga_resources', ['AncillaryResource'])

        # Adding model 'Style'
        db.create_table('ga_resources_style', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('stylesheet_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('ga_resources', ['Style'])

        # Adding model 'StyleTemplate'
        db.create_table('ga_resources_styletemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('stylesheet_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('ga_resources', ['StyleTemplate'])

        # Adding model 'StyleTemplateVariable'
        db.create_table('ga_resources_styletemplatevariable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='attribute', max_length=24)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('ga_resources', ['StyleTemplateVariable'])

        # Adding model 'LayerGroup'
        db.create_table('ga_resources_layergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ga_resources', ['LayerGroup'])

        # Adding model 'WMSLayer'
        db.create_table('ga_resources_wmslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_wms_layer', to=orm['ga_resources.Style'])),
        ))
        db.send_create_signal('ga_resources', ['WMSLayer'])

        # Adding M2M table for field styles on 'WMSLayer'
        db.create_table('ga_resources_wmslayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wmslayer', models.ForeignKey(orm['ga_resources.wmslayer'], null=False)),
            ('style', models.ForeignKey(orm['ga_resources.style'], null=False))
        ))
        db.create_unique('ga_resources_wmslayer_styles', ['wmslayer_id', 'style_id'])

        # Adding model 'WMVSLayer'
        db.create_table('ga_resources_wmvslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_wmvs_layer', to=orm['ga_resources.Style'])),
        ))
        db.send_create_signal('ga_resources', ['WMVSLayer'])

        # Adding M2M table for field styles on 'WMVSLayer'
        db.create_table('ga_resources_wmvslayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wmvslayer', models.ForeignKey(orm['ga_resources.wmvslayer'], null=False)),
            ('style', models.ForeignKey(orm['ga_resources.style'], null=False))
        ))
        db.create_unique('ga_resources_wmvslayer_styles', ['wmvslayer_id', 'style_id'])

        # Adding model 'WMTSLayer'
        db.create_table('ga_resources_wmtslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_wmts_layer', to=orm['ga_resources.Style'])),
        ))
        db.send_create_signal('ga_resources', ['WMTSLayer'])

        # Adding M2M table for field styles on 'WMTSLayer'
        db.create_table('ga_resources_wmtslayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wmtslayer', models.ForeignKey(orm['ga_resources.wmtslayer'], null=False)),
            ('style', models.ForeignKey(orm['ga_resources.style'], null=False))
        ))
        db.create_unique('ga_resources_wmtslayer_styles', ['wmtslayer_id', 'style_id'])

        # Adding model 'WFSLayer'
        db.create_table('ga_resources_wfslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
        ))
        db.send_create_signal('ga_resources', ['WFSLayer'])

        # Adding model 'WCSLayer'
        db.create_table('ga_resources_wcslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
        ))
        db.send_create_signal('ga_resources', ['WCSLayer'])

        # Adding model 'SOSLayer'
        db.create_table('ga_resources_soslayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.LayerGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
        ))
        db.send_create_signal('ga_resources', ['SOSLayer'])


    def backwards(self, orm):
        # Deleting model 'DataResource'
        db.delete_table('ga_resources_dataresource')

        # Removing M2M table for field access_groups on 'DataResource'
        db.delete_table('ga_resources_dataresource_access_groups')

        # Removing M2M table for field modify_groups on 'DataResource'
        db.delete_table('ga_resources_dataresource_modify_groups')

        # Deleting model 'ResourceGroup'
        db.delete_table('ga_resources_resourcegroup')

        # Removing M2M table for field resources on 'ResourceGroup'
        db.delete_table('ga_resources_resourcegroup_resources')

        # Deleting model 'AncillaryResource'
        db.delete_table('ga_resources_ancillaryresource')

        # Deleting model 'Style'
        db.delete_table('ga_resources_style')

        # Deleting model 'StyleTemplate'
        db.delete_table('ga_resources_styletemplate')

        # Deleting model 'StyleTemplateVariable'
        db.delete_table('ga_resources_styletemplatevariable')

        # Deleting model 'LayerGroup'
        db.delete_table('ga_resources_layergroup')

        # Deleting model 'WMSLayer'
        db.delete_table('ga_resources_wmslayer')

        # Removing M2M table for field styles on 'WMSLayer'
        db.delete_table('ga_resources_wmslayer_styles')

        # Deleting model 'WMVSLayer'
        db.delete_table('ga_resources_wmvslayer')

        # Removing M2M table for field styles on 'WMVSLayer'
        db.delete_table('ga_resources_wmvslayer_styles')

        # Deleting model 'WMTSLayer'
        db.delete_table('ga_resources_wmtslayer')

        # Removing M2M table for field styles on 'WMTSLayer'
        db.delete_table('ga_resources_wmtslayer_styles')

        # Deleting model 'WFSLayer'
        db.delete_table('ga_resources_wfslayer')

        # Deleting model 'WCSLayer'
        db.delete_table('ga_resources_wcslayer')

        # Deleting model 'SOSLayer'
        db.delete_table('ga_resources_soslayer')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ga_irods.rodsenvironment': {
            'Meta': {'object_name': 'RodsEnvironment'},
            'auth': ('django.db.models.fields.TextField', [], {}),
            'cwd': ('django.db.models.fields.TextField', [], {}),
            'def_res': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'home_coll': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zone': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.ancillaryresource': {
            'Meta': {'object_name': 'AncillaryResource'},
            'foreign_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'foreign_key_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sqlite_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True'})
        },
        'ga_resources.dataresource': {
            'Meta': {'object_name': 'DataResource'},
            'access_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'data_resource_access_groups'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'anonymous_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True'}),
            'cache_ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'data_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.ogr'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'vector'", 'max_length': '24'}),
            'method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'modify_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'data_resource_modify_groups'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'perform_caching': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'resource_irods_env': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_irods.RodsEnvironment']", 'null': 'True'}),
            'resource_irods_file': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'time_represented': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'})
        },
        'ga_resources.layergroup': {
            'Meta': {'object_name': 'LayerGroup'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'ga_resources.resourcegroup': {
            'Meta': {'object_name': 'ResourceGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_timeseries': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'min_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'resources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_resources.DataResource']", 'symmetrical': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'ga_resources.soslayer': {
            'Meta': {'object_name': 'SOSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.style': {
            'Meta': {'object_name': 'Style'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'stylesheet_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'ga_resources.styletemplate': {
            'Meta': {'object_name': 'StyleTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'stylesheet_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'ga_resources.styletemplatevariable': {
            'Meta': {'object_name': 'StyleTemplateVariable'},
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'attribute'", 'max_length': '24'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'ga_resources.wcslayer': {
            'Meta': {'object_name': 'WCSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.wfslayer': {
            'Meta': {'object_name': 'WFSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.wmslayer': {
            'Meta': {'object_name': 'WMSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_wms_layer'", 'to': "orm['ga_resources.Style']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'wms_layer'", 'symmetrical': 'False', 'to': "orm['ga_resources.Style']"}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.wmtslayer': {
            'Meta': {'object_name': 'WMTSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_wmts_layer'", 'to': "orm['ga_resources.Style']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'wmts_layer'", 'symmetrical': 'False', 'to': "orm['ga_resources.Style']"}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.wmvslayer': {
            'Meta': {'object_name': 'WMVSLayer'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_wmvs_layer'", 'to': "orm['ga_resources.Style']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.LayerGroup']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'wmvs_layer'", 'symmetrical': 'False', 'to': "orm['ga_resources.Style']"}),
            'title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['ga_resources']