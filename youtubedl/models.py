from django.db import models

class Track(models.Model):
    title = models.CharField(max_length=255)
    s3_file_url = models.URLField(max_length=1024, blank=True, null=True)
    s3_file_key = models.CharField(max_length=1024, blank=True, null=True)
    upload_id = models.IntegerField()
    uploader = models.CharField(max_length=255)
    uploader_id = models.CharField(max_length=255)
    uploader_url = models.URLField(max_length=1024)
    timestamp = models.DateTimeField()
    # description = models.CharField(max_length=255, blank=True)
    duration = models.FloatField()
    webpage_url = models.URLField(max_length=1024)
    # license = models.CharField(max_length=100)
    view_count = models.BigIntegerField()
    like_count = models.BigIntegerField()
    comment_count = models.BigIntegerField()
    repost_count = models.BigIntegerField()
    genre = models.CharField(max_length=50, blank=True)
    extractor = models.CharField(max_length=50)
    webpage_url_basename = models.CharField(max_length=255)
    extractor_key = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    upload_id = models.CharField(max_length=255)
    extractor = models.CharField(max_length=50)
    uploader = models.CharField(max_length=255)
    webpage_url = models.URLField(max_length=1024)
    webpage_url_basename = models.CharField(max_length=255)
    extractor_key = models.CharField(max_length=50)
    tracks = models.ManyToManyField(Track, related_name='playlists')

    def __str__(self):
        return self.title

class Thumbnail(models.Model):
    track = models.ForeignKey(Track, related_name='thumbnails', on_delete=models.CASCADE)
    url = models.URLField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return f'{self.track.title} - {self.width}x{self.height}'
