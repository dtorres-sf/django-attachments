# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-28 00:00
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('attachments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='attachment',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]