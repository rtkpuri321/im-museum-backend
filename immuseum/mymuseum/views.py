from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *
from .utils.access_token_gen import *
from .utils.upload_images import *
from django.contrib.auth.models import User
from django.db import transaction


# Create your views here.

class UserRegister(APIView):
    def post(self, request):
        serializer = UserDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                user_queryset = UserDetails.objects.filter(username=username)
                if len(user_queryset) == 0:
                    return Response({'error': 'Invalid Username'}, status=status.HTTP_401_UNAUTHORIZED)
                
                user_details = UserDetails.objects.get(username=username)
                if user_details.password == password:
                    # Check if a User with the same email already exists
                    user = User.objects.filter(username=user_details.username).first()

                    # If a User with the same email doesn't exist, create a new User
                    # if not user:
                    #     user = User.objects.create_user(
                    #         username=user_details.username,
                    #         email=user_details.email,
                    #         password=user_details.password  # Note: Password should be properly hashed
                    #     )
                    access_token = generate_access_token(user,user_details.id,'end_user')
                    return Response({'message': 'Login Successful! Welcome to ImMuseum', 'access_token': access_token})
                else:
                    return Response({'error': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":f'Error in login: {str(e)}'}, status=500)

class UserDataAPIView(APIView):
    def get(self, request):
        try:
            # Assuming the user is authenticated, you can access the user object
            # auth_data = request.user
            # user_id = auth_data.id
            user_id = 1
            # Retrieve user data from the UserDetails model
            try:
                user_details = UserDetails.objects.get(id=user_id)
            except UserDetails.DoesNotExist:
                return Response({'error': 'User details not found'}, status=404)
            
            # Serialize the user data
            serializer = GetUserDataSerializer(user_details)
            serialized_data = serializer.data
            
            # Retrieve images associated with the user
            user_images = UserImages.objects.filter(user_details=user_details)
            
            # Serialize the images data
            image_serializer = GetUserImageSerializer(user_images, many=True)
            images_data = image_serializer.data
            
            return Response({"user_data": serialized_data, "images": images_data, "status": True}, status=200)
        except Exception as e:
            print(e)
            return Response({"error":f'Error in uploading image: {str(e)}'}, status=500)

class AddUserImageView(APIView):
    def post(self, request):
        try:
            user_id = 1  # Temporary user_id for testing, replace this with your actual logic to retrieve user_id
            try:
                user = UserDetails.objects.get(id=user_id)
            except UserDetails.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
            with transaction.atomic():
                serializer = UserImageSerializer(data=request.data)
                if serializer.is_valid():
                    image_data = serializer.validated_data
                    image_path = upload_image(image_file=image_data['image'], image_name=image_data['image'].name)
                    
                    # Save image details to database
                    image = UserImages.objects.create(
                        image=image_path,
                        image_desc=image_data['image_desc']
                    )
                    image.user_details = user  
                    image.save()
                
                    return Response({"message": "Image added successfully", "image_id": image.image_id}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))

class GetImage(APIView):
    def get(self, request, user_id, image_name):
        # Check if the file extension indicates an image file
        if not image_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return Response({"error": "Invalid image file format"}, status=400)
        
        # Construct the path to the image
        image_path = os.path.join('images', f'user_{user_id}', image_name)
        
        # Open and read the image file in binary mode
        with open(os.path.join(settings.STATIC_ROOT, image_path), 'rb') as image_file:
            image_data = image_file.read()
        
        # Create a response with the image data and content type
        response = Response(image_data, content_type='image/jpeg')
        return response
