from django.http import JsonResponse
from django.conf import settings
import jwt

class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow preflight OPTIONS requests without token validation
        if request.method == 'OPTIONS':
            response = JsonResponse({'detail': 'Preflight request allowed.'})
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            return response

        # Exclude token validation for certain URLs
        excluded_urls = ['/login/', '/register/']
        if request.path_info in excluded_urls:
            return self.get_response(request)

        # Retrieve the token from the request headers
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'error': 'Token is missing'}, status=401)

        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        else:
            return JsonResponse({'error': 'Token is invalid'}, status=401)

        try:
            # Verify the token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Attach the user ID from the token payload to the request for further processing
            auth_data = {
                'user_id': payload['user_id']
            }
            request.auth_data = auth_data
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return self.get_response(request)
