# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handler', models.CharField(max_length=255)),
                ('actor_object_id', models.PositiveIntegerField()),
                ('action_object_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('target_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=True)),
                ('is_global', models.BooleanField(default=False)),
                ('action_object_content_type', models.ForeignKey(related_name='action_object', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor_content_type', models.ForeignKey(related_name='actor', to='contenttypes.ContentType')),
                ('target_content_type', models.ForeignKey(related_name='target', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('actor_only', models.BooleanField(default=True, verbose_name=b'Only follow actions where the object is the actor')),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.ForeignKey(to='activity.Action')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='stream',
            unique_together=set([('user', 'action')]),
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
