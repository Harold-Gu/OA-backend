from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response

from .models import Absent, AbsentType, AbsentStatusChoices
from .serializers import AbsentSerializer, AbsentTypeSerializer
from rest_framework.views import APIView
from .utils import get_responder
from oaauth.serializers import UserSerializer

# Create your views here.
# 1. Initiate attendance record (create)
# 2. Handle attendance record (update)
# 3. View one's own attendance list (list?who=my)
# 4. View the attendance list of subordinates (list?who=sub)
class AbsentViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer
    
    def update(self, request, *args, **kwargs):
        # By default, if you want to modify a certain piece of data, you must upload all the fields specified in the serialization of this data.
        # If you only want to modify a part of the data, you can set partial=True in the kwargs.
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            result = queryset.filter(responder=request.user)
        else:
            result = queryset.filter(requester=request.user)

        # result: Represents the data that meets the requirements
        # pageinage_queryset method: Handles the pagination logic processing
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response: In addition to returning the serialized data, it will also return the total amount of data and the URL of the previous page.
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(result, many=True)
        return Response(data=serializer.data)


# 1. leave type
class AbsentTypeView(APIView):
    def get(self, request):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(types, many=True)
        return Response(data=serializer.data)


# 2. Display the approver
class ResponderView(APIView):
    def get(self, request):
        responder = get_responder(request)
        # Serializer: If the serialized object is None, no error will be raised. Instead, an empty dictionary containing all fields except the primary key will be returned.
        serializer = UserSerializer(responder)
        return Response(data=serializer.data)

