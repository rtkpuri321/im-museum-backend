# serializers.py
from rest_framework import serializers
from .models import *

class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)  # Set email as required
    username = serializers.CharField(max_length=20,  required=True)
    password = serializers.CharField(max_length=255, required=True)  # Set password as required

    class Meta:
        model = UserDetails
        fields = ['mobile_no', 'email', 'account_no', 'ifsc', 'vpa', 'password']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class GetUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        exclude = ['password']  # Exclude the password field from serialization

class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImages
        fields = ['image','image_desc']  # Specify the fields to include in the serializer
