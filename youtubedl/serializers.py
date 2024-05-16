from rest_framework import serializers
from .models import Track, Playlist, Thumbnail
from core.utils import YoutubeDLHelper
from datetime import datetime, timezone
import json

class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ['url', 'width', 'height']

class TrackSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, write_only=True)

    class Meta:
        model = Track
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        ydl = None
        data = kwargs.get('data')
        if args and isinstance(args[0], YoutubeDLHelper):
            ydl = args[0]
            args = args[1:]
            data = ydl.info[0]

        if data and isinstance(data, dict):
            data['upload_id'] = data['id']
            data['timestamp'] = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc)
            for thumbnail in data['thumbnails']:
                for k in ['id', 'preference', 'resolution']:
                    if k in thumbnail:
                        del thumbnail[k]
            default_fields = {
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
                'genre': '',
                'vcodec': 0,
                'video_ext': 0
            }
            for k, default in default_fields.items():
                if data.get(k) is None or data[k] == "none":
                    data[k] = default
            
            remove_keys = [
                'id', '__last_playlist_index', '_filename', '_has_drm', '_type', '_version',
                'aspect_ratio', 'audio_ext', 'description', 'display_id', 'duration_string',
                'epoch', 'filename','filesize_approx','format_id', 'format', 'formats', 'fulltitle','genres', 
                'http_headers','license', 'n_entries', 'original_url', 'playlist_autonumber', 
                'playlist_count','playlist_id', 'playlist_index', 'playlist_title', 
                'playlist_uploader_id','playlist_uploader', 'playlist', 'preference', 'protocol', 
                'release_year','requested_subtitles', 'resolution', 'thumbnail', 'upload_date','url', 'vbr', 
                'video_ext'
            ]
            for k in remove_keys:
                if k in data:
                    del data[k]
            
            kwargs['data'] = data
        super(TrackSerializer, self).__init__(*args, **kwargs)
    
    def to_representation(self, instance):
        """
        Remove the 'thumbnails' field from the serialized output.
        """
        representation = super().to_representation(instance)
        representation.pop('thumbnails', None)  # Remove 'thumbnails' from the output
        return representation

    def create(self, validated_data):
        thumbnails = validated_data.pop('thumbnails', [])
        track = Track.objects.create(**validated_data)
        for thumbnail in thumbnails:
            Thumbnail.objects.create(track=track, **thumbnail)
        return track

class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)
    class Meta:
        model = Playlist
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        ydl = None
        if args and isinstance(args[0], YoutubeDLHelper):
            ydl = args[0]
            args = args[1:]
            data = ydl.info[0]
        if ydl and hasattr(ydl, 'info') and isinstance(ydl.info, list):
            kwargs['data'] = {
                'title': data['playlist_title'],
                'upload_id': data['playlist_id'],
                'uploader': ydl.parts[3],
                'extractor': data['extractor'],
                'extractor_key': data['extractor_key'],
                'webpage_url': ydl.url,
                'webpage_url_basename': ydl.parts[5],
                'tracks': []
            }
            for track in ydl.info:
                serializer = TrackSerializer(data=track)
                if serializer.is_valid():
                    kwargs['data']['tracks'].append(serializer.validated_data)
                else:
                    print(serializer.errors)
                    exit(serializer.errors)
        super(PlaylistSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        tracks = validated_data.pop('tracks', [])
        playlist = Playlist.objects.create(**validated_data)
        for track in tracks:
            thumbnails = track.pop('thumbnails', [])
            track = Track.objects.create(**track)
            for thumbnail in thumbnails:
                Thumbnail.objects.create(**thumbnail, track=track)
            playlist.tracks.add(track)
        return playlist