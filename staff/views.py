from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from oaauth.models import OADepartment, UserStatusChoices
from oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer, ActiveStaffSerializer, StaffUploadSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse
from OA_backend.celery import debug_task
from .tasks import send_mail_task
from django.views import View
from django.http.response import JsonResponse
from urllib import parse
from rest_framework import generics
from rest_framework import exceptions
from oaauth.serializers import UserSerializer
from .paginations import StaffListPagination
from rest_framework import viewsets
from rest_framework import mixins
from datetime import datetime
import json
import pandas as pd
from django.http.response import HttpResponse
from django.db import transaction



OAUser = get_user_model()

aes = aeser.AESCipher(settings.SECRET_KEY)


def send_active_email(request, email):
    token = aes.encrypt(email)
    # /staff/active?token=xxx
    active_path = reverse("staff:active_staff") + "?" + parse.urlencode({"token": token})
    # http://127.0.0.1:8000/staff/active?token=xxx
    active_url = request.build_absolute_uri(active_path)
    # Send a link to the user. After they click on this link, they will be redirected to the activated page to complete the activation process.
    # To distinguish each user, in the email sending the link, the link should include the email address of this user.
    # For the email address, encryption should be performed: AES
    # http://localhost:8000/staff/active?token=4dFLaXTbbzciZKGm0LIafmhOuuW11S+7kEtqdUSeFf4=
    message = f"Please click on the following link to activate your account.：{active_url}"
    subject = f'Account activation',
    # send_mail(subject, recipient_list=[email], message=message, from_email=settings.DEFAULT_FROM_EMAIL)
    send_mail_task.delay(email, subject, message)


class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer


# The process of activating employees:
# 1. When a user visits the activation link, they will be redirected to a page containing a form. In the view, the token can be obtained. To ensure that the post function knows this token when the user submits the form, we can store the token in the cookie before returning the page.
# 2. Verify whether the email and password uploaded by the user are correct, and decrypt the email in the token and compare it with the email submitted by the user. If they are the same, then the activation is successful.
class ActiveStaffView(View):
    def get(self, request):
        # Obtain the token and store it in the cookie to facilitate its use by the user in the next session.
        # http://127.0.0.1:8000/staff/active?token=6AkzQXz+uIIlV/+I6gXMitowszWkiiDIj9J/XBfctIY=
        token = request.GET.get('token')
        response = render(request, 'active.html')
        response.set_cookie('token', token)
        return response

    def post(self, request):
        # Retrieve the token from the cookie.
        try:
            token = request.COOKIES.get('token')
            email = aes.decrypt(token)
            serializer = ActiveStaffSerializer(data=request.POST)
            if serializer.is_valid():
                form_email = serializer.validated_data.get('email')
                user = serializer.validated_data.get('user')
                if email != form_email:
                    return JsonResponse({"code": 400, "message": "Email error!"})
                user.status = UserStatusChoices.ACTIVED
                user.save()
                return JsonResponse({"code": 200, "message": ""})
            else:
                detail = list(serializer.errors.values())[0][0]
                return JsonResponse({"code": 400, "message": detail})
        except Exception as e:
            print(e)
            return JsonResponse({"code": 400, "message": "Token error!"})


