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
                'parts': ydl.parts,
                'path': ydl.path,
                'url': ydl.url,
                'type': ydl.type,
                'download': ydl.download(),
            }
            # return Response(data=response,status=status.HTTP_200_OK)

            # S3 upload successful
            serializer = TrackSerializer(ydl) if ydl.type == 'track' else PlaylistSerializer(ydl)
            response['is_valid'] = serializer.is_valid()
            response['errors'] = serializer.errors
            if response['is_valid']:
                # response['msg'] = f'{ydl.type.capitalize()} downloaded'
                response['success'] = bool(serializer.save())

            return Response(data=response,status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
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
