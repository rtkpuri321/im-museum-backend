# serializers.py
from rest_framework import serializers
from .models import UserDetails

class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)  # Set email as required
    password = serializers.CharField(max_length=255, required=True)  # Set password as required

    class Meta:
        model = UserDetails
        fields = ['mobile_no', 'email', 'account_no', 'ifsc', 'vpa', 'password']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()