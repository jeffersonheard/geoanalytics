# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'StyleTemplateVariable'
        db.delete_table(u'ga_resources_styletemplatevariable')

        # Deleting model 'StyleTemplate'
        db.delete_table(u'ga_resources_styletemplate')

        # Deleting model 'AnimatedResourceLayer'
        db.delete_table(u'ga_resources_animatedresourcelayer')

        # Removing M2M table for field styles on 'AnimatedResourceLayer'
        db.delete_table('ga_resources_animatedresourcelayer_styles')

        # Adding model 'Verb'
        db.create_table(u'ga_resources_verb', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('verb', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal(u'ga_resources', ['Verb'])

        # Adding model 'KeyValue'
        db.create_table(u'ga_resources_keyvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ga_resources', ['KeyValue'])

        # Adding model 'SemanticRelationship'
        db.create_table(u'ga_resources_semanticrelationship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subject', to=orm['pages.Page'])),
            ('obj', self.gf('django.db.models.fields.related.ForeignKey')(related_name='obj', to=orm['pages.Page'])),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
        ))
        db.send_create_signal(u'ga_resources', ['SemanticRelationship'])

        # Deleting field 'DataResource.time_represented'
        db.delete_column(u'ga_resources_dataresource', 'time_represented')

        # Adding field 'DataResource.metadata_url'
        db.add_column(u'ga_resources_dataresource', 'metadata_url',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataResource.metadata_xml'
        db.add_column(u'ga_resources_dataresource', 'metadata_xml',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'StyleTemplateVariable'
        db.create_table(u'ga_resources_styletemplatevariable', (
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='attribute', max_length=24)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'ga_resources', ['StyleTemplateVariable'])

        # Adding model 'StyleTemplate'
        db.create_table(u'ga_resources_styletemplate', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('stylesheet', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ga_resources', ['StyleTemplate'])

        # Adding model 'AnimatedResourceLayer'
        db.create_table(u'ga_resources_animatedresourcelayer', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_for_animation', to=orm['ga_resources.Style'])),
            ('cache_seconds', self.gf('django.db.models.fields.PositiveIntegerField')(default=60)),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
        ))
        db.send_create_signal(u'ga_resources', ['AnimatedResourceLayer'])

        # Adding M2M table for field styles on 'AnimatedResourceLayer'
        db.create_table(u'ga_resources_animatedresourcelayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('animatedresourcelayer', models.ForeignKey(orm[u'ga_resources.animatedresourcelayer'], null=False)),
            ('style', models.ForeignKey(orm[u'ga_resources.style'], null=False))
        ))
        db.create_unique(u'ga_resources_animatedresourcelayer_styles', ['animatedresourcelayer_id', 'style_id'])

        # Deleting model 'Verb'
        db.delete_table(u'ga_resources_verb')

        # Deleting model 'KeyValue'
        db.delete_table(u'ga_resources_keyvalue')

        # Deleting model 'SemanticRelationship'
        db.delete_table(u'ga_resources_semanticrelationship')

        # Adding field 'DataResource.time_represented'
        db.add_column(u'ga_resources_dataresource', 'time_represented',
                      self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, db_index=True),
                      keep_default=False)

        # Deleting field 'DataResource.metadata_url'
        db.delete_column(u'ga_resources_dataresource', 'metadata_url')

        # Deleting field 'DataResource.metadata_xml'
        db.delete_column(u'ga_resources_dataresource', 'metadata_xml')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ga_resources.ancillaryresource': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AncillaryResource', '_ormbases': [u'pages.Page']},
            'foreign_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'foreign_key_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            'local_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sqlite_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True'})
        },
        u'ga_resources.catalogpage': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'CatalogPage', '_ormbases': [u'pages.Page']},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'ga_resources.dataresource': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'DataResource', '_ormbases': [u'pages.Page']},
            'cache_ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10', 'null': 'True', 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.shapefile'", 'max_length': '255'}),
            'metadata_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'metadata_xml': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'perform_caching': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resource_config': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'spatial_metadata': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ga_resources.SpatialMetadata']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'ga_resources.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.Page']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ga_resources.orderedresource': {
            'Meta': {'object_name': 'OrderedResource'},
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.ResourceGroup']"})
        },
        u'ga_resources.renderedlayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RenderedLayer', '_ormbases': [u'pages.Page']},
            'cache_seconds': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
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
        u'ga_resources.semanticrelationship': {
            'Meta': {'object_name': 'SemanticRelationship'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'obj'", 'to': u"orm['pages.Page']"}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subject'", 'to': u"orm['pages.Page']"}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        },
        u'ga_resources.spatialmetadata': {
            'Meta': {'object_name': 'SpatialMetadata'},
            'bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'native_bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True'}),
            'native_srs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'three_d': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ga_resources.style': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Style', '_ormbases': [u'pages.Page']},
            'legend': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'legend_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'legend_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet': ('django.db.models.fields.TextField', [], {})
        },
        u'ga_resources.verb': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Verb', '_ormbases': [u'pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'verb': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
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