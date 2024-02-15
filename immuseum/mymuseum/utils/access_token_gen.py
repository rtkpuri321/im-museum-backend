from django.contrib.auth import get_user_model
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
import datetime
import uuid

def generate_access_token(user,user_id,role):
    """
    Generate an access token for the user with the given role.
    """
    try:
        token_expiration = oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        access_token = generate_token()
        expires = datetime.datetime.now() + datetime.timedelta(seconds=token_expiration)

        # Generate unique integers for source_refresh_token_id and id_token_id
        source_refresh_token_id = uuid.uuid4().int & (1<<32)-1
        id_token_id = uuid.uuid4().int & (1<<32)-1

        # Save the access token with UserDetails instance
        access_token_obj = AccessToken.objects.create(
            user=user,  # Make sure 'user' is an instance of UserDetails
            token=access_token,
            expires=expires,
            scope=role,  # Assign the role as the scope
            source_refresh_token_id=source_refresh_token_id,
            id_token_id=id_token_id,
            user_id=user_id
        )

        # Add user_id to the token payload
        # access_token_obj.token = {
        #     'access_token': access_token_obj.token,
        #     'end_user_id': user_id  # Include the user_id in the token payload
        # }
        access_token_obj.save()

        return access_token
    except Exception as e:
        print(e)
        raise e

