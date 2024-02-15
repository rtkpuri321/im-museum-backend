from rest_framework import status
from rest_framework.response import Response
from oauth2_provider.models import AccessToken
import datetime
import pytz
from django.utils import timezone

class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude certain URLs from token validation, if needed
        excluded_paths = ['/login/', '/register/']
        if request.path_info not in excluded_paths:
            access_token = request.headers.get('Authorization')
            if access_token:
                try:
                    access_token_obj = AccessToken.objects.get(token=access_token)
                    # Assuming expires is a timezone-naive datetime object
                    expires_naive = access_token_obj.expires.replace(tzinfo=None)  # Remove timezone information

                    expires_aware_utc = timezone.make_aware(expires_naive, timezone=pytz.utc)
                    if expires_aware_utc < timezone.now():
                        return Response({'error': 'Token expired'}, status=status.HTTP_401_UNAUTHORIZED)
                    # Attach user details to the request for further processing
                    request.user = access_token_obj.user
                except AccessToken.DoesNotExist:
                    return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

        response = self.get_response(request)
        return response
