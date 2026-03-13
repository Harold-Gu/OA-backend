from rest_framework import serializers
from .models import Inform, InformRead
from oaauth.serializers import UserSerializer, DepartmentSerializer
from oaauth.models import OADepartment


class InformReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformRead
        fields = "__all__"

class InformSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)
    # department_ids: This is a list that contains department IDs.
    # If the backend is expected to accept a list, then the use of ListField is necessary: [1,2]
    department_ids = serializers.ListField(write_only=True)
    reads = InformReadSerializer(many=True, read_only=True)

    class Meta:
        model = Inform
        fields = "__all__"
        read_only_fields = ('public', )

    # Rewrite the create method of the Inform object to save it
    def create(self, validated_data):
        request = self.context['request']
        department_ids = validated_data.pop("department_ids")
        # department_ids: ['0', '1', '2']
        # If you want to perform the same operation on all values in a list, you can use the map method

        department_ids = list(map(lambda value: int(value), department_ids))
        if 0 in department_ids:
            inform = Inform.objects.create(public=True, author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids).all()
            inform = Inform.objects.create(public=False, author=request.user, **validated_data)
            inform.departments.set(departments)
            inform.save()
        return inform


class ReadInformSerializer(serializers.Serializer):
    inform_pk = serializers.IntegerField(error_messages={"required": 'Please provide the ID of the inform!'})