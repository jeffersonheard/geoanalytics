# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Verb'
        db.delete_table(u'ga_resources_verb')

        # Deleting model 'KeyValue'
        db.delete_table(u'ga_resources_keyvalue')

        # Deleting model 'SemanticRelationship'
        db.delete_table(u'ga_resources_semanticrelationship')

        # Deleting model 'SpatialMetadata'
        db.delete_table(u'ga_resources_spatialmetadata')

        # Deleting field 'DataResource.spatial_metadata'
        db.delete_column(u'ga_resources_dataresource', 'spatial_metadata_id')

        # Adding field 'DataResource.native_bounding_box'
        db.add_column(u'ga_resources_dataresource', 'native_bounding_box',
                      self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True),
                      keep_default=False)

        # Adding field 'DataResource.bounding_box'
        db.add_column(u'ga_resources_dataresource', 'bounding_box',
                      self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.three_d'
        db.add_column(u'ga_resources_dataresource', 'three_d',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'DataResource.native_srs'
        db.add_column(u'ga_resources_dataresource', 'native_srs',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.public'
        db.add_column(u'ga_resources_dataresource', 'public',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'DataResource.owner'
        db.add_column(u'ga_resources_dataresource', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'DataResource.edit_users'
        db.add_column(u'ga_resources_dataresource', 'edit_users',
                      self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default='', max_length=2048, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.view_users'
        db.add_column(u'ga_resources_dataresource', 'view_users',
                      self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default='', max_length=2048, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.edit_groups'
        db.add_column(u'ga_resources_dataresource', 'edit_groups',
                      self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default='', max_length=2048, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.view_groups'
        db.add_column(u'ga_resources_dataresource', 'view_groups',
                      self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default='', max_length=2048, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Verb'
        db.create_table(u'ga_resources_verb', (
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'ga_resources', ['Verb'])

        # Adding model 'KeyValue'
        db.create_table(u'ga_resources_keyvalue', (
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page'])),
        ))
        db.send_create_signal(u'ga_resources', ['KeyValue'])

        # Adding model 'SemanticRelationship'
        db.create_table(u'ga_resources_semanticrelationship', (
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('obj', self.gf('django.db.models.fields.related.ForeignKey')(related_name='obj', to=orm['pages.Page'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subject', to=orm['pages.Page'])),
        ))
        db.send_create_signal(u'ga_resources', ['SemanticRelationship'])

        # Adding model 'SpatialMetadata'
        db.create_table(u'ga_resources_spatialmetadata', (
            ('native_bounding_box', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True)),
            ('native_srs', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bounding_box', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('three_d', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'ga_resources', ['SpatialMetadata'])

        # Adding field 'DataResource.spatial_metadata'
        db.add_column(u'ga_resources_dataresource', 'spatial_metadata',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ga_resources.SpatialMetadata'], unique=True, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'DataResource.native_bounding_box'
        db.delete_column(u'ga_resources_dataresource', 'native_bounding_box')

        # Deleting field 'DataResource.bounding_box'
        db.delete_column(u'ga_resources_dataresource', 'bounding_box')

        # Deleting field 'DataResource.three_d'
        db.delete_column(u'ga_resources_dataresource', 'three_d')

        # Deleting field 'DataResource.native_srs'
        db.delete_column(u'ga_resources_dataresource', 'native_srs')

        # Deleting field 'DataResource.public'
        db.delete_column(u'ga_resources_dataresource', 'public')

        # Deleting field 'DataResource.owner'
        db.delete_column(u'ga_resources_dataresource', 'owner_id')

        # Deleting field 'DataResource.edit_users'
        db.delete_column(u'ga_resources_dataresource', 'edit_users')

        # Deleting field 'DataResource.view_users'
        db.delete_column(u'ga_resources_dataresource', 'view_users')

        # Deleting field 'DataResource.edit_groups'
        db.delete_column(u'ga_resources_dataresource', 'edit_groups')

        # Deleting field 'DataResource.view_groups'
        db.delete_column(u'ga_resources_dataresource', 'view_groups')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ga_resources.catalogpage': {
            'Meta': {'ordering': "['title']", 'object_name': 'CatalogPage', '_ormbases': [u'pages.Page']},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'ga_resources.dataresource': {
            'Meta': {'ordering': "['title']", 'object_name': 'DataResource', '_ormbases': [u'pages.Page']},
            'big': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.spatialite'", 'max_length': '255'}),
            'edit_groups': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '2048', 'blank': 'True'}),
            'edit_users': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '2048', 'blank': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_refresh': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'md5sum': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'metadata_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'metadata_xml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'native_bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True'}),
            'native_srs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'next_refresh': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'refresh_every': ('timedelta.fields.TimedeltaField', [], {'null': 'True', 'blank': 'True'}),
            'resource_config': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'three_d': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'view_groups': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '2048', 'blank': 'True'}),
            'view_users': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '2048', 'blank': 'True'})
        },
        u'ga_resources.orderedresource': {
            'Meta': {'object_name': 'OrderedResource'},
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.ResourceGroup']"})
        },
        u'ga_resources.relatedresource': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RelatedResource', '_ormbases': [u'pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.related.excel'", 'max_length': '255'}),
            'foreign_key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'foreign_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            'how': ('django.db.models.fields.CharField', [], {'default': "'left'", 'max_length': '8'}),
            'key_transform': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'left_index': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'local_key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'right_index': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ga_resources.renderedlayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RenderedLayer', '_ormbases': [u'pages.Page']},
            'cache_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            'default_class': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '255'}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_for_layer'", 'to': u"orm['ga_resources.Style']"}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ga_resources.Style']", 'symmetrical': 'False'})
        },
        u'ga_resources.resourcegroup': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'ResourceGroup', '_ormbases': [u'pages.Page']},
            'is_timeseries': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'min_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'resources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ga_resources.DataResource']", 'symmetrical': 'False', 'through': u"orm['ga_resources.OrderedResource']", 'blank': 'True'})
        },
        u'ga_resources.style': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Style', '_ormbases': [u'pages.Page']},
            'legend': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'legend_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'legend_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet': ('django.db.models.fields.TextField', [], {})
        },
        u'generic.assignedkeyword': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AssignedKeyword'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': u"orm['generic.Keyword']"}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        u'generic.keyword': {
            'Meta': {'object_name': 'Keyword'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pages.page': {
            'Meta': {'ordering': "('titles',)", 'object_name': 'Page'},
            '_meta_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'gen_description': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_menus': ('mezzanine.pages.fields.MenusField', [], {'default': '(1, 2, 3)', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'in_sitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': u"orm['generic.AssignedKeyword']", 'frozen_by_south': 'True'}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['pages.Page']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'titles': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['ga_resources']