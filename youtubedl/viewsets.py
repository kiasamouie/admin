import os
from django.http import FileResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Track, Playlist, Thumbnail
from .serializers import TrackSerializer, PlaylistSerializer, ThumbnailSerializer

from django.core.exceptions import ObjectDoesNotExist
from core.utils import YoutubeDLHelper
from django.forms.models import model_to_dict

class YoutubeDLViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def list(self, request):
        if request.query_params.get('type') is None:
            return Response(data={'msg': 'Type missing'},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('type') == 'tracks':
            queryset = Track.objects.all()
            serializer = TrackSerializer(queryset, many=True)
        else:
            queryset = Playlist.objects.all()
            serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(methods=['post'], detail=False)
    def download(self, request):
        try:
            ydl = YoutubeDLHelper(request.data["url"])
            response = {
                'success': False,
                'info': ydl.info,
                'path': ydl.path,
                'url': ydl.url,
                'type': ydl.type,
                'platform': ydl.platform,
                'download': ydl.download(),
            }

            # return Response(data=response, status=status.HTTP_200_OK)

            if ydl.type == 'track':
                result = self.handle_download(ydl, TrackSerializer, Track, ydl.info[0]['id'])
            else:
                result = self.handle_download(ydl, PlaylistSerializer, Playlist, ydl.info[0]['playlist_id'])

            response['is_valid'] = result['is_valid']
            response['errors'] = result['errors']
            response['success'] = result['is_valid']

            return Response(data=response, status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError) as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_download(self, ydl, serializer_class, model_class, upload_id):
        try:
            instance = model_class.objects.get(upload_id=upload_id)
            serializer = serializer_class(instance, ydl=ydl)
        except model_class.DoesNotExist:
            serializer = serializer_class(ydl=ydl)
        
        if serializer.is_valid():
            instance = serializer.save()
            return {'instance': instance, 'created': instance._state.adding, 'is_valid': True, 'errors': None}
        else:
            return {'instance': None, 'created': False, 'is_valid': False, 'errors': serializer.errors}
    
    @action(methods=['post'], detail=False)
    def save_track(self, request):
        try:
            response = {
                'success': False,
                'message': 'File not found',
            }

            file_path = request.data.get("dir")
            if os.path.isfile(file_path):
                file_handle = open(file_path, 'rb')
                response = FileResponse(file_handle, as_attachment=True, filename=os.path.basename(file_path))
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return Response(data=response, status=status.HTTP_404_NOT_FOUND)

        except (TokenError, KeyError) as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['get'], detail=False)
    def stats(self, request):
        return Response([
            {
                'title': 'Tracks',
                'total': Track.objects.count(),
                'rate': '0.43%',
                'levelUp': True,
                'levelDown': False,
                'icon': 'faMusic'
            },
            {
                'title': 'Playlists',
                'total': Playlist.objects.count(),
                'rate': '0.43%',
                'levelUp': True,
                'levelDown': False,
                'icon': 'faClipboardList'
            },
            {
                'title': 'Thumbnails',
                'total': Thumbnail.objects.count(),
                'rate': '0.43%',
                'levelUp': True,
                'levelDown': False,
                'icon': 'faImage'
            }
        ], status=status.HTTP_200_OK)
