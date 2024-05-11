import jwt
from django.conf import settings
from datetime import datetime, timedelta

def generate_access_token(user_id, expires_in_minutes=60):
    try:
        # Define the expiration time for the token
        expiration_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        # Create the payload containing user ID and expiration time
        payload = {
            'user_id': user_id,
            'exp': expiration_time
        }
        
        # Generate the JWT token with the payload and sign it with the secret key
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        return access_token
    
    except Exception as e:
        print(f"Error generating access token: {e}")
        return None


# from django.core.management.utils import get_random_secret_key

# SECRET_KEY = get_random_secret_key()

# print("SECRET_KEY: ", SECRET_KEY)
