from rest_framework import serializers
from .models import Absent, AbsentType, AbsentStatusChoices
from oaauth.serializers import UserSerializer
from rest_framework import exceptions
from .utils import get_responder


class AbsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentType
        fields = "__all__"


class AbsentSerializer(serializers.ModelSerializer):
    # read_only: This parameter will only be serialized when serializing the ORM model into a dictionary.
    # write_only: This parameter will only be used when validating the data.
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responder = UserSerializer(read_only=True)
    class Meta:
        model = Absent
        fields = "__all__"

    # Verify whether the absent_type_id exists in the database
    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError("Attendance type does not exist!")
        return value

    # create
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        # Obtain the approver
        responder = get_responder(request)

        # If you are the leader of the board, your leave request can be approved directly.
        if responder is None:
            validated_data['status'] = AbsentStatusChoices.PASS
        else:
            validated_data['status'] = AbsentStatusChoices.AUDITING
        absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
        return absent

    # update
    def update(self, instance, validated_data):
        if instance.status != AbsentStatusChoices.AUDITING:
            raise exceptions.APIException(detail='The already confirmed leave data cannot be modified!')
        request = self.context['request']
        user = request.user
        if instance.responder.uid != user.uid:
            raise exceptions.AuthenticationFailed(detail='You have no authority to handle this attendance record!')
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance