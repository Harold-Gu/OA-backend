from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'absent'

router = DefaultRouter(trailing_slash=False)
# GET /absent
# POST /absent
# http://localhost:8000/absent/absent
router.register('absent', views.AbsentViewSet, basename='absent')

urlpatterns = [
    # http://localhost:8000/absent/type
    path('type', views.AbsentTypeView.as_view(), name='absenttypes'),
    path('responder', views.ResponderView.as_view(), name='getresponder')
] + router.urls


