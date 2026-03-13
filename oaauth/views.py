from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import LoginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ResetPwdSerializer
from rest_framework import status

class LoginView(APIView):
    def post(self, request):
        # 1. Verify whether the data is available
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            return Response({'token': token, 'user': UserSerializer(user).data})
        else:

            detail = list(serializer.errors.values())[0][0]
            # When DRF returns a response that is not a 200 status, its error parameter is called "detail", so we also refer to it as "detail" here.
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)




class ResetPwdView(APIView):
    def post(self, request):
        from rest_framework.request import Request
        # Request: It is encapsulated by DRF, rest_framework.request.Request
        # This object is a modification of the Django's HttpRequest object
        serializer = ResetPwdSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            pwd1 = serializer.validated_data.get('pwd1')
            request.user.set_password(pwd1)
            request.user.save()
            return Response()
        else:
            print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
