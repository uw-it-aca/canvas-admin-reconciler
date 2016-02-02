# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('canvas_id', models.IntegerField(unique=True)),
                ('sis_id', models.CharField(max_length=128, unique=True, null=True, blank=True)),
                ('account_name', models.CharField(max_length=256)),
                ('account_short_name', models.CharField(max_length=128)),
                ('account_type', models.CharField(max_length=16, choices=[(b'sdb', b'SDB'), (b'adhoc', b'Ad Hoc'), (b'root', b'Root'), (b'test', b'Test')])),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.NullBooleanField()),
                ('is_blessed_for_course_request', models.NullBooleanField()),
                ('queue_id', models.CharField(max_length=30, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('net_id', models.CharField(max_length=20)),
                ('reg_id', models.CharField(max_length=32)),
                ('role', models.CharField(max_length=32)),
                ('account_id', models.CharField(max_length=128)),
                ('canvas_id', models.IntegerField()),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('provisioned_date', models.DateTimeField(null=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('is_deleted', models.NullBooleanField()),
                ('queue_id', models.CharField(max_length=30, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
