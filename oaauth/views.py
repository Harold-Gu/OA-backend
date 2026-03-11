from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoginSerializer,UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status


class LoginView(APIView):
    def post(self, request):
        # 1.Verify whether the data is available
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token,"user":UserSerializer(user).data})
        else:
            print(serializer.errors)
            return Response({"message":"Parameter verification failed"},status=status.HTTP_400_BAD_REQUEST)