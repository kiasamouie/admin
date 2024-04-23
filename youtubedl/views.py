from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from .models import Track, Playlist, Thumbnail
from .serializers import TrackSerializer, PlaylistSerializer, ThumbnailSerializer

from django.core.exceptions import ObjectDoesNotExist
from core.utils import S3Client, YoutubeDLHelper

from django.forms.models import model_to_dict

import os

class YoutubeDLView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    ydl = None

    def get(self, request):
        if request.query_params.get('type') is None:
            return Response(data={'msg': 'Type missing'},status=status.HTTP_400_BAD_REQUEST)
        
        if request.query_params.get('type') == 'tracks':
            records = Track.objects.all()
            serializer = TrackSerializer(records, many=True)
        else:
            records = Playlist.objects.all()
            serializer = PlaylistSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            self.ydl = YoutubeDLHelper(request.data["url"])
            info = self.ydl.extract_info()
            if self.ydl.type == 'track':
                self.ydl.path = os.path.join(self.ydl.path,f"{info['webpage_url_basename']}.mp3")
            response = {
                'success': False,
                'info': info,
                'path': self.ydl.path,
                'type': self.ydl.type,
            }
            # return Response(data=response,status=status.HTTP_200_OK)

            if self.ydl.exists():
                response['msg'] = f'{self.ydl.type.capitalize()} already exists'
            else:
                # self.ydl.download([request.data["url"]])

                if self.ydl.exists() or True:
                    serializer = TrackSerializer(data=info) if self.ydl.type == 'track' else PlaylistSerializer(data=info)
                    response['is_valid'] = serializer.is_valid(self.ydl)
                    response['errors'] = serializer.errors
                    if response['is_valid']:
                        response['msg'] = f'{self.ydl.type.capitalize()} downloaded'
                        response['path'] = self.ydl.path
                        response['success'] = bool(serializer.save())
                        # response['s3'] = S3Client().upload_file(file_input=self.ydl.path, object_name=self.ydl.path.split("/media/",1)[1])

            return Response(data=response,status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
