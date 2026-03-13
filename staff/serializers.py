from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

OAUser = get_user_model()


class AddStaffSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=20, error_messages={"required": "Please enter your username!"})
    email = serializers.EmailField(error_messages={"required": "Please enter your email address!", 'invalid': 'Please enter the correct format of the email address!'})
    password = serializers.CharField(max_length=20, error_messages={"required": 'enter your password'})

    def validate(self, attrs):
        request = self.context['request']
        email = attrs.get('email')

        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use!')


        if request.user.department.leader.uid != request.user.uid:
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
