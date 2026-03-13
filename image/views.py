from rest_framework.views import APIView
from .serializers import UploadImageSerializer
from rest_framework.response import Response
from shortuuid import uuid
import os
from django.conf import settings


class UploadImageView(APIView):
    def post(self, request):
        # 1. The image is xx.png, xx.py -> xx.png
        # 2. .png/.jpg/.jpeg, .txt/.py
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('image')
            # abc.png => sdfsdafsdjag + '.png'
            # os.path.splitext('abc.png') = ('abc', '.png')
            filename = uuid() + os.path.splitext(file.name)[-1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path, 'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)
            except Exception:
                return Response({
                    "errno": 1,
                    "message": "Image saving failed!"
                })
            # abc.png => /media/abc.png
            file_url = settings.MEDIA_URL + filename
            return Response({
                "errno": 0, # Note: The values are numeric, not strings.
                "data": {
                    "url": file_url, # The "image src" field must be filled in.
                    "alt": "", # Please provide the English translation of the text.
                    "href": file_url # The link to the picture, not necessary.
                }
            })
        else:
            print(serializer.errors)
            return Response({
                "errno": 1, # As long as it is not equal to 0, it is fine.
                "message": list(serializer.errors.values())[0][0]
            })
