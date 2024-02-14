from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *
from .utils.access_token_gen import *
from django.contrib.auth.models import User


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
        # try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user_details = UserDetails.objects.get(email=email)
                if user_details.password == password:
                    # Check if a User with the same email already exists
                    user = User.objects.filter(email=user_details.email).first()

                    # If a User with the same email doesn't exist, create a new User
                    if not user:
                        user = User.objects.create_user(
                            username=user_details.username,
                            email=user_details.email,
                            password=user_details.password  # Note: Password should be properly hashed
                        )
                    access_token = generate_access_token(user, 'end_user')
                    return Response({'message': 'Login Successful! Welcome to ImMuseum', 'access_token': access_token})
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({"error":'Error in login. '+str(e)}, status=500)
