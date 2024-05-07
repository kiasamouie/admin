# Generated by Django 5.0.1 on 2024-05-07 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('upload_id', models.IntegerField()),
                ('uploader', models.CharField(max_length=255)),
                ('uploader_id', models.CharField(max_length=255)),
                ('uploader_url', models.URLField(max_length=1024)),
                ('timestamp', models.DateTimeField()),
                ('duration', models.FloatField()),
                ('webpage_url', models.URLField(max_length=1024)),
                ('view_count', models.BigIntegerField()),
                ('like_count', models.BigIntegerField()),
                ('comment_count', models.BigIntegerField()),
                ('repost_count', models.BigIntegerField()),
                ('genre', models.CharField(blank=True, max_length=50)),
                ('webpage_url_basename', models.CharField(max_length=255)),
                ('webpage_url_domain', models.CharField(max_length=255)),
                ('extractor', models.CharField(max_length=50)),
                ('extractor_key', models.CharField(max_length=50)),
                ('url', models.URLField(max_length=1024)),
                ('tbr', models.IntegerField(null=True)),
                ('ext', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thumbnails', to='youtubedl.track')),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('upload_id', models.CharField(max_length=255)),
                ('uploader', models.CharField(max_length=255)),
                ('extractor', models.CharField(max_length=50)),
                ('extractor_key', models.CharField(max_length=50)),
                ('webpage_url', models.URLField(max_length=1024)),
                ('webpage_url_basename', models.CharField(max_length=255)),
                ('tracks', models.ManyToManyField(related_name='playlists', to='youtubedl.track')),
            ],
        ),
    ]