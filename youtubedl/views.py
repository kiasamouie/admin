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

class YoutubeDLView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

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
            ydl = YoutubeDLHelper(request.data["url"])
            response = {
                'success': False,
                'info': ydl.info,
                'parts': ydl.parts,
                'path': ydl.path,
                'url': ydl.url,
                'type': ydl.type,
                # 'download_and_upload_s3': ydl.download_and_upload_s3(),
            }
            # return Response(data=response,status=status.HTTP_200_OK)
            
            # ydl.download([request.data["url"]])
            # response['s3'] = S3Client().upload_file(file_input=ydl.path, object_name=ydl.path.split("/media/",1)[1])

            # S3 upload successful
            if ydl.download_and_upload_s3():
                serializer = TrackSerializer(ydl) if ydl.type == 'track' else PlaylistSerializer(ydl)
                response['s3_uploaded'] = ydl.uploaded
                response['is_valid'] = serializer.is_valid()
                response['errors'] = serializer.errors
                if response['is_valid']:
                    # response['msg'] = f'{ydl.type.capitalize()} downloaded'
                    response['success'] = bool(serializer.save())

            return Response(data=response,status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)
