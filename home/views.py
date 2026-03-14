from rest_framework.views import APIView
from inform.models import Inform, InformRead
from inform.serializers import InformSerializer
from django.db.models import Q
from django.db.models import Prefetch
from rest_framework. response import Response
from absent.models import Absent
from absent.serializers import AbsentSerializer
from oaauth.models import OADepartment
from django.db.models import Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


# @cache_page(60*15)
# def cache_demo_view(request):
#     pass


class LatestInformView(APIView):
    """
    Return the latest 10 notifications
    """
    def get(self, request):
        current_user = request.user
        informs = Inform.objects.prefetch_related(
            Prefetch("reads", queryset=InformRead.objects.filter(user_id=current_user.uid)),
            'departments'
        ).filter(
            Q(public=True) | Q(departments=current_user.department) | Q(author=current_user)
        ).distinct().order_by('-create_time')[:10]

        serializer = InformSerializer(informs, many=True)
        return Response(serializer.data)


class LatestAbsentView(APIView):

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        # Members of the board can view the attendance information of all employees, while non-board members can only see the attendance information of their own departments.
        current_user = request.user
        queryset = Absent.objects
        if current_user.department.name != 'Board Department':
            queryset = queryset.filter(requester__department_id=current_user.department_id)
        queryset = queryset.all()[:10]
        serializer = AbsentSerializer(queryset, many=True)
        return Response(serializer.data)


class DepartmentStaffCountView(APIView):

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        rows = OADepartment.objects.annotate(staff_count=Count("staffs")).values("name", "staff_count")
        # print(rows)
        print('='*10)
        return Response(rows)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"code": 200})