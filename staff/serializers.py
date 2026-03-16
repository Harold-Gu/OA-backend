from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

OAUser = get_user_model()


class AddStaffSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=20, error_messages={"required": "Please enter your username!"})
    email = serializers.EmailField(error_messages={"required": "Please enter your email address!", 'invalid': 'Please enter the correct format of the email address!'})
    password = serializers.CharField(max_length=20, error_messages={"required": 'enter your password'})
    department_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        request = self.context['request']
        email = attrs.get('email')

        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use!')

        user = request.user
        is_board = user.department.name == 'Board Department'
        is_leader = user.department.leader_id == user.uid
        is_manager = user.department.manager_id == user.uid

        if not (is_board or is_leader or is_manager):
            raise serializers.ValidationError('Non-department leaders are not allowed to add employees!')
        return attrs


class ActiveStaffSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={"required": "Please enter your email address!", 'invalid': 'Please enter a valid email address format!' })
    password = serializers.CharField(max_length=20, error_messages={"required": 'enter your password'})

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = OAUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Incorrect email or password!")
        attrs['user'] = user
        return attrs


class StaffUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xlsx', 'xls'])],
        error_messages={'required': 'Please upload the file!'}
    )