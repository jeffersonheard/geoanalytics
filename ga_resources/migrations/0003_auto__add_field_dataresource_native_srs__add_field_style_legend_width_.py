# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataResource.native_srs'
        db.add_column('ga_resources_dataresource', 'native_srs',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.legend_width'
        db.add_column('ga_resources_style', 'legend_width',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Style.legend_height'
        db.add_column('ga_resources_style', 'legend_height',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DataResource.native_srs'
        db.delete_column('ga_resources_dataresource', 'native_srs')

        # Deleting field 'Style.legend_width'
        db.delete_column('ga_resources_style', 'legend_width')

        # Deleting field 'Style.legend_height'
        db.delete_column('ga_resources_style', 'legend_height')


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
            'Meta': {'ordering': "('_order',)", 'object_name': 'AncillaryResource', '_ormbases': ['pages.Page']},
            'foreign_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'foreign_key_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'local_key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'sqlite_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True'})
        },
        'ga_resources.animatedresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AnimatedResourceLayer', '_ormbases': ['pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_for_animation'", 'to': "orm['ga_resources.Style']"}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_resources.Style']", 'symmetrical': 'False'})
        },
        'ga_resources.dataresource': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'DataResource', '_ormbases': ['pages.Page']},
            'bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'cache_ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10', 'null': 'True', 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.ogr'", 'max_length': '255'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'vector'", 'max_length': '24'}),
            'method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'native_srs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'perform_caching': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'resource_irods_env': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_irods.RodsEnvironment']", 'null': 'True', 'blank': 'True'}),
            'resource_irods_file': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'time_represented': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'ga_resources.orderedresource': {
            'Meta': {'object_name': 'OrderedResource'},
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.ResourceGroup']"})
        },
        'ga_resources.rasterresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RasterResourceLayer', '_ormbases': ['pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styled_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.RenderedLayer']", 'null': 'True', 'blank': 'True'})
        },
        'ga_resources.renderedlayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RenderedLayer', '_ormbases': ['pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_for_layer'", 'to': "orm['ga_resources.Style']"}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_resources.Style']", 'symmetrical': 'False'})
        },
        'ga_resources.resourcegroup': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'ResourceGroup', '_ormbases': ['pages.Page']},
            'is_timeseries': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'min_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'resources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ga_resources.DataResource']", 'symmetrical': 'False', 'through': "orm['ga_resources.OrderedResource']", 'blank': 'True'})
        },
        'ga_resources.style': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Style', '_ormbases': ['pages.Page']},
            'legend': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'legend_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'legend_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.styletemplate': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'StyleTemplate', '_ormbases': ['pages.Page']},
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet': ('django.db.models.fields.TextField', [], {})
        },
        'ga_resources.styletemplatevariable': {
            'Meta': {'object_name': 'StyleTemplateVariable'},
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'attribute'", 'max_length': '24'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'ga_resources.vectorresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'VectorResourceLayer', '_ormbases': ['pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.DataResource']"}),
            'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styled_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ga_resources.RenderedLayer']", 'null': 'True', 'blank': 'True'})
        },
        'generic.assignedkeyword': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AssignedKeyword'},
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['generic.Keyword']"}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        'generic.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'pages.page': {
            'Meta': {'ordering': "('titles',)", 'object_name': 'Page'},
            '_meta_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            '_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'gen_description': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_menus': ('mezzanine.pages.fields.MenusField', [], {'default': '(1, 2, 3)', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'in_sitemap': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('mezzanine.generic.fields.KeywordsField', [], {'object_id_field': "'object_pk'", 'to': "orm['generic.AssignedKeyword']", 'frozen_by_south': 'True'}),
            'keywords_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'titles': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['ga_resources']