# put /staff/staff/<uid>
class StaffViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin
):
    queryset = OAUser.objects.all()
    pagination_class = StaffListPagination

    def get_serializer_class(self):
        if self.request.method in ['GET', 'PUT']:
            return UserSerializer
        else:
            return AddStaffSerializer

    def get_queryset(self):
        department_id = self.request.query_params.get('department_id')
        realname = self.request.query_params.get('realname')
        date_joined = self.request.query_params.getlist('date_joined[]')

        queryset = self.queryset
        # Logic for returning the list of employees:
        # 1. If it is the board, then return all employees
        # 2. If it is not the board but is the leader of a department, then return the employees of that department
        # 3. If it is neither the board nor the leader of a department, then throw a 403 Forbidden error
        user = self.request.user
        if user.department.name != "Board Department":
            if user.uid != user.department.leader.uid:
                raise exceptions.PermissionDenied()
            else:
                queryset = queryset.filter(department_id=user.department_id)
        else:
            # In the board of directors, filtering is conducted based on department IDs.
            if department_id:
                queryset = queryset.filter(department_id=department_id)

        if realname:
            queryset = queryset.filter(realname__icontains=realname)
        if date_joined:
            try:
                start_date = datetime.strptime(date_joined[0], "%Y-%m-%d")
                end_date = datetime.strptime(date_joined[1], "%Y-%m-%d")
                queryset = queryset.filter(date_joined__range=(start_date, end_date))
            except Exception:
                pass
        return queryset.order_by("-date_joined").all()

    # New employee recruitment
    def create(self, request, *args, **kwargs):
        # If using a view set, the view set will automatically place the request into the context.
        # If directly inheriting fromAPIView, then it is necessary to manually pass the request object to serializer.context.
        serializer = AddStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            realname = serializer.validated_data['realname']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 1. Save user data
            user = OAUser.objects.create_user(email=email, realname=realname, password=password)
            department = request.user.department
            user.department = department
            user.save()

            # 2. Sending activation email I/O: Network request, file reading and writing
            send_active_email(request, email)

            return Response()
        else:
            return Response(data={'detail': list(serializer.errors.values())[0][0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)




class StaffDownloadView(APIView):
    def get(self, request):
        # /staff/download?pks=[x,y]
        # ['x','y'] -> A string in JSON format
        pks = request.query_params.get('pks')
        try:
            pks = json.loads(pks)
        except Exception:
            return Response({"detail": "Employee parameter error!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            current_user = request.user
            queryset = OAUser.objects
            if current_user.department.name != 'Board Department':
                if current_user.department.leader_id != current_user.uid:
                    return Response({'detail': "No permission to download!"}, status=status.HTTP_403_FORBIDDEN)
                else:
                    # If it is the leader of a department, then filter the employees to those who are from this department first.
                    queryset = queryset.filter(department_id=current_user.department_id)
            queryset = queryset.filter(pk__in=pks)
            result = queryset.values("realname", "email", "department__name", 'date_joined', 'status')
            staff_df = pd.DataFrame(list(result))
            staff_df = staff_df.rename(
                columns={"realname": "name", "email": 'email', 'department__name': 'department name', "date_joined": 'joined date',
                         'status': 'status'})
            response = HttpResponse(content_type='application/xlsx')
            response['Content-Disposition'] = "attachment; filename=staff's information.xlsx"
            # 把staff_df写入到Response中
            with pd.ExcelWriter(response) as writer:
                staff_df.to_excel(writer, sheet_name='information of staffs')
            return response
        except Exception as e:
            print(e)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StaffUploadView(APIView):
    def post(self, request):
        serializer = StaffUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')
            current_user = request.user
            if current_user.department.name != 'Board Department' or current_user.department.leader_id != current_user.uid:
                return Response({"detail": "You do not have the permission to access!"}, status=status.HTTP_403_FORBIDDEN)

            staff_df = pd.read_excel(file)
            users = []
            for index, row in staff_df.iterrows():
                # Obtain the department
                if current_user.department.name != 'Board Department':
                    department = current_user.department
                else:
                    try:
                        department = OADepartment.objects.filter(name=row['department']).first()
                        if not department:
                            return Response({"detail": f"{row['department']}inexistence！"}, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response({"detail": "The department list does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    email = row['email']
                    realname = row['name']
                    password = "111111"
                    user = OAUser(email=email, realname=realname, department=department, status=UserStatusChoices.UNACTIVE)
                    user.set_password(password)
                    users.append(user)
                except Exception:
                    return Response({"detail": "Please check the email addresses, names and department names in the document!"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # Atomic operation (transaction)
                with transaction.atomic():
                    # Uniformly add the data to the database.
                    OAUser.objects.bulk_create(users)
            except Exception:
                return Response({"detail": "Error in adding employee data!"}, status=status.HTTP_400_BAD_REQUEST)

            # Send emails asynchronously to each newly added employee
            for user in users:
                send_active_email(request, user.email)
            return Response()
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

class TestCeleryView(APIView):
    def get(self, request):
        # Execute the "debug_task" task asynchronously using Celery.
        debug_task.delay()
        return Response({"detail": "succeed!"})

