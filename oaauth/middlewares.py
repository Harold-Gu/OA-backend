from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import reverse

OAUser = get_user_model()


class LoginCheckMiddleware(MiddlewareMixin):
    keyword = "JWT"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For those interfaces that do not require login to access, you can list them here.
        self.white_list = [reverse("oaauth:login"), reverse("staff:active_staff"), reverse('home:health_check')]

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 1. If None is returned, the normal execution will occur (including the execution of the view and the code of other middleware)
        # 2. If an HttpResponse object is returned, the view and the subsequent middleware code will not be executed
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()
            request.auth = None
            return None
        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError("Please pass in the JWT!")

            if len(auth) == 1:
                msg = "Invalid JWT request header!"
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = 'Invalid JWT request header! There should be no spaces in the JWT Token!'
                raise exceptions.AuthenticationFailed(msg)

            try:
                jwt_token = auth[1]
                jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
                userid = jwt_info.get('userid')
                try:
                    # Bind the current user to the request object
                    user = OAUser.objects.get(pk=userid)
                    # HttpRequest object: It is a built-in component of Django.
                    request.user = user
                    request.auth = jwt_token
                except:
                    msg = 'User does not exist!'
                    raise exceptions.AuthenticationFailed(msg)
            except ExpiredSignatureError:
                msg = "JWT Token has expired!"
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            print(e)
            return JsonResponse(data={"detail": "Please log in first!"}, status=HTTP_403_FORBIDDEN)