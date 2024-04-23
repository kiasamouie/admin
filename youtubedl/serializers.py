from rest_framework import serializers
from .models import Track, Playlist, Thumbnail
from core.utils import YoutubeDLHelper
from datetime import datetime, timezone

class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = "__all__"

class TrackSerializer(serializers.ModelSerializer):
    # thumbnails = ThumbnailSerializer(many=True, read_only=True)
    class Meta:
        model = Track
        fields = "__all__"
    
    def is_valid(self, ydl: YoutubeDLHelper = None):
        self.initial_data['upload_id'] = self.initial_data['id']
        self.initial_data['timestamp'] = datetime.fromtimestamp(self.initial_data['timestamp'], tz=timezone.utc)
        for k in ['view_count', 'like_count', 'comment_count', 'genre']:
            if self.initial_data[k] is None:
                self.initial_data[k] = "" if k == 'genre' else 0
        for k in ['id','description','license','formats','thumbnails']:        
            del self.initial_data[k]
        return super().is_valid()

class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)
    class Meta:
        model = Playlist
        fields = "__all__"

    def is_valid(self, ydl: YoutubeDLHelper):
        self.initial_data['upload_id'] = self.initial_data['id']
        self.initial_data['uploader'] = self.initial_data['webpage_url'].split("/")[3]
        self.initial_data['tracks'] = []
        for entry in self.initial_data['entries']:
            track_serializer = TrackSerializer(data=ydl.extract_info(url=entry["url"]))
            if track_serializer.is_valid():
                track = track_serializer.save()
                self.initial_data['tracks'].append(track.id)
            else:
                print(track_serializer.data)
                print(track_serializer.errors)
                exit()
        for k in ['id','_type','entries']:        
            del self.initial_data[k]
        return super().is_valid()