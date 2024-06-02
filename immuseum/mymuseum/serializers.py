# serializers.py
from rest_framework import serializers
from .models import *

class UserDetailsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)  # Set email as required
    username = serializers.CharField(max_length=20,  required=True)
    password = serializers.CharField(max_length=255, required=True)  # Set password as required

    class Meta:
        model = UserDetails
        fields = ['mobile_no', 'email', 'account_no', 'ifsc', 'vpa', 'password',"username"]

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class GetUserDataSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDetails
        exclude = ['password']  # Exclude the password field from serialization
    def get_profile_pic(self, obj):  # Method name should match the field name
        # Check if the image field is not empty
        if obj.profile_pic:
            try:
                # Convert the ImageFieldFile object to a string
                image_url = str(obj.profile_pic)
                # Extract the file ID from the original Google Drive link
                file_id = image_url.split("/")[5]
                # Construct the new link format
                new_link = f"https://drive.google.com/thumbnail?id={file_id}"
                return new_link
            except IndexError:
                # If the image URL is not in the expected format, return None
                return None
        else:
            # If the image field is empty, return None
            return None

class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImages
        fields = ['image','image_desc']  # Specify the fields to include in the serializer

class GetUserImageSerializer(serializers.ModelSerializer):
    # Define a new field for the converted Google Drive link
    converted_image_link = serializers.SerializerMethodField()

    def get_converted_image_link(self, obj):
        # Check if the image field is not empty
        if obj.image:
            try:
                # Convert the ImageFieldFile object to a string
                image_url = str(obj.image)
                # Extract the file ID from the original Google Drive link
                file_id = image_url.split("/")[5]
                # Construct the new link format
                new_link = f"https://drive.google.com/thumbnail?id={file_id}"
                return new_link
            except IndexError:
                # If the image URL is not in the expected format, return None
                return None
        else:
            # If the image field is empty, return None
            return None

    class Meta:
        model = UserImages
        fields = ['image_id', 'image', 'converted_image_link', 'image_desc', 'image_likes', 'status_flag']

class UserCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserComments
        fields = '__all__'

class ShowUserDetailsSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = UserDetails
        fields = ["id", "username", "profile_pic"]

    def get_profile_pic(self, obj):  # Method name should match the field name
        # Check if the image field is not empty
        if obj.profile_pic:
            try:
                # Convert the ImageFieldFile object to a string
                image_url = str(obj.profile_pic)
                # Extract the file ID from the original Google Drive link
                file_id = image_url.split("/")[5]
                # Construct the new link format
                new_link = f"https://drive.google.com/thumbnail?id={file_id}"
                return new_link
            except IndexError:
                # If the image URL is not in the expected format, return None
                return None
        else:
            # If the image field is empty, return None
            return None

class ShowCommentsSerializer(serializers.ModelSerializer):
    commenter_user_id = ShowUserDetailsSerializer()  # Use nested serializer
    class Meta:
        model = UserComments
        fields = '__all__'