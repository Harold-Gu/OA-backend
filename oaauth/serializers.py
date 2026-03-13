from rest_framework import serializers
from .models import OAUser,UserStatusChoices,OADepartment
from rest_framework import exceptions


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=20, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("User does not exist.")
            if not user.check_password(password):
                raise serializers.ValidationError("Incorrect password.")
            if user.status == UserStatusChoices.UNACTIVE:
                raise serializers.ValidationError("This user is inactive.")
            elif user.status == UserStatusChoices.LOCKED:
                raise serializers.ValidationError("This user is locked.")
            #In order to reduce the number of times SQL statements are executed,Put 'user' directly into 'attrs'
            attrs['user'] = user


        else:
            raise serializers.ValidationError("Please enter your email and password")
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = OAUser
        exclude = ('password',"groups",'user_permissions')

class ResetPwdSerializer(serializers.Serializer):
    oldpwd = serializers.CharField(min_length=6, max_length=20)
    pwd1 = serializers.CharField(min_length=6, max_length=20)
    pwd2 = serializers.CharField(min_length=6, max_length=20)

    def validate(self, attrs):
        oldpwd = attrs['oldpwd']
        pwd1 = attrs['pwd1']
        pwd2 = attrs['pwd2']

        user = self.context['request'].user
        if not user.check_password(oldpwd):
            raise exceptions.ValidationError("Old password is incorrect!")

        if pwd1 != pwd2:
            raise exceptions.ValidationError("The two new passwords do not match!")
        return attrs