from django.http import JsonResponse
from django.conf import settings
import jwt

class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude token validation for certain URLs
        excluded_urls = ['/login/', '/register/']
        if request.path_info in excluded_urls:
            return self.get_response(request)

        # Retrieve the token from the request headers
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'error': 'Token is missing'}, status=401)

        try:
            # Verify the token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            # Attach the user ID from the token payload to the request for further processing
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return self.get_response(request)
