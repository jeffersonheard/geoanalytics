# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataResource'
        db.create_table(u'ga_resources_dataresource', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('method', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('resource_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('resource_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('resource_irods_file', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True, blank=True)),
            ('time_represented', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('perform_caching', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cache_ttl', self.gf('django.db.models.fields.PositiveIntegerField')(default=10, null=True, blank=True)),
            ('data_cache', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True, blank=True)),
            ('bounding_box', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='vector', max_length=24)),
            ('driver', self.gf('django.db.models.fields.CharField')(default='ga_resources.drivers.ogr', max_length=255)),
        ))
        db.send_create_signal(u'ga_resources', ['DataResource'])

        # Adding model 'OrderedResource'
        db.create_table(u'ga_resources_orderedresource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.ResourceGroup'])),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'ga_resources', ['OrderedResource'])

        # Adding model 'ResourceGroup'
        db.create_table(u'ga_resources_resourcegroup', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('is_timeseries', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('min_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('max_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'ga_resources', ['ResourceGroup'])

        # Adding model 'AncillaryResource'
        db.create_table(u'ga_resources_ancillaryresource', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('resource_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('sqlite_cache', self.gf('django.db.models.fields.FilePathField')(max_length=100, null=True)),
            ('foreign_key_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('foreign_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('local_key', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'ga_resources', ['AncillaryResource'])

        # Adding model 'Style'
        db.create_table(u'ga_resources_style', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('legend', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('stylesheet_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'ga_resources', ['Style'])

        # Adding model 'StyleTemplate'
        db.create_table(u'ga_resources_styletemplate', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('stylesheet', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'ga_resources', ['StyleTemplate'])

        # Adding model 'StyleTemplateVariable'
        db.create_table(u'ga_resources_styletemplatevariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='attribute', max_length=24)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'ga_resources', ['StyleTemplateVariable'])

        # Adding model 'RenderedLayer'
        db.create_table(u'ga_resources_renderedlayer', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_for_layer', to=orm['ga_resources.Style'])),
        ))
        db.send_create_signal(u'ga_resources', ['RenderedLayer'])

        # Adding M2M table for field styles on 'RenderedLayer'
        db.create_table(u'ga_resources_renderedlayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('renderedlayer', models.ForeignKey(orm[u'ga_resources.renderedlayer'], null=False)),
            ('style', models.ForeignKey(orm[u'ga_resources.style'], null=False))
        ))
        db.create_unique(u'ga_resources_renderedlayer_styles', ['renderedlayer_id', 'style_id'])

        # Adding model 'RasterResourceLayer'
        db.create_table(u'ga_resources_rasterresourcelayer', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('styled_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.RenderedLayer'], null=True, blank=True)),
        ))
        db.send_create_signal(u'ga_resources', ['RasterResourceLayer'])

        # Adding model 'VectorResourceLayer'
        db.create_table(u'ga_resources_vectorresourcelayer', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('styled_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.RenderedLayer'], null=True, blank=True)),
        ))
        db.send_create_signal(u'ga_resources', ['VectorResourceLayer'])

        # Adding model 'AnimatedResourceLayer'
        db.create_table(u'ga_resources_animatedresourcelayer', (
            (u'page_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pages.Page'], unique=True, primary_key=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('data_resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ga_resources.DataResource'])),
            ('default_style', self.gf('django.db.models.fields.related.ForeignKey')(related_name='default_for_animation', to=orm['ga_resources.Style'])),
        ))
        db.send_create_signal(u'ga_resources', ['AnimatedResourceLayer'])

        # Adding M2M table for field styles on 'AnimatedResourceLayer'
        db.create_table(u'ga_resources_animatedresourcelayer_styles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('animatedresourcelayer', models.ForeignKey(orm[u'ga_resources.animatedresourcelayer'], null=False)),
            ('style', models.ForeignKey(orm[u'ga_resources.style'], null=False))
        ))
        db.create_unique(u'ga_resources_animatedresourcelayer_styles', ['animatedresourcelayer_id', 'style_id'])


    def backwards(self, orm):
        # Deleting model 'DataResource'
        db.delete_table(u'ga_resources_dataresource')

        # Deleting model 'OrderedResource'
        db.delete_table(u'ga_resources_orderedresource')

        # Deleting model 'ResourceGroup'
        db.delete_table(u'ga_resources_resourcegroup')

        # Deleting model 'AncillaryResource'
        db.delete_table(u'ga_resources_ancillaryresource')

        # Deleting model 'Style'
        db.delete_table(u'ga_resources_style')

        # Deleting model 'StyleTemplate'
        db.delete_table(u'ga_resources_styletemplate')

        # Deleting model 'StyleTemplateVariable'
        db.delete_table(u'ga_resources_styletemplatevariable')

        # Deleting model 'RenderedLayer'
        db.delete_table(u'ga_resources_renderedlayer')

        # Removing M2M table for field styles on 'RenderedLayer'
        db.delete_table('ga_resources_renderedlayer_styles')

        # Deleting model 'RasterResourceLayer'
        db.delete_table(u'ga_resources_rasterresourcelayer')

        # Deleting model 'VectorResourceLayer'
        db.delete_table(u'ga_resources_vectorresourcelayer')

        # Deleting model 'AnimatedResourceLayer'
        db.delete_table(u'ga_resources_animatedresourcelayer')

        # Removing M2M table for field styles on 'AnimatedResourceLayer'
        db.delete_table('ga_resources_animatedresourcelayer_styles')


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
        u'ga_irods.rodsenvironment': {
            'Meta': {'object_name': 'RodsEnvironment'},
            'auth': ('django.db.models.fields.TextField', [], {}),
            'cwd': ('django.db.models.fields.TextField', [], {}),
            'def_res': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'home_coll': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zone': ('django.db.models.fields.TextField', [], {})
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
        u'ga_resources.animatedresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'AnimatedResourceLayer', '_ormbases': [u'pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_for_animation'", 'to': u"orm['ga_resources.Style']"}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ga_resources.Style']", 'symmetrical': 'False'})
        },
        u'ga_resources.dataresource': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'DataResource', '_ormbases': [u'pages.Page']},
            'bounding_box': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'cache_ttl': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10', 'null': 'True', 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_cache': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'driver': ('django.db.models.fields.CharField', [], {'default': "'ga_resources.drivers.ogr'", 'max_length': '255'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'vector'", 'max_length': '24'}),
            'method': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'perform_caching': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resource_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'resource_irods_env': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_irods.RodsEnvironment']", 'null': 'True', 'blank': 'True'}),
            'resource_irods_file': ('django.db.models.fields.FilePathField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'time_represented': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'ga_resources.orderedresource': {
            'Meta': {'object_name': 'OrderedResource'},
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.ResourceGroup']"})
        },
        u'ga_resources.rasterresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RasterResourceLayer', '_ormbases': [u'pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styled_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.RenderedLayer']", 'null': 'True', 'blank': 'True'})
        },
        u'ga_resources.renderedlayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'RenderedLayer', '_ormbases': [u'pages.Page']},
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
        u'ga_resources.style': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Style', '_ormbases': [u'pages.Page']},
            'legend': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'ga_resources.styletemplate': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'StyleTemplate', '_ormbases': [u'pages.Page']},
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'stylesheet': ('django.db.models.fields.TextField', [], {})
        },
        u'ga_resources.styletemplatevariable': {
            'Meta': {'object_name': 'StyleTemplateVariable'},
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'attribute'", 'max_length': '24'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'ga_resources.vectorresourcelayer': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'VectorResourceLayer', '_ormbases': [u'pages.Page']},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'data_resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.DataResource']"}),
            u'page_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pages.Page']", 'unique': 'True', 'primary_key': 'True'}),
            'styled_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ga_resources.RenderedLayer']", 'null': 'True', 'blank': 'True'})
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
