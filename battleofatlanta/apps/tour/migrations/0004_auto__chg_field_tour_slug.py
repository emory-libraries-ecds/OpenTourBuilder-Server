# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Tour.slug'
        db.alter_column('tour_tour', 'slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name'))

    def backwards(self, orm):

        # Changing field 'Tour.slug'
        db.alter_column('tour_tour', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))

    models = {
        'tour.tour': {
            'Meta': {'object_name': 'Tour'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        'tour.tourstop': {
            'Meta': {'ordering': "['position']", 'object_name': 'TourStop'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'tour': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tour.Tour']"})
        }
    }

    complete_apps = ['tour']