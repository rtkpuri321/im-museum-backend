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
                    access_token = generate_access_token(user_details.id)
                    return Response({'message': 'Login Successfull! Welcome to ImMuseum', 'access_token': access_token})
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
            user_id = request.auth_data.get('user_id')
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
            user_id = request.auth_data.get('user_id')  # Temporary user_id for testing, replace this with your actual logic to retrieve user_id
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
    def get(self, request):
        try:
            user_id = request.auth_data.get('user_id')
            # Retrieve user data from the UserDetails model
            try:
                user_details = UserDetails.objects.get(id=user_id)
            except UserDetails.DoesNotExist:
                return Response({'error': 'User details not found'}, status=404)
            
            # Retrieve images associated with the user
            user_images = UserImages.objects.filter(status_flag=1).order_by('-created_on')
            # Extract user interests
            user_interests = user_details.interest

            # Filter images based on user interests
            if user_interests and len(user_interests)>0:
                filtered_images = []
                for image in user_images:
                    for interest in user_interests:
                        if interest.lower() in image.image_desc.lower():
                            filtered_images.append(image)
            else:
                filtered_images = user_images
            
            # Serialize the images data
            image_serializer = GetUserImageSerializer(filtered_images, many=True)
            images_data = image_serializer.data
            
            return Response({"images": images_data, "status": True}, status=200)
        except Exception as e:
            print(e)
            return Response({"error":f'Error in uploading image: {str(e)}'}, status=500)

class ImageLikeAPI(APIView):
    def post(self, request):
        try:
            # Get the image ID from the request data
            image_id = request.data.get('image_id')

            user_id = request.auth_data.get('user_id')

            # Check if the image ID is provided
            if not image_id:
                return Response({'error': 'Image ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Get the image object from the database
                image = UserImages.objects.get(image_id=image_id)
            except UserImages.DoesNotExist:
                return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

            # Increment the like count for the image
            if ImageLikeAudit.objects.filter(image_id=image_id, user_id=user_id, status_flag=1).count()>0:
                if image.image_likes:
                    image.image_likes -= 1
                ImageLikeAudit.objects.filter(image_id=image_id, user_id=user_id).update(status_flag=0)

            else:
                if image.image_likes:
                    image.image_likes += 1
                else:
                    image.image_likes = 1

                if ImageLikeAudit.objects.filter(image_id=image_id, user_id=user_id, status_flag=0).count()>0:
                    ImageLikeAudit.objects.filter(image_id=image_id, user_id=user_id).update(status_flag=1)
                else:
                    ImageLikeAudit.objects.create(image_id=image_id, user_id=user_id)
            
            image.save()
            # Return success response
            return Response({'message': 'Like submitted successfully', 'likes':image.image_likes if image.image_likes else 0, "status":True}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error in liking image: {str(e)}, image_id:{image_id}")
            return Response({'message': 'Error in liking image.', "status":False}, status=500)
        
class AddUserInterest(APIView):
    def post(self, request):
        try:
            # Parse the payload to extract interests
            interests = request.data.get('interest', [])

            # Retrieve the user based on the authenticated user or any other identifier
            user_id = request.auth_data.get('user_id')  # Assuming you have user authentication enabled
            try:
                user = UserDetails.objects.get(id=user_id)
            except UserDetails.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update the user's interests with the new interests provided in the payload
            user.interest = interests

            # Save the user object to persist the changes
            user.save()

            return Response({"message": "Interests added successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Error in adding interests.", "status":False}, status=500)
        
class ViewUserComments(APIView):
    def post(self, request):
        try:
            data = request.data
            # Extract data from the request
            image_id = data.get('image_id')
            user_id = request.auth_data.get('user_id')
            comment = data.get('comment')
            
            # Validate the presence of required fields
            if not image_id and not comment:
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the new comment
            UserComments.objects.create(
                image_id_id=image_id,
                commenter_user_id_id=user_id,
                comment=comment,
                status_flag=1
            )
            
            return Response({'message':'User comment submitted!!!', "status":True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            data = request.query_params
            # Extract data from the request
            image_id = data.get('image_id')
            user_id = request.auth_data.get('user_id')
            
            # Validate the presence of required fields
            if not image_id:
                return Response({'error': 'Missing required fields', 'status': False})
            
            # Create the new comment
            comments = UserComments.objects.filter(
                image_id_id=image_id,
                status_flag=1
            )
            
            # Serialize the newly created comment
            serializer = ShowCommentsSerializer(comments, many=True)
            
            return Response({'message':'User comment submitted!!!', 'comments': serializer.data, "status":True} ,status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateProfilePicView(APIView):
    def post(self, request):
        try:
            user_id = request.auth_data.get('user_id')
            profile_pic = request.FILES.get('profile_pic')

            try:
                user = UserDetails.objects.get(id=user_id)
            except UserDetails.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if not profile_pic:
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Use the helper function to upload the image
            uploaded_image_path = upload_image(profile_pic, profile_pic.name, type='profile_pic')
            
            user.profile_pic = uploaded_image_path
            user.save()

            return Response({'message': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
