from rest_framework import serializers
from .models import OAUser,UserStatusChoices,OADepartment

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