from rest_framework import viewsets
from .models import Inform, InformRead
from .serializers import InformSerializer, ReadInformSerializer
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Prefetch


class InformViewSet(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer

    # Notification List:
    # 1. inform.public=True
    # 2. inform.departments includes the department where the user is located # 3. inform.author = request.user
    def get_queryset(self):
        # If multiple conditions are combined through union-find, then the Q function needs to be used.
        queryset = self.queryset.select_related('author').prefetch_related(Prefetch("reads", queryset=InformRead.objects.filter(user_id=self.request.user.uid)), 'departments').filter(Q(public=True) | Q(departments=self.request.user.department) | Q(author=self.request.user)).distinct()
        return queryset
        # for inform in queryset:
        #     inform.is_read = InformRead.objects.filter(inform=inform, user=self.request.user).exsits()
        # return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author.uid == request.user.uid:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['read_count'] = InformRead.objects.filter(inform_id=instance.id).count()
        return Response(data=data)


class ReadInformView(APIView):
    def post(self, request):
        #Notification ID
        serializer = ReadInformSerializer(data=request.data)
        if serializer.is_valid():
            inform_pk = serializer.validated_data.get('inform_pk')
            if InformRead.objects.filter(inform_id=inform_pk, user_id=request.user.uid).exists():
                return Response()
            else:
                try:
                    InformRead.objects.create(inform_id=inform_pk, user_id=request.user.uid)
                except Exception as e:
                    print(e)
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response()
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)