# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Admin'
        db.create_table('astra_admin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('net_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('reg_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('account_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('canvas_id', self.gf('django.db.models.fields.IntegerField')()),
            ('added_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('provisioned_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('deleted_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('is_deleted', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('queue_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
        ))
        db.send_create_signal('astra', ['Admin'])

        # Adding model 'Account'
        db.create_table('astra_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('canvas_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('sis_id', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True, blank=True)),
            ('account_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('account_short_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('account_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('added_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_deleted', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('is_blessed_for_course_request', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('queue_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
        ))
        db.send_create_signal('astra', ['Account'])


    def backwards(self, orm):
        # Deleting model 'Admin'
        db.delete_table('astra_admin')

        # Deleting model 'Account'
        db.delete_table('astra_account')


    models = {
        'astra.account': {
            'Meta': {'object_name': 'Account'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'account_short_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'account_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'added_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'canvas_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blessed_for_course_request': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'queue_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sis_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'astra.admin': {
            'Meta': {'object_name': 'Admin'},
            'account_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'added_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'canvas_id': ('django.db.models.fields.IntegerField', [], {}),
            'deleted_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'net_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'provisioned_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'queue_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'reg_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['astra